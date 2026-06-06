"""Script d'orchestration : recupere et nettoie les donnees OpenAgenda"""
import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.openagenda_client import fetch_events
from src.data.preprocessing import process

# --- Config ---
REGION = "Nouvelle-Aquitaine"
DAYS_HISTORY = 365  # 1 an d'historique
OUTPUT_PATH = Path("data/events.jsonl")


def main():
    date_min = (datetime.now() - timedelta(days=DAYS_HISTORY)).strftime("%Y-%m-%d")
    print(f"Recuperation des evenements de {REGION} depuis {date_min}...")
    raw_events = fetch_events(REGION, date_min) # appel client API

    print(f"\nNettoyage et structuration...")
    events = process(raw_events)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(f"\n=== Recapitulatif ===")
    print(f"Bruts        : {len(raw_events)}")
    print(f"Apres process: {len(events)}")
    print(f"Sauvegarde   : {OUTPUT_PATH}")

    statuses = Counter(e.get("status_label") for e in events)
    print(f"\n  Distribution par etat :")
    for status, count in statuses.most_common():
        print(f"    {status}: {count}")

    departments = Counter(e.get("location_department") for e in events)
    print(f"\n  Top 5 departements :")
    for dept, count in departments.most_common(5):
        print(f"    {dept}: {count}")


if __name__ == "__main__":
    main()