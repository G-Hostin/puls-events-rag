"""Transforme un evenement OpenAgenda en Document LangChain"""
from langchain_core.documents import Document


def _format_keywords(keywords) -> str:
    """Formate la liste de mots-cles en string"""
    if not keywords or not isinstance(keywords, list):
        return ""
    return ", ".join(str(k) for k in keywords)


def _format_location(event: dict) -> str:
    """Formate la localisation en une phrase"""
    parts = [
        event.get("location_name"),
        event.get("location_city"),
        event.get("location_department"),
    ]
    parts = [p for p in parts if p]
    return " - ".join(parts) if parts else ""


def build_page_content(event: dict) -> str:
    """
    Compose le contenu textuel qui sera vectorise
    Rassemble les champs semantiquement utiles pour la recherche
    """
    sections = []

    title = event.get("title_fr")
    if title:
        sections.append(f"Titre : {title}")

    category = event.get("category")
    if category:
        sections.append(f"Categorie : {category}")

    keywords = _format_keywords(event.get("keywords_fr"))
    if keywords:
        sections.append(f"Mots-cles : {keywords}")

    location = _format_location(event)
    if location:
        sections.append(f"Lieu : {location}")

    description = event.get("description_fr")
    if description:
        sections.append(f"Description : {description}")

    long_description = event.get("longdescription_fr")
    if long_description and long_description != description:
        sections.append(f"Description detaillee : {long_description}")

    conditions = event.get("conditions_fr")
    if conditions:
        sections.append(f"Conditions : {conditions}")

    return "\n\n".join(sections)


def build_metadata(event: dict) -> dict:
    """
    Construit les metadonnees a stocker a cote du vecteur
    Inclut tout ce qui n'est pas dans page_content mais utile pour le RAG
    """
    return {
        "uid": event.get("uid"),
        "title": event.get("title_fr"),
        "url": event.get("canonicalurl"),
        "date_begin": event.get("firstdate_begin"),
        "date_end": event.get("lastdate_end"),
        "date_range": event.get("daterange_fr"),
        "city": event.get("location_city"),
        "department": event.get("location_department"),
        "region": event.get("location_region"),
        "postalcode": event.get("location_postalcode"),
        "status": event.get("status_label"),
        "attendancemode": event.get("attendancemode_label"),
        "age_min": event.get("age_min"),
        "age_max": event.get("age_max"),
        "image": event.get("image"),
        "online_link": event.get("onlineaccesslink"),
        "accessibility": event.get("accessibility_label_fr"),
    }


def event_to_document(event: dict) -> Document:
    """Convertit un evenement en Document LangChain"""
    return Document(
        page_content=build_page_content(event),
        metadata=build_metadata(event),
    )