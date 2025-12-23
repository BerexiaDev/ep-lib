from loguru import logger
from flask import has_app_context
from ep_lib.utils.minio_utils import generate_presigned_url

class  MinioUtilities():

    IMAGE_BUCKET = None
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
        Falls back to the original keys if URL generation fails or no app context.
        """
        if not image_keys:
            return []

        if not has_app_context():
            return image_keys

        urls = []
        for key in image_keys:
            try:
                urls.append(generate_presigned_url(bucket=bucket_name, object_name=key))
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"Failed to build presigned URL for '{key}': {exc}")
                urls.append(key)
        return urls