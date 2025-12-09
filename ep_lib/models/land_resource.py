from ep_lib.utils.enums import DocTypeEnum
from ep_lib.models.base_import import BaseImport
from ep_lib.utils.enums import MongoCollectionsEnum

class LandResources(BaseImport):
    __TABLE__ = MongoCollectionsEnum.LAND_RESOURCES.value
    IMAGE_BUCKET = "land-resources"
    DOC_TYPE_ENUM = DocTypeEnum.RESSOURCE_FONCIERE.value
    JSON_ARRAY_FIELDS = ["polygone"]
    STRING_FIELDS = ["resource_id"]

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
    title_ar = None
    title_en = None
    title_es = None
    
    images = None

    document_type = None
    intensity = None
    is_archived = None
    archived_on = None

    polygone = None
    images = None

    status = None
    updated_at = None
    created_at = None


    @classmethod
    def insert_ressources_foncieres_df(cls, df, drop_collection=True, is_from_moovapps=False):
        cls.insert_from_df(df, drop_collection, is_from_moovapps)