import pandas as pd
from loguru import logger
from ep_lib.document import Document

class UnclassifiedAccommodation(Document):
    __TABLE__ = 'unclassified_accommodation'
    
    sip_id = None
    title_fr = None
    title_en = None
    title_es = None
    progress_report = None
    branch = None
    asset_type = None
    new_decree_category = None
    type_of_classification = None
    capacity_in_units = None
    bed_capacity = None
    opening_date = None
    region = None
    city = None
    district_municipality = None
    latitude = None
    longitude = None
    description_fr = None
    description_en = None
    description_es = None
    is_archived = None
    archived_on = None
    status = None
    updated_at = None

    @classmethod
    def insert_herbegement_non_classe_df(cls, df):
        """Insert data for herbegement_non_classe"""
        cls.drop()
        
        records = []
        
        mapping = {
            "id": "sip_id",
            "titre": "title_fr",
            "etat_avancement": "progress_report",
            "thematique": "branch",
            "type_actif": "asset_type",
            "categorie_actif": "new_decree_category",
            "type_classement": "type_of_classification",
            "capacite_unite": "capacity_in_units",
            "capacite_lit": "bed_capacity",
            "date_ouverture": "opening_date",
            "region": "region",
            "prefecture_province": "city",
            "arrondissement_commune": "district_municipality",
            "latitude": "latitude",
            "longitude": "longitude",
            "description": "description_fr",
            "description_en": "description_en",
            "description_es": "description_es",
            "titre_en": "title_en",
            "titre_es": "title_es",
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
            logger.info(f"Inserted {len(inserted_ids)} new UnclassifiedAccommodation records.")
        else:
            logger.info("No new UnclassifiedAccommodation to insert.") 
