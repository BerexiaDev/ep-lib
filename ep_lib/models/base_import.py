import json
import pandas as pd
from loguru import logger
from ep_lib.utils.strings import clean_value
from ep_lib.document import Document
from ep_lib.models.minio_utilities import MinioUtilities


class BaseImport(Document, MinioUtilities):
    """
    Abstract base class for all Land and Tourism models.
    Centralizes data cleaning, type casting, and array parsing.
    """

    DOC_TYPE_ENUM = None 
    
    # Dynamic Configurations: specific fields to process automatically
    JSON_ARRAY_FIELDS = [] 
    INT_FIELDS = [] 
    FLOAT_FIELDS = ["latitude", "longitude"]
    

    def __init__(self, **kwargs):
        Document.__init__(self, **kwargs)
        if self.IMAGE_BUCKET:
            MinioUtilities.__init__(self, image_bucket=self.IMAGE_BUCKET, **kwargs)

    @classmethod
    def _process_arrays(cls, record: dict, idx: int) -> dict:
        """
        Dynamically handles any field defined in JSON_ARRAY_FIELDS.
        Converts stringified JSON or lists into Python lists.
        """
        for field in cls.JSON_ARRAY_FIELDS:
            if field in record and record[field] is not None:
                val = record[field]
                try:
                    # if it's a string, try to parse it as JSON
                    if isinstance(val, str):
                        # Clean potential dirty strings before parsing if necessary
                        val = val.strip()
                        if val:
                            record[field] = json.loads(val)
                        else:
                            record[field] = None
                    # if it's already a list or tuple, ensure it's a list
                    elif isinstance(val, (list, tuple)):
                        record[field] = list(val)
                except (json.JSONDecodeError, ValueError, TypeError):
                    logger.warning(f"[{cls.__TABLE__}] Row {idx}: Failed to parse array field '{field}'. Value: {val}")
                    record[field] = None
        return record

    @classmethod
    def _process_floats(cls, record: dict) -> dict:
        """Handles fields that must be strict floats (e.g. latitude, longitude)"""
        for field in cls.FLOAT_FIELDS:
            if field in record and record[field] is not None:
                try:
                    record[field] = float(record[field])
                except (ValueError, TypeError):
                    record[field] = None
        return record

    @classmethod
    def _process_integers(cls, record: dict) -> dict:
        """Handles fields that must be strict integers (e.g. opening_date)."""
        for field in cls.INT_FIELDS:
            if field in record and record[field] is not None:
                try:
                    record[field] = int(float(record[field])) # float cast handles "2020.0" strings
                except (ValueError, TypeError):
                    record[field] = None
        return record

    @classmethod
    def _process_multilingual(cls, record: dict) -> dict:
        """Applies fallback logic: If EN/ES is missing, use FR."""
        # Generic fields usually requiring translation
        translatable = ["title", "description", "location_description"]
        
        for base in translatable:
            fr_key = f"{base}_fr"
            if not record.get(fr_key):
                continue
                
            for lang in ["en", "es"]:
                key = f"{base}_{lang}"
                # Only set if key exists in mapping but value is empty
                if key in record: 
                    record[key] = clean_value(record.get(key)) or record.get(fr_key)
        return record

    @classmethod
    def _determine_doc_type(cls, record: dict):
        """Returns the specific enum value or calculates it if needed."""
        if cls.DOC_TYPE_ENUM:
            return cls.DOC_TYPE_ENUM
        return record.get("document_type")

    @classmethod
    def insert_from_df(cls, df: pd.DataFrame, drop_collection=True):
        """
        Master insertion method.
        """
        try:
            if df is None or df.empty:
                logger.info(f"[{cls.__TABLE__}] No data to insert.")
                return
            
            # IMPORT INSIDE THE METHOD TO BREAK THE CIRCULAR LOOP
            from ep_lib.utils.conts import EXCEL_TO_MONGO_FIELD_MAPPINGS

            mapping = EXCEL_TO_MONGO_FIELD_MAPPINGS.get(cls.__TABLE__)
            if not mapping:
                logger.error(f"[{cls.__TABLE__}] No field mapping found.")
                return

            records = []
            # Pre-filter columns to avoid checking every row
            valid_cols = {src: dst for src, dst in mapping.items() if src in df.columns}

            for idx, row in df.iterrows():
                rec = {}
                for src, dst in valid_cols.items():
                    rec[dst] = clean_value(row.get(src))

                # dynamic Processing
                rec = cls._process_multilingual(rec)
                rec = cls._process_floats(rec)
                rec = cls._process_arrays(rec, idx)
                rec = cls._process_integers(rec)

                # set Document Type
                d_type = cls._determine_doc_type(rec)
                if d_type:
                    rec["document_type"] = d_type

                records.append(rec)

            if not records:
                logger.info(f"[{cls.__TABLE__}] Processed 0 valid records.")
                return

            if drop_collection:
                cls.drop()
                logger.info(f"[{cls.__TABLE__}] Collection dropped.")

            cls.bulk_upsert(records)
            logger.success(f"[{cls.__TABLE__}] Successfully inserted {len(records)} records.")
        
        except Exception as e:
            logger.error(f"[{cls.__TABLE__}] Failed to insert records: {e}")

    
    def to_moovapps_dict(self) -> dict:
        """
        Converts the document instance to a dictionary suitable for Moovapps API insertion.
        The final dict:
        - uses only Excel/Moovapps field names
        - contains exactly the fields defined in MONGO_TO_EXCEL_FIELD_MAPPINGS
        """
        from ep_lib.utils.conts import MONGO_TO_EXCEL_FIELD_MAPPINGS

        record = self.to_dict()
        field_mapping = MONGO_TO_EXCEL_FIELD_MAPPINGS.get(self.__TABLE__, {})

        # Build a dict whose keys are Excel fields and values come from Mongo fields
        # (missing Mongo fields become None)
        transformed_record = {
            excel_field: record.get(mongo_field)
            for mongo_field, excel_field in field_mapping.items()
        }
        return transformed_record