# PFE-002 — Moteur de recherche sémantique multilingue

Moteur de recherche sémantique (FR / AR / EN) pour documents administratifs,
basé sur sentence-transformers, Qdrant et FastAPI. 100 % logiciels libres et gratuits.

## Prérequis

### Logiciels
| Logiciel | Version | Lien |
|---|---|---|
| Python | **3.12** (pas 3.11 ni 3.13) | https://www.python.org/downloads/ |
| Git | récente | https://git-scm.com/ |
| Docker Desktop | récente | https://www.docker.com/products/docker-desktop/ |

Sous Windows, Docker Desktop nécessite **WSL 2** (voir « Dépannage »).

### Matériel (estimations)
- Processeur standard, **aucune carte graphique (GPU) nécessaire**.
- Mémoire vive : **8 Go minimum**, 16 Go confortable.
- Espace disque libre : **environ 10 Go** (Docker Desktop, PyTorch, modèle d'embeddings).
- Connexion Internet pour la première installation (téléchargement d'environ 1 Go).

## Installation

Commandes pour Windows PowerShell (équivalents Linux / macOS en commentaire) :

```powershell
git clone https://github.com/mariembenkrima-creator/pfe002-recherche-semantique.git
cd pfe002-recherche-semantique
py -3.12 -m venv .venv            # Linux / macOS : python3.12 -m venv .venv
.venv\Scripts\Activate.ps1        # Linux / macOS : source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Vérifier l'installation (environ une minute, toutes les lignes doivent être `PASSED`) :

```powershell
python -m pytest
```

## Démarrage

1. Ouvrir **Docker Desktop** et attendre « Engine running ».
2. Démarrer la base vectorielle Qdrant :

```powershell
docker compose up -d
```

3. Vérifier : http://localhost:6333/healthz doit afficher `healthz check passed`.

## Première recherche

```powershell
python scripts/demo_recherche.py
```

Au premier lancement, le modèle d'embeddings est téléchargé (environ 470 Mo). Résultat attendu :

```
Question : Combien de temps dure le congé de maternité ?

1. [ar] score 0.63 : تتمتع الموظفة بإجازة أمومة مدفوعة الأجر لمدة ثلاثة أشهر.
2. [fr] score 0.53 : Les demandes de congé annuel doivent être déposées ...
3. [ar] score 0.23 : يجب تقديم التصريح الضريبي السنوي قبل نهاية شهر مارس.
```

La question est en français et la meilleure réponse est en arabe : c'est la **recherche translingue**.
Pour poser votre propre question :

```powershell
python scripts/demo_recherche.py "How are travel expenses reimbursed?"
```

> **Démonstration provisoire.** Ce script indexe 9 phrases d'exemple avec le modèle
> `paraphrase-multilingual-MiniLM-L12-v2`. Le modèle définitif sera choisi sur mesures (sprint 4),
> et cette démonstration sera remplacée par l'appel `POST /search` de l'API (sprint 6).

## Dépannage

| Message | Cause | Solution |
|---|---|---|
| `docker : Le terme «docker» n'est pas reconnu` | Docker non installé, ou terminal ouvert avant l'installation | Installer Docker Desktop, puis fermer et rouvrir le terminal |
| `failed to connect to the docker API ... daemon` | Docker Desktop n'est pas lancé | Ouvrir Docker Desktop et attendre « Engine running » |
| `WSL is not installed` (Docker Desktop) | Composant Linux de Windows manquant | PowerShell **administrateur** : `wsl --install --no-distribution --web-download`, puis redémarrer |
| `L'opération demandée nécessite une élévation` | Terminal non administrateur | Clic droit sur PowerShell → « Exécuter en tant qu'administrateur » |
| `Activate.ps1 ne peut pas être chargé` | Scripts bloqués par Windows | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`, puis réessayer |
| Avertissements `symlinks` ou `HF_TOKEN` | Limites de Windows et de Hugging Face | Sans conséquence, à ignorer |

## Arborescence
| Dossier | Rôle |
|---|---|
| `src/semsearch/ingestion` | Dépôt, empreinte SHA-256, extraction, OCR |
| `src/semsearch/normalisation` | Langue, nettoyage, métadonnées, découpage |
| `src/semsearch/indexation` | Embeddings, Qdrant, index BM25 |
| `src/semsearch/recherche` | Recherche sémantique, lexicale, hybride |
| `src/semsearch/api` | Service FastAPI |
| `src/semsearch/evaluation` | Jeu de référence et métriques |
| `scripts/` | Scripts utilitaires (démonstration, vérifications, qualité) |
| `data/`, `models/` | Non versionnés |
| `qdrant_storage/` | Données de Qdrant, non versionnées |

## Base vectorielle Qdrant

```powershell
docker compose up -d      # démarrer Qdrant
docker compose down       # arrêter Qdrant (les données sont conservées)
```

- Interface web : http://localhost:6333/dashboard
- Point de santé : http://localhost:6333/healthz

Les données sont stockées dans `qdrant_storage/` (volume Docker défini dans `docker-compose.yml`).
Elles survivent à l'arrêt et à la suppression du conteneur. Ce dossier est **exclu du dépôt**
(volumineux, régénéré par l'ingestion). Pour repartir d'une base vide : `docker compose down`,
puis supprimer `qdrant_storage/`.

Vérifier la persistance :

```powershell
python scripts/verifier_persistance.py ecrire
docker compose down
docker compose up -d
python scripts/verifier_persistance.py verifier   # doit afficher "OK"
```

## API (FastAPI)

```powershell
uvicorn semsearch.api.main:app --reload
```

- Point de santé : http://127.0.0.1:8000/health renvoie `{"statut": "ok", "qdrant": "connecte"}`,
  ou `"injoignable"` si Qdrant est arrêté.
- Documentation interactive (OpenAPI) : http://127.0.0.1:8000/docs
- L'adresse de Qdrant est configurable avec la variable d'environnement `QDRANT_URL`
  (par défaut `http://localhost:6333`).

## Qualité du code

Une seule commande vérifie le formatage, l'analyse statique et les tests, avec la couverture :

```powershell
python scripts/qualite.py
```

Elle s'arrête au premier échec avec un message explicite. Outils : Ruff (formatage et analyse
statique) et pytest-cov (couverture). Les règles sont définies dans `pyproject.toml`.

Corriger automatiquement le style avant un commit :

```powershell
ruff format .
ruff check --fix .
```

## Corpus d'amorçage

```powershell
python scripts/charger_corpus.py
```

Télécharge 12 PDF dans `data/raw/amorcage/` (non versionné) : 4 documents officiels de l'ONU,
chacun en français, arabe et anglais, et écrit un manifeste avec la taille, l'empreinte SHA-256
et la licence de chaque fichier. Les fichiers déjà présents ne sont pas retéléchargés.

| Cote | Type | Titre |
|---|---|---|
| ST/SGB/2018/1 | Circulaire du Secrétaire général | Statut et Règlement du personnel |
| ST/SGB/2024/2 | Circulaire du Secrétaire général | Organisation du Bureau pour la prévention des catastrophes |
| ST/SGB/2010/7 | Circulaire du Secrétaire général | Organisation du secrétariat de la CESAO |
| A/RES/68/252 | Résolution de l'Assemblée générale | Gestion des ressources humaines |

**Licence** : documents officiels de l'ONU portant une cote ; l'ONU ne revendique pas de droit
d'auteur sur ces documents (ST/AI/189/Add.9/Rev.2). Reproduction libre en citant la source.
La liste des sources et la licence de chacune sont consignées dans `corpus/sources_amorcage.json`.

**Limites** : corpus réduit, PDF à texte natif uniquement (pas de document scanné pour tester
l'OCR). Il sera complété aux sprints suivants.
