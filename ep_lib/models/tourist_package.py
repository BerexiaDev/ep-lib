from ep_lib.utils.enums import DocTypeEnum
from ep_lib.models.base_import import BaseImport
from ep_lib.utils.enums import MongoCollectionsEnum


class TouristPackages(BaseImport):
    __TABLE__ = MongoCollectionsEnum.TOURIST_PACKAGES.value
    IMAGE_BUCKET = "tourist-packages"
    DOC_TYPE_ENUM = DocTypeEnum.TOURIST_PACKAGE.value

    sip_id = None
    package_id = None
    circuit_id = None
    resource_id = None
    tourist_resource = None
    duration_hours = None
    duration_days = None
    thematic = None
    district_commune = None
    accommodation_category = None
    title_fr = None
    title_ar = None
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
    images = None

    status = None
    updated_at = None
    created_at = None

    @classmethod
    def insert_packages_touristiques_df(cls, df, drop_collection=True):
       cls.insert_from_df(df, drop_collection)