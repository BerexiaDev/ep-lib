
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


# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "bmp",
    "webp",
    "svg",
    "pdf",
    "xls",
    "xlsx",
    "csv",
    "doc",
    "docx",
    "txt",
}

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