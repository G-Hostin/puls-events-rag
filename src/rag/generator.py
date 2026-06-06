import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

load_dotenv()

CHAT_MODEL = os.getenv("MISTRAL_CHAT_MODEL", "mistral-small-latest")


def get_llm():
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise RuntimeError("MISTRAL_API_KEY manquante dans .env")
    return ChatMistralAI(
        model=CHAT_MODEL,
        api_key=api_key,
        temperature=0.3,
    )