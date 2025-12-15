from typing import List, Dict
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
        Upsert records based strictly on '<primary_key_field>'.
        - If '<primary_key_field>' exists in record -> Update that specific doc.
        - If '<primary_key_field>' is missing -> Generate new '<primary_key_field>' and Insert.
        - Automatically handles created/updated timestamps.
        """
        if not records:
            return

        operations = []
        if create_date_field or update_date_field:
            now = get_now_utc()

        for rec in records:
            rec_data = rec.copy()
            
            # 1. Identify the ID
            doc_id = rec_data.pop(primary_key_field, None)
            
            if not doc_id:
                doc_id = generate_id() # Generate a new ID if none provided
            
            # Remove any existing creation/update timestamps so the upsert can regenerate them cleanly
            if create_date_field in rec_data:
                del rec_data[create_date_field]
            
            if update_date_field in rec_data:
                del rec_data[update_date_field]
            
            # 2. Prepare the $set payload (Updates applied to BOTH new and existing)
            set_payload = rec_data
            if update_date_field:
                set_payload[update_date_field] = now

            # 3. Prepare the $setOnInsert payload (Applied ONLY to new inserts)
            insert_payload = {}
            if create_date_field:
                insert_payload[create_date_field] = now

            op = UpdateOne(
                filter={primary_key_field: doc_id},
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
    

