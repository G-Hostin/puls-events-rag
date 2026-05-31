"""Tests unitaires pour le vectorstore"""
import json
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from langchain_core.documents import Document

from src.vectorstore.event_to_document import (
    build_metadata,
    build_page_content,
    event_to_document,
)
from src.vectorstore.chunking import chunk_documents

load_dotenv()

INDEX_DIR = Path("data/index")


# --- Fixture commune ---

@pytest.fixture
def sample_event():
    return {
        "uid": "abc123",
        "title_fr": "Concert de jazz",
        "description_fr": "Une soiree musicale.",
        "longdescription_fr": "Une soiree musicale avec un quartet de jazz reconnu.",
        "conditions_fr": "Entree libre",
        "keywords_fr": ["concert", "jazz", "musique"],
        "category": "Musique",
        "canonicalurl": "https://example.com/event/abc123",
        "firstdate_begin": "2025-06-01T20:00:00+00:00",
        "lastdate_end": "2025-06-01T23:00:00+00:00",
        "daterange_fr": "1 juin 2025, 20h00",
        "location_name": "Salle Pleyel",
        "location_city": "Bordeaux",
        "location_department": "Gironde",
        "location_region": "Nouvelle-Aquitaine",
        "location_postalcode": "33000",
        "status_label": "Programme",
        "attendancemode_label": "Sur place",
        "age_min": None,
        "age_max": None,
        "image": None,
        "onlineaccesslink": None,
        "accessibility_label_fr": None,
    }


# --- Tests build_page_content ---

def test_page_content_contains_title(sample_event):
    content = build_page_content(sample_event)
    assert "Concert de jazz" in content


def test_page_content_contains_description(sample_event):
    content = build_page_content(sample_event)
    assert "Une soiree musicale" in content


def test_page_content_contains_keywords(sample_event):
    content = build_page_content(sample_event)
    assert "jazz" in content
    assert "musique" in content


def test_page_content_contains_location(sample_event):
    content = build_page_content(sample_event)
    assert "Bordeaux" in content
    assert "Salle Pleyel" in content


def test_page_content_skips_empty_fields():
    event = {"title_fr": "Test", "description_fr": None}
    content = build_page_content(event)
    assert "Test" in content
    assert "None" not in content


# --- Tests build_metadata ---

def test_metadata_contains_essential_fields(sample_event):
    meta = build_metadata(sample_event)
    assert meta["uid"] == "abc123"
    assert meta["title"] == "Concert de jazz"
    assert meta["city"] == "Bordeaux"
    assert meta["url"] == "https://example.com/event/abc123"


# --- Tests event_to_document ---

def test_event_to_document_returns_document(sample_event):
    doc = event_to_document(sample_event)
    assert isinstance(doc, Document)
    assert "Concert de jazz" in doc.page_content
    assert doc.metadata["uid"] == "abc123"


# --- Tests chunking ---

def test_chunk_short_document_returns_one_chunk():
    doc = Document(
        page_content="Texte tres court",
        metadata={"uid": "1"},
    )
    chunks = chunk_documents([doc])
    assert len(chunks) == 1
    assert chunks[0].metadata["uid"] == "1"


def test_chunk_long_document_returns_multiple_chunks():
    long_text = "Phrase pleine de texte. " * 200  # ~4800 caracteres
    doc = Document(page_content=long_text, metadata={"uid": "1"})
    chunks = chunk_documents([doc])
    assert len(chunks) > 1
    # Tous les chunks heritent du meme uid
    for chunk in chunks:
        assert chunk.metadata["uid"] == "1"


def test_chunk_preserves_all_metadata():
    doc = Document(
        page_content="texte",
        metadata={"uid": "1", "city": "Bordeaux", "title": "Test"},
    )
    chunks = chunk_documents([doc])
    assert chunks[0].metadata == {"uid": "1", "city": "Bordeaux", "title": "Test"}


# --- Test d'integration (besoin de l'index construit + cle Mistral) ---

@pytest.mark.skipif(
    not INDEX_DIR.exists(),
    reason="Index FAISS non construit. Lance d'abord scripts/build_index.py",
)
@pytest.mark.skipif(
    not os.getenv("MISTRAL_API_KEY") or os.getenv("MISTRAL_API_KEY") == "ta_cle_ici",
    reason="MISTRAL_API_KEY non configuree",
)
def test_search_returns_relevant_events():
    """Verifie qualitativement qu'une recherche retourne des resultats coherents."""
    from src.vectorstore.indexing import load_index

    index = load_index(INDEX_DIR)
    results = index.similarity_search("concert musique", k=3)
    assert len(results) == 3
    # Au moins un resultat doit mentionner musique/concert/instrument
    keywords = ["musique", "concert", "chant", "jazz", "rock", "festival", "spectacle"]
    found = any(
        any(kw in r.page_content.lower() for kw in keywords)
        for r in results
    )
    assert found, "Aucun resultat ne semble lie a la musique"