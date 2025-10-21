import pandas as pd
from loguru import logger
from util.enum import DocTypeEnum
from ep_lib.document import Document

class RestaurantProducts(Document):
    __TABLE__ = 'restaurant_products'
    
    sip_id = None
    title_fr = None
    title_en = None
    title_es = None
    progress_report = None
    region = None
    city = None
    district_municipality = None
    seat_count = None
    specialty = None
    latitude = None
    longitude = None
    fork_rating = None
    opening_date = None
    description_fr = None
    description_en = None
    description_es = None

    document_type = None
    intensity = None
    is_archived = None
    archived_on = None
    

    @classmethod
    def insert_produits_restauration_df(cls, df):
        """Insert data for produits_restauration"""
        cls.drop()
        
        records = []
        
        mapping = {
            "id": "sip_id",
            "titre": "title_fr",
            "etat_avancement": "progress_report",
            "region": "region",
            "prefecture_province": "city",
            "arrondissement_commune": "district_municipality",
            "nombre_couverts": "seat_count",
            "latitude": "latitude",
            "longitude": "longitude",
            "nombre_fourchettes": "fork_rating",
            "date_ouverture": "opening_date",
            "description": "description_fr",
            "description_en": "description_en",
            "description_es": "description_es",
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
            rec["document_type"] = DocTypeEnum.RESTAURATION_PRODUCT.value
            
            # Cast lat/long to float
            for coord_field in ["latitude", "longitude"]:
                if coord_field in rec and rec[coord_field] is not None:
                    try:
                        rec[coord_field] = float(rec[coord_field])
                    except (ValueError, TypeError):
                        rec[coord_field] = None
            
            # Handle opening_date conversion
            od = rec.get("opening_date")
            if od:
                try:
                    rec["opening_date"] = int(od)
                except (ValueError, TypeError):
                    rec["opening_date"] = None

            records.append(rec)
        
        if records:
            inserted_ids = cls.bulk_insert(records, ordered=False)
            logger.info(f"Inserted {len(inserted_ids)} new RestaurantProducts records.")
        else:
            logger.info("No new RestaurantProducts to insert.")