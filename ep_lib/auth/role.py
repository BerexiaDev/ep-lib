from ep_lib.document import Document


class Role(Document):
    __TABLE__ = "roles"
    
    name = None
    description = None
    screens = None
    mode = None
    created_at = None
    updated_at = None
    is_archived = None
    archived_on = None

