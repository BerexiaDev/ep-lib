from ep_lib.models.base_import import BaseImport
from ep_lib.utils.enums import DocTypeEnum
from ep_lib.utils.enums import MongoCollectionsEnum



class AccommodationOpportunities(BaseImport):
    __TABLE__ = MongoCollectionsEnum.ACCOMMODATION_OPPORTUNITIES.value
    IMAGE_BUCKET = "accommodation-opportunities"
    DOC_TYPE_ENUM = DocTypeEnum.OPPORTUNITE_HEBERGEMENT.value
    STRING_FIELDS = ["sip_id"]

    sip_id = None
    opportunity_type = None
    investment_type = None
    management_type = None
    asset_type = None
    category = None
    classification_type = None
    capacity = None
    title_fr = None
    title_ar = None
    title_en = None
    title_es = None
    branch = None
    region = None
    city = None
    district_municipality = None
    description_fr = None
    description_ar = None
    description_en = None
    description_es = None
    latitude = None
    longitude = None
    area = None
    investment_amount = None
    asset_status = None
    document_type = None
    is_archived = None
    archived_on = None
    images = None

    status = None
    updated_at = None
    created_at = None

    @classmethod
    def insert_opportunites_hebergement_df(cls, df, drop_collection=True, is_from_moovapps=False):
        cls.insert_from_df(df, drop_collection, is_from_moovapps)