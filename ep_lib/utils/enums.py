from enum import Enum

class TicketingStatusEnum(Enum):
    """Generic status enum for all ticketing sections (Contact, Etudes Concepte, etc.)"""
    IN_PROGRESS = "IN_PROGRESS"
    PROCESSED = "PROCESSED"
    CLOSED = "CLOSED"
    
    
class DocTypeEnum(Enum):
    HEBERGEMENT_TOURISTIQUE = "HEBERGEMENT_TOURISTIQUE"
    ANIMATION_TOURISTIQUE = "ANIMATION_TOURISTIQUE"
    AMENAGEMENT_TOURISTIQUE = "AMENAGEMENT_TOURISTIQUE"
    SIGNALETIQUE_TOURISTIQUE = "SIGNALETIQUE_TOURISTIQUE"
    RESTAURATION_PRODUCT = "RESTAURATION_PRODUCT"

    OPPORTUNITE_HEBERGEMENT = "OPPORTUNITE_HEBERGEMENT"
    OPPORTUNITE_FONCIER = "OPPORTUNITE_FONCIER"
    RESSOURCE_FONCIERE = "RESSOURCE_FONCIERE"
    RESSOURCE_TOURISTIQUE = "RESSOURCE_TOURISTIQUE"
    TOURIST_PACKAGE = "TOURIST_PACKAGE"
    MARKETPLACE = "MARKETPLACE"
    PROJECT_BANK = "PROJECT_BANK"
    EHT_ARRIVALS_NIGHTS = "EHT_ARRIVALS_NIGHTS"
    POST_BORDER_ARRIVALS = "POST_BORDER_ARRIVALS"


class MongoCollectionsEnum(Enum):
    TOURIST_PRODUCTS = "tourist_products"
    RESTAURANT_PRODUCTS = "restaurant_products"
    UNCLASSIFIED_ACCOMMODATION = "unclassified_accommodation"
    TOURIST_PACKAGES = "tourist_packages"
    ACCOMMODATION_OPPORTUNITIES = "accommodation_opportunities"
    LAND_OPPORTUNITIES = "land_opportunities"
    PROJECT_BANK = "project_bank"
    LAND_RESOURCES = "land_resources"
    TOURIST_RESOURCES = "tourism_resources"
    MARKETPLACE = "marketplace"
    TOURISM_INVESTMENT = "tourism_investment"
    TOURISM_OFFER = "tourism_offer"
    EHT_ARRIVALS_NIGHTS = "arrivees_nuitees"
    POST_BORDER_ARRIVALS = "arrivees_post_frontieres"


class S2IStatusEnum(Enum):
    ACTIF = "ACTIF"  # éléments à afficher
    ARCHIVE = "ARCHIVE"  # éléments archivés (pas de suppression physique)

    SUPPRIME = "SUPPRIME"  # supprimés côté Moovapps → marqués comme supprimés côté e-Produit

    PENDING_MOOVAPPS = "PENDING_MOOVAPPS"  # en attente de validation côté Moovapps
    PENDING_AJOUT_E_PRODUITS = "PENDING_AJOUT_E_PRODUITS"  # ajout en attente côté e-Produit
    PENDING_UPDATE_E_PRODUITS = "PENDING_UPDATE_E_PRODUITS"  # mise à jour en attente côté e-Produit

    REJETE_MOOVAPPS = "REJETE_MOOVAPPS"  # rejeté par Moovapps
    REJETE_E_PRODUITS = "REJETE_E_PRODUITS"  # rejeté par e-Produit