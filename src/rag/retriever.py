from pathlib import Path
from src.vectorstore.indexing import load_index

INDEX_DIR = Path("data/index")
TOP_K = 5


def get_retriever(k: int = TOP_K):
    index = load_index(INDEX_DIR)
    return index.as_retriever(search_kwargs={"k": k})