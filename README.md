# PFE-002 — Moteur de recherche sémantique multilingue

Moteur de recherche sémantique (FR / AR / EN) pour documents administratifs,
basé sur sentence-transformers, Qdrant et FastAPI.

## Prérequis
- Python 3.11+
- Git
- Docker (pour Qdrant)

## Installation
```bash
git clone https://github.com/mariembenkrima-creator/pfe002-recherche-semantique.git
cd pfe002-recherche-semantique
python -m venv .venv
source .venv/bin/activate        # Windows (Git Bash) : source .venv/Scripts/activate
pip install -e .
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
| `data/`, `models/` | Non versionnés |