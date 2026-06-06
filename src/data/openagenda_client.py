"""Client pour l'API OpenAgenda via opendatasoft"""
import time
import requests

API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"
PAGE_SIZE = 100
MAX_RETRIES = 3
RETRY_DELAY = 2  # secondes


def _fetch_page(params: dict) -> dict:
    """Appelle l'API"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(API_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == MAX_RETRIES:
                raise RuntimeError(f"Echec apres {MAX_RETRIES} tentatives : {e}")
            print(f"  Tentative {attempt} echouee, nouvelle tentative dans {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)


def fetch_events(region: str, date_min: str, max_events: int = 2000) -> list[dict]:
    """
    Recupere les evenements les plus recents d'une region depuis une date minimale.

    Args:
        region: nom de la region (ex. "Nouvelle-Aquitaine")
        date_min: date au format ISO (ex. "2025-05-27")
        max_events: nombre maximum d'evenements a recuperer (defaut: 2000).

    Returns:
        Liste des evenements bruts (dicts), tries par date decroissante.
    """
    where_clause = f'location_region="{region}" AND firstdate_begin >= date\'{date_min}\''
    all_events = []
    offset = 0

    while len(all_events) < max_events:
        params = {
            "limit": PAGE_SIZE,
            "offset": offset,
            "where": where_clause,
            "order_by": "firstdate_begin DESC",  # plus recents en premier
        }
        print(f"Recuperation offset={offset}...")
        data = _fetch_page(params)
        results = data.get("results", [])
        if not results:
            break
        all_events.extend(results)
        offset += PAGE_SIZE

    # Tronque au cas ou on a un peu depasse
    all_events = all_events[:max_events]
    print(f"  Total recupere : {len(all_events)} evenements")
    return all_events