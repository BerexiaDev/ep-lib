from flask_restx import Resource
from flask import request


from ep_lib.audit_logger.service.audit_service import get_audit_logs_paginated
from ep_lib.dto import AuditDto
from ep_lib.reqparse import get_default_paginated_request_parse
from ep_lib.auth.decorator import token_required

api = AuditDto.api
audit_pagination = AuditDto.audit_pagination


@api.route("/search")
class AuditSearch(Resource):
    @token_required(roles=["ADMIN"])
    @api.doc("Get Audit logs")
    @api.marshal_list_with(audit_pagination, skip_none=True)
    @api.response(200, "Audit log successfully retrieved paginated.")
    def post(self):
        parser = get_default_paginated_request_parse()
        parser.remove_argument("search_value")
        args = parser.parse_args()
        return get_audit_logs_paginated(args, request.json)
