"""Collecte : relevé hebdomadaire des prix des livrets concurrents.

Chaque site a un extracteur dans `sites.py` qui expose `extraire(html) -> list[Produit]`.
Avant de lire un site, on vérifie son robots.txt ; une page interdite est sautée et journalisée.
Le relevé est écrit en JSON lines, un fichier par jour, jamais modifié ensuite.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib import robotparser
from urllib.parse import urlsplit

import requests

from gemmw.collecte.sites import SITES, Produit, Site
from gemmw.config import settings

log = logging.getLogger(__name__)


def telecharger(url: str) -> str:
    reponse = requests.get(url, headers={"User-Agent": settings.user_agent}, timeout=30)
    reponse.raise_for_status()
    return reponse.text


class Robots:
    """Un cache des robots.txt, un par domaine, pour ne les lire qu'une fois par collecte."""

    def __init__(self) -> None:
        self._parsers: dict[str, robotparser.RobotFileParser] = {}

    def autorise(self, url: str) -> bool:
        parts = urlsplit(url)
        racine = f"{parts.scheme}://{parts.netloc}"
        if racine not in self._parsers:
            rp = robotparser.RobotFileParser(f"{racine}/robots.txt")
            try:
                rp.read()
            except Exception:  # noqa: BLE001 - un robots.txt illisible vaut autorisation
                rp = None  # type: ignore[assignment]
            self._parsers[racine] = rp
        rp = self._parsers[racine]
        return True if rp is None else rp.can_fetch(settings.user_agent, url)


def collecter_site(site: Site, robots: Robots) -> list[tuple[str, Produit]]:
    """Toutes les pages d'un site, catégories et pages suivantes -> (url de page, produit)."""
    resultats: list[tuple[str, Produit]] = []
    a_visiter = list(site.urls)
    visitees: set[str] = set()
    vus: set[str] = set()  # un produit présent dans plusieurs catégories n'est relevé qu'une fois
    while a_visiter:
        url = a_visiter.pop(0)
        if url in visitees:
            continue
        visitees.add(url)
        if not robots.autorise(url):
            log.warning("robots.txt interdit %s, page sautée", url)
            continue
        try:
            html = telecharger(url)
        except requests.RequestException as e:
            log.warning("échec %s : %s", url, e)
            continue
        produits = [p for p in site.extraire(html) if p.url not in vus]
        vus.update(p.url for p in produits)
        log.info("%s : %d produits sur %s", site.nom, len(produits), url)
        resultats.extend((url, p) for p in produits)
        if site.pages_suivantes:
            a_visiter.extend(u for u in site.pages_suivantes(html, url) if u not in visitees)
        time.sleep(settings.delai_entre_requetes_s)
    return resultats


def lancer_collecte(sortie: Path) -> Path:
    sortie.mkdir(parents=True, exist_ok=True)
    horodatage = datetime.now(UTC)
    chemin = sortie / f"releve-{horodatage:%Y-%m-%d}.jsonl"
    robots = Robots()
    n = 0
    with chemin.open("a", encoding="utf-8") as f:
        for site in SITES:
            for page, p in collecter_site(site, robots):
                ligne = {
                    "releve_le": horodatage.isoformat(),
                    "site": site.nom,
                    "page": page,
                    **p.__dict__,
                }
                f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
                n += 1
    log.info("%d lignes écrites dans %s", n, chemin)
    return chemin
