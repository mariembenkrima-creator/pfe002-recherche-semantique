# PFE-002 — Moteur de recherche sémantique multilingue

Moteur de recherche sémantique (FR / AR / EN) pour documents administratifs,
basé sur sentence-transformers, Qdrant et FastAPI.

## Prérequis
- Python 3.12
- Git
- Docker Desktop (pour Qdrant)

## Installation
```bash
git clone https://github.com/mariembenkrima-creator/pfe002-recherche-semantique.git
cd pfe002-recherche-semantique
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell : .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
pytest
```

## Arborescence
| Dossier | Rôle |
|---|---|
| `src/semsearch/ingestion` | Dépôt, empreinte SHA-256, extraction, OCR |
| `src/semsearch/normalisation` | Langue, nettoyage, métadonnées, découpage |
| `src/semsearch/indexation` | Embeddings, Qdrant, index BM25 |
| `src/semsearch/recherche` | Recherche sémantique, lexicale, hybride |
| `src/semsearch/api` | Service FastAPI |
| `src/semsearch/evaluation` | Jeu de référence et métriques |
| `scripts/` | Scripts utilitaires (ex. vérification de Qdrant) |
| `data/`, `models/` | Non versionnés |
| `qdrant_storage/` | Données de Qdrant, non versionnées |

## Base vectorielle Qdrant

Qdrant tourne dans un conteneur Docker. Prérequis : [Docker Desktop](https://www.docker.com/products/docker-desktop/) installé et démarré.

```bash
docker compose up -d      # démarrer Qdrant
docker compose down       # arrêter Qdrant (les données sont conservées)
```

- Interface web : http://localhost:6333/dashboard
- Point de santé : http://localhost:6333/healthz

### Persistance des données

Les données de Qdrant sont stockées dans le dossier `qdrant_storage/` à la racine du projet. C'est le volume Docker défini dans `docker-compose.yml`. Elles survivent à l'arrêt et à la suppression du conteneur.

Ce dossier est **exclu du dépôt** (voir `.gitignore`), car il est volumineux et se régénère à partir de l'ingestion.

Pour repartir d'une base vide : `docker compose down`, puis supprimer le dossier `qdrant_storage/`.

### Vérifier la persistance

```bash
python scripts/verifier_persistance.py ecrire     # écrit 3 vecteurs de test
docker compose down
docker compose up -d
python scripts/verifier_persistance.py verifier   # doit afficher "OK"
```