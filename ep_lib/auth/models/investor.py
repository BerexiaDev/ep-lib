from ep_lib.document import Document
from ep_lib.auth.models.jwt_base import JWTbase

class Investor(Document, JWTbase):
    __TABLE__ = "investors"
    
    email = None
    password_hash = None
    full_name = None
    projet = None
    property_or_activity_type = None
    target_regions = None
    investment_amount = None
    company_name= None
    headquarters_location = None
    profile = None
    business_sector = None
    role = None
    phone = None
    terms_accepted = None
    created_on = None
    updated_on = None
    
    
    def __repr__(self):
        return "<Investor '{} {}'>".format(self.full_name,self.email)