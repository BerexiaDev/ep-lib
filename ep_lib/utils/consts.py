
from ep_lib.utils.enums import MongoCollectionsEnum
from ep_lib.models.tourist_product import TouristProduct
from ep_lib.models.restaurant_products  import RestaurantProducts
from ep_lib.models.unclassified_accommodation  import UnclassifiedAccommodation
from ep_lib.models.tourist_package  import TouristPackages
from ep_lib.models.accommodation_opportunitie  import AccommodationOpportunities
from ep_lib.models.land_opportunitie  import LandOpportunities
from ep_lib.models.project_bank  import ProjectBank
from ep_lib.models.land_resource  import LandResources
from ep_lib.models.tourist_resource  import TouristResources
from ep_lib.models.marketplace  import Marketplace
from ep_lib.models.tourism_investment  import TourismInvestment
from ep_lib.models.tourism_offer  import TourismOffer
from ep_lib.services.weviate_service import (
    cast_tourist_product_to_weaviate_poi,
    cast_restaurant_product_to_weaviate_poi,
    cast_tourist_resource_to_weaviate_poi,
    cast_accommodation_opportunity_to_weaviate_investment,
    cast_land_opportunity_to_weaviate_investment,
    cast_land_resources_to_weaviate_investment,
)



MongoCollectionToModelMap = {
    MongoCollectionsEnum.TOURIST_PRODUCTS.value: TouristProduct,
    MongoCollectionsEnum.RESTAURANT_PRODUCTS.value: RestaurantProducts,
    MongoCollectionsEnum.UNCLASSIFIED_ACCOMMODATION.value: UnclassifiedAccommodation,
    MongoCollectionsEnum.TOURIST_PACKAGES.value: TouristPackages,
    MongoCollectionsEnum.ACCOMMODATION_OPPORTUNITIES.value: AccommodationOpportunities,
    MongoCollectionsEnum.LAND_OPPORTUNITIES.value: LandOpportunities,
    MongoCollectionsEnum.PROJECT_BANK.value: ProjectBank,
    MongoCollectionsEnum.LAND_RESOURCES.value: LandResources,
    MongoCollectionsEnum.TOURIST_RESOURCES.value: TouristResources,
    MongoCollectionsEnum.MARKETPLACE.value: Marketplace,
    MongoCollectionsEnum.TOURISM_INVESTMENT.value: TourismInvestment,
    MongoCollectionsEnum.TOURISM_OFFER.value: TourismOffer,
}


REGION_TO_DIRECTION = {
    "Tanger-Tétouan-Al Hoceima": "nord",
    "Oriental": "nord-est",
    "Fès-Meknès": "centre-nord",
    "Rabat-Salé-Kénitra": "nord-ouest",
    "Casablanca-Settat": "ouest",
    "Béni Mellal-Khénifra": "centre",
    "Marrakech-Safi": "centre-sud",
    "Drâa-Tafilalet": "sud-est",
    "Souss-Massa": "sud-ouest",
    "Guelmim-Oued Noun": "sud-ouest",
    "Laâyoune-Sakia El Hamra": "sud",
    "Dakhla-Oued Ed-Dahab": "extreme sud",
}

COLLECTION_CONFIG_MAP = {
    MongoCollectionsEnum.TOURIST_PRODUCTS: {
        "collection_name": TouristProduct,
        "schema_name": "POI",
        "cast_to_weaviate_poi": cast_tourist_product_to_weaviate_poi,
        "remove_empty_properties": ["cid", "title", "city"],
        "is_valid_string": ["title", "city"],
        "safe_str_clean": ["cid", "type_of_classification", "region", "title", "city"]
    },
    MongoCollectionsEnum.RESTAURANT_PRODUCTS: {
        "collection_name": RestaurantProducts,
        "schema_name": "POI",
        "cast_to_weaviate_poi": cast_restaurant_product_to_weaviate_poi,
        "remove_empty_properties": ["cid", "title", "city"],
        "is_valid_string": ["title", "city"],
        "safe_str_clean": ["cid", "type_of_classification", "fork_rating", "region", "title", "city"]
    },
    MongoCollectionsEnum.TOURIST_RESOURCES: {
        "collection_name": TouristResources,
        "schema_name": "POI",
        "cast_to_weaviate_poi": cast_tourist_resource_to_weaviate_poi,
        "remove_empty_properties": ["cid", "title", "city"],
        "is_valid_string": ["title", "city"],
        "safe_str_clean": ["cid", "type_of_classification", "region", "title", "city", "intensity"]
    },
    MongoCollectionsEnum.ACCOMMODATION_OPPORTUNITIES: {
        "collection_name": AccommodationOpportunities,
        "schema_name": "INVESTMENT",
        "cast_to_weaviate_poi": cast_accommodation_opportunity_to_weaviate_investment,
        "remove_empty_properties": ["cid", "title_fr", "region"],
        "is_valid_string": ["poi_type", "title_fr", "region"],
        "safe_str_clean": [
            "cid", "poi_type", "opportunity_id", "title_fr", "title_en", "title_es",
            "opportunity_type", "investment_type", "management_type", "asset_type",
            "category", "classification_type", "branch", "region", "city",
            "district_municipality", "availability", "accessibility", "transfer_conditions",
            "document_type", "urban_planning_status", "asset_status"
        ]
    },
    MongoCollectionsEnum.LAND_OPPORTUNITIES: {
        "collection_name": LandOpportunities,
        "schema_name": "INVESTMENT",
        "cast_to_weaviate_poi": cast_land_opportunity_to_weaviate_investment,
        "remove_empty_properties": ["cid", "title_fr", "region"],
        "is_valid_string": ["poi_type", "title_fr", "region"],
        "safe_str_clean": [
            "cid", "poi_type", "opportunity_id", "title_fr", "title_en", "title_es",
            "opportunity_type", "investment_type", "management_type", "asset_type",
            "category", "classification_type", "branch", "region", "city",
            "availability", "accessibility", "transfer_conditions", "site_topography",
            "environmental_constraints", "document_type", "urban_planning_status"
        ]
    },
    MongoCollectionsEnum.LAND_RESOURCES: {
        "collection_name": LandResources,
        "schema_name": "LAND_RESOURCES",
        "cast_to_weaviate_poi": cast_land_resources_to_weaviate_investment,
        "remove_empty_properties": ["cid", "resource_id", "region"],
        "is_valid_string": ["poi_type", "resource_id", "region"],
        "safe_str_clean": [
            "cid", "poi_type", "title_fr", "title_en", "title_es", "land_type",
            "land_regime", "branch", "region", "city", "district_municipality",
            "direction", "availability", "accessibility", "transfer_conditions",
            "site_topography", "environmental_constraints", "urban_planning_status",
            "document_type", "area", "investment_amount", "intensity"
        ]
    }
}