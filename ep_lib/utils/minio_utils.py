import io
import os
import uuid
import mimetypes
from datetime import timedelta
import mimetypes
import os
from typing import Optional, Tuple
from urllib.parse import urlparse, urlunparse

from flask import current_app
from loguru import logger
from minio import Minio
from minio.error import S3Error
from ep_lib.utils.conts import ALLOWED_EXTENSIONS
from werkzeug.utils import secure_filename



def _normalize_endpoint(endpoint: str) -> Tuple[str, Optional[bool]]:
    """
    Normalize endpoint to the format expected by MinIO SDK and infer secure flag if scheme provided.
    """
    if "://" not in endpoint:
        return endpoint, None

    parsed = urlparse(endpoint)
    host = parsed.netloc or parsed.path
    is_secure = parsed.scheme == "https"
    return host, is_secure


def get_minio_client() -> Minio:
    """
    Build a MinIO client from the current Flask app configuration.
    """
    config = current_app.config
    endpoint, inferred_secure = _resolve_endpoint(config)
    secure = config.get("MINIO_SECURE", False) if inferred_secure is None else inferred_secure

    access_key = config.get("MINIO_ROOT_USER")
    secret_key = config.get("MINIO_ROOT_PASSWORD")
    region = config.get("MINIO_REGION") or None

    if not access_key or not secret_key:
        raise RuntimeError("Both MINIO_ROOT_USER and MINIO_ROOT_PASSWORD must be configured.")

    return Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure,
        region=region,
    )


def _resolve_endpoint(config):
    """
    Resolve the MinIO endpoint, falling back to MINIO_PUBLIC_URL when necessary.
    """
    endpoint = config.get("MINIO_ENDPOINT")
    inferred_secure = None

    if endpoint:
        endpoint, inferred_secure = _normalize_endpoint(endpoint)

    if (not endpoint or endpoint == "minio:9000") and config.get("MINIO_PUBLIC_URL"):
        parsed_public = urlparse(config["MINIO_PUBLIC_URL"])
        host = parsed_public.netloc or parsed_public.path
        if host:
            endpoint = host
            if inferred_secure is None:
                inferred_secure = parsed_public.scheme == "https"

    if not endpoint:
        raise RuntimeError("Unable to resolve MinIO endpoint. Set MINIO_ENDPOINT or MINIO_PUBLIC_URL.")

    return endpoint, inferred_secure


def ensure_bucket(client: Minio, bucket_name: str, region: Optional[str] = None) -> None:
    """
    Ensure the target bucket exists, create it if missing.
    """
    try:
        if client.bucket_exists(bucket_name):
            return
        client.make_bucket(bucket_name, location=region) if region else client.make_bucket(bucket_name)
        logger.info(f"Created MinIO bucket '{bucket_name}'.")
    except S3Error as exc:
        if exc.code not in {"BucketAlreadyOwnedByYou", "BucketAlreadyExists"}:
            raise
        logger.debug(f"Bucket '{bucket_name}' already exists: {exc.code}")


def upload_bytes(client: Minio, bucket: str, object_name: str, data: bytes, content_type: Optional[str] = None) -> None:
    """
    Upload raw bytes to MinIO under the specified object name.
    """
    ensure_bucket(client, bucket, current_app.config.get("MINIO_REGION"))
    data_stream = io.BytesIO(data)
    data_stream.seek(0)

    client.put_object(
        bucket_name=bucket,
        object_name=object_name,
        data=data_stream,
        length=len(data),
        content_type=content_type or "application/octet-stream",
    )


def generate_presigned_url(bucket: str, object_name: str, expires_seconds: Optional[int] = None) -> str:
    """
    Generate a presigned GET URL for an object stored in MinIO.
    """
    client = get_minio_client()
    ttl = expires_seconds or current_app.config.get("MINIO_PRESIGNED_TTL", 36000)
    if ttl <= 0:
        raise ValueError("Presigned URL expiry must be greater than zero seconds.")

    try:
        presigned = client.get_presigned_url(
            method="GET",
            bucket_name=bucket,
            object_name=object_name,
            expires=timedelta(seconds=ttl),
        )
        public_base = current_app.config.get("MINIO_PUBLIC_URL")
        if public_base:
            target = urlparse(public_base)
            netloc = target.netloc or target.path
            if netloc:
                parsed = list(urlparse(presigned))
                parsed[0] = target.scheme or parsed[0]
                parsed[1] = netloc
                if target.path not in ("", "/"):
                    parsed[2] = target.path.rstrip("/") + parsed[2]
                presigned = urlunparse(parsed)
            else:
                logger.warning(f"MINIO_PUBLIC_URL '{public_base}' is missing host information.")
        return presigned
    except S3Error as exc:
        logger.error(f"Failed to generate presigned URL for '{bucket}/{object_name}': {exc}")
        raise

def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_content_type(filename):
    """Get MIME type for file"""
    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        extension = os.path.splitext(filename)[1].lower()
        if extension in [".jpg", ".jpeg"]:
            content_type = "image/jpeg"
        elif extension == ".png":
            content_type = "image/png"
        elif extension == ".bmp":
            content_type = "image/bmp"
        elif extension == ".webp":
            content_type = "image/webp"
        elif extension == ".svg":
            content_type = "image/svg+xml"
        elif extension == ".pdf":
            content_type = "application/pdf"
        elif extension == ".xls":
            content_type = "application/vnd.ms-excel"
        elif extension == ".xlsx":
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif extension == ".csv":
            content_type = "text/csv"
        else:
            content_type = "application/octet-stream"
    return content_type

def delete_object(client: Minio, bucket: str, object_name: str) -> None:
    """
    Delete an object from MinIO.
    """
    try:
        client.remove_object(bucket_name=bucket, object_name=object_name)
        logger.info(f"Deleted object '{object_name}' from bucket '{bucket}'.")
    except S3Error as exc:
        logger.error(f"Failed to delete object '{object_name}' from bucket '{bucket}': {exc}")
        raise

def check_object_exists(client: Minio, bucket: str, object_name: str):
    """
    Check if an object exists in MinIO.
    """
    try:
        return client.stat_object(bucket_name=bucket, object_name=object_name)
    except S3Error as exc:
        logger.error(f"Failed to stat object '{object_name}' from bucket '{bucket}': {exc}")
        raise

def download_file_from_minio(bucket_name: str, file_id: str) -> bytes:
    """
    Download a file from MinIO by file ID.
    
    Args:
        bucket_name: Name of the MinIO bucket
        file_id: Object name (file ID) in MinIO
        
    Returns:
        bytes: File content
    """
    try:
        client = get_minio_client()
        
        # Get object from MinIO
        response = client.get_object(bucket_name, file_id)
        file_data = response.read()
        response.close()
        response.release_conn()
        
        return file_data
        
    except S3Error as exc:
        logger.error(f"Failed to download file '{file_id}' from bucket '{bucket_name}': {exc}")
        raise Exception(f"File not found: {exc}")
    except Exception as e:
        logger.error(f"Failed to download file from MinIO: {str(e)}")
        raise Exception(f"Failed to download file from MinIO: {str(e)}")


def upload_response_files_to_minio(files, bucket_name: str):
    """
    Upload multiple files to MinIO for ticketing responses.
    """
    
    try:
        if not files or all(file.filename == '' for file in files):
            return None, "No files selected"
        
        results = []
        client = get_minio_client()
        
        for file in files:
            if file.filename:
                # Secure the filename
                original_filename = secure_filename(file.filename)
                if not original_filename:
                    continue
                
                # Get file extension
                file_ext = os.path.splitext(original_filename)[1].lower()
                
                # Generate unique object name (file ID) for MinIO
                file_id = f"{uuid.uuid4()}{file_ext}"
                
                # Get file content as bytes
                file.seek(0)
                file_data = file.read()
                file.seek(0)  # Reset for potential reuse
                
                # Detect content type
                content_type, _ = mimetypes.guess_type(original_filename)
                if not content_type:
                    content_type = "application/octet-stream"
                
                # Upload to MinIO using upload_bytes
                upload_bytes(client, bucket_name, file_id, file_data, content_type)
                
                # Return file_id as the main identifier for download
                results.append({
                    "file_id": file_id,
                    "filename": original_filename,
                    "size": len(file_data),
                    "content_type": content_type
                })
        
        return results, None
    except Exception as e:
        logger.error(f"Erreur lors de l'upload des fichiers vers MinIO : {e}")
        return None, str(e)
