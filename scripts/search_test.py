"""Script CLI pour tester la recherche dans l'index FAISS"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vectorstore.indexing import load_index

INDEX_DIR = Path("data/index")
TOP_K = 5


def main():
    if len(sys.argv) < 2:
        print('Usage : uv run python scripts/search_test.py "ma question"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f'Recherche : "{query}"\n')

    print("Chargement de l'index...")
    index = load_index(INDEX_DIR)
    print("Recherche en cours...\n")

    results = index.similarity_search_with_score(query, k=TOP_K)

    print(f"=== Top {TOP_K} resultats ===\n")
    for i, (doc, score) in enumerate(results, 1):
        title = doc.metadata.get("title", "?")
        city = doc.metadata.get("city", "?")
        date = doc.metadata.get("date_range") or doc.metadata.get("date_begin", "?")
        url = doc.metadata.get("url", "")

        # Premier extrait du contenu (200 caracteres)
        preview = doc.page_content[:200].replace("\n", " ")

        print(f"{i}. {title}")
        print(f"   Lieu      : {city}")
        print(f"   Date      : {date}")
        print(f"   Distance  : {score:.4f}")
        print(f"   URL       : {url}")
        print(f"   Extrait   : {preview}...")
        print()


if __name__ == "__main__":
    main()