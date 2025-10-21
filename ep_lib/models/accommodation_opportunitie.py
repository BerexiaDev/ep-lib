import pandas as pd
from loguru import logger
from util.enum import DocTypeEnum
from ep_lib.document import Document

class AccommodationOpportunities(Document):
    __TABLE__ = 'accommodation_opportunities'
    
    opportunity_id = None
    opportunity_type = None
    investment_type = None
    management_type = None
    asset_type = None
    category = None
    classification_type = None
    capacity = None
    title_fr = None
    title_en = None
    title_es = None
    branch = None
    region = None
    city = None
    district_municipality = None
    description_fr = None
    description_en = None
    description_es = None
    latitude = None
    longitude = None
    urban_planning_status = None
    accessibility = None
    availability = None
    area = None
    investment_amount = None
    asset_status = None
    transfer_conditions = None
    document_type = None
    is_archived = None
    archived_on = None

    @classmethod
    def insert_opportunites_hebergement_df(cls, df):
        """Insert data for opportunites_hebergement"""
        cls.drop()
        
        records = []
        
        mapping = {
            "id": "opportunity_id",
            "type_opportunite": "opportunity_type",
            "type_investissement": "investment_type",
            "type_gestion": "management_type",
            "type_actif": "asset_type",
            "categorie": "category",
            "type_classement": "classification_type",
            "capacite": "capacity",
            "titre": "title_fr",
            "thematique": "branch",
            "region": "region",
            "prefecture_province": "city",
            "arrondissement_commune": "district_municipality",
            "description_opportunite": "description_fr",
            "latitude": "latitude",
            "longitude": "longitude",
            "affectation_urbanistique": "urban_planning_status",
            "accessibilite": "accessibility",
            "disponibilite": "availability",
            "superficie": "area",
            "investissement": "investment_amount",
            "situation_actif": "asset_status",
            "conditions_reprise": "transfer_conditions",
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
            rec["description_en"] = clean_value(rec.get("description_en")) or rec.get("description_fr")
            rec["description_es"] = clean_value(rec.get("description_es")) or rec.get("description_fr")
            rec["document_type"] = DocTypeEnum.OPPORTUNITE_HEBERGEMENT.value
            
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
            logger.info(f"Inserted {len(inserted_ids)} new AccommodationOpportunities records.")
        else:
            logger.info("No new AccommodationOpportunities to insert.")