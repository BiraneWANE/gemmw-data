"""Entrepôt : SQLite pour démarrer, PostgreSQL quand il y aura du volume. Même schéma."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")


def ouvrir(chemin: Path) -> sqlite3.Connection:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(chemin)
    conn.executescript(SCHEMA)
    return conn
