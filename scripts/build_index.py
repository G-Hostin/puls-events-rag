"""Construit l'index FAISS a partir des donnees nettoyees"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vectorstore.event_to_document import event_to_document
from src.vectorstore.chunking import chunk_documents
from src.vectorstore.indexing import build_index

INPUT_PATH = Path("data/events.jsonl")
OUTPUT_DIR = Path("data/index")


def main():
    if not INPUT_PATH.exists():
        print(f"Erreur : {INPUT_PATH} introuvable. Lance d'abord scripts/fetch_data.py")
        sys.exit(1)

    print(f"Chargement de {INPUT_PATH}...")
    events = []
    with INPUT_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            events.append(json.loads(line))
    print(f"  {len(events)} evenements charges")

    print("\nTransformation en documents LangChain...")
    documents = [event_to_document(e) for e in events]
    print(f"  {len(documents)} documents crees")

    print("\nDecoupage en chunks...")
    chunks = chunk_documents(documents)
    print(f"  {len(chunks)} chunks generes")

    chunks_per_event = Counter(c.metadata["uid"] for c in chunks)
    print(f"  Moyenne : {len(chunks) / len(documents):.2f} chunks/evenement")
    print(f"  Max     : {max(chunks_per_event.values())} chunks pour un evenement")

    print("\nConstruction de l'index FAISS...")
    build_index(chunks, OUTPUT_DIR)

    print("\n=== Termine ===")
    print(f"Evenements : {len(events)}")
    print(f"Documents  : {len(documents)}")
    print(f"Chunks     : {len(chunks)}")
    print(f"Index      : {OUTPUT_DIR}")


if __name__ == "__main__":
    main()