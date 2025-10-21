import pandas as pd
from loguru import logger
from util.enum import DocTypeEnum
from ep_lib.document import Document

class LandOpportunities(Document):
    __TABLE__ = 'land_opportunities'
    
    opportunity_id = None
    opportunity_type = None
    investment_type = None
    management_type = None
    classification_type = None
    
    title_fr = None
    title_en = None
    title_es = None
    
    branch = None
    region = None
    city = None  # from prefecture_province
    
    location_description_fr = None
    location_description_en = None
    location_description_es = None
    
    description_fr = None
    description_en = None
    description_es = None
    
    latitude = None
    longitude = None
    site_topography = None
    
    asset_type = None
    category = None
    urban_planning_status = None
    environmental_constraints = None
    
    accessibility = None
    availability = None
    transfer_conditions = None
    
    area = None
    investment_amount = None

    document_type = None
    is_archived = None
    archived_on = None

    @classmethod
    def insert_opportunites_foncier_df(cls, df):
        """Insert data for opportunites_foncier"""
        cls.drop()
        
        records = []
        
        mapping = {
            "id": "opportunity_id",
            "type_opportunite": "opportunity_type",
            "type_investissement": "investment_type",
            "type_gestion": "management_type",
            "type_classement": "classification_type",
            "categorie": "category",
            "titre": "title_fr",
            "thematique": "branch",
            "region": "region",
            "prefecture_province": "city",
            "description_localisation": "location_description_fr",
            "description_opportunite": "description_fr",
            "latitude": "latitude",
            "longitude": "longitude",
            "topographie_site": "site_topography",
            "type_actif": "asset_type",
            "affectation_urbanistique": "urban_planning_status",
            "contrainte_environnementale": "environmental_constraints",
            "accessibilite": "accessibility",
            "disponibilite": "availability",
            "conditions_reprise": "transfer_conditions",
            "superficie": "area",
            "investissement": "investment_amount",
            "description_localisation_en": "location_description_en",
            "description_localisation_es": "location_description_es",
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
                    rec[dst_field] = clean_value(row.get(src_col))
            
            # Handle multilingual fallbacks
            rec["title_en"] = clean_value(rec.get("title_en")) or rec.get("title_fr")
            rec["title_es"] = clean_value(rec.get("title_es")) or rec.get("title_fr")
            rec["location_description_en"] = clean_value(rec.get("location_description_en")) or rec.get("location_description_fr")
            rec["location_description_es"] = clean_value(rec.get("location_description_es")) or rec.get("location_description_fr")
            rec["description_en"] = clean_value(rec.get("description_en")) or rec.get("description_fr")
            rec["description_es"] = clean_value(rec.get("description_es")) or rec.get("description_fr")
            rec["document_type"] = DocTypeEnum.OPPORTUNITE_FONCIER.value
            
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
            logger.info(f"Inserted {len(inserted_ids)} new LandOpportunities records.")
        else:
            logger.info("No new LandOpportunities to insert.")