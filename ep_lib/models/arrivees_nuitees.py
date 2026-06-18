from ep_lib.models.base_import import BaseImport
from ep_lib.utils.enums import DocTypeEnum, MongoCollectionsEnum

class ArriveesNuitees(BaseImport):
    
    __TABLE__ = MongoCollectionsEnum.EHT_ARRIVALS_NIGHTS.value

    DOC_TYPE_ENUM = DocTypeEnum.EHT_ARRIVALS_NIGHTS.value

    STRING_FIELDS = ["sip_id"]
    INT_FIELDS = ["nights", "year", "arrivals"]


    sip_id = None
    region = None
    province = None
    branch = None
    nights = None
    category = None    
    nationality = None
    arrivals = None
    destination = None
    year = None
    month = None

    status = None
    updated_at = None
    created_at = None

    is_archived = None
    archived_on = None


    @classmethod
    def insert_eht_arrivals_nights_df(cls, df, drop_collection=True, is_from_moovapps=False):
        cls.insert_from_df(df, drop_collection, is_from_moovapps)