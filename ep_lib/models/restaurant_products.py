from ep_lib.utils.enums import DocTypeEnum
from ep_lib.models.base_import import BaseImport
from ep_lib.utils.enums import MongoCollectionsEnum


class RestaurantProducts(BaseImport):
    __TABLE__ = MongoCollectionsEnum.RESTAURANT_PRODUCTS.value
    IMAGE_BUCKET = "restaurant-products"
    DOC_TYPE_ENUM = DocTypeEnum.RESTAURATION_PRODUCT.value
    INT_FIELDS = ["opening_date"]
    STRING_FIELDS = ["sip_id"]

    sip_id = None
    title_fr = None
    title_en = None
    title_es = None
    title_ar = None
    progress_report = None
    region = None
    city = None
    district_municipality = None
    seat_count = None
    specialty = None
    latitude = None
    longitude = None
    fork_rating = None
    opening_date = None
    description_fr = None
    description_ar = None
    description_en = None
    description_es = None

    document_type = None
    intensity = None
    is_archived = None
    archived_on = None
    images = None
    
    status = None
    updated_at = None
    created_at = None


    @classmethod
    def insert_produits_restauration_df(cls, df, drop_collection=True, is_from_moovapps=False):
        cls.insert_from_df(df, drop_collection, is_from_moovapps)