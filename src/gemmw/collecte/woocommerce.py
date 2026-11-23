"""Commandes de la boutique du site (WooCommerce, famillemw.fr), via son API REST.

Il faut une clé d'API en lecture seule, créée dans WordPress (WooCommerce > Réglages >
Avancé > API REST, droits « Lecture »), placée dans .env : GEMMW_WC_URL, GEMMW_WC_CLE,
GEMMW_WC_SECRET. Le fichier écrit contient les emails des clientes : il reste dans data/brut
(ignoré par git) et n'est lu que pour être haché à l'import.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import date
from pathlib import Path

import requests

log = logging.getLogger(__name__)

PAR_PAGE = 100


def recuperer_commandes(
    url: str,
    cle: str,
    secret: str,
    get: Callable[..., requests.Response] = requests.get,
) -> list[dict]:
    """Toutes les commandes, page par page (l'API en renvoie 100 au plus à la fois)."""
    commandes: list[dict] = []
    page = 1
    while True:
        reponse = get(
            f"{url.rstrip('/')}/wp-json/wc/v3/orders",
            params={"per_page": PAR_PAGE, "page": page, "status": "any", "orderby": "id"},
            auth=(cle, secret),
            timeout=30,
        )
        reponse.raise_for_status()
        lot = reponse.json()
        commandes.extend(lot)
        if len(lot) < PAR_PAGE:
            return commandes
        page += 1


def ecrire(commandes: list[dict], dossier: Path, jour: date | None = None) -> Path:
    dossier.mkdir(parents=True, exist_ok=True)
    chemin = dossier / f"commandes-site-{(jour or date.today()).isoformat()}.json"
    chemin.write_text(json.dumps(commandes, ensure_ascii=False, indent=1), encoding="utf-8")
    log.info("%s commande(s) écrites dans %s", len(commandes), chemin)
    return chemin
