from ep_lib.utils.strings import safe_str, clean_text, to_token_list
from ep_lib.utils.enums import MongoCollectionsEnum
from ep_lib.utils.consts import REGION_TO_DIRECTION


def get_poi_type_of_tourist_product(asset_type:str):
    if asset_type == "Hébergement":
        result = "hotel"
    elif asset_type == "Animation":
        result = "animation"
    else:
        result = None
        
    return result


def cast_tourist_product_to_weaviate_poi(tourist_product: dict) -> dict:
    """Cast raw tourist product documents into POI payloads suitable for vector stores."""
    tags = to_token_list(
        tourist_product.get("new_decree_category"),
        tourist_product.get("type_of_classification"),
    )

    retrieval_text_parts = [
        clean_text(tourist_product.get("title_fr")),
        clean_text(tourist_product.get("title_en")),
        clean_text(tourist_product.get("title_es")),
        clean_text(tourist_product.get("description_fr")),
        clean_text(tourist_product.get("description_en")),
        clean_text(tourist_product.get("description_es")),
        clean_text(tourist_product.get("asset_type")),
        clean_text(tourist_product.get("branch")),
        clean_text(tourist_product.get("document_type")),
        clean_text(tourist_product.get("new_decree_category")),
        clean_text(tourist_product.get("type_of_classification")),
        clean_text(tourist_product.get("city")),
        clean_text(tourist_product.get("region")),
        REGION_TO_DIRECTION.get(tourist_product.get("region")) or "",
        clean_text(tourist_product.get("district_municipality")),
    ]

    retrieval_text = " ".join(filter(None, retrieval_text_parts))

    return {
        "cid": str(tourist_product["_id"]),
        "poi_type": get_poi_type_of_tourist_product(tourist_product.get("asset_type")),
        "title_fr": clean_text(tourist_product.get("title_fr")),
        "title_en": clean_text(tourist_product.get("title_en")),
        "title_es": clean_text(tourist_product.get("title_es")),
        "type_of_classification": safe_str(clean_text(tourist_product.get("type_of_classification"))),
        "new_decree_category": safe_str(clean_text(tourist_product.get("new_decree_category"))),
        "branch": safe_str(clean_text(tourist_product.get("branch"))),
        "city": safe_str(clean_text(tourist_product.get("city"))),
        "region": safe_str(clean_text(tourist_product.get("region"))),
        "latitude": tourist_product.get("latitude"),
        "longitude": tourist_product.get("longitude"),
        "description_fr": clean_text(tourist_product.get("description_fr")),
        "description_en": clean_text(tourist_product.get("description_en")),
        "description_es": clean_text(tourist_product.get("description_es")),
        "tags": tags,
        "retrievalText": retrieval_text,
        "collection_name": MongoCollectionsEnum.TOURIST_PRODUCTS.value,
        "direction": REGION_TO_DIRECTION.get(tourist_product.get("region")) or "",
        "district_municipality": safe_str(clean_text(tourist_product.get("district_municipality"))),
    }


def cast_restaurant_product_to_weaviate_poi(restaurant_product: dict) -> dict:
    tags = to_token_list(
        restaurant_product.get("fork_rating"),
    )

    retrieval_text_parts = [
        clean_text(restaurant_product.get("title_fr")),
        clean_text(restaurant_product.get("title_en")),
        clean_text(restaurant_product.get("title_es")),
        clean_text(restaurant_product.get("description_fr")),
        clean_text(restaurant_product.get("description_en")),
        clean_text(restaurant_product.get("description_es")),
        clean_text(restaurant_product.get("specialty")),
        clean_text(restaurant_product.get("branch")),
        clean_text(restaurant_product.get("document_type")),
        clean_text(restaurant_product.get("city")),
        clean_text(restaurant_product.get("region")),
        REGION_TO_DIRECTION.get(restaurant_product.get("region")) or "",
        clean_text(restaurant_product.get("district_municipality")),
    ]

    retrieval_text = " ".join(filter(None, retrieval_text_parts))

    return {
        "cid": str(restaurant_product["_id"]),
        "poi_type": "restaurant",
        "title_fr": clean_text(restaurant_product.get("title_fr")),
        "title_en": clean_text(restaurant_product.get("title_en")),
        "title_es": clean_text(restaurant_product.get("title_es")),
        "fork_rating": safe_str(clean_text(restaurant_product.get("fork_rating"))),
        "new_decree_category": safe_str(clean_text(restaurant_product.get("new_decree_category"))),
        "branch": safe_str(clean_text(restaurant_product.get("branch"))),
        "city": safe_str(clean_text(restaurant_product.get("city"))),
        "region": safe_str(clean_text(restaurant_product.get("region"))),
        "latitude": restaurant_product.get("latitude"),
        "longitude": restaurant_product.get("longitude"),
        "description_fr": clean_text(restaurant_product.get("description_fr")),
        "description_en": clean_text(restaurant_product.get("description_en")),
        "description_es": clean_text(restaurant_product.get("description_es")),
        "tags": tags,
        "retrievalText": retrieval_text,
        "collection_name": MongoCollectionsEnum.RESTAURANT_PRODUCTS.value,
        "direction": REGION_TO_DIRECTION.get(restaurant_product.get("region")) or "",
        "district_municipality": safe_str(clean_text(restaurant_product.get("district_municipality"))),
    }


def cast_tourist_resource_to_weaviate_poi(tourist_resource: dict) -> dict:
    retrieval_text_parts = [
        clean_text(tourist_resource.get("title_fr")),
        clean_text(tourist_resource.get("title_en")),
        clean_text(tourist_resource.get("title_es")),
        clean_text(tourist_resource.get("description_fr")),
        clean_text(tourist_resource.get("description_en")),
        clean_text(tourist_resource.get("description_es")),
        clean_text(tourist_resource.get("resource_type")),
        clean_text(tourist_resource.get("branch")),
        clean_text(tourist_resource.get("document_type")),
        clean_text(tourist_resource.get("intensity")),
        clean_text(tourist_resource.get("city")),
        clean_text(tourist_resource.get("region")),
        REGION_TO_DIRECTION.get(tourist_resource.get("region")) or "",
        clean_text(tourist_resource.get("resource_type")),
    ]

    retrieval_text = " ".join(filter(None, retrieval_text_parts))

    return {
        "cid": str(tourist_resource.get("_id")),
        "poi_type": "ressource_touristique",
        "title_fr": clean_text(tourist_resource.get("title_fr")),
        "title_en": clean_text(tourist_resource.get("title_en")),
        "title_es": clean_text(tourist_resource.get("title_es")),
        "new_decree_category": safe_str(clean_text(tourist_resource.get("new_decree_category"))),
        "branch": safe_str(clean_text(tourist_resource.get("branch"))),
        "city": safe_str(clean_text(tourist_resource.get("city"))),
        "region": safe_str(clean_text(tourist_resource.get("region"))),
        "latitude": tourist_resource.get("latitude"),
        "longitude": tourist_resource.get("longitude"),
        "description_fr": clean_text(tourist_resource.get("description_fr")),
        "description_en": clean_text(tourist_resource.get("description_en")),
        "description_es": clean_text(tourist_resource.get("description_es")),
        "tags": [],
        "retrievalText": retrieval_text,
        "collection_name": MongoCollectionsEnum.TOURIST_RESOURCES.value,
        "direction": REGION_TO_DIRECTION.get(tourist_resource.get("region")) or "",
        "resource_type": safe_str(clean_text(tourist_resource.get("resource_type"))),
    }


def cast_accommodation_opportunity_to_weaviate_investment(
    opportunity: dict,
) -> dict:
    """Cast accommodation investment opportunities into Weaviate payloads."""
    tags = to_token_list(
        opportunity.get("opportunity_type"),
        opportunity.get("investment_type"),
        opportunity.get("management_type"),
        opportunity.get("asset_type"),
        opportunity.get("category"),
        opportunity.get("classification_type"),
        opportunity.get("availability"),
    )

    retrieval_text_parts = [
        clean_text(opportunity.get("title_fr")),
        clean_text(opportunity.get("title_en")),
        clean_text(opportunity.get("title_es")),
        clean_text(opportunity.get("description_fr")),
        clean_text(opportunity.get("description_en")),
        clean_text(opportunity.get("description_es")),
        clean_text(opportunity.get("opportunity_type")),
        clean_text(opportunity.get("investment_type")),
        clean_text(opportunity.get("management_type")),
        clean_text(opportunity.get("asset_type")),
        clean_text(opportunity.get("category")),
        clean_text(opportunity.get("classification_type")),
        clean_text(opportunity.get("branch")),
        clean_text(opportunity.get("document_type")),
        clean_text(opportunity.get("region")),
        clean_text(opportunity.get("city")),
        REGION_TO_DIRECTION.get(opportunity.get("region")) or "",
        clean_text(opportunity.get("district_municipality")),
        clean_text(opportunity.get("urban_planning_status")),
        clean_text(opportunity.get("availability")),
        clean_text(opportunity.get("accessibility")),
        clean_text(opportunity.get("transfer_conditions")),
    ]

    retrieval_text = " ".join(filter(None, retrieval_text_parts))

    poi_type = "investment_accommodation"

    cid = opportunity.get("_id") or opportunity.get("opportunity_id")
    cid = str(cid) if cid is not None else None

    return {
        "cid": cid,
        "poi_type": poi_type,
        "title_fr": clean_text(opportunity.get("title_fr")),
        "title_en": clean_text(opportunity.get("title_en")),
        "title_es": clean_text(opportunity.get("title_es")),
        "opportunity_id": clean_text(opportunity.get("opportunity_id")),
        "opportunity_type": clean_text(opportunity.get("opportunity_type")),
        "investment_type": clean_text(opportunity.get("investment_type")),
        "management_type": clean_text(opportunity.get("management_type")),
        "asset_type": clean_text(opportunity.get("asset_type")),
        "category": safe_str(opportunity.get("category")),
        "classification_type": safe_str(opportunity.get("classification_type")),
        "branch": safe_str(clean_text(opportunity.get("branch"))),
        "region": safe_str(clean_text(opportunity.get("region"))),
        "city": safe_str(clean_text(opportunity.get("city"))),
        "district_municipality": safe_str(clean_text(opportunity.get("district_municipality"))),
        "availability": safe_str(clean_text(opportunity.get("availability"))),
        "accessibility": safe_str(clean_text(opportunity.get("accessibility"))),
        "transfer_conditions": clean_text(opportunity.get("transfer_conditions")),
        "document_type": clean_text(opportunity.get("document_type")),
        "latitude": opportunity.get("latitude"),
        "longitude": opportunity.get("longitude"),
        "area": opportunity.get("area"),
        "investment_amount": opportunity.get("investment_amount"),
        "asset_status": clean_text(opportunity.get("asset_status")),
        "urban_planning_status": clean_text(opportunity.get("urban_planning_status")),
        "tags": tags,
        "retrievalText": retrieval_text,
        "collection_name": MongoCollectionsEnum.ACCOMMODATION_OPPORTUNITIES.value,
        "direction": REGION_TO_DIRECTION.get(opportunity.get("region")) or "",
    }


def cast_land_opportunity_to_weaviate_investment(opportunity: dict) -> dict:
    """Cast land investment opportunities into Weaviate payloads."""
    tags = to_token_list(
        opportunity.get("opportunity_type"),
        opportunity.get("investment_type"),
        opportunity.get("management_type"),
        opportunity.get("asset_type"),
        opportunity.get("category"),
        opportunity.get("classification_type"),
        opportunity.get("availability"),
        opportunity.get("site_topography"),
    )

    retrieval_text_parts = [
        clean_text(opportunity.get("title_fr")),
        clean_text(opportunity.get("title_en")),
        clean_text(opportunity.get("title_es")),
        clean_text(opportunity.get("description_fr")),
        clean_text(opportunity.get("description_en")),
        clean_text(opportunity.get("description_es")),
        clean_text(opportunity.get("location_description_fr")),
        clean_text(opportunity.get("location_description_en")),
        clean_text(opportunity.get("location_description_es")),
        clean_text(opportunity.get("opportunity_type")),
        clean_text(opportunity.get("investment_type")),
        clean_text(opportunity.get("management_type")),
        clean_text(opportunity.get("classification_type")),
        clean_text(opportunity.get("asset_type")),
        clean_text(opportunity.get("category")),
        clean_text(opportunity.get("site_topography")),
        clean_text(opportunity.get("urban_planning_status")),
        clean_text(opportunity.get("environmental_constraints")),
        clean_text(opportunity.get("availability")),
        clean_text(opportunity.get("accessibility")),
        clean_text(opportunity.get("transfer_conditions")),
        clean_text(opportunity.get("branch")),
        clean_text(opportunity.get("region")),
        clean_text(opportunity.get("city")),
        REGION_TO_DIRECTION.get(opportunity.get("region")) or "",
    ]

    retrieval_text = " ".join(filter(None, retrieval_text_parts))

    poi_type = "investment_land"

    cid = opportunity.get("_id") or opportunity.get("opportunity_id")
    cid = str(cid) if cid is not None else None

    return {
        "cid": cid,
        "poi_type": poi_type,
        "title_fr": clean_text(opportunity.get("title_fr")),
        "title_en": clean_text(opportunity.get("title_en")),
        "title_es": clean_text(opportunity.get("title_es")),
        "opportunity_id": clean_text(opportunity.get("opportunity_id")),
        "opportunity_type": clean_text(opportunity.get("opportunity_type")),
        "investment_type": clean_text(opportunity.get("investment_type")),
        "management_type": clean_text(opportunity.get("management_type")),
        "classification_type": safe_str(opportunity.get("classification_type")),
        "asset_type": clean_text(opportunity.get("asset_type")),
        "category": safe_str(opportunity.get("category")),
        "branch": safe_str(clean_text(opportunity.get("branch"))),
        "region": safe_str(clean_text(opportunity.get("region"))),
        "city": safe_str(clean_text(opportunity.get("city"))),
        "site_topography": clean_text(opportunity.get("site_topography")),
        "environmental_constraints": clean_text(opportunity.get("environmental_constraints")),
        "urban_planning_status": clean_text(opportunity.get("urban_planning_status")),
        "availability": safe_str(clean_text(opportunity.get("availability"))),
        "accessibility": safe_str(clean_text(opportunity.get("accessibility"))),
        "transfer_conditions": clean_text(opportunity.get("transfer_conditions")),
        "document_type": clean_text(opportunity.get("document_type")),
        "latitude": opportunity.get("latitude"),
        "longitude": opportunity.get("longitude"),
        "area": opportunity.get("area"),
        "investment_amount": opportunity.get("investment_amount"),
        "tags": tags,
        "retrievalText": retrieval_text,
        "collection_name": MongoCollectionsEnum.LAND_OPPORTUNITIES.value,
        "direction": REGION_TO_DIRECTION.get(opportunity.get("region")) or "",
    }


def cast_land_resources_to_weaviate_investment(opportunity: dict) -> dict:
    """Cast land investment opportunities into Weaviate payloads."""
    tags = to_token_list(
        opportunity.get("land_type"),
        opportunity.get("land_regime"),
        opportunity.get("category"),
        opportunity.get("site_topography"),
    )

    retrieval_text_parts = [
        clean_text(opportunity.get("title_fr")),
        clean_text(opportunity.get("title_en")),
        clean_text(opportunity.get("title_es")),
        clean_text(opportunity.get("land_type")),
        clean_text(opportunity.get("land_regime")),
        clean_text(opportunity.get("area")),
        clean_text(opportunity.get("site_topography")),
        clean_text(opportunity.get("urban_planning_status")),
        clean_text(opportunity.get("environmental_constraints")),
        clean_text(opportunity.get("accessibility")),
        clean_text(opportunity.get("availability")),
        clean_text(opportunity.get("transfer_conditions")),
        clean_text(opportunity.get("transfer_conditions")),
        clean_text(opportunity.get("investment_amount")),
        clean_text(opportunity.get("intensity")),
        clean_text(opportunity.get("intensity")),
        clean_text(opportunity.get("branch")),
        clean_text(opportunity.get("region")),
        clean_text(opportunity.get("city")),
        clean_text(opportunity.get("district_municipality")),
        REGION_TO_DIRECTION.get(opportunity.get("region")) or "",
    ]

    retrieval_text = " ".join(filter(None, retrieval_text_parts))

    poi_type = "land_resource"

    cid = opportunity.get("_id") or opportunity.get("resource_id")
    cid = str(cid) if cid is not None else None
    direction = REGION_TO_DIRECTION.get(opportunity.get("region")) or ""

    return {
        "cid": cid,
        "poi_type": poi_type,

        "title_fr": clean_text(opportunity.get("title_fr")),
        "title_en": clean_text(opportunity.get("title_en")),
        "title_es": clean_text(opportunity.get("title_es")),

        "land_type": clean_text(opportunity.get("land_type")),
        "land_regime": clean_text(opportunity.get("land_regime")),

        "branch": safe_str(clean_text(opportunity.get("branch"))),
        "region": safe_str(clean_text(opportunity.get("region"))),
        "city": safe_str(clean_text(opportunity.get("city"))),
        "district_municipality": safe_str(clean_text(opportunity.get("district_municipality"))),
        "direction": direction,

        "site_topography": clean_text(opportunity.get("site_topography")),
        "environmental_constraints": clean_text(opportunity.get("environmental_constraints")),
        "urban_planning_status": clean_text(opportunity.get("urban_planning_status")),
        "availability": safe_str(clean_text(opportunity.get("availability"))),
        "accessibility": safe_str(clean_text(opportunity.get("accessibility"))),
        "transfer_conditions": clean_text(opportunity.get("transfer_conditions")),

        "document_type": clean_text(opportunity.get("document_type")),
        "latitude": opportunity.get("latitude"),
        "longitude": opportunity.get("longitude"),
        "area": opportunity.get("area"),
        "investment_amount": opportunity.get("investment_amount"),
        "intensity": clean_text(opportunity.get("intensity")),  # was missing before

        "tags": tags,
        "retrievalText": retrieval_text,

        "collection_name": MongoCollectionsEnum.LAND_RESOURCES.value,
    }