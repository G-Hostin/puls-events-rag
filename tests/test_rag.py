import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv()

INDEX_DIR = Path("data/index")

pytestmark = pytest.mark.skipif(
    not INDEX_DIR.exists() or not os.getenv("MISTRAL_API_KEY"),
    reason="Index FAISS ou MISTRAL_API_KEY manquants",
)


def test_answer_returns_response_and_sources():
    from src.rag.chain import answer

    result = answer("concert de musique a Bordeaux", k=3)

    assert isinstance(result["answer"], str)
    assert len(result["answer"]) > 0
    assert len(result["sources"]) == 3
    assert all("title" in s and "uid" in s for s in result["sources"])


def test_answer_refuses_out_of_scope_question():
    from src.rag.chain import answer

    result = answer("Quelle est la capitale du Japon ?", k=3)
    response_lower = result["answer"].lower()
    assert any(
        kw in response_lower
        for kw in [
            "aucun", "pas d'", "ne correspond", "ne trouve",
            "ne peux pas", "evenements culturels", "nouvelle-aquitaine",
        ]
    )