import json
import os
import sys
import types
from pathlib import Path

# Shim pour contourner un bug d'import dans ragas (utilise un module langchain_community.chat_models.vertexai qui n'existe plus depuis langchain-community 0.4). On n'utilise pas VertexAI, le shim suffit.
if "langchain_community.chat_models.vertexai" not in sys.modules:
    _shim = types.ModuleType("langchain_community.chat_models.vertexai")
    class ChatVertexAI:  # placeholder
        pass
    _shim.ChatVertexAI = ChatVertexAI
    sys.modules["langchain_community.chat_models.vertexai"] = _shim

from datasets import Dataset
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from ragas import evaluate
from ragas.run_config import RunConfig
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import answer_relevancy, context_precision, faithfulness

from src.rag.chain import build_chain

load_dotenv()

QUESTIONS_PATH = Path("data/eval/questions.jsonl")
RESULTS_PATH = Path("data/eval/results.json")


def load_questions():
    questions = []
    with QUESTIONS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            questions.append(json.loads(line))
    return questions


def run_rag(questions, chain, retriever):
    rows = []
    for q in questions:
        print(f"  [{q['id']}/10] {q['question']}")
        sources = retriever.invoke(q["question"])
        answer = chain.invoke(q["question"])
        rows.append({
            "question": q["question"],
            "answer": answer,
            "contexts": [doc.page_content for doc in sources],
            "ground_truth": q["reference_answer"],
        })
    return rows


def main():
    if not QUESTIONS_PATH.exists():
        print(f"Erreur : {QUESTIONS_PATH} introuvable")
        sys.exit(1)

    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("Erreur : MISTRAL_API_KEY manquante")
        sys.exit(1)

    print("Chargement du jeu d'evaluation...")
    questions = load_questions()
    print(f"  {len(questions)} questions chargees")

    print("\nConstruction de la chaine RAG...")
    chain, retriever = build_chain()

    print("\nGeneration des reponses...")
    rows = run_rag(questions, chain, retriever)

    dataset = Dataset.from_list(rows)

    print("\nConfiguration de l'evaluateur Ragas (Mistral)...")
    evaluator_llm = LangchainLLMWrapper(
        ChatMistralAI(model="mistral-small-latest", api_key=api_key, temperature=0)
    )
    evaluator_embeddings = LangchainEmbeddingsWrapper(
        MistralAIEmbeddings(model="mistral-embed", api_key=api_key)
    )

    print("\nLancement de l'evaluation (peut prendre quelques minutes)...")
    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
        run_config=RunConfig(max_workers=1, max_retries=15, max_wait=60),
    )

    print("\n=== Resultats ===")
    df = result.to_pandas()
    summary = {
        "faithfulness": float(df["faithfulness"].mean()),
        "answer_relevancy": float(df["answer_relevancy"].mean()),
        "context_precision": float(df["context_precision"].mean()),
    }
    for metric, score in summary.items():
        print(f"  {metric:25s} : {score:.3f}")

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "summary": summary,
        "per_question": df.to_dict(orient="records"),
    }
    with RESULTS_PATH.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nDetail sauvegarde dans : {RESULTS_PATH}")


if __name__ == "__main__":
    main()