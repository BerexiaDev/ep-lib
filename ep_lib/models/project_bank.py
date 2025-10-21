import pandas as pd
from loguru import logger
from ep_lib.document import Document

class ProjectBank(Document):
    __TABLE__ = 'project_bank'
    
    project_id = None
    opportunity_type = None
    
    title_fr = None
    title_en = None
    title_es = None
    
    asset_type = None
    category = None
    classification_type = None
    
    region = None
    city = None
    district_municipality = None
    
    latitude = None
    longitude = None
    
    branch = None  # thematique
    
    description_fr = None
    description_en = None
    description_es = None
    
    area = None
    investment_amount = None
    is_archived = None
    archived_on = None

    @classmethod
    def insert_banque_de_projet_df(cls, df):
        """Insert data for Banque de projet"""
        cls.drop()
        
        records = []
        
        mapping = {
            "id": "project_id",
            "type_opportunite": "opportunity_type",
            "titre": "title_fr",
            "type_actif": "asset_type",
            "categorie": "category",
            "type_classement": "classification_type",
            "region": "region",
            "prefecture_province": "city",
            "arrondissement_commune": "district_municipality",
            "latitude": "latitude",
            "longitude": "longitude",
            "thematique": "branch",
            "description": "description_fr",
            "superficie": "area",
            "investissement": "investment_amount",
            "titre_en": "title_en",
            "titre_es": "title_es",
            "description_en": "description_en",
            "description_es": "description_es",
            "id_foncier": "land_id",
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
            logger.info(f"Inserted {len(inserted_ids)} new ProjectBank records.")
        else:
            logger.info("No new ProjectBank to insert.") 