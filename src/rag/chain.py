from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.rag.retriever import TOP_K, get_retriever
from src.rag.prompt import prompt, format_documents
from src.rag.generator import get_llm


def build_chain(k: int = TOP_K):
    retriever = get_retriever(k=k)
    llm = get_llm()

    chain = (
        {
            "context": retriever | format_documents,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever


def answer(question: str, k: int = TOP_K) -> dict:
    chain, retriever = build_chain(k=k)
    sources = retriever.invoke(question)
    response = chain.invoke(question)
    return {
        "answer": response,
        "sources": [
            {
                "uid": s.metadata.get("uid"),
                "title": s.metadata.get("title"),
                "city": s.metadata.get("city"),
                "url": s.metadata.get("url"),
            }
            for s in sources
        ],
    }