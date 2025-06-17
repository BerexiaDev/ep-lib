import datetime

from flask_restx import Namespace, fields


class NullableString(fields.String):
    __schema_type__ = ["string", "null"]
    __schema_example__ = "nullable string"


class NullableInteger(fields.Integer):
    __schema_type__ = ["integer", "null"]
    __schema_example__ = "nullable integer"


class NullableFloat(fields.Float):
    __schema_type__ = ["number", "null"]
    __schema_example__ = "nullable float"


class NullableBoolean(fields.Boolean):
    __schema_type__ = ["boolean", "null"]
    __schema_example__ = "nullable boolean"
    

class NullableDatetime(fields.DateTime):
    __schema_type__ = ['string', 'null']
    __schema_example__ = 'nullable Datetime'


class DynamicField(fields.Raw):
    def format(self, value):
        return self.serialize_field(value)

    @staticmethod
    def serialize_field(value):
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        if isinstance(value, datetime.date):
            return value.isoformat()
        if isinstance(value, dict):
            return {k: DynamicField.serialize_field(v) for k, v in value.items()}
        if isinstance(value, list):
            return [DynamicField.serialize_field(v) for v in value]
        return value


class AuditDto:
    api = Namespace("AuditTrail")

    user_info = api.model(
        "User",
        {
            "id": fields.String(),
            "full_name": fields.String(required=True),
            "email": fields.String(required=True),
        },
    )

    audit_info = api.model(
        "AuditTrail Info",
        {
            "id": fields.String(required=True),
            "collection": NullableString(),
            "action": fields.String(required=True),
            "user": fields.Nested(user_info),
            "old_value": DynamicField(),
            "new_value": DynamicField(),
            "created_on": fields.DateTime(),
        },
    )

    audit_pagination = api.model(
        "AuditTrail page",
        {
            "page": fields.Integer,
            "size": fields.Integer,
            "total": fields.Integer,
            "content": fields.List(fields.Nested(audit_info), skip_none=True),
        },
    )



class UserDto:
    api = Namespace('user', description='user related operations')
    
    
    user = api.model('user', {
        'full_name': fields.String(required=True, description='Full name'),
        'email': fields.String(required=True, description='user email address'),
        'password': NullableString(required=False, description='user password', skip_none=True),
        'created_on': NullableDatetime(description='Created on'),
        'modified_on': NullableDatetime(description='Modified on'),
        'role': fields.String(required=True, description='User role as a string'),
        "is_active": fields.Boolean(description='Is User Admin'),
        'id': NullableString(description='user Identifier')
    })


class InvestorDto:
    api = Namespace('investors', description='investors related operations')
    
    
    investor = api.model('investor', {
        'email':  fields.String(description='Investor email address'),
        'full_name':  fields.String(description='Full name of the investor'),
        'projet':  fields.String(description='Project associated with the investor'),
        'property_or_activity_type':  fields.String(description='Type of property or activity'),
        'target_regions':  fields.String(description='Target regions for investment'),
        'investment_amount':  fields.String(description='Investment amount'),
        'company_name':  fields.String(description='Company name'),
        'headquarters_location':  fields.String(description='Headquarters location'),
        'profile':  fields.String(description='Investor profile'),
        'business_sector':  fields.String(description='Business sector'),
        'role':  fields.String(description='Role of the investor'),
        'phone':  fields.String(description='Phone number'),
        'terms_accepted': fields.Boolean(description='Terms and conditions accepted'),
        'password': fields.String(description='Password'),
        'confim_password': fields.String(description='Confirm Password'),
        'created_on': NullableDatetime(description='Created on'),
        'updated_on': NullableDatetime(description='Updated on'),
    })


class AuthDto:
    api = Namespace('auth', description='authentication related operations')
    user_auth = api.model('auth_details', {
        'email': fields.String(required=True, description='The email address'),
        'password': fields.String(required=True, description='The user password '),
    })
    
    refresh_token_auth = api.model('refresh_token', {
        'refresh_token': fields.String(required=True, description='The refresh token'),
    })
    
    reset_password_auth = api.model('reset_password_details', {
        'email': fields.String(required=True, description='The email address'),
        'password': fields.String(required=True, description='The user password '),
        'token': fields.String(required=True, description='The token value'),
    })
    
    # Define the model for the password update inputs
    password_update_model = api.model('PasswordUpdate', {
        'old_password': fields.String(required=True, description='The old password'),
        'new_password': fields.String(required=True, description='The new password'),
        'confirm_password': fields.String(required=True, description='Confirmation of the new password'),
    })
    

class InvestorAuthDto:
    api = Namespace('Investors auth', description='Investor authentication related operations')
    investor_auth = api.model('auth_details', {
        'email': fields.String(required=True, description='The email address'),
        'password': fields.String(required=True, description='The user password '),
    })
    
    refresh_token_auth = api.model('refresh_token', {
        'refresh_token': fields.String(required=True, description='The refresh token'),
    })
    
    reset_password_auth = api.model('reset_password_details', {
        'email': fields.String(required=True, description='The email address'),
        'password': fields.String(required=True, description='The user password '),
        'token': fields.String(required=True, description='The token value'),
    })
    
    # Define the model for the password update inputs
    password_update_model = api.model('PasswordUpdate', {
        'old_password': fields.String(required=True, description='The old password'),
        'new_password': fields.String(required=True, description='The new password'),
        'confirm_password': fields.String(required=True, description='Confirmation of the new password'),
    })
    

class HealthCheckDTO:
    api = Namespace("Health Check", description="Health Check operations")
    healthcheck = api.model("Health Check", {
        "status": fields.String, 
        "message": fields.String
    })