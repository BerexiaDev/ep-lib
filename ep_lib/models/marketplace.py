from ep_lib.utils.enums import DocTypeEnum
from ep_lib.models.base_import import BaseImport
from ep_lib.utils.enums import MongoCollectionsEnum

class Marketplace(BaseImport):
    __TABLE__ = MongoCollectionsEnum.MARKETPLACE.value
    IMAGE_BUCKET = "marketplace"
    DOC_TYPE_ENUM = DocTypeEnum.MARKETPLACE.value

    # Basic identification
    sip_id = None
    
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
    title_ar = None
    title_en = None
    title_es = None
    branch = None  # thematique
    
    # Physical properties
    area = None
    investment_amount = None
    asset_status = None
    
    # Multilingual descriptions
    description_fr = None
    description_ar = None
    description_en = None
    description_es = None
    
    # Document type
    document_type = None
    is_archived = None
    archived_on = None
    images = None

    status = None
    updated_at = None
    created_at = None

    @classmethod
    def insert_marketplace_df(cls, df, drop_collection=True, is_from_moovapps=False):
        cls.insert_from_df(df, drop_collection, is_from_moovapps)
        

