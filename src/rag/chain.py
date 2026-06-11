from langchain_core.output_parsers import StrOutputParser

from src.rag.retriever import TOP_K, get_retriever
from src.rag.prompt import prompt, format_documents
from src.rag.generator import get_llm


def build_chain(k: int = TOP_K):

    retriever = get_retriever(k=k)
    llm = get_llm()
    generation = prompt | llm | StrOutputParser()
    return generation, retriever


def answer(question: str, k: int = TOP_K) -> dict:
    generation, retriever = build_chain(k=k)

    docs = retriever.invoke(question)  # une seule recherche
    response = generation.invoke({
        "context": format_documents(docs),
        "question": question,
    })

    return {
        "answer": response,
        "sources": [
            {
                "uid": s.metadata.get("uid"),
                "title": s.metadata.get("title"),
                "city": s.metadata.get("city"),
                "url": s.metadata.get("url"),
            }
            for s in docs
        ],
    }
