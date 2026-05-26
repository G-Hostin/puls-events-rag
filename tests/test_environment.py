"""Verifie que l'environnement est correctement configure."""
import os


def test_faiss_import():
    import faiss
    index = faiss.IndexFlatL2(128)
    assert index.ntotal == 0


def test_langchain_faiss():
    from langchain_community.vectorstores import FAISS
    assert FAISS is not None


def test_langchain_mistral():
    from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
    assert ChatMistralAI is not None
    assert MistralAIEmbeddings is not None


def test_fastapi():
    from fastapi import FastAPI
    app = FastAPI()
    assert app is not None


def test_env_key():
    from dotenv import load_dotenv
    load_dotenv()
    key = os.getenv("MISTRAL_API_KEY")
    assert key is not None, "MISTRAL_API_KEY manquante dans .env"