from flask import current_app
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointIdsList
from typing import Optional, List, Dict, Any
from loguru import logger

class QdrantSingleton:
    _instance: Optional['QdrantSingleton'] = None
    _client: Optional[QdrantClient] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QdrantSingleton, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_client(cls) -> QdrantClient:
        """
        Lazily initialize and return a singleton Qdrant client.
        """
        if cls._client is None:
            url = current_app.config.get("QDRANT_URL")
            qdrant_url = url
            api_key = current_app.config.get("QDRANT_API_KEY", None)

            cls._client = QdrantClient(
                url=qdrant_url,
                api_key=api_key
            )
        return cls._client

    # Health check
    @classmethod
    def ping(cls) -> Dict[str, Any]:
        """
        Simple health check to ensure Qdrant is reachable.
        """
        client = cls.get_client()
        try:
            response = client.get_collections()
            logger.info("✅ Qdrant connection successful.")
            return response.dict()
        except Exception as e:
            logger.error(f"❌ Qdrant ping failed: {e}")
            raise

    # Create collection if not exists
    @classmethod
    def create_collection_if_not_exists(
        cls,
        name: str,
        vector_size: int = 1536,
        distance: Distance = Distance.COSINE
    ) -> None:
        """
        Creates a Qdrant collection if it doesn't already exist.
        """
        client = cls.get_client()
        collections = client.get_collections().collections
        existing_names = [c.name for c in collections]

        if name not in existing_names:
            logger.info(f"🆕 Creating Qdrant collection '{name}'...")
            client.recreate_collection(
                collection_name=name,
                vectors_config=VectorParams(size=vector_size, distance=distance)
            )
        else:
            logger.debug(f"Collection '{name}' already exists.")

    @classmethod
    def create_schema(
        cls,
        schema_name: str,
        vector_size: Optional[int] = None,
        distance: Distance = Distance.COSINE,
    ) -> None:
        """Create a Qdrant collection acting as a schema container."""
        client = cls.get_client()

        resolved_vector_size = (
            vector_size
            or current_app.config.get("QDRANT_VECTOR_SIZE")
            or 1536
        )

        # Allow distance override via config using the Distance enum name.
        distance_name = current_app.config.get("QDRANT_DISTANCE")
        resolved_distance = distance
        if isinstance(distance_name, str):
            try:
                resolved_distance = Distance[distance_name.upper()]
            except KeyError:
                logger.warning(
                    f"Unknown QDRANT_DISTANCE '{distance_name}', falling back to {distance}."
                )

        try:
            client.get_collection(schema_name)
            logger.info(f"Schema '{schema_name}' already exists in Qdrant.")
            return
        except Exception:
            logger.debug(f"Schema '{schema_name}' not found; creating new collection.")

        client.create_collection(
            collection_name=schema_name,
            vectors_config=VectorParams(size=resolved_vector_size, distance=resolved_distance),
        )
        logger.info(f"Schema '{schema_name}' created successfully in Qdrant.")

    @classmethod
    def delete_schema(cls, schema_name: str) -> bool:
        """Delete the Qdrant collection backing the given schema name."""
        client = cls.get_client()
        try:
            client.delete_collection(collection_name=schema_name)
            logger.info(f"Schema '{schema_name}' deleted successfully from Qdrant.")
            return True
        except Exception as exc:
            logger.error(f"Failed to delete schema '{schema_name}' from Qdrant: {exc}")
            return False

    # Upsert data (id, vector, payload)
    @classmethod
    def upsert_points(
        cls,
        collection: str,
        points: List[Dict[str, Any]]
    ) -> None:
        """
        Upserts multiple points into Qdrant.
        Each point = { "id": str|int, "vector": [float], "payload": dict }
        """
        client = cls.get_client()
        try:
            client.upsert(collection_name=collection, points=points)
            logger.info(f"✅ Upserted {len(points)} points into '{collection}'.")
        except Exception as e:
            logger.error(f"❌ Failed to upsert into '{collection}': {e}")
            raise

    # Search by vector + optional filters
    @classmethod
    def search(
        cls,
        collection: str,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs vector search in Qdrant with optional filters.
        Filters follow Qdrant's filter syntax (dict).
        """
        client = cls.get_client()
        try:
            results = client.search(
                collection_name=collection,
                query_vector=query_vector,
                query_filter=filters,
                limit=limit
            )
            return [r.model_dump() for r in results]
        except Exception as e:
            logger.error(f"❌ Qdrant search failed: {e}")
            raise

    @classmethod
    def delete_point(cls, collection_name: str, point_id: str) -> None:
        """
        Deletes a single point by ID from Qdrant.
        """
        client = cls.get_client()
        try:
            client.delete(
                collection_name=collection_name,
                points_selector=PointIdsList(points=[point_id])
            )
            logger.info(f"🗑️ Deleted point {point_id} from {collection_name}")
        except Exception as e:
            logger.error(f"❌ Failed to delete point {point_id}: {e}")
            raise