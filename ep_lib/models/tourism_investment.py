from ep_lib.models.base_import import BaseImport
from ep_lib.utils.enums import MongoCollectionsEnum

class TourismInvestment(BaseImport):
    __TABLE__ = MongoCollectionsEnum.TOURISM_INVESTMENT.value
    IMAGE_BUCKET = "tourism-investment"
	
    sip_id = None
    region = None	
    prefecture_province = None	
    arrondissement_commune = None	
    type_actif = None	
    categorie = None	
    type_classement = None	
    thematique = None	
    promoteur = None	
    type_gestion = None	
    nationalite = None	
    profil_investisseur = None	
    date_ouverture = None	
    etat_avancement = None	
    investissement_touristique = None	
    emplois_directs = None
    intensity = None
    is_archived = None
    archived_on = None
    images = None

    status = None
    updated_at = None
    created_at = None

    @classmethod
    def insert_tourism_investment_df(cls, df, drop_collection=True, is_from_moovapps=False):
        cls.insert_from_df(df, drop_collection, is_from_moovapps)