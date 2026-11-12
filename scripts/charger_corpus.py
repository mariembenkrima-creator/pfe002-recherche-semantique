"""Charge le corpus d'amorçage (ticket « Script de chargement d'un corpus d'amorçage »).

Utilisation :
    python scripts/charger_corpus.py

Lit la liste des sources dans corpus/sources_amorcage.json, télécharge chaque
document dans chaque langue vers data/raw/amorcage/, puis écrit un manifeste
avec la taille, l'empreinte SHA-256 et la licence de chaque fichier.
Les fichiers déjà présents ne sont pas retéléchargés.
"""

import hashlib
import json
import sys
import urllib.request
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
FICHIER_SOURCES = RACINE / "corpus" / "sources_amorcage.json"
DOSSIER_SORTIE = RACINE / "data" / "raw" / "amorcage"
EN_TETES = {"User-Agent": "pfe002-recherche-semantique (corpus d'amorcage)"}


def telecharger(url: str) -> bytes:
    """Télécharge un fichier et vérifie que c'est bien un PDF."""
    requete = urllib.request.Request(url, headers=EN_TETES)
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        contenu = reponse.read()
    if not contenu.startswith(b"%PDF"):
        raise ValueError("le fichier reçu n'est pas un PDF")
    return contenu


def main() -> int:
    sources = json.loads(FICHIER_SOURCES.read_text(encoding="utf-8"))["sources"]
    manifeste = []
    erreurs = 0

    for source in sources:
        for langue in source["langues"]:
            nom = source["cote"].replace("/", "_") + f"-{langue}.pdf"
            destination = DOSSIER_SORTIE / langue / nom
            url = source["url"].replace("{LANGUE}", langue.upper())

            if destination.exists():
                contenu = destination.read_bytes()
                etat = "déjà présent"
            else:
                try:
                    contenu = telecharger(url)
                except (OSError, ValueError) as erreur:
                    print(f"ÉCHEC   {nom} : {erreur}")
                    erreurs += 1
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(contenu)
                etat = "téléchargé"

            print(f"{etat:<13} {nom} ({len(contenu) // 1024} Ko)")
            manifeste.append(
                {
                    "fichier": f"{langue}/{nom}",
                    "cote": source["cote"],
                    "langue": langue,
                    "type": source["type"],
                    "titre": source["titre"],
                    "emetteur": source["emetteur"],
                    "date": source["date"],
                    "taille_octets": len(contenu),
                    "sha256": hashlib.sha256(contenu).hexdigest(),
                    "url": url,
                    "licence": source["licence"],
                }
            )

    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)
    chemin_manifeste = DOSSIER_SORTIE / "manifeste.json"
    texte = json.dumps(manifeste, ensure_ascii=False, indent=2)
    chemin_manifeste.write_text(texte, encoding="utf-8")

    langues = Counter(entree["langue"] for entree in manifeste)
    types = Counter(entree["type"] for entree in manifeste)
    print(f"\n{len(manifeste)} fichier(s) dans {DOSSIER_SORTIE}")
    print(f"Langues : {dict(langues)}")
    print(f"Types   : {dict(types)}")
    print(f"Manifeste : {chemin_manifeste}")

    if erreurs:
        print(f"\n{erreurs} téléchargement(s) en échec : relancez le script.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
