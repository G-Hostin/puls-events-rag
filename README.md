# Puls-Events RAG

POC d'assistant intelligent de recommandation d'evenements culturels pour Puls-Events.
Systeme RAG (Retrieval-Augmented Generation) combinant LangChain, Mistral AI et FAISS,
base sur les donnees Open Agenda.

## Stack

- Python 3.12
- LangChain (`langchain`, `langchain-community`, `langchain-mistralai`)
- FAISS (`faiss-cpu`)
- Mistral AI (`mistralai`)
- FastAPI + Uvicorn
- UV pour la gestion des dependances

## Structure

```
puls-events-rag/
├── src/
│   ├── data/          # Collecte et nettoyage des donnees OpenAgenda
│   ├── vectorstore/   # Construction de l'index FAISS
│   ├── rag/           # Chaine RAG (LangChain + Mistral)
│   └── api/           # Endpoints FastAPI
├── tests/             # Tests unitaires
├── data/              # Donnees brutes et index FAISS persiste
└── docs/              # Rapport technique, slides
```

## Installation

Prerequis : Python 3.12+, [UV](https://docs.astral.sh/uv/), une cle Mistral
(gratuite sur [console.mistral.ai](https://console.mistral.ai)).

```bash
git clone <repo>
cd puls-events-rag

# Installer les dependances
uv sync

# Configurer la cle API
cp .env.example .env  # puis editer .env pour renseigner MISTRAL_API_KEY

# Verifier l'environnement
uv run pytest tests/test_environment.py -v
```

## Tests

```bash
uv run pytest
```
