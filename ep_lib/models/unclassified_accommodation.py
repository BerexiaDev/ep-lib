from ep_lib.models.base_import import BaseImport
from ep_lib.utils.enums import MongoCollectionsEnum


class UnclassifiedAccommodation(BaseImport):
    __TABLE__ = MongoCollectionsEnum.UNCLASSIFIED_ACCOMMODATION.value
    IMAGE_BUCKET = "unclassified-accommodation"
    INT_FIELDS = ["opening_date"]
    STRING_FIELDS = ["sip_id"]

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
    intensity = None
    is_archived = None
    archived_on = None
    images = None

    status = None
    updated_at = None
    created_at = None

    @classmethod
    def insert_herbegement_non_classe_df(cls, df, drop_collection=True, is_from_moovapps=False):
        cls.insert_from_df(df, drop_collection, is_from_moovapps)