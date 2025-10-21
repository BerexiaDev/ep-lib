import pandas as pd
from loguru import logger
from util.enum import DocTypeEnum
from ep_lib.document import Document

class TouristPackages(Document):
    __TABLE__ = 'tourist_packages'
    
    package_id = None
    resource_id = None
    tourist_resource = None
    duration_hours = None
    duration_days = None
    thematic = None
    district_commune = None
    accommodation_category = None
    title_fr = None
    title_en = None
    title_es = None
    branch = None
    district_municipality = None
    region = None
    latitude = None
    longitude = None
    product_id = None
    product_title = None
    restaurant_id = None
    restaurant_title = None
    document_type = None
    intensity = None
    is_archived = None
    archived_on = None

    @classmethod
    def insert_packages_touristiques_df(cls, df):
        """Insert data for packages_touristiques"""
        cls.drop()
        
        records = []
        
        mapping = {
            "id_circuit": "circuit_id",
            "id_ressource": "resource_id",
            "ressource_touristique": "tourist_resource",
            "duree_heure": "duration_hours",
            "duree_jour": "duration_days",
            "titre": "title_fr",
            "thematique": "thematic",
            "arrondissement_commune": "district_commune",
            "Préfecture/Province": "city",
            "region": "region",
            "latitude": "latitude",
            "longitude": "longitude",
            "id_produit": "product_id",
            "titre_produit": "product_title",
            "id_restaurant": "restaurant_id",
            "titre_restaurant": "restaurant_title",
            "categorie_hebergement": "accommodation_category",
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
            
            # Set document type
            rec["document_type"] = DocTypeEnum.TOURIST_PACKAGE.value
            
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
            logger.info(f"Inserted {len(inserted_ids)} new TouristPackages records.")
        else:
            logger.info("No new TouristPackages to insert.")