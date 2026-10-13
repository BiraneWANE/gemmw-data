"""Collecte : relevé hebdomadaire des prix des livrets concurrents.

Chaque site a un module dans `sites/` qui expose `extraire(html) -> list[Produit]`.
Le relevé est écrit en JSON lines, un fichier par jour, jamais modifié ensuite.
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path

import requests

from gemmw.collecte.sites import SITES, Produit
from gemmw.config import settings


def telecharger(url: str) -> str:
    reponse = requests.get(url, headers={"User-Agent": settings.user_agent}, timeout=30)
    reponse.raise_for_status()
    return reponse.text


def lancer_collecte(sortie: Path) -> Path:
    sortie.mkdir(parents=True, exist_ok=True)
    horodatage = datetime.now(UTC)
    chemin = sortie / f"releve-{horodatage:%Y-%m-%d}.jsonl"
    with chemin.open("a", encoding="utf-8") as f:
        for site in SITES:
            for url in site.urls:
                produits: list[Produit] = site.extraire(telecharger(url))
                for p in produits:
                    ligne = {"releve_le": horodatage.isoformat(), "site": site.nom, **p.__dict__}
                    f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
                time.sleep(settings.delai_entre_requetes_s)
    return chemin
