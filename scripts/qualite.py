"""Chaîne de qualité en une seule commande (ticket MBKP0IA-15).

Utilisation :
    python scripts/qualite.py

Exécute dans l'ordre : vérification du formatage, analyse statique,
puis tests avec mesure de la couverture. S'arrête au premier échec.
"""

import subprocess
import sys

# Chaque étape : (nom affiché, commande à lancer, conseil en cas d'échec)
ETAPES = [
    (
        "Formatage",
        [sys.executable, "-m", "ruff", "format", "--check", "."],
                "Lancez 'ruff format .'. Si Ruff signale 'invalid-syntax', corrigez d'abord la ligne indiquée.",
    ),
    (
        "Analyse statique",
        [sys.executable, "-m", "ruff", "check", "."],
        "Lancez 'ruff check --fix .' puis corrigez à la main le reste.",
    ),
    (
        "Tests et couverture",
        [sys.executable, "-m", "pytest"],
        "Lisez le détail du test en échec ci-dessus.",
    ),
]


def main() -> int:
    for numero, (nom, commande, conseil) in enumerate(ETAPES, start=1):
        print(f"\n=== Étape {numero}/{len(ETAPES)} : {nom} ===", flush=True)
        resultat = subprocess.run(commande, check=False)
        if resultat.returncode != 0:
            print(f"\nÉCHEC à l'étape « {nom} ».")
            print(f"Conseil : {conseil}")
            return resultat.returncode
    print("\nSUCCÈS : formatage, analyse statique et tests sont au vert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
