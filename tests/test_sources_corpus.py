"""Vérifie la liste des sources du corpus d'amorçage, sans rien télécharger."""

import json
from pathlib import Path

FICHIER_SOURCES = Path(__file__).parent.parent / "corpus" / "sources_amorcage.json"
SOURCES = json.loads(FICHIER_SOURCES.read_text(encoding="utf-8"))["sources"]


def test_trois_langues_couvertes():
    langues = {langue for source in SOURCES for langue in source["langues"]}
    assert {"fr", "ar", "en"} <= langues


def test_au_moins_deux_types_de_documents():
    types = {source["type"] for source in SOURCES}
    assert len(types) >= 2


def test_licence_consignee_pour_chaque_source():
    for source in SOURCES:
        assert source["licence"].strip(), f"licence manquante : {source['cote']}"
        assert source["licence_reference"].startswith("https://")


def test_url_contient_la_langue():
    for source in SOURCES:
        assert "{LANGUE}" in source["url"], f"URL sans {{LANGUE}} : {source['cote']}"
