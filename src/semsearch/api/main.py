"""Service HTTP du moteur de recherche (ticket MBKP0IA-14)."""
import os

from fastapi import FastAPI
from qdrant_client import QdrantClient

# Adresse de Qdrant : lue dans une variable d'environnement, sinon valeur par défaut
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# Création de l'application FastAPI (titre et description apparaissent dans la documentation)
app = FastAPI(
    title="PFE-002 — Moteur de recherche sémantique",
    description="API du moteur de recherche sémantique multilingue (FR / AR / EN).",
    version="0.1.0",
)

## Client Qdrant : il ne se connecte pas tout de suite, seulement quand on l'utilise.
# timeout=2 : on n'attend pas plus de 2 secondes une réponse de Qdrant.
# check_compatibility=False : pas d'appel réseau au démarrage. Les versions du client
# et du serveur sont déjà figées toutes les deux en 1.20.0 (requirements.txt et docker-compose.yml).
client_qdrant = QdrantClient(url=QDRANT_URL, timeout=2, check_compatibility=False)


def qdrant_est_connecte() -> bool:
    """Renvoie True si Qdrant répond, False sinon."""
    try:
        client_qdrant.get_collections()
        return True
    except Exception:
        return False


@app.get("/health", summary="État du service")
def health():
    """Indique si le service fonctionne et s'il est connecté à Qdrant."""
    return {
        "statut": "ok",
        "qdrant": "connecte" if qdrant_est_connecte() else "injoignable",
    }