"""Démonstration provisoire de recherche sémantique (ticket MBKP0IA-16).

Utilisation :
    python scripts/demo_recherche.py
    python scripts/demo_recherche.py "votre question"

Indexe une dizaine de phrases administratives (FR / AR / EN) dans Qdrant,
puis affiche les 3 phrases les plus proches de la question par le sens.

Modèle PROVISOIRE : le choix définitif se fera sur mesures au sprint 4.
"""

import sys

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

MODELE = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION = "demo_recherche"
QUESTION_PAR_DEFAUT = "Combien de temps dure le congé de maternité ?"

# Corpus de démonstration : (langue, phrase)
PHRASES = [
    (
        "fr",
        "Les demandes de congé annuel doivent être déposées au service du personnel un mois à l'avance.",
    ),
    (
        "fr",
        "La circulaire fixe les modalités de remboursement des frais de déplacement des agents.",
    ),
    (
        "fr",
        "Tout recrutement de personnel contractuel est soumis à l'autorisation préalable du ministère.",
    ),
    ("ar", "تتمتع الموظفة بإجازة أمومة مدفوعة الأجر لمدة ثلاثة أشهر."),
    ("ar", "يجب تقديم التصريح الضريبي السنوي قبل نهاية شهر مارس."),
    ("ar", "يحدد هذا القرار مواقيت العمل الإدارية خلال شهر رمضان."),
    (
        "en",
        "Employees working remotely must use the secure connection provided by the IT department.",
    ),
    (
        "en",
        "Public procurement contracts above the threshold require an open call for tenders.",
    ),
    (
        "en",
        "The annual performance review takes place each December with the direct supervisor.",
    ),
]


def main() -> None:
    question = sys.argv[1] if len(sys.argv) > 1 else QUESTION_PAR_DEFAUT

    print(f"Chargement du modèle {MODELE}")
    print(
        "(au premier lancement seulement : téléchargement d'environ 470 Mo)", flush=True
    )
    modele = SentenceTransformer(MODELE)

    # 1. Transformer chaque phrase en vecteur
    textes = [texte for _, texte in PHRASES]
    vecteurs = modele.encode(textes, normalize_embeddings=True)

    # 2. Recréer la collection de démonstration et y ranger les vecteurs
    client = QdrantClient(url="http://localhost:6333", check_compatibility=False)
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=len(vecteurs[0]), distance=Distance.COSINE),
    )
    points = []
    for i, (langue, texte) in enumerate(PHRASES):
        charge = {"langue": langue, "texte": texte}
        points.append(PointStruct(id=i, vector=vecteurs[i].tolist(), payload=charge))
    client.upsert(collection_name=COLLECTION, points=points, wait=True)

    # 3. Transformer la question en vecteur et chercher les phrases les plus proches
    vecteur_question = modele.encode(question, normalize_embeddings=True)
    resultats = client.query_points(
        collection_name=COLLECTION, query=vecteur_question.tolist(), limit=3
    ).points

    print(f"\nQuestion : {question}\n")
    for rang, point in enumerate(resultats, start=1):
        langue = point.payload["langue"]
        texte = point.payload["texte"]
        print(f"{rang}. [{langue}] score {point.score:.2f} : {texte}")


if __name__ == "__main__":
    main()
