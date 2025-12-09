import json
import math
import time
from decimal import Decimal
from numbers import Number
from typing import List, Dict, Any, Tuple

from loguru import logger

from ep_lib.components.openai_singleton import OpenAISingleton
from ep_lib.components.qdruant_singleton import QdrantSingleton



# Type alias for a Point of Interest
POI = Dict[str, str]


def _is_non_finite_number(value: Any) -> bool:
    if isinstance(value, Decimal):
        return not value.is_finite()
    if isinstance(value, Number):
        try:
            return math.isnan(value) or math.isinf(value)
        except TypeError:
            return False
    return False


def _sanitize_non_finite_entries(value: Any, path: str = "") -> Tuple[Any, List[tuple]]:
    issues: List[tuple] = []

    if isinstance(value, dict):
        sanitized: Dict[str, Any] = {}
        for key, nested in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            sanitized_child, child_issues = _sanitize_non_finite_entries(nested, child_path)
            sanitized[key] = sanitized_child
            issues.extend(child_issues)
        return sanitized, issues

    if isinstance(value, list):
        sanitized_list: List[Any] = []
        for idx, item in enumerate(value):
            child_path = f"{path}[{idx}]" if path else f"[{idx}]"
            sanitized_child, child_issues = _sanitize_non_finite_entries(item, child_path)
            sanitized_list.append(sanitized_child)
            issues.extend(child_issues)
        return sanitized_list, issues

    if isinstance(value, Decimal):
        if value.is_finite():
            return float(value), issues
        issues.append((path or "<root>", value))
        return None, issues

    if isinstance(value, Number) and not isinstance(value, bool):
        if _is_non_finite_number(value):
            issues.append((path or "<root>", value))
            return None, issues

    return value, issues




def embed_pois(options: Dict[str, Any]) -> List[List[float]]:

    pois: List[dict] = options.get("pois", [])
    model_name: str = options.get("model_name")
    model_config: Dict[str, Any] = options.get("model_config", {})
    batch_size: int = options.get("batch_size", 500)

    # Switch to specified embedding model if provided
    if model_name:
        OpenAISingleton.set_embedding_model(model_name)

    # Helper to clean and stringify individual POI values
    def clean_value(val: Any) -> str:
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return ""
        return str(val).strip()

    # Prepare texts from configured properties
    props: List[str] = model_config.get("safe_str_clean", [])
    texts: List[str] = []
    for poi in pois:
        parts = [clean_value(poi.get(prop)) for prop in props]
        # Combine non-empty parts into one text string
        joined = " ".join(part for part in parts if part)
        texts.append(joined)

    # Batch embedding requests to respect token limits
    all_embeddings: List[List[float]] = []
    total = len(texts)
    total_batches = (total + batch_size - 1) // batch_size
    logger.info(f"Starting embedding of {total} items in {total_batches} batches (batch size={batch_size})")

    for idx in range(total_batches):
        start = idx * batch_size
        batch_texts = texts[start:start + batch_size]
        batch_num = idx + 1
        logger.info(f"Embedding batch {batch_num}/{total_batches}, texts {start}:{start + len(batch_texts)}")
        # Request embeddings for this batch
        batch_embeddings = OpenAISingleton.get_embeddings(batch_texts)
        all_embeddings.extend(batch_embeddings)
        logger.info(f"Completed batch {batch_num}/{total_batches}")

    logger.info(f"Finished embedding all {total} items.")
    return all_embeddings



def ingest_pois(options: Dict[str, object]) -> None:
    pois: List[POI] = options["pois"]
    embeddings: List[List[float]] = options["embeddings"]
    model_config: Dict = options["model_config"]
    batch_size = options.get("batch_size", 500)  # Default to batches of 500

    # Create objects using schema properties from model config
    schema_properties = model_config.get("schema_properties")
    objects = []

    for poi in pois:
        if schema_properties:
            obj = {}
            for prop in schema_properties:
                prop_name = prop["name"] if isinstance(prop, dict) else str(prop)
                if prop_name in poi:
                    obj[prop_name] = poi[prop_name]
        else:
            obj = dict(poi)
        objects.append(obj)
    
    # Validate embeddings
    valid_embeddings = []
    valid_objects = []
    
    def resolve_display_title(obj: Dict[str, Any]) -> str:
        return (
            obj.get("title_fr")
            or obj.get("title_en")
            or obj.get("title_es")
            or obj.get("title")
            or "Unknown"
        )

    for idx, (obj, embedding) in enumerate(zip(objects, embeddings)):
        if embedding is None or any(_is_non_finite_number(val) for val in embedding):
            logger.warning(
                f"Skipping POI #{idx+1} ('{resolve_display_title(obj)}') due to invalid embedding"
            )
            continue
        
        valid_objects.append(obj)
        valid_embeddings.append(embedding)
    
    if len(valid_objects) < len(objects):
        logger.warning(f"Filtered out {len(objects) - len(valid_objects)} POIs with invalid embeddings")
    
    # Process in batches to avoid overwhelming Qdrant
    total_objects = len(valid_objects)
    total_batches = (total_objects + batch_size - 1) // batch_size  # Ceiling division
    
    logger.info(f"Ingesting {total_objects} POIs into Qdrant in {total_batches} batches of {batch_size}")
    
    for i in range(0, total_objects, batch_size):
        batch_objects = valid_objects[i:i+batch_size]
        batch_embeddings = valid_embeddings[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        
        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_objects)} POIs)")
        
        # Try with retries
        max_retries = 5
        retry_delay = 2
        success = False
        
        for attempt in range(max_retries):
            try:
                points = []
                for obj, vector in zip(batch_objects, batch_embeddings):
                    point_id = obj.get("cid") or obj.get("id") or obj.get("_id")
                    if point_id is None:
                        point_id = f"auto-{batch_num}-{len(points)}"

                    point_id = str(point_id)

                    payload = {**obj}
                    payload.setdefault("cid", point_id)

                    sanitized_payload, payload_issues = _sanitize_non_finite_entries(payload, "payload")
                    if payload_issues:
                        sample = ", ".join(
                            f"{path}=>{repr(value)}" for path, value in payload_issues[:5]
                        )
                        logger.warning(
                            f"Sanitized non-finite values for point '{point_id}' (replaced with None) -> {sample}"
                        )
                        if len(payload_issues) > 5:
                            logger.warning(
                                f"Additional non-finite locations omitted ({len(payload_issues) - 5} more)"
                            )

                    points.append(
                        {
                            "id": point_id,
                            "vector": vector,
                            "payload": sanitized_payload,
                        }
                    )

                try:
                    json.dumps(points, allow_nan=False)
                except ValueError as json_err:
                    logger.error(
                        f"JSON encoding check failed for batch {batch_num}: {json_err}"
                    )
                    # Keep raising so retry logic surfaces the failure with detailed logs
                    raise

                QdrantSingleton.upsert_points(
                    collection=model_config["schema_name"],
                    points=points,
                )

                logger.info(f"Successfully ingested batch {batch_num}/{total_batches}")
                success = True
                break
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Batch error details: {error_msg}")
                
                if attempt < max_retries - 1:
                    logger.warning(f"Batch {batch_num} failed (attempt {attempt+1}/{max_retries}). Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Batch {batch_num} failed after {max_retries} attempts")
                    raise
        
        if success:
            logger.info(f"Completed {batch_num}/{total_batches} batches ({min(i+batch_size, total_objects)}/{total_objects} POIs)")
    
    logger.success(f"Successfully ingested all {total_objects} POIs into Qdrant")
