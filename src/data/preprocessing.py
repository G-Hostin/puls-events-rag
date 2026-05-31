"""Nettoyage et structuration des donnees OpenAgenda"""
import json
import re

# Liste des champs retenus pour le dataset final
FIELDS_TO_KEEP = [
    # Identification / contenu
    "uid", "canonicalurl", "title_fr", "description_fr", "longdescription_fr",
    "conditions_fr", "keywords_fr", "category",
    # Temporel
    "daterange_fr", "timings", "firstdate_begin", "lastdate_end",
    # Localisation
    "location_coordinates", "location_name", "location_address",
    "location_postalcode", "location_city", "location_department", "location_region",
    # Lieu
    "location_phone", "location_website", "location_description_fr",
    # Pratique evenement
    "status", "accessibility_label_fr", "age_min", "age_max", "image",
    "attendancemode", "onlineaccesslink", "registration",
]

HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def clean_html(text):
    """Retire les balises HTML et normalise les espaces"""
    if not text:
        return text
    text = HTML_TAG_RE.sub(" ", text)
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip()


def parse_json_string(value):
    """Transforme une string JSON en vrai dict python (status, attendancemode etc)"""
    if not value:
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None


def extract_label_fr(parsed):
    """Extrait le label francais d'un champ status/attendancemode parse"""
    if not parsed or not isinstance(parsed, dict):
        return None
    label = parsed.get("label")
    if isinstance(label, dict):
        return label.get("fr")
    return None


def select_fields(event: dict) -> dict:
    """Garde uniquement les champs retenus"""
    return {field: event.get(field) for field in FIELDS_TO_KEEP}


def is_valid(event: dict) -> bool:
    """Verifie qu'un evenement contient le min requis"""
    if not event.get("title_fr"):
        return False
    if not event.get("description_fr") and not event.get("longdescription_fr"):
        return False
    if not event.get("firstdate_begin"):
        return False
    return True


def deduplicate(events: list[dict]) -> list[dict]:
    """Supprime les doublons avec le uid"""
    seen = set()
    unique = []
    for event in events:
        uid = event.get("uid")
        if uid and uid not in seen:
            seen.add(uid)
            unique.append(event)
    return unique


def transform(event: dict) -> dict:
    """Applique le nettoyage detaille a un evenement"""
    event = select_fields(event)

    # Nettoyage HTML des champs texte
    for text_field in ("description_fr", "longdescription_fr",
                       "conditions_fr", "location_description_fr"):
        event[text_field] = clean_html(event.get(text_field))

    # Parsing des champs JSON-string pour extraire les labels lisibles
    event["status_label"] = extract_label_fr(parse_json_string(event.get("status")))
    event["attendancemode_label"] = extract_label_fr(parse_json_string(event.get("attendancemode")))

    # On remplace les champs bruts par les labels exploitables
    event.pop("status", None)
    event.pop("attendancemode", None)

    return event


def process(raw_events: list[dict]) -> list[dict]:
    """Pipeline complet : selection, nettoyage, validation, deduplication (enchaine les function)"""
    transformed = [transform(e) for e in raw_events]
    valid = [e for e in transformed if is_valid(e)]
    unique = deduplicate(valid)
    return unique