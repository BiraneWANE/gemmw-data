"""Import des ventes depuis les exports de Payhip, d'Etsy et de la boutique du site.

Les deux plateformes exportent des fichiers de forme différente ; chacune a son lecteur qui
ramène tout à un même tableau de ventes (une ligne par commande). L'email de l'acheteuse est
remplacé par un haché salé avant d'entrer dans la base : on sait reconnaître une cliente qui
revient, on ne peut pas retrouver qui elle est (voir GOUVERNANCE.md).
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

COLONNES = [
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


@dataclass(frozen=True)
class RapportImport:
    plateforme: str
    lues: int
    inserees: int
    ignorees: int  # déjà présentes (même plateforme, même référence)


def hacher_email(email: str, sel: str) -> str:
    """SHA-256 de l'email normalisé (minuscules, sans espaces) avec un sel secret."""
    normalise = email.strip().lower()
    return hashlib.sha256(f"{sel}:{normalise}".encode()).hexdigest()


def lire_payhip(chemin: Path, sel: str) -> pd.DataFrame:
    """Export « Customers » de Payhip. Une ligne par commande, montants dans la devise de vente."""
    brut = pd.read_csv(chemin, dtype=str, keep_default_na=False)
    brut = brut[brut["Status"].str.lower().eq("paid")]
    brut = brut[brut["Currency"].str.upper().eq("EUR")]
    montant = pd.to_numeric(brut["Amount Gross"], errors="coerce")
    frais = pd.to_numeric(brut["PayPal/Stripe Fee"], errors="coerce").fillna(0) + pd.to_numeric(
        brut["Payhip Fee"], errors="coerce"
    ).fillna(0)
    tva = pd.to_numeric(brut["EU VAT Amount"], errors="coerce").fillna(0)
    date = pd.to_datetime(brut["Date"], errors="coerce", utc=True)
    ventes = pd.DataFrame(
        {
            "plateforme": "payhip",
            # Payhip n'exporte pas d'identifiant de commande : email + date + montant en font un
            "commande_ref": [
                hashlib.sha1(f"{e}|{d}|{m}".encode()).hexdigest()[:16]  # noqa: S324 - pas un secret
                for e, d, m in zip(brut["Email"], brut["Date"], brut["Amount Gross"], strict=True)
            ],
            "vendue_le": date.dt.strftime("%Y-%m-%d"),
            "produit": brut["Items in Cart"].str.strip(),
            "prix_ttc_eur": montant,
            "frais_eur": frais.round(2),
            "tva_eur": tva.round(2),
            "acheteuse_hash": [hacher_email(e, sel) for e in brut["Email"]],
            "pays": brut["EU VAT Country Name"].replace("", None),
        }
    )
    return ventes[COLONNES].dropna(subset=["prix_ttc_eur", "vendue_le"]).reset_index(drop=True)


def lire_etsy(chemin: Path, sel: str) -> pd.DataFrame:
    """Export « Orders » (EtsySoldOrders) du Shop Manager. Une ligne par commande."""
    brut = pd.read_csv(chemin, dtype=str, keep_default_na=False)
    brut = brut[brut["Currency"].str.upper().eq("EUR")]
    statut_ok = ~brut["Status"].str.lower().isin({"canceled", "cancelled", "refunded"})
    brut = brut[statut_ok]
    total = pd.to_numeric(brut["Order Total"], errors="coerce")
    net = pd.to_numeric(brut["Order Net"], errors="coerce")
    tva = pd.to_numeric(brut["Sales Tax"], errors="coerce").fillna(0)
    date = pd.to_datetime(brut["Sale Date"], format="%m/%d/%y", errors="coerce", utc=True)
    ventes = pd.DataFrame(
        {
            "plateforme": "etsy",
            "commande_ref": brut["Order ID"].str.strip(),
            "vendue_le": date.dt.strftime("%Y-%m-%d"),
            "produit": brut["SKU"].replace("", None).fillna("(voir détail articles)"),
            "prix_ttc_eur": total,
            # Etsy ne détaille pas ses frais dans ce fichier : net = total - frais - taxe reversée
            "frais_eur": (total - net - tva).round(2),
            "tva_eur": tva.round(2),
            "acheteuse_hash": [hacher_email(e, sel) for e in brut["Buyer"]],
            "pays": brut["Ship Country"].replace("", None),
        }
    )
    return ventes[COLONNES].dropna(subset=["prix_ttc_eur", "vendue_le"]).reset_index(drop=True)


STATUTS_SITE_PAYES = {"completed", "processing"}


def lire_site(chemin: Path, sel: str) -> pd.DataFrame:
    """Commandes de la boutique WooCommerce (famillemw.fr), au format JSON de l'API REST.

    Une ligne par commande payée. Les commandes à 0 € (livrets offerts, commandes d'essai
    avec un code à 100 %) ne sont pas des ventes : elles sont écartées. Les produits sont
    désignés par leur référence (SKU), la même que dans le catalogue commun.
    """
    commandes = json.loads(chemin.read_text(encoding="utf-8"))
    lignes = []
    for c in commandes:
        total = float(c.get("total") or 0)
        if c.get("status") not in STATUTS_SITE_PAYES or total <= 0:
            continue
        facturation = c.get("billing") or {}
        skus = [li.get("sku") or str(li.get("product_id", "")) for li in c.get("line_items", [])]
        lignes.append(
            {
                "plateforme": "site",
                "commande_ref": str(c["id"]),
                "vendue_le": str(c.get("date_paid") or c.get("date_created") or "")[:10],
                "produit": "+".join(skus),
                "prix_ttc_eur": total,
                # Les frais Stripe et PayPal n'apparaissent pas dans la commande WooCommerce
                "frais_eur": 0.0,
                "tva_eur": round(float(c.get("total_tax") or 0), 2),
                "acheteuse_hash": hacher_email(facturation.get("email", ""), sel),
                "pays": facturation.get("country") or None,
            }
        )
    return pd.DataFrame(lignes, columns=COLONNES)


LECTEURS = {"payhip": lire_payhip, "etsy": lire_etsy, "site": lire_site}


def charger(conn: sqlite3.Connection, ventes: pd.DataFrame, plateforme: str) -> RapportImport:
    """Insère les ventes absentes de la base ; une commande déjà connue est ignorée, pas écrasée."""
    inserees = 0
    for ligne in ventes.itertuples(index=False):
        cur = conn.execute(
            "INSERT OR IGNORE INTO vente "
            "(plateforme, commande_ref, vendue_le, produit, prix_ttc_eur, frais_eur, tva_eur,"
            " acheteuse_hash, pays) VALUES (?,?,?,?,?,?,?,?,?)",
            tuple(ligne),
        )
        inserees += cur.rowcount
    conn.commit()
    return RapportImport(plateforme, len(ventes), inserees, len(ventes) - inserees)


def importer(conn: sqlite3.Connection, chemin: Path, plateforme: str, sel: str) -> RapportImport:
    ventes = LECTEURS[plateforme](chemin, sel)
    return charger(conn, ventes, plateforme)


def rattacher_au_catalogue(conn: sqlite3.Connection, produits: list) -> int:
    """Copie le catalogue dans la base et remplit la référence (SKU) des ventes qui n'en ont pas.

    Renvoie le nombre de ventes rattachées. Une vente qu'on ne sait pas rattacher garde un SKU
    vide : elle reste visible, pour qu'on complète le catalogue plutôt que de la perdre.
    """
    from gemmw.catalogue import Index

    conn.executemany(
        "INSERT INTO produit (sku, livret, format, prix_eur, age) VALUES (?,?,?,?,?) "
        "ON CONFLICT(sku) DO UPDATE SET livret=excluded.livret, format=excluded.format, "
        "prix_eur=excluded.prix_eur, age=excluded.age",
        [(p.sku, p.livret, p.format, p.prix_eur, p.age) for p in produits],
    )
    index = Index(produits)
    rattachees = 0
    a_traiter = conn.execute(
        "SELECT id, plateforme, produit FROM vente WHERE sku IS NULL"
    ).fetchall()
    for id_vente, plateforme, produit in a_traiter:
        sku = index.sku(plateforme, produit)
        if sku:
            conn.execute("UPDATE vente SET sku = ? WHERE id = ?", (sku, id_vente))
            rattachees += 1
    conn.commit()
    return rattachees
