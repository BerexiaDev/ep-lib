from ep_lib.utils.enums import DocTypeEnum
from ep_lib.models.base_import import BaseImport
from ep_lib.utils.enums import MongoCollectionsEnum

class LandOpportunities(BaseImport):
    __TABLE__ = MongoCollectionsEnum.LAND_OPPORTUNITIES.value
    IMAGE_BUCKET = "land-opportunities"
    DOC_TYPE_ENUM = DocTypeEnum.OPPORTUNITE_FONCIER.value
    JSON_ARRAY_FIELDS = ["polygone"]

    opportunity_id = None
    opportunity_type = None
    investment_type = None
    management_type = None
    classification_type = None
    
    title_fr = None
    title_ar = None
    title_en = None
    title_es = None
    
    branch = None
    region = None
    city = None  # from prefecture_province
    
    location_description_fr = None
    location_description_ar = None
    location_description_en = None
    location_description_es = None
    
    description_fr = None
    description_ar = None
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
    intensity = None

    document_type = None
    is_archived = None
    archived_on = None
    images = None

    polygone = None

    status = None
    updated_at = None
    created_at = None

    @classmethod
    def insert_opportunites_foncier_df(cls, df, drop_collection=True):
        cls.insert_from_df(df, drop_collection)