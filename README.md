# Puls-Events RAG

POC d'assistant intelligent de recommandation d'evenements culturels pour Puls-Events.
Systeme RAG (Retrieval-Augmented Generation) combinant LangChain, Mistral AI et FAISS,
base sur les donnees Open Agenda (region Nouvelle-Aquitaine).

## Stack technique

- **Python 3.12**
- **LangChain** (`langchain`, `langchain-community`, `langchain-mistralai`, `langchain-text-splitters`)
- **FAISS** (`faiss-cpu`) pour la base vectorielle
- **Mistral AI** : `mistral-embed` (embeddings, 1024d) et `mistral-small-latest` (generation)
- **FastAPI** + Uvicorn pour l'exposition REST
- **Ragas** pour l'evaluation automatique de la qualite RAG
- **Docker** + Docker Compose pour la conteneurisation
- **UV** pour la gestion des dependances

## Structure du projet

```
puls-events-rag/
├── src/
│   ├── data/             # Collecte et nettoyage des donnees OpenAgenda
│   ├── vectorstore/      # Documents LangChain, chunking, index FAISS
│   ├── rag/              # Chaine RAG (retriever, prompt, generator, chain)
│   └── api/              # Application FastAPI
├── scripts/              # Scripts d'orchestration (fetch, build, evaluate)
├── tests/                # Tests unitaires (pytest)
├── data/
│   ├── events.jsonl      # Donnees nettoyees (gitignored, reconstructible)
│   ├── index/            # Index FAISS persiste (gitignored, reconstructible)
│   └── eval/             # Jeu d'evaluation annote + resultats Ragas
├── docs/                 # Rapport technique, slides
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Prerequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (pour le lancement via conteneur)
- Une cle API Mistral gratuite sur [console.mistral.ai](https://console.mistral.ai)

Pour un developpement local sans Docker, il faut en plus :

- Python 3.12+
- [UV](https://docs.astral.sh/uv/)

## Configuration

Cree un fichier `.env` a la racine :

```bash
MISTRAL_API_KEY=ta_cle_mistral
MISTRAL_CHAT_MODEL=mistral-small-latest
MISTRAL_EMBED_MODEL=mistral-embed
ADMIN_API_KEY=testcleapi
```

## Lancement via Docker (recommande)

```bash
# Construit l'image
docker compose build

# Lance l'API en arriere-plan
docker compose up -d

# Voir les logs
docker compose logs -f
```

L'API est accessible sur `http://localhost:8000`.
Documentation interactive Swagger : `http://localhost:8000/docs`.

### Premier lancement : initialiser l'index

Au tout premier demarrage, l'index FAISS n'existe pas. Il faut le construire
via l'endpoint protege `/rebuild` (qui telecharge les donnees OpenAgenda et
calcule les embeddings) :

```bash
curl -X POST http://localhost:8000/rebuild -H "X-API-Key: testcleapi"
```

Ou via Swagger : `POST /rebuild`, bouton "Try it out", renseigner le header
`x-api-key`, executer. Comptez 3-5 minutes (fetch + indexation de ~2000 evenements).

### Utilisation

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Quels concerts de jazz a Bordeaux ?"}'
```

### Arret

```bash
docker compose down
```

## Lancement en local sans Docker

```bash
# Installer les dependances
uv sync

# Recuperer les donnees OpenAgenda
uv run python scripts/fetch_data.py

# Construire l'index FAISS
uv run python scripts/build_index.py

# Lancer l'API
uv run uvicorn src.api.app:app --reload
```

## Endpoints API

| Methode | Route      | Description                                                           |
| ------- | ---------- | --------------------------------------------------------------------- |
| `GET`   | `/health`  | Verifie que l'API repond                                              |
| `POST`  | `/ask`     | Pose une question, recoit une reponse + sources                       |
| `POST`  | `/rebuild` | Rafraichit les donnees et reconstruit l'index (protege par X-API-Key) |
| `GET`   | `/docs`    | Documentation Swagger interactive                                     |

## Tests

```bash
uv run pytest
```

## Evaluation automatique (Ragas)

Le jeu d'evaluation annote (10 questions/reponses de reference) est dans
`data/eval/questions.jsonl`. Pour lancer l'evaluation :

```bash
uv run python scripts/evaluate_rag.py
```

Trois metriques sont calculees (LLM-juge : `mistral-small`) :

- **Faithfulness** : la reponse est-elle supportee par le contexte ?
- **Answer relevancy** : la reponse repond-elle a la question ?
- **Context precision** : les documents retrouves sont-ils pertinents ?

Les resultats sont sauvegardes dans `data/eval/results.json`.
