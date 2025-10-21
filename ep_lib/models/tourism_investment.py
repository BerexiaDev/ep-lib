import pandas as pd
from loguru import logger
from ep_lib.document import Document

class TourismInvestment(Document):
    __TABLE__ = 'tourism_investment'
    
    id = None	
    region = None	
    prefecture_province = None	
    arrondissement_commune = None	
    type_actif = None	
    categorie = None	
    type_classement = None	
    thematique = None	
    promoteur = None	
    type_gestion = None	
    nationalite = None	
    profil_investisseur = None	
    date_ouverture = None	
    etat_avancement = None	
    investissement_touristique = None	
    emplois_directs = None
    is_archived = None
    archived_on = None
    status = None
    updated_at = None

    @classmethod
    def insert_tourism_investment_df(cls, df):
        """Insert data for Banque de projet"""
        cls.drop()
        
        records = []
        
        mapping = {
            "id": "id",
            "region": "region",
            "prefecture_province": "city",
            "arrondissement_commune": "district_municipality",
            "type_actif": "asset_type",
            "categorie": "category",
            "type_classement": "classification_type",
            "thematique": "branch",
            "promoteur": "promoter",
            "type_gestion": "management_type",
            "nationalite": "nationality",
            "profil_investisseur": "investor_profile",
            "date_ouverture": "opening_date",
            "etat_avancement": "progress_report",
            "investissement_touristique": "tourism_investment",
            "emplois_directs": "direct_jobs"
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
