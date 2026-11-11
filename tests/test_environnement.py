import sys


def test_version_python():
    # Le projet est déclaré pour Python 3.12
    assert sys.version_info[:2] == (3, 12)


def test_package_installe():
    import semsearch  # noqa: F401


def test_dependances_installees():
    import fastapi  # noqa: F401
    import qdrant_client  # noqa: F401
    import sentence_transformers  # noqa: F401
