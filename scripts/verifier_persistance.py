"""Vérifie que Qdrant garde ses vecteurs après un redémarrage (ticket MBKP0IA-13).

Utilisation :
    python scripts/verifier_persistance.py ecrire     -> crée 3 vecteurs de test
    python scripts/verifier_persistance.py verifier   -> vérifie qu'ils sont toujours là
"""

import sys

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

COLLECTION = "test_persistance"
client = QdrantClient(url="http://localhost:6333")


def ecrire():
    # On repart de zéro si la collection existe déjà
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)

    # Création de la collection : vecteurs de 4 nombres, comparés par distance cosinus
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=4, distance=Distance.COSINE),
    )

    # Ajout de 3 points : identifiant + vecteur + payload (informations attachées)
    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(id=1, vector=[0.1, 0.2, 0.3, 0.4], payload={"texte": "arrêté"}),
            PointStruct(
                id=2, vector=[0.4, 0.3, 0.2, 0.1], payload={"texte": "circulaire"}
            ),
            PointStruct(
                id=3, vector=[0.2, 0.2, 0.2, 0.2], payload={"texte": "note de service"}
            ),
        ],
        wait=True,
    )
    print(f"3 vecteurs écrits dans la collection '{COLLECTION}'.")


def verifier():
    if not client.collection_exists(COLLECTION):
        print("ÉCHEC : la collection a disparu.")
        sys.exit(1)

    nombre = client.count(COLLECTION, exact=True).count
    print(f"{nombre} vecteur(s) trouvé(s) dans '{COLLECTION}'.")

    if nombre != 3:
        print("ÉCHEC : il manque des vecteurs.")
        sys.exit(1)
    print("OK : les vecteurs ont survécu au redémarrage.")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("ecrire", "verifier"):
        print(__doc__)
        sys.exit(1)
    ecrire() if sys.argv[1] == "ecrire" else verifier()
