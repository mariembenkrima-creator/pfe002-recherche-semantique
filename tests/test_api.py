"""Tests du squelette FastAPI (ticket MBKP0IA-14)."""

import subprocess
import sys

from fastapi.testclient import TestClient

from semsearch.api.main import app

client = TestClient(app)


def test_health_repond_200_avec_etat_qdrant():
    # Critère 1 : GET /health renvoie 200 et l'état de la connexion à Qdrant
    reponse = client.get("/health")
    assert reponse.status_code == 200
    contenu = reponse.json()
    assert contenu["statut"] == "ok"
    # Le test passe que Qdrant soit allumé ou non : on vérifie juste que l'état est indiqué
    assert contenu["qdrant"] in ("connecte", "injoignable")


def test_documentation_openapi_accessible():
    # Critère 2 : la documentation OpenAPI se charge sans erreur
    reponse = client.get("/openapi.json")
    assert reponse.status_code == 200
    assert "/health" in reponse.json()["paths"]

    page_docs = client.get("/docs")
    assert page_docs.status_code == 200


def test_demarrage_rapide_sans_modele():
    # Critère 3 : le service démarre en moins de 5 secondes, sans modèle chargé.
    # On lance un Python tout neuf qui charge l'API et mesure le temps.
    code = (
        "import sys, time\n"
        "debut = time.perf_counter()\n"
        "import semsearch.api.main\n"
        "duree = time.perf_counter() - debut\n"
        "assert 'sentence_transformers' not in sys.modules, 'un modele est charge au demarrage'\n"
        "print(duree)\n"
    )
    resultat = subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert resultat.returncode == 0, resultat.stderr
    duree = float(resultat.stdout.strip())
    print(f"Temps de démarrage : {duree:.2f} s")
    assert duree < 5
