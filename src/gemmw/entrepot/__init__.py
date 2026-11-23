"""Entrepôt : SQLite pour démarrer, PostgreSQL quand il y aura du volume. Même schéma."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")


def ouvrir(chemin: Path) -> sqlite3.Connection:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(chemin)
    conn.executescript(SCHEMA)
    _migrer(conn)
    return conn


def _migrer(conn: sqlite3.Connection) -> None:
    """Ajoute aux bases déjà créées les colonnes apparues depuis (sans rien perdre)."""
    colonnes = {ligne[1] for ligne in conn.execute("PRAGMA table_info(vente)")}
    if "sku" not in colonnes:
        conn.execute("ALTER TABLE vente ADD COLUMN sku TEXT")
        conn.commit()
