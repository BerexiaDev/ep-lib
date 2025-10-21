import pandas as pd
from loguru import logger
from util.enum import DocTypeEnum
from ep_lib.document import Document

class LandResources(Document):
    __TABLE__ = 'land_resources'
    
    resource_id = None
    region = None
    city = None
    district_municipality = None
    
    land_type = None
    land_regime = None
    area = None
    site_topography = None
    
    urban_planning_status = None
    environmental_constraints = None
    accessibility = None
    availability = None
    transfer_conditions = None
    
    latitude = None
    longitude = None
    
    branch = None           # thematique
    investment_amount = None
    
    title_fr = None
    title_en = None
    title_es = None
    
    images = None

    document_type = None
    intensity = None
    is_archived = None
    archived_on = None
    status = None
    updated_at = None

    @classmethod
    def insert_ressources_foncieres_df(cls, df):
        """Insert data for ressources_foncieres"""
        cls.drop()
        
        records = []
        
        mapping = {
            "id": "resource_id",
            "region": "region",
            "prefecture_province": "city",
            "arrondissement_commune": "district_municipality",
            "type_foncier": "land_type",
            "regime_foncier": "land_regime",
            "superficie": "area",
            "topographie": "site_topography",
            "affectation_urbanistique": "urban_planning_status",
            "contrainte_environnementale": "environmental_constraints",
            "accessibilite": "accessibility",
            "disponibilite": "availability",
            "condition_reprise": "transfer_conditions",
            "latitude (X)": "latitude",
            "longitude (Y)": "longitude",
            "thematique": "branch",
            "investissement": "investment_amount",
            "titre_en": "title_en",
            "titre_es": "title_es",
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
            rec["title_fr"] = None  # No title_fr in the headers
            rec["title_en"] = clean_value(rec.get("title_en")) or rec.get("title_fr")
            rec["title_es"] = clean_value(rec.get("title_es")) or rec.get("title_fr")
            rec["document_type"] = DocTypeEnum.RESSOURCE_FONCIERE.value
            
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
            logger.info(f"Inserted {len(inserted_ids)} new LandResources records.")
        else:
            logger.info("No new LandResources to insert.")
