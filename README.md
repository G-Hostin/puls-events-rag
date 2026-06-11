# Puls-Events RAG

POC d'assistant intelligent de recommandation d'événements culturels pour Puls-Events.
Système RAG (Retrieval-Augmented Generation) combinant LangChain, Mistral AI et FAISS,
basé sur les données Open Agenda (région Nouvelle-Aquitaine).

## Stack technique

- **Python 3.13**
- **LangChain** (`langchain`, `langchain-community`, `langchain-mistralai`, `langchain-text-splitters`)
- **FAISS** (`faiss-cpu`) pour la base vectorielle
- **Mistral AI** : `mistral-embed` (embeddings, 1024d) et `mistral-small-latest` (génération)
- **FastAPI** + Uvicorn pour l'exposition REST
- **Ragas** pour l'évaluation automatique de la qualité RAG
- **Docker** + Docker Compose pour la conteneurisation
- **UV** pour la gestion des dépendances

## Structure du projet

```
puls-events-rag/
├── src/
│   ├── data/             # Collecte et nettoyage des données OpenAgenda
│   ├── vectorstore/      # Documents LangChain, chunking, index FAISS
│   ├── rag/              # Chaîne RAG (retriever, prompt, generator, chain)
│   └── api/              # Application FastAPI
├── scripts/              # Scripts d'orchestration (fetch, build, evaluate)
├── tests/                # Tests unitaires (pytest)
├── data/
│   ├── events.jsonl      # Données nettoyées (gitignored, reconstructible)
│   ├── index/            # Index FAISS persisté (gitignored, reconstructible)
│   └── eval/             # Jeu d'évaluation annoté + résultats Ragas
├── docs/                 # Rapport technique, slides
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Documentation

Le rapport technique complet (architecture, choix techniques, résultats, limites et
perspectives) est disponible ici :
[docs/Rapport technique Puls Events.pdf](docs/Rapport%20technique%20Puls%20Events.pdf).

## Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) ou Docker Engine (Linux), pour le lancement via conteneur
- Une clé API Mistral gratuite sur [console.mistral.ai](https://console.mistral.ai)

Pour un développement local sans Docker, il faut en plus :

- Python 3.13+
- [UV](https://docs.astral.sh/uv/)

## Configuration

Crée un fichier `.env` à la racine :

```bash
MISTRAL_API_KEY=ta_cle_mistral
MISTRAL_CHAT_MODEL=mistral-small-latest
MISTRAL_EMBED_MODEL=mistral-embed
ADMIN_API_KEY=testcleapi
```

## Lancement via Docker (recommandé)

```bash
# Construit l'image
docker compose build

# Lance l'API en arrière-plan
docker compose up -d

# Voir les logs
docker compose logs -f
```

L'API est accessible sur `http://localhost:8000`.
Documentation interactive Swagger : `http://localhost:8000/docs`.

### Premier lancement : initialiser l'index

Au tout premier démarrage, l'index FAISS n'existe pas. Il faut le construire
via l'endpoint protégé `/rebuild` (qui télécharge les données OpenAgenda et
calcule les embeddings) :

```bash
curl -X POST http://localhost:8000/rebuild -H "X-API-Key: testcleapi"
```

Ou via Swagger : `POST /rebuild`, bouton "Try it out", renseigner le header
`x-api-key`, exécuter. Comptez 3-5 minutes (fetch + indexation de ~2000 événements).

> Sous Windows (PowerShell), `curl` se comporte différemment : le plus simple
> est de passer par Swagger (`/docs`) pour appeler `/rebuild` et `/ask`.

### Utilisation

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Quels concerts de jazz a Bordeaux ?"}'
```

### Arrêt

```bash
docker compose down
```

## Lancement en local sans Docker

```bash
# Installer les dépendances
uv sync

# Récupérer les données OpenAgenda
uv run python scripts/fetch_data.py

# Construire l'index FAISS
uv run python scripts/build_index.py

# Lancer l'API
uv run uvicorn src.api.app:app --reload
```

## Endpoints API

| Méthode | Route      | Description                                                           |
| ------- | ---------- | --------------------------------------------------------------------- |
| `GET`   | `/health`  | Vérifie que l'API répond                                              |
| `POST`  | `/ask`     | Pose une question, reçoit une réponse + sources                       |
| `POST`  | `/rebuild` | Rafraîchit les données et reconstruit l'index (protégé par X-API-Key) |
| `GET`   | `/docs`    | Documentation Swagger interactive                                     |

## Tests

```bash
uv run pytest
```

## Évaluation automatique (Ragas)

Le jeu d'évaluation annoté (10 questions/réponses de référence) est dans
`data/eval/questions.jsonl`. Pour lancer l'évaluation :

```bash
uv run python scripts/evaluate_rag.py
```

Trois métriques sont calculées (LLM-juge : `mistral-small`) :

- **Faithfulness** : la réponse est-elle supportée par le contexte ?
- **Answer relevancy** : la réponse répond-elle à la question ?
- **Context precision** : les documents retrouvés sont-ils pertinents ?

Résultats obtenus (sur les 10 questions annotées) :

| Métrique          | Score |
| ----------------- | ----- |
| Faithfulness      | 0.611 |
| Answer relevancy  | 0.830 |
| Context precision | 0.702 |

Le détail par question est sauvegardé dans `data/eval/results.json`.
