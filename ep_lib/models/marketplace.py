import pandas as pd
from loguru import logger
from util.enum import DocTypeEnum
from ep_lib.document import Document
from util.strings import generate_id

class Marketplace(Document):
    __TABLE__ = 'marketplace'
    
    # Basic identification
    id = None
    
    # Opportunity details
    opportunity_type = None
    investment_type = None
    management_type = None
    asset_type = None
    category = None
    classification_type = None
    capacity = None
    
    # Restaurant specific fields
    specialty = None
    fork_rating = None
    seat_count = None
    
    # Location
    region = None
    city = None
    district_municipality = None
    latitude = None
    longitude = None
    
    # Content
    title_fr = None
    branch = None  # thematique
    description_fr = None
    
    # Physical properties
    area = None
    investment_amount = None
    asset_status = None
    
    # Multilingual descriptions
    description_en = None
    description_es = None
    
    # Document type
    document_type = None
    is_archived = None
    archived_on = None
    status = None
    updated_at = None

    @classmethod
    def insert_marketplace_df(cls, df):
        """Insert data for marketplace"""
        cls.drop()
        
        records = []
        
        mapping = {
            "id": "id",
            "type_opportunite": "opportunity_type",
            "type_investissement": "investment_type",
            "type_gestion": "management_type",
            "type_actif": "asset_type",
            "categorie": "category",
            "type_classement": "classification_type",
            "capacite": "capacity",
            "specialite": "specialty",
            "nombre_fourchettes": "fork_rating",
            "nombre_couverts": "seat_count",
            "region": "region",
            "prefecture_province": "city",
            "arrondissement_commune": "district_municipality",
            "latitude": "latitude",
            "longitude": "longitude",
            "titre": "title_fr",
            "thematique": "branch",
            "description": "description_fr",
            "superficie": "area",
            "investissement": "investment_amount",
            "situation_actif": "asset_status",
            "description_opportunite_en": "description_en",
            "description_opportunite_es": "description_es",
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
                    cleand_value = clean_value(row.get(src_col))
                    if src_col == "id" and cleand_value is None:
                        rec[dst_field] = generate_id()
                    else:
                        rec[dst_field] = cleand_value
            
            # Handle multilingual fallbacks
            rec["description_en"] = clean_value(rec.get("description_en")) or rec.get("description_fr")
            rec["description_es"] = clean_value(rec.get("description_es")) or rec.get("description_fr")
            rec["document_type"] = DocTypeEnum.MARKETPLACE.value
            
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
            logger.info(f"Inserted {len(inserted_ids)} new Marketplace records.")
        else:
            logger.info("No new Marketplace to insert.")
