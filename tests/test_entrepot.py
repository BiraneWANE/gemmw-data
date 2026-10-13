import sqlite3

import pytest

from gemmw.entrepot import ouvrir


def test_schema_se_cree(tmp_path):
    conn = ouvrir(tmp_path / "t.db")
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"releve_prix", "vente"} <= tables


def test_prix_negatif_refuse(tmp_path):
    conn = ouvrir(tmp_path / "t.db")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO releve_prix (releve_le, site, titre, prix_eur, url) VALUES (?,?,?,?,?)",
            ("2026-10-12", "x", "t", -1, "u"),
        )
