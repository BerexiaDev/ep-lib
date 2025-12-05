from ep_lib.utils.enums import DocTypeEnum
from ep_lib.models.base_import import BaseImport
from ep_lib.utils.enums import MongoCollectionsEnum

class TouristResources(BaseImport):
    __TABLE__ = MongoCollectionsEnum.TOURIST_RESOURCES.value
    IMAGE_BUCKET = "tourism-resources"
    DOC_TYPE_ENUM = DocTypeEnum.RESSOURCE_TOURISTIQUE.value


    resource_id = None
    title_fr = None
    title_ar = None
    title_en = None
    title_es = None
    resource_type = None
    region = None
    city = None
    latitude = None
    longitude = None
    description_fr = None
    description_ar = None
    description_en = None
    description_es = None
    images = None
    intensity = None
    branch = None
    is_archived = None
    archived_on = None

    status = None
    updated_at = None
    created_at = None


    @classmethod
    def insert_ressources_touristiques_df(cls, df, drop_collection=True, is_from_moovapps=False):
        cls.insert_from_df(df, drop_collection, is_from_moovapps)