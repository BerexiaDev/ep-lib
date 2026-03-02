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



def create_response_dto(api, model_name, model=None, is_paginated=False, skip_none=False):
    """
    Creates a standardized API response model with Flask-RESTx.

    :param api: API instance (e.g. api = Namespace('my_namespace', description='My Namespace'))
    :param model_name: str, Name for the response model
    :param model: The data model to include in the response (e.g. api.model('MyModel', {...}))
    :param is_paginated: bool, If True, wraps data in pagination structure (default: False)
    :return: flask_restx.Model, A standardized API response model
    """

    response_dto = api.model(model_name, {
        'status': fields.String(description='Response status', skip_none=True, example='success'),
        'message': fields.String(description='Response message', skip_none=True, example='Request successful'),
    })

    if is_paginated:
        response_dto = response_dto.inherit(model_name, response_dto, {
            'content': fields.List(fields.Nested(model, skip_none=skip_none), description='Response data', required=True) if model else fields.Raw,
            'total': fields.Integer(description='Total number of records', required=True),
            'page': fields.Integer(description='Current page number', required=True),
            'size': fields.Integer(description='Number of records per page', required=True),
        })
    else:
        response_dto = response_dto.inherit(model_name, response_dto, {
            'data': fields.Nested(model, description='Response data', skip_none=skip_none),
        })

    return response_dto


def create_message_model(api, model, pagination=False):
    message_structure = {
        'status': fields.String,
        'message': fields.String,
        'data': fields.Nested(model),
    }
    if pagination:
        message_structure['data'] = fields.Nested(
            api.model('Page', {
                'page': fields.Integer,
                'size': fields.Integer,
                'total': fields.Integer,
                'data': fields.List(fields.Nested(model)),
            }),
        )

    return api.model('Message', message_structure)

def merge_models(name: str, api: Namespace, *models):
    combined: dict = {}
    for m in models:
        if not isinstance(m, dict):
            raise TypeError(f"{m} is not a restx Model")
        combined.update(m)
    return api.model(name, combined)



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


class TouristProductDTO:
    api = Namespace("TouristProduct",
                    description="Tourist Product related operations")
    tourist_product = api.model(
        "TouristProduct",
        {
            "id": NullableString(description="Tourist Product ID"),
            "sip_id": NullableString(description="SMIT ID"),
            "title_fr": NullableString(description="Title in French"),
            "title_en": NullableString(description="Title in English"),
            "title_es": NullableString(description="Title in Spanish"),
            "title_ar": NullableString(description="Title in Arabic"),
            "progress_report": NullableString(description="Progress report"),
            "branch": NullableString(description="Branch/Theme"),
            "asset_type": NullableString(description="Asset type"),
            "new_decree_category": NullableString(description="New decree category"),
            "type_of_classification": NullableString(description="Type of classification"),
            "capacity_in_units": NullableInteger(description="Capacity in units"),
            "bed_capacity": NullableInteger(description="Bed capacity"),
            "opening_date": NullableInteger(description="Opening date"),
            "region": NullableString(description="Region"),
            "city": NullableString(description="City"),
            "district_municipality": NullableString(description="District/Municipality"),
            "latitude": fields.Float(description="Latitude"),
            "longitude": fields.Float(description="Longitude"),
            "description_fr": NullableString(description="Description in French"),
            "description_en": NullableString(description="Description in English"),
            "description_es": NullableString(description="Description in Spanish"),
            "description_ar": NullableString(description="Description in Arabic"),
            "document_type": NullableString(description="Document type"),
            "intensity": NullableInteger(description="Intensity"),
            "archived_on": NullableDatetime(description="Date of archivation"),
            "images": fields.Raw(
                description="Can be images URLs separated by comma or a List of URL strings", 
                example=["http://url1.com", "http://url2.com"]
            ),
            "status": NullableString(description="Resource status", skip_none=True),
            "created_at": NullableDatetime(description="Creation date", skip_none=True),
            "updated_at": NullableDatetime(description="Last update date", skip_none=True),
        },
    )


class RestaurantProductDTO:
    api = Namespace("Restaurant Product",
                    description="Restaurant Product related operations")
    restaurant_product = api.model(
        "Restaurant Product",
        {
            "id": NullableString(description="Restaurant Product ID"),
            "sip_id": NullableString(description="SMIT ID"),
            "title_fr": NullableString(description="Title in French"),
            "title_en": NullableString(description="Title in English"),
            "title_es": NullableString(description="Title in Spanish"),
            "title_ar": NullableString(description="Title in Arabic"),
            "progress_report": NullableString(description="Progress report"),
            "region": NullableString(description="Region"),
            "city": NullableString(description="City"),
            "district_municipality": NullableString(description="District/Municipality"),
            "seat_count": NullableInteger(description="Number of seats"),
            "specialty": NullableString(description="Restaurant specialty"),
            "latitude": fields.Float(description="Latitude"),
            "longitude": fields.Float(description="Longitude"),
            "fork_rating": NullableString(description="Fork rating"),
            "opening_date": NullableInteger(description="Opening date"),
            "description_fr": NullableString(description="Description in French"),
            "description_en": NullableString(description="Description in English"),
            "description_es": NullableString(description="Description in Spanish"),
            "description_ar": NullableString(description="Description in Arabic"),
            "document_type": NullableString(description="Document type"),
            "intensity": NullableInteger(description="Intensity"),
            "archived_on": NullableDatetime(description="Date of archivation"),
            "images": fields.Raw(
                description="Can be images URLs separated by comma or a List of URL strings", 
                example=["http://url1.com", "http://url2.com"]
            ),
            "status": NullableString(description="Resource status", skip_none=True),
            "created_at": NullableDatetime(description="Creation date", skip_none=True),
            "updated_at": NullableDatetime(description="Last update date", skip_none=True),
        },
    )


class UnclassifiedAccommodationDTO:
    api = Namespace("Unclassified Accommodation",
                    description="Unclassified Accommodation related operations")
    unclassified_accommodation = api.model(
        "Unclassified Accommodation",
        {
            "id": NullableString(description="Unclassified Accommodation ID"),
            "sip_id": NullableString(description="SMIT ID"),
            "title_fr": NullableString(description="Title in French"),
            "title_en": NullableString(description="Title in English"),
            "title_es": NullableString(description="Title in Spanish"),
            "title_ar": NullableString(description="Title in Arabic"),
            "progress_report": NullableString(description="Progress report"),
            "branch": NullableString(description="Branch/Theme"),
            "asset_type": NullableString(description="Asset type"),
            "new_decree_category": NullableString(description="New decree category"),
            "type_of_classification": NullableString(description="Type of classification"),
            "capacity_in_units": NullableInteger(description="Capacity in units"),
            "bed_capacity": NullableInteger(description="Bed capacity"),
            "opening_date": NullableInteger(description="Opening date"),
            "region": NullableString(description="Region"),
            "city": NullableString(description="City"),
            "district_municipality": NullableString(description="District/Municipality"),
            "latitude": fields.Float(description="Latitude"),
            "longitude": fields.Float(description="Longitude"),
            "description_fr": NullableString(description="Description in French"),
            "description_en": NullableString(description="Description in English"),
            "description_es": NullableString(description="Description in Spanish"),
            "description_ar": NullableString(description="Description in Arabic"),
            "intensity": NullableInteger(description="Intensity"),
            "archived_on": NullableDatetime(description="Date of archivation"),
            "images": fields.Raw(
                description="Can be images URLs separated by comma or a List of URL strings", 
                example=["http://url1.com", "http://url2.com"]
            ),
            "status": NullableString(description="Resource status", skip_none=True),
            "created_at": NullableDatetime(description="Creation date", skip_none=True),
            "updated_at": NullableDatetime(description="Last update date", skip_none=True),
        },
    )


class TouristPackageDTO:
    api = Namespace("Tourist Package",
                    description="Tourist Package related operations")

    product_details_model = api.clone(
        "TouristPackageProductDetails",
        TouristProductDTO.tourist_product,
    )

    restaurant_details_model = api.clone(
        "TouristPackageRestaurantDetails",
        RestaurantProductDTO.restaurant_product,
    )

    tourist_package = api.model(
        "Tourist Package",
        {
            "id": NullableString(description="Tourist Package ID"),
            "sip_id": NullableString(description="SMIT Package ID"),
            "package_id": NullableString(description="Package ID"),
            "resource_id": NullableString(description="Resource ID"),
            "tourist_resource": NullableString(description="Tourist resource"),
            "duration_hours": NullableFloat(description="Duration in hours"),
            "duration_days": NullableFloat(description="Duration in days"),
            "thematic": NullableString(description="Thematic"),
            "district_commune": NullableString(description="District/Commune"),
            "accommodation_category": NullableString(description="Accommodation category"),
            "title_fr": NullableString(description="Title in French"),
            "title_en": NullableString(description="Title in English"),
            "title_es": NullableString(description="Title in Spanish"),
            "title_ar": NullableString(description="Title in Arabic"),
            "branch": NullableString(description="Branch/Theme"),
            "district_municipality": NullableString(description="District/Municipality"),
            "region": NullableString(description="Region"),
            "latitude": fields.Float(description="Latitude"),
            "longitude": fields.Float(description="Longitude"),
            "product_id": NullableString(description="Product ID"),
            "product_title": NullableString(description="Product title"),
            "restaurant_id": NullableString(description="Restaurant ID"),
            "restaurant_title": NullableString(description="Restaurant title"),
            "circuit_id": fields.Integer(description="Circuit id"),
            "document_type": NullableString(description="Document type"),
            "intensity": NullableInteger(description="Intensity"),
            "product_details": fields.Nested(product_details_model, skip_none=True),
            "restaurant_details": fields.Nested(restaurant_details_model, skip_none=True),
            "archived_on": NullableDatetime(description="Date of archivation"),
            "images": fields.Raw(
                description="Can be images URLs separated by comma or a List of URL strings", 
                example=["http://url1.com", "http://url2.com"]
            ),
            "status": NullableString(description="Resource status", skip_none=True),
            "created_at": NullableDatetime(description="Creation date", skip_none=True),
            "updated_at": NullableDatetime(description="Last update date", skip_none=True),
        },
    )


class AccommodationOpportunityDTO:
    api = Namespace("Accommodation Opportunity",
                    description="Accommodation Opportunity related operations")
    accommodation_opportunity = api.model(
        "Accommodation Opportunity",
        {
            "id": NullableString(description="Accommodation Opportunity ID"),
            "sip_id": NullableString(description="SMIT Opportunity ID"),
            "opportunity_type": NullableString(description="Opportunity type"),
            "investment_type": NullableString(description="Investment type"),
            "management_type": NullableString(description="Management type"),
            "asset_type": NullableString(description="Asset type"),
            "category": NullableString(description="Category"),
            "classification_type": NullableString(description="Classification type"),
            "capacity": NullableInteger(description="Capacity"),
            "title_fr": NullableString(description="Title in French"),
            "title_en": NullableString(description="Title in English"),
            "title_es": NullableString(description="Title in Spanish"),
            "title_ar": NullableString(description="Title in Arabic"),
            "branch": NullableString(description="Branch/Theme"),
            "region": NullableString(description="Region"),
            "city": NullableString(description="City"),
            "district_municipality": NullableString(description="District/Municipality"),
            "description_fr": NullableString(description="Description in French"),
            "description_en": NullableString(description="Description in English"),
            "description_es": NullableString(description="Description in Spanish"),
            "description_ar": NullableString(description="Description in Arabic"),
            "latitude": fields.Float(description="Latitude"),
            "longitude": fields.Float(description="Longitude"),
            "area": NullableString(description="Area"),
            "investment_amount": fields.Float(description="Investment amount"),
            "asset_status": NullableString(description="Asset status"),
            "document_type": NullableString(description="Document type"),
            "archived_on": NullableDatetime(description="Date of archivation"),
            "images": fields.Raw(
                description="Can be images URLs separated by comma or a List of URL strings", 
                example=["http://url1.com", "http://url2.com"]
            ),
            "status": NullableString(description="Resource status", skip_none=True),
            "created_at": NullableDatetime(description="Creation date", skip_none=True),
            "updated_at": NullableDatetime(description="Last update date", skip_none=True),
        },
    )


class LandOpportunityDTO:
    api = Namespace("Land Opportunity",
                    description="Land Opportunity related operations")
    land_opportunity = api.model(
        "Land Opportunity",
        {
            "id": NullableString(description="Land Opportunity ID"),
            "sip_id": NullableString(description="SMIT Opportunity ID"),
            "opportunity_type": NullableString(description="Opportunity type"),
            "investment_type": NullableString(description="Investment type"),
            "management_type": NullableString(description="Management type"),
            "classification_type": NullableString(description="Classification type"),
            "title_fr": NullableString(description="Title in French"),
            "title_en": NullableString(description="Title in English"),
            "title_es": NullableString(description="Title in Spanish"),
            "title_ar": NullableString(description="Title in Arabic"),
            "branch": NullableString(description="Branch/Theme"),
            "region": NullableString(description="Region"),
            "city": NullableString(description="City"),
            "location_description_fr": NullableString(description="Location description in French"),
            "location_description_en": NullableString(description="Location description in English"),
            "location_description_es": NullableString(description="Location description in Spanish"),
            "location_description_ar": NullableString(description="Location description in Arabic"),
            "description_fr": NullableString(description="Description in French"),
            "description_en": NullableString(description="Description in English"),
            "description_es": NullableString(description="Description in Spanish"),
            "description_ar": NullableString(description="Description in Arabic"),
            "latitude": fields.Float(description="Latitude"),
            "longitude": fields.Float(description="Longitude"),
            "asset_type": NullableString(description="Asset type"),
            "category": NullableString(description="Category"),
            "area": NullableString(description="Area"),
            "investment_amount": NullableString(description="Investment amount"),
            "document_type": NullableString(description="Document type"),
            "district_municipality": NullableString(description="Arrondissement Commune"),
            "archived_on": NullableDatetime(description="Date of archivation"),
            "polygone": fields.Raw(description="Polygon coordinates supporting both simple polygons [[lat,lng],...] and MultiPolygons [[[lat,lng],...], [[lat,lng],...]]"),
            "images": fields.Raw(
                description="Can be images URLs separated by comma or a List of URL strings", 
                example=["http://url1.com", "http://url2.com"]
            ),
            "status": NullableString(description="Resource status", skip_none=True),
            "created_at": NullableDatetime(description="Creation date", skip_none=True),
            "updated_at": NullableDatetime(description="Last update date", skip_none=True),
        },
    )


class LandResourceDTO:
    api = Namespace("Land Resource", description="Land Resource related operations")
    land_resource = api.model(
        "Land Resource",
        {
            "id": NullableString(description="Record ID (_id)"),
            "sip_id": NullableString(description="SMIT Resource ID"),
            "region": NullableString(description="Region"),
            "city": NullableString(description="City"),
            "district_municipality": NullableString(description="District / Municipality"),
            "land_type": NullableString(description="Land type"),
            "land_regime": NullableString(description="Land regime"),
            "area": NullableString(description="Area (in square meters)"),
            "site_topography": NullableString(description="Site topography"),
            "urban_planning_status": NullableString(description="Urban planning status"),
            "environmental_constraints": NullableString(description="Environmental constraints"),
            "accessibility": NullableString(description="Accessibility"),
            "availability": NullableString(description="Availability"),
            "transfer_conditions": NullableString(description="Transfer conditions"),
            "latitude": fields.Float(description="Latitude"),
            "longitude": fields.Float(description="Longitude"),
            "branch": NullableString(description="Branch / Theme"),
            "investment_amount": NullableString(description="Investment amount"),
            "title_fr": NullableString(description="Title in French"),
            "title_en": NullableString(description="Title in English"),
            "title_es": NullableString(description="Title in Spanish"),
            "title_ar": NullableString(description="Title in Arabic"),
            "document_type": NullableString(description="Document type"),
            "intensity": NullableString(description="Intensity"),
            "archived_on": NullableDatetime(description="Date of archivation"),
            "polygone": fields.Raw(description="Polygon coordinates supporting both simple polygons [[lat,lng],...] and MultiPolygons [[[lat,lng],...], [[lat,lng],...]]"),
            "images": fields.Raw(
                description="Can be images URLs separated by comma or a List of URL strings", 
                example=["http://url1.com", "http://url2.com"]
            ),
            "status": NullableString(description="Resource status", skip_none=True),
            "created_at": NullableDatetime(description="Creation date", skip_none=True),
            "updated_at": NullableDatetime(description="Last update date", skip_none=True),
        },
    )


class TouristResourceDTO:
    api = Namespace("Tourist Resource", description="Tourist Resource related operations")
    tourist_resource = api.model(
        "Tourist Resource",
        {
            "id": NullableString(description="Record ID (_id)"),
            "sip_id": NullableString(description="SMIT Resource ID"),
            "title_fr": NullableString(description="Title in French"),
            "title_en": NullableString(description="Title in English"),
            "title_es": NullableString(description="Title in Spanish"),
            "title_ar": NullableString(description="Title in Arabic"),
            "resource_type": NullableString(description="Resource type"),
            "region": NullableString(description="Region"),
            "city": NullableString(description="City"),
            "latitude": fields.Float(description="Latitude"),
            "longitude": fields.Float(description="Longitude"),
            "description_fr": NullableString(description="Description in French"),
            "description_en": NullableString(description="Description in English"),
            "description_es": NullableString(description="Description in Spanish"),
            "description_ar": NullableString(description="Description in Arabic"),
            "images": fields.Raw(
                description="Can be images URLs separated by comma or a List of URL strings", 
                example=["http://url1.com", "http://url2.com"]
            ),
            "document_type": NullableString(description="Document type"),
            "intensity": NullableString(description="Intensity"),
            "district_municipality": NullableString(description="Arrondissement Commune"),
            "archived_on": NullableDatetime(description="Date of archivation"),
            "status": NullableString(description="Resource status", skip_none=True),
            "created_at": NullableDatetime(description="Creation date", skip_none=True),
            "updated_at": NullableDatetime(description="Last update date", skip_none=True),
        },
    )
    
    
class ProjectBankDTO:
    api = Namespace("Bank project", description="Bank project related operations")
    project_bank = api.model(
        "Project Bank",
        {
            "id": NullableString(description="Record ID (_id)"),
            "sip_id": NullableString(description="SMIT Project ID"),
            "opportunity_type": NullableString(description="Opportunity type"),
            "title_fr": NullableString(description="Title in French"),
            "title_en": NullableString(description="Title in English"),
            "title_es": NullableString(description="Title in Spanish"),
            "title_ar": NullableString(description="Title in Arabic"),
            "asset_type": NullableString(description="Asset type"),
            "category": NullableString(description="Category"),
            "classification_type": NullableString(description="Classification type"),
            "region": NullableString(description="Region"),
            "city": NullableString(description="City"),
            "district_municipality": NullableString(description="District/Municipality"),
            "latitude": fields.Float(description="Latitude"),
            "longitude": fields.Float(description="Longitude"),
            "branch": NullableString(description="Branch/Theme"),
            "description_fr": NullableString(description="Description in French"),
            "description_en": NullableString(description="Description in English"),
            "description_es": NullableString(description="Description in Spanish"),
            "description_ar": NullableString(description="Description in Arabic"),
            "area": NullableString(description="Area"),
            "investment_amount": NullableString(description="Investment amount"),
            "archived_on": NullableDatetime(description="Date of archivation"),
            "images": fields.Raw(
                description="Can be images URLs separated by comma or a List of URL strings", 
                example=["http://url1.com", "http://url2.com"]
            ),
            "status": NullableString(description="Resource status", skip_none=True),
            "created_at": NullableDatetime(description="Creation date", skip_none=True),
            "updated_at": NullableDatetime(description="Last update date", skip_none=True),
            "document_type": NullableString(description="Document type"),
        },
    )    
    

class MarketplaceDTO:
    api = Namespace("Marketplace", description="Marketplace related operations")
    marketplace = api.model(
        "Marketplace",
        {
            "id": NullableString(description="Record ID (_id)"),
            "sip_id": NullableString(description="SMIT Marketplace ID"),
            "opportunity_type": NullableString(description="Opportunity type"),
            "investment_type": NullableString(description="Investment type"),
            "management_type": NullableString(description="Management type"),
            "asset_type": NullableString(description="Asset type"),
            "category": NullableString(description="Category"),
            "classification_type": NullableString(description="Classification type"),
            "capacity": NullableInteger(description="Capacity"),
            "specialty": NullableString(description="Restaurant specialty"),
            "fork_rating": NullableString(description="Fork rating"),
            "seat_count": NullableInteger(description="Number of seats"),
            "region": NullableString(description="Region"),
            "city": NullableString(description="City"),
            "district_municipality": NullableString(description="District/Municipality"),
            "latitude": fields.Float(description="Latitude"),
            "longitude": fields.Float(description="Longitude"),
            "title_fr": NullableString(description="Title in French"),
            "title_ar": NullableString(description="Title in arabic"),
            "title_en": NullableString(description="Title in english"),
            "title_es": NullableString(description="Title in spanish"),
            "branch": NullableString(description="Branch/Theme"),
            "description_fr": NullableString(description="Description in French"),
            "area": NullableString(description="Area"),
            "investment_amount": NullableString(description="Investment amount"),
            "asset_status": NullableString(description="Asset status"),
            "description_ar": NullableString(description="Description in Arabic"),
            "description_en": NullableString(description="Description in English"),
            "description_es": NullableString(description="Description in Spanish"),
            "document_type": NullableString(description="Document type"),
            "archived_on": NullableDatetime(description="Date of archivation"),
            "images": fields.Raw(
                description="Can be images URLs separated by comma or a List of URL strings", 
                example=["http://url1.com", "http://url2.com"]
            ),
            "status": NullableString(description="Resource status", skip_none=True),
            "created_at": NullableDatetime(description="Creation date", skip_none=True),
            "updated_at": NullableDatetime(description="Last update date", skip_none=True),
        },
    )

class TourismOfferDTO:
    api = Namespace("TourismOffer",
                    description="Tourism Offer related operations")
    tourism_offer = api.model(
        "TourismOffer",
        {
            "id": NullableString(description="Tourism Offer ID"),
            "region": NullableString(description="Region"),
            "city": NullableString(description="City"),
            "district_municipality": NullableString(description="District/Municipality"),
            "asset_type": NullableString(description="Asset type"),
            "category": NullableString(description="Category"),
            "classification_type": NullableString(description="Classification type"),
            "branch": NullableString(description="Branch/Theme"),
            "promoter": NullableString(description="Promoter"),
            "management_type": NullableString(description="Management type"),
            "nationality": NullableString(description="Nationality"),
            "investor_profile": NullableString(description="Investor profile"),
            "opening_date": NullableInteger(description="Opening date"),
            "progress_report": NullableString(description="Progress report"),
            "number_of_ehtc": NullableInteger(description="Number of EHTC"),
            "capacity_in_units": NullableInteger(description="Capacity in units"),
            "bed_capacity": NullableInteger(description="Bed capacity"),
            "direct_jobs": NullableInteger(description="Direct jobs"),
            "intensity": NullableInteger(description="Intensity"),
            "archived_on": NullableDatetime(description="Date of archivation"),
            "images": fields.Raw(
                description="Can be images URLs separated by comma or a List of URL strings", 
                example=["http://url1.com", "http://url2.com"]
            ),
            "status": NullableString(description="Resource status", skip_none=True),
            "created_at": NullableDatetime(description="Creation date", skip_none=True),
            "updated_at": NullableDatetime(description="Last update date", skip_none=True),
        },
    )



class TourismInvestmentDTO:
    api = Namespace("TourismInvestment",
                    description="Tourism Investment related operations")
    tourism_investment = api.model(
        "TourismInvestment",
        {
            "id": NullableString(description="Tourism Investment ID"),
            "region": NullableString(description="Region"),
            "city": NullableString(description="City"),
            "district_municipality": NullableString(description="District/Municipality"),
            "asset_type": NullableString(description="Asset type"),
            "category": NullableString(description="Category"),
            "classification_type": NullableString(description="Classification type"),
            "branch": NullableString(description="Branch/Theme"),
            "promoter": NullableString(description="Promoter"),
            "management_type": NullableString(description="Management type"),
            "nationality": NullableString(description="Nationality"),
            "investor_profile": NullableString(description="Investor profile"),
            "opening_date": NullableInteger(description="Opening date"),
            "progress_report": NullableString(description="Progress report"),
            "tourism_investment": NullableInteger(description="Tourism investment amount"),
            "direct_jobs": NullableInteger(description="Direct jobs"),
            "intensity": NullableInteger(description="Intensity"),
            "archived_on": NullableDatetime(description="Date of archivation"),
            "images": fields.Raw(
                description="Can be images URLs separated by comma or a List of URL strings", 
                example=["http://url1.com", "http://url2.com"]
            ),
            "status": NullableString(description="Resource status", skip_none=True),
            "created_at": NullableDatetime(description="Creation date", skip_none=True),
            "updated_at": NullableDatetime(description="Last update date", skip_none=True),
        },
    )

class S2IDTO:
    api = Namespace("S2I", description="S2I import/export operations")    

    s2i_item = merge_models(
        "S2I Item",
        api,                  # just grab any Namespace instance
        TouristProductDTO.tourist_product,
        RestaurantProductDTO.restaurant_product,
        UnclassifiedAccommodationDTO.unclassified_accommodation,
        TouristPackageDTO.tourist_package,
        AccommodationOpportunityDTO.accommodation_opportunity,
        LandOpportunityDTO.land_opportunity,
        ProjectBankDTO.project_bank,
        LandResourceDTO.land_resource,
        TouristResourceDTO.tourist_resource,
        MarketplaceDTO.marketplace,
        TourismInvestmentDTO.tourism_investment,
        TourismOfferDTO.tourism_offer
    )

    save_response_s2i_item = api.model(
        "S2I Item save Response",
        {
            "status": fields.String(example="success"),
            "message": fields.String(example="Ressource créée avec succès"),
            "id": fields.String(description="ID of the created resource"),
            "data": fields.Nested(s2i_item, description="Created resource data", skip_none=True),
        }
    )
