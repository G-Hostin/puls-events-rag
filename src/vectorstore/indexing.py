"""Construction et chargement de l'index FAISS"""
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_mistralai import MistralAIEmbeddings

load_dotenv()

EMBED_MODEL = os.getenv("MISTRAL_EMBED_MODEL", "mistral-embed")
BATCH_SIZE = 32  # nombre de textes envoyes par requete Mistral


def _get_embeddings() -> MistralAIEmbeddings:
    """Instancie le modele d'embeddings Mistral"""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise RuntimeError(
            "MISTRAL_API_KEY manquante .env"
        )
    return MistralAIEmbeddings(model=EMBED_MODEL, api_key=api_key)


def build_index(documents: list[Document], output_dir: str | Path) -> FAISS:
    """
    Construit un index FAISS a partir des documents fournis
    Sauvegarde l'index sur disque dans output_dir
    """
    embeddings = _get_embeddings()
    print(f"  Modele d'embeddings : {EMBED_MODEL}")
    print(f"  Nombre de documents : {len(documents)}")
    print(f"  Construction de l'index (peut prendre quelques minutes)...")

    # FAISS.from_documents pr batching et appelle l'API par lots
    vectorstore = FAISS.from_documents(documents, embeddings)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(output_dir))
    print(f"  Index sauvegarde dans : {output_dir}")

    return vectorstore


def load_index(input_dir: str | Path) -> FAISS:
    """Recharge un index FAISS sauvegarde"""
    embeddings = _get_embeddings()
    return FAISS.load_local(
        str(input_dir),
        embeddings,
        allow_dangerous_deserialization=True,  # requis pour les metadonnees pickled
    )