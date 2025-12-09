from ep_lib.models.base_import import BaseImport
from ep_lib.utils.enums import DocTypeEnum
from ep_lib.utils.enums import MongoCollectionsEnum


class TouristProduct(BaseImport):
    __TABLE__ = MongoCollectionsEnum.TOURIST_PRODUCTS.value
    IMAGE_BUCKET = "tourist-products"
    STRING_FIELDS = ["sip_id"]
    INT_FIELDS = ["opening_date"]
    
    sip_id = None
    title_fr = None
    title_ar = None
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
    description_ar = None
    description_en = None
    description_es = None

    document_type = None
    intensity = None
    images = None

    status = None
    updated_at = None
    created_at = None


    @classmethod
    def _determine_doc_type(cls, record: dict):
        """Override base method for complex logic"""
        return cls._get_doc_type(
            record.get("asset_type"), 
            record.get("new_decree_category")
        )
    
    @classmethod
    def _get_doc_type(cls, asset_type: str, new_decree_category: str):
        """
        Get the document type based on asset type and new decree category.
        Args:
            asset_type:
            new_decree_category:

        Returns:
            The document type as a string or None if no match is found.
        """
        # 1) normalize inputs - handle None values
        if asset_type is None:
            asset_key = ""
        else:
            asset_key = asset_type.strip().lower()
        
        if new_decree_category is None:
            decree_key = ""
        else:
            decree_key = new_decree_category.strip().lower()

        # 2) special override: if asset is "aménagement" AND decree is "signalétique"
        if asset_key == "aménagement" and decree_key == "signalétique":
            return DocTypeEnum.SIGNALETIQUE_TOURISTIQUE.value

        # 3) general mapping
        _MAP = {
            "hébergement":  DocTypeEnum.HEBERGEMENT_TOURISTIQUE.value,
            "animation":    DocTypeEnum.ANIMATION_TOURISTIQUE.value,
            "aménagement":  DocTypeEnum.AMENAGEMENT_TOURISTIQUE.value,
        }

        return _MAP.get(asset_key)

    @classmethod
    def insert_produits_touristiques_df(cls, df, drop_collection=True, is_from_moovapps=False):
        cls.insert_from_df(df, drop_collection, is_from_moovapps)
        
