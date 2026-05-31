"""Decoupage des documents en chunks pour la vectorisation"""
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def chunk_documents(documents: list[Document]) -> list[Document]:
    """
    Decoupe chaque document en chunks de taille controlee.
    Les metadonnees sont propagees a chaque chunk pour pouvoir retrouver l'evenement parent depuis n'importe quel chunk
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    return chunks