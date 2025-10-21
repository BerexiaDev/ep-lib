import pandas as pd
from loguru import logger
from util.enum import DocTypeEnum
from ep_lib.document import Document


class TouristResources(Document):
    __TABLE__ = 'ressources_touristiques'
    
    resource_id = None
    title_fr = None
    title_en = None
    title_es = None
    resource_type = None
    region = None
    city = None
    latitude = None
    longitude = None
    description_fr = None
    description_en = None
    description_es = None
    images = None
    intensity = None
    branch = None
    is_archived = None
    archived_on = None
    status = None
    updated_at = None


    @classmethod
    def insert_ressources_touristiques_df(cls, df):
        """Insert data for ressources_touristiques"""
        cls.drop()
        
        records = []
        
        mapping = {
            "id": "resource_id",
            "titre": "title_fr",
            "type_ressource": "resource_type",
            "thematique": "branch",
            "region": "region",
            "prefecture_province": "city",
            "latitude": "latitude",
            "longitude": "longitude",
            "description": "description_fr",
            "description_en": "description_en",
            "description_es": "description_es",
            "images": "images",
            "intensite": "intensity",
        }
        
        def clean_value(value):
            """Convert pandas NaN to None, handle empty strings and other null-like values"""
            if pd.isna(value):
                return None
            if value == '' or value == 'None' or value == 'null':
                return None
            return value
        
        for idx, row in df.iterrows():
            rec = {}
            for src_col, dst_field in mapping.items():
                if src_col in df.columns:
                    rec[dst_field] = clean_value(row.get(src_col))
            
            # Handle multilingual fallbacks
            rec["title_en"] = clean_value(rec.get("title_en")) or rec.get("title_fr")
            rec["title_es"] = clean_value(rec.get("title_es")) or rec.get("title_fr")
            rec["description_en"] = clean_value(rec.get("description_en")) or rec.get("description_fr")
            rec["description_es"] = clean_value(rec.get("description_es")) or rec.get("description_fr")
            rec["document_type"] = DocTypeEnum.RESSOURCE_TOURISTIQUE.value
            
            # Cast lat/long to float
            for coord_field in ["latitude", "longitude"]:
                if coord_field in rec and rec[coord_field] is not None:
                    try:
                        rec[coord_field] = float(rec[coord_field])
                    except (ValueError, TypeError):
                        rec[coord_field] = None

            records.append(rec)
        
        if records:
            inserted_ids = cls.bulk_insert(records, ordered=False)
            logger.info(f"Inserted {len(inserted_ids)} new TouristResources records.")
        else:
            logger.info("No new TouristResources to insert.") 
