from typing import Any, List, Dict
from app.main import mongo
from ep_lib.utils.strings import generate_id
from loguru import logger
from pymongo import UpdateOne
from ep_lib.utils.date_utils import get_now_utc


class Document:
    __TABLE__ = None
    _id = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    # @property
    def db(self, **kwargs):
        return mongo.db[self.__TABLE__]

    def save(self, **kwargs):
        self._id = self._id or generate_id()
        data = self.to_dict()
        if self._id:
            result = self.db(**kwargs).update_one(
                {'_id': self._id},
                {'$set': data},
                upsert=True
            )
            if result.upserted_id:
                self._id = result.upserted_id
        return self

    def load(self, query=None, **kwargs):
        if not query:
            query = {'_id': self._id}
        result = self.db(**kwargs).find_one(query)
        if not result:
            return None
        self.from_dict(result)
        return self

    def update(self, modifier: Dict, **kwargs):
        """
        Updates the current document in the database using a MongoDB modifier.
        Example: doc.update({"$set": {"status": "archived"}})
        """
        if not self._id:
            logger.warning("Cannot update a document that hasn't been saved (no _id).")
            return None
            
        return self.db(**kwargs).update_one({'_id': self._id}, modifier)

    @classmethod
    def update_by_filter(cls, filter: Dict[str, Any], modifier: Dict[str, Any], **kwargs):
        """
        Update one document matching the given filter using a MongoDB modifier.

        Example:
            Model.update_by_filter(
                {"_id": doc_id},
                {"$set": {"sync_status.qdrant": True}}
            )
        """
        if not isinstance(filter, dict) or not filter:
            logger.warning("update_by_filter called with empty or invalid filter")
            return None

        if not isinstance(modifier, dict) or not modifier:
            logger.warning("update_by_filter called with empty or invalid modifier")
            return None

        return cls.db(**kwargs).update_one(filter, modifier)
        

    @classmethod
    def update_many(cls, query: Dict, modifier: Dict, **kwargs):
        """
        Updates multiple documents matching the query.
        Example: Document.update_many({"status": "pending"}, {"$set": {"status": "done"}})
        """
        return cls().db(**kwargs).update_many(query, modifier)

    def delete(self, query=None, **kwargs):
        if self.id:
            if not query:
                query = {'_id': self._id}
            self.db(**kwargs).delete_one(query)
        return self

    def to_dict(self):
        return self.__dict__

    def from_dict(self, d):
        if d:
            self.__dict__ = d
        else:
            self.id = None
        return self

    @classmethod
    def get_all(cls, query=None, skip=0, limit=0, sort=None, random_sample=False, collation=None, **kwargs):
        """Return documents matching *query* with optional sampling.

        When ``random_sample`` is True and a positive ``limit`` is provided, the
        query is executed through an aggregation pipeline that performs a
        ``$sample`` stage. This yields a randomized subset of documents while
        respecting the provided filters and limit.
        """

        query = query or {}
        collection = cls().db(**kwargs)

        if random_sample and limit > 0:
            pipeline = []
            if query:
                pipeline.append({"$match": query})
            pipeline.append({"$sample": {"size": limit}})
            if collation:
                cursor = collection.aggregate(pipeline, collation=collation)
            else:
                cursor = collection.aggregate(pipeline)
            return [cls(**r) for r in cursor]

        if collation:
            cursor = collection.find(query, collation=collation)
        else:
            cursor = collection.find(query)
        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)

        return [cls(**r) for r in cursor]

    @classmethod
    def delete_all(cls, query):
        if query:
            cls().db().delete_many(query)


    @classmethod
    def count(cls, query = None, **kwargs) -> int:
        """
        Count documents matching a given query.
        If no query is provided, count all documents.
        """
        query = query or {}
        return cls().db(**kwargs).count_documents(query)
    
    @classmethod
    def drop(cls, **kwargs):
        count_before = cls.count()
        logger.info(f"Dropping collection {cls.__TABLE__} with {count_before} documents")
        return cls().db(**kwargs).drop()
    
    @classmethod
    def bulk_insert(cls, data: List[Dict], **kwargs):
        """
        Perform a bulk insert of multiple documents into the collection.
        Ensures each document has a unique _id.
        """
        if not data:
            return []

        # Assign generated _id if not already provided
        for doc in data:
            if '_id' not in doc or not doc['_id']:
                doc['_id'] = generate_id()

        result = cls().db(**kwargs).insert_many(data)
        return result.inserted_ids

    @classmethod
    def bulk_upsert(cls, records: List[Dict], primary_key_field="sip_id", create_date_field="created_at", update_date_field="updated_at"):
        """
        Universal Upsert Logic:
        1. Check 'primary_key_field' (PK):
        - If PK is '_id' and missing in record -> Generate new '_id' (Treat as Insert).
        - If PK is custom (e.g. 'sip_id') and missing -> SKIP record.
        2. _id Generation:
        - If PK is custom: '_id' is generated in $setOnInsert.
        - If PK is '_id': The generated value is used in the Filter (effectively setting it).
        """
        if not records:
            return

        operations = []
        now = get_now_utc() if (create_date_field or update_date_field) else None

        for rec in records:
            rec_data = rec.copy()
            
            # 1. Determine Primary Key Value
            doc_pk_value = rec_data.get(primary_key_field)
            
            # LOGIC SPLIT:
            if primary_key_field == "_id":
                # Case A: PK is _id. 
                # If missing, we generate it (Pure Insert). 
                # If present, we use it (Update).
                if not doc_pk_value:
                    doc_pk_value = generate_id()
            else:
                # Case B: PK is custom (e.g., sip_id).
                # If missing, we strictly SKIP.
                if not doc_pk_value:
                    continue

            # 2. Cleanup Data
            # Remove _id and PK from the payload to prevent duplication/errors in $set
            rec_data.pop("_id", None) 
            rec_data.pop(primary_key_field, None)
            
            # Remove any existing creation/update timestamps so the upsert can regenerate them cleanly
            if create_date_field in rec_data:
                del rec_data[create_date_field]
            
            if update_date_field in rec_data:
                del rec_data[update_date_field]

            # 3. Prepare $set (Updates for everyone)
            set_payload = rec_data
            if update_date_field:
                set_payload[update_date_field] = now

            # 4. Prepare $setOnInsert (Insert-only defaults)
            insert_payload = {}
            
            if create_date_field:
                insert_payload[create_date_field] = now

            # SPECIAL HANDLING FOR _id GENERATION
            # If the PK is NOT _id, we must generate an _id for the new doc here.
            # (If the PK IS _id, the filter below handles the assignment automatically).
            if primary_key_field != "_id":
                insert_payload["_id"] = generate_id()

            # 5. Build Operation
            op = UpdateOne(
                filter={primary_key_field: doc_pk_value},
                update={
                    "$set": set_payload,
                    "$setOnInsert": insert_payload
                },
                upsert=True
            )
            operations.append(op)

        # Execute
        if operations:
            result = cls().db().bulk_write(operations)
            logger.info(f"Bulk Upsert - Matched/Updated: {result.matched_count}, New Inserts: {result.upserted_count}")


    @classmethod
    def aggregate(cls, pipeline):
        """Perform an aggregation pipeline query."""
        return [cls(**r) for r in cls().db().aggregate(pipeline)]
    
    @classmethod
    def get_all_by_fields(cls, listFields):
        try:
            # Build Mongo projection (map 'id' to '_id' if requested)
            projection = {}
            for f in listFields:
                if f.lower() in ("id",):
                    projection["_id"] = 1
                else:
                    projection[f] = 1

            # projection = {field: 1 for field in listFields}
            cursor = cls().db().find({}, projection)
            return [cls(**result) for result in cursor]
        except Exception as e:
            logger.error(f"Error fetching contacts by fields: {e}")
            return []
