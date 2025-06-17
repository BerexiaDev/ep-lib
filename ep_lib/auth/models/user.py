from ep_lib.document import Document
from .jwt_base import JWTbase


class User(Document, JWTbase):
    __TABLE__ = "users"

    email = None
    password_hash = None
    full_name = None
    created_on = None
    modified_on = None
    admin = None
    role = None
    is_active= None
    is_new_user = None
    

    def __repr__(self):
        return "<User '{} {}'>".format(self.first_name,self.last_name)


