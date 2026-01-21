from datetime import datetime
from flask import Blueprint, request, g

from ep_lib.audit_logger.models.audit_trail import AuditTrail
from ep_lib.audit_logger.utils import get_json_body, get_only_changed_values_and_id, get_action, get_primary_key_value
from ep_lib.audit_logger.utils import IGNORE_PATHS
from ep_lib.auth.user import User

SUCCESS_STATUS_CODES = [200, 201, 204]
DEFAULT_LOG_METHODS = ["POST", "PUT", "DELETE", "PATCH"]
PRIMARY_KEY_MAPPING = {
    "users": "email",
    "portal_users": "email",
    
    # Tourism and accommodation services
    "accommodation_opportunities": "title_fr",
    "land_opportunities": "title_fr", 
    "land_resources": "title_fr",
    "tourist_products": "title_fr",
    "tourist_packages": "title_fr",
    "restaurant_products": "title_fr",
    "ressources_touristiques": "title_fr",
    "unclassified_accommodation": "title_fr",
    "tourism_investment": "title_fr",
    "project_bank": "title_fr",
    "marketplace": "description_fr",
    "tourism_offer": "promoteur",
    
    # Ticketing and request services
    "contact_messages": "subject",
    "investment_project": "fullName",
    "advanced_communication_tools": "name",
    "experiences_metaverse": "name", 
    "tourism_resource_modeling": "name",
    "tourism_prediction_request": "name",
    "etudes_concepte": "study_title",
    
    # Other services
    "dynamic_pages": "page_type",
}
AUDIT_COLLECTION_NAME = "audit_trails"



class AuditBlueprint(Blueprint):
    """
        AuditBlueprint is a blueprint that logs changes to a collection in a MongoDB database.
        
        The blueprint automatically skips logging for requests from the ep-fo frontend
        by checking for the 'X-Frontend-Source' header set to 'ep-fo'.
    """
    def __init__(self, *args, **kwargs):
        self.log_methods = kwargs.pop("log_methods", DEFAULT_LOG_METHODS)
        self.audit_collection = None

        super(AuditBlueprint, self).__init__(*args, **kwargs)
        self.after_request(self.after_data_request)

    def _is_frontend_request(self) -> bool:
        """
        Check if the request comes from the ep-fo frontend.
        Detected by the custom header 'X-Frontend-Source' set to 'ep-fo'.
        """
        frontend_source = request.headers.get('X-Frontend-Source', '').lower()
        return frontend_source == 'ep-fo'

    def _is_loggable(self, response) -> bool:
        # Skip logging for requests from ep-fo frontend
        if self._is_frontend_request():
            return False
            
        # Explicit override from query param
        is_loggable_param = request.args.get("isLoggable")
        if is_loggable_param is not None:
            # Normalize to lowercase for safety
            return is_loggable_param.lower() == "true" and response.status_code in SUCCESS_STATUS_CODES

        # Always log S2I operations regardless of method
        table_name = g.get("table_name", "")
        if table_name.startswith("s2i_"):
            return response.status_code in SUCCESS_STATUS_CODES

        # Default: check method and status
        return request.method in self.log_methods and response.status_code in SUCCESS_STATUS_CODES

    def after_data_request(self, response):
        table_name = g.get("table_name")
        endpoint = request.path
        
        if not table_name or table_name == AUDIT_COLLECTION_NAME or endpoint in IGNORE_PATHS or "swagger" in endpoint or request.method == "OPTIONS" or "search" in endpoint:
            return response
        

        primary_key = PRIMARY_KEY_MAPPING.get(table_name, "name")
        primary_key_splits = primary_key.split(".")

        if self._is_loggable(response):
            old_data = g.get("old_data", None)

            if g.get("new_data"):
                new_data = g.new_data
            else:
                new_data = get_json_body(request)

            if request.method == 'DELETE':
                new_data = new_data or None
                if old_data:
                    if isinstance(old_data, list):
                        old_data = [
                            {
                                "_id": d.get("_id"),
                                "name": get_primary_key_value(primary_key_splits, d)
                            } for d in old_data
                        ]
                    else:
                        _id = old_data.get("_id")
                        primary_value = get_primary_key_value(primary_key_splits, old_data)
                        old_data = {
                            "_id": _id,
                            "name": primary_value
                        }

            elif request.method == 'GET':
                # For S2I operations, we use the data we set in g.new_data
                if table_name.startswith("s2i_"):
                    new_data = g.get("new_data", None)
                    old_data = None
                else:
                    new_data = old_data = None
            else:
                if g.get("new_data") is None:
                    # Always call change detection, even when old_data is None
                    # This ensures we catch changes from None to actual values
                    new_data, old_data = get_only_changed_values_and_id(old_data or {}, new_data)

                    # Only for update operations, if old_value has no data, do not log
                    if request.method in ["PUT", "PATCH"]:
                        if not old_data or (isinstance(old_data, dict) and not old_data) or (isinstance(old_data, list) and len(old_data) == 0):
                            return response

                if response.status_code == 201:
                    if isinstance(new_data, list):
                        final_value = [get_primary_key_value(primary_key_splits, d) for d in new_data]
                        new_data = {
                            "name": ",".join(final_value) if final_value else ""
                        }
                    else:
                        primary_value = get_primary_key_value(primary_key_splits, new_data)
                        new_data = {
                            "name": primary_value
                        }
            
            # Handle S2I operations specially
            if table_name.startswith("s2i_"):
                if table_name.startswith("s2i_import"):
                    # For import operations, create a descriptive message
                    section = new_data.get("section", "all sections") if new_data else "all sections"
                    new_data = {
                        "name": f"Import completed for {section}",
                        "operation": "import",
                        "section": section
                    }
                elif table_name.startswith("s2i_export"):
                    # For export operations, create a descriptive message
                    section = new_data.get("section", "all sections") if new_data else "all sections"
                    new_data = {
                        "name": f"Export completed for {section}",
                        "operation": "export", 
                        "section": section
                    }


            # Handle S2I operations action mapping
            if table_name.startswith("s2i_import"):
                action = "IMPORT"
            elif table_name.startswith("s2i_export"):
                action = "EXPORT"
            else:
                action = get_action(request.method, response.status_code)
            
            # Handle missing Authorization header (e.g., during login requests)
            auth_header = request.headers.get('Authorization')
            user_info = None
            
            if auth_header and ' ' in auth_header:
                try:
                    auth_token = auth_header.split(" ")[1]
                    decode_resp = User.decode_auth_token(auth_token)
                    user = User().load({'_id': decode_resp.get("token")})
                    user_info = user.to_dict()
                except Exception:
                    # If token decoding fails, user_info remains None
                    pass
            
            # Skip audit logging if user_info cannot be determined
            if user_info is None:
                return response
            
            self.create_log(action, table_name, endpoint, new_value=new_data, old_value=old_data, user_info=user_info)

        return response

    def create_log(self, action: str, table_name: str, endpoint: str, new_value=None, old_value=None, user_info=None):
        user_info = user_info if user_info else {"email": "system@email.com", "fullname": "System User"}

        audit_log = {
            "collection": table_name,
            "action": action,
            "endpoint": endpoint,
            "user": {
              "id": user_info.get("id"),
              "email": user_info.get("email"),
              "full_name": user_info.get("full_name")
            },
            "old_value": old_value,
            "new_value": new_value,
            "created_on": datetime.utcnow()
        }
        action = AuditTrail(**audit_log)
        action.save()
