from ep_lib.models.base_import import BaseImport
from ep_lib.utils.enums import DocTypeEnum, MongoCollectionsEnum

class ArriveesPostFrontieres(BaseImport):
    __TABLE__ = MongoCollectionsEnum.POST_BORDER_ARRIVALS.value
    DOC_TYPE_ENUM = DocTypeEnum.POST_BORDER_ARRIVALS.value

    STRING_FIELDS = ["sip_id"]
    INT_FIELDS = ["year"]

    sip_id = None
    nomination_structure_fr = None
    nomination_structure_ar = None
    nomination_structure_en = None
    nomination_structure_es = None
    year = None
    month_fr = None
    month_en = None
    month_es = None
    month_ar = None
    structure_type_fr = None
    structure_type_ar = None
    structure_type_en = None
    structure_type_es = None
    visitor_type = None

    status = None
    updated_at = None
    created_at = None

    is_archived = None
    archived_on = None

    @classmethod
    def insert_post_border_arrivals_df(cls, df, drop_collection=True, is_from_moovapps=False):
        cls.insert_from_df(df, drop_collection, is_from_moovapps)