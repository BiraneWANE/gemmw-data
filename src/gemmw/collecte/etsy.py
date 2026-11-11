"""Collecte Etsy : les annonces actives qui ressemblent aux livrets Gem'MW, via l'API officielle.

Etsy n'autorise pas la lecture de ses pages par un robot : on passe par son API v3
(`findAllListingsActive`), avec une clé d'application créée sur etsy.com/developers.
Sans clé (variable GEMMW_ETSY_API_KEY vide), cette collecte est simplement sautée.
On ne garde que les annonces en euros, pour comparer des prix comparables.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable

import requests

from gemmw.collecte.sites import Produit

log = logging.getLogger(__name__)

API = "https://openapi.etsy.com/v3/application/listings/active"
PAR_PAGE = 100


def annonce_vers_produit(annonce: dict) -> Produit | None:
    prix = annonce.get("price") or {}
    if prix.get("currency_code") != "EUR" or not prix.get("divisor"):
        return None
    montant = prix["amount"] / prix["divisor"]
    titre = (annonce.get("title") or "").strip()
    url = (annonce.get("url") or "").split("?")[0]
    if not titre or not url or montant <= 0:
        return None
    return Produit(titre=titre, prix_eur=round(montant, 2), url=url, format="etsy")


def rechercher(
    mots_cles: str,
    cle: str,
    pages: int = 1,
    get: Callable[..., requests.Response] = requests.get,
    pause_s: float = 0.5,
) -> list[Produit]:
    produits: list[Produit] = []
    vus: set[str] = set()
    for n in range(pages):
        reponse = get(
            API,
            headers={"x-api-key": cle},
            params={"keywords": mots_cles, "limit": PAR_PAGE, "offset": n * PAR_PAGE},
            timeout=30,
        )
        reponse.raise_for_status()
        resultats = reponse.json().get("results", [])
        for annonce in resultats:
            p = annonce_vers_produit(annonce)
            if p and p.url not in vus:
                vus.add(p.url)
                produits.append(p)
        if len(resultats) < PAR_PAGE:
            break
        time.sleep(pause_s)
    log.info("Etsy « %s » : %d annonces en euros", mots_cles, len(produits))
    return produits


def collecter_etsy(cle: str, recherches: tuple[str, ...], **kw) -> list[Produit]:
    if not cle:
        log.info("Pas de clé Etsy (GEMMW_ETSY_API_KEY) : collecte Etsy sautée")
        return []
    tous: list[Produit] = []
    vus: set[str] = set()
    for mots in recherches:
        try:
            for p in rechercher(mots, cle, **kw):
                if p.url not in vus:
                    vus.add(p.url)
                    tous.append(p)
        except requests.RequestException as e:
            log.warning("Etsy « %s » : échec %s", mots, e)
    return tous
