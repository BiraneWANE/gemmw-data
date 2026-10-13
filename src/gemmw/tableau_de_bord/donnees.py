"""Lecture des données du tableau de bord : relevés de prix (JSON lines) et entrepôt (SQLite)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

PRIX_GEMMW = 5.90


def lire_releves(dossiers: list[Path]) -> pd.DataFrame:
    """Tous les relevés trouvés dans les dossiers donnés (data/exemples, data/brut), concaténés."""
    lignes: list[dict] = []
    for dossier in dossiers:
        for fichier in sorted(dossier.glob("releve-*.jsonl")):
            with fichier.open(encoding="utf-8") as f:
                lignes.extend(json.loads(ligne) for ligne in f if ligne.strip())
    if not lignes:
        return pd.DataFrame(
            columns=["releve_le", "site", "page", "titre", "prix_eur", "prix_initial_eur", "url"]
        )
    df = pd.DataFrame(lignes)
    df["releve_le"] = pd.to_datetime(df["releve_le"], utc=True).dt.date
    df["en_promo"] = df["prix_initial_eur"].notna()
    df["pack"] = df["titre"].str.lower().str.startswith("pack")
    return df.drop_duplicates(subset=["releve_le", "url"]).reset_index(drop=True)


def dernier_releve(releves: pd.DataFrame) -> pd.DataFrame:
    if releves.empty:
        return releves
    return releves[releves["releve_le"] == releves["releve_le"].max()]


def lire_ventes(chemin_db: Path) -> pd.DataFrame:
    if not chemin_db.exists():
        return pd.DataFrame(
            columns=[
                "plateforme",
                "commande_ref",
                "vendue_le",
                "produit",
                "prix_ttc_eur",
                "frais_eur",
                "tva_eur",
                "acheteuse_hash",
                "pays",
            ]
        )
    with sqlite3.connect(chemin_db) as conn:
        df = pd.read_sql_query("SELECT * FROM vente ORDER BY vendue_le", conn)
    df["vendue_le"] = pd.to_datetime(df["vendue_le"]).dt.date
    df["net_eur"] = (df["prix_ttc_eur"] - df["frais_eur"] - df["tva_eur"]).round(2)
    return df


def resume_ventes(ventes: pd.DataFrame) -> dict:
    if ventes.empty:
        return {"commandes": 0, "ca_ttc": 0.0, "net": 0.0, "clientes": 0, "retour": 0}
    par_cliente = ventes.groupby("acheteuse_hash").size()
    return {
        "commandes": len(ventes),
        "ca_ttc": round(ventes["prix_ttc_eur"].sum(), 2),
        "net": round(ventes["net_eur"].sum(), 2),
        "clientes": int(par_cliente.size),
        "retour": int((par_cliente > 1).sum()),
    }
