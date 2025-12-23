import time

from loguru import logger
from flask import current_app, has_app_context

from ep_lib.utils.minio_utils import generate_presigned_url, get_minio_client


BASE_MINIO_BUCKETS = [
    # Buckets used across Document/MinioUtilities models
    "accommodation-opportunities",
    "attachments",
    "arrivees-nuitees",
    "arrivees-post-frontieres",
    "dynamic-pages",
    "etudes-concepte",
    "investment-projects",
    "land-opportunities",
    "land-resources",
    "marketplace",
    "project-bank",
    "restaurant-products",
    "ressources-touristiques",
    "taux-occupation",
    "ticketing-responses",
    "tourism-investment",
    "tourism-offer",
    "tourism-prediction-requests",
    "tourism-resource-modeling",
    "tourism-resources",
    "tourist-packages",
    "tourist-products",
    "unclassified-accommodation",
    # Legacy/misnamed buckets kept for compatibility if they exist in environments
    "investment-project",
    "tourism-prediction-request",
]


def check_minio_health(required_buckets=None, raise_on_error=True, retries=2, retry_delay=0.5):
    """
    Verify MinIO connectivity and presence of required buckets.
    Returns a dict with overall health, missing buckets, and optional error info.
    """
    buckets_to_check = list(dict.fromkeys(required_buckets or BASE_MINIO_BUCKETS))
    result = {"healthy": True, "missing_buckets": [], "error": None}
    start_time = time.monotonic()

    endpoint = region = secure = None
    if has_app_context():
        cfg = current_app.config
        endpoint = cfg.get("MINIO_ENDPOINT") or cfg.get("MINIO_PUBLIC_URL")
        secure = cfg.get("MINIO_SECURE")

    logger.bind(
        bucket_count=len(buckets_to_check),
        buckets=buckets_to_check,
        endpoint=endpoint,
        region=region,
        secure=secure,
    ).info("Starting MinIO health check")

    try:
        client = get_minio_client()
    except Exception as exc:  # noqa: BLE001
        logger.bind(endpoint=endpoint, region=region, secure=secure).error(
            f"Failed to initialize MinIO client: {exc}"
        )
        result["healthy"] = False
        result["error"] = f"MinIO connection failed: {exc}"
        if raise_on_error:
            raise
        return result

    for bucket in buckets_to_check:
        last_exc = None
        try:
            attempts = max(1, retries)
            for attempt in range(1, attempts + 1):
                try:
                    if not client.bucket_exists(bucket):
                        logger.warning(f"Bucket '{bucket}' is missing.")
                        result["missing_buckets"].append(bucket)
                    break
                except Exception as exc:  # noqa: BLE001
                    last_exc = exc
                    logger.warning(
                        f"Bucket existence check failed for '{bucket}' "
                        f"(attempt {attempt}/{attempts}): {exc}"
                    )
                    if attempt < attempts:
                        time.sleep(retry_delay)
        except Exception as exc:  # noqa: BLE001
            last_exc = last_exc or exc
        if last_exc:
            result["missing_buckets"].append(bucket)
            if not result["error"]:
                result["error"] = f"Bucket check failed for '{bucket}': {last_exc}"

    if result["missing_buckets"]:
        result["healthy"] = False
        if not result["error"]:
            result["error"] = f"Missing buckets: {', '.join(result['missing_buckets'])}"

    elapsed = time.monotonic() - start_time
    logger.info(f"MinIO health check result in {elapsed:.2f}s: {result}")

    if raise_on_error and not result["healthy"]:
        raise RuntimeError(result["error"] or "MinIO health check failed.")

    return result


class MinioUtilities:

    IMAGE_BUCKET = None
    _minio_disabled = False  # cache failures to avoid repeated connection attempts

    def __init__(self, image_bucket, **kwargs):
        self.IMAGE_BUCKET = image_bucket
        
        raw_images = kwargs.get("images")
        if raw_images is None and "image" in kwargs:
            raw_images = kwargs.get("image")

        normalized = self.normalize_images(raw_images)
        kwargs["images"] = normalized

        self.image_filenames = normalized  # keep original keys for exports
        self.images = self.prefetch_presigned_urls(self.IMAGE_BUCKET, normalized)

    def normalize_images(self, value):
        """
        Convert persisted image metadata into a list of filenames.
        Accepts existing lists, comma/semicolon separated strings, or single values.
        """
        if value in (None, "", [], ()):
            return []

        if isinstance(value, list):
            return [v.strip() for v in value if isinstance(v, str) and v.strip()]

        if isinstance(value, (set, tuple)):
            return [str(v).strip() for v in value if str(v).strip()]

        if isinstance(value, str):
            tokens = value.replace(";", ",").split(",")
            return [token.strip() for token in tokens if token.strip()]

        return [str(value)]

    def prefetch_presigned_urls(self, bucket_name, image_keys):
        """
        Resolve stored image keys to presigned URLs when MinIO is configured.
        If MinIO is unreachable or URL generation fails, return an empty list.
        """
        if not image_keys:
            return []

        if not has_app_context():
            logger.warning("No Flask app context; skipping presigned URL generation.")
            return []

        if type(self)._minio_disabled:
            return []

        urls = []
        try:
            for key in image_keys:
                urls.append(generate_presigned_url(bucket=bucket_name, object_name=key))
            return urls
        except Exception as exc:  # noqa: BLE001
            # Connection/configuration issues should result in an empty image list
            logger.warning(f"Failed to build presigned URLs for images: {exc}")
            type(self)._minio_disabled = True
            return []
