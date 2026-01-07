# ep_lib/auth/role_helper.py
from ep_lib.auth.role import Role

class RoleHelper:

    @staticmethod
    def get_role_by_name(name: str):
        role = Role().load({"name": name})
        return role

