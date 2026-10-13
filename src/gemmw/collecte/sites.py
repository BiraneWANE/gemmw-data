"""Un extracteur par site concurrent. Chacun ne fait qu'une chose : HTML -> liste de produits."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class Produit:
    titre: str
    prix_eur: float
    url: str
    format: str = ""  # "pdf", "papier", ...


@dataclass(frozen=True)
class Site:
    nom: str
    urls: tuple[str, ...]
    extraire: Callable[[str], list[Produit]]


def extraire_woocommerce(html: str) -> list[Produit]:
    """Boutiques WooCommerce : le prix de chaque variation est dans `data-product_variations`."""
    soupe = BeautifulSoup(html, "html.parser")
    produits: list[Produit] = []
    for carte in soupe.select("li.product"):
        lien = carte.select_one("a.woocommerce-LoopProduct-link, a.woocommerce-loop-product__link")
        titre = carte.select_one(".woocommerce-loop-product__title")
        prix = carte.select_one(".price .amount bdi, .price .amount")
        if not (lien and titre and prix):
            continue
        produits.append(
            Produit(
                titre=titre.get_text(strip=True),
                prix_eur=_prix(prix.get_text()),
                url=lien.get("href", ""),
            )
        )
    for form in soupe.select("form.variations_form[data-product_variations]"):
        for v in json.loads(form["data-product_variations"]):
            produits.append(
                Produit(
                    titre=soupe.title.get_text(strip=True) if soupe.title else "",
                    prix_eur=float(v["display_price"]),
                    url=form.get("action", ""),
                    format=" ".join(str(x) for x in v.get("attributes", {}).values()),
                )
            )
    return produits


def _prix(texte: str) -> float:
    chiffres = "".join(c for c in texte if c.isdigit() or c in ",.")
    return float(chiffres.replace(",", "."))


SITES: tuple[Site, ...] = (
    Site(
        nom="mespetitslivrets",
        urls=("https://mespetitslivrets.fr/categorie-produit/livrets/",),
        extraire=extraire_woocommerce,
    ),
    Site(
        nom="clesskidscreations",
        urls=("https://clesskidscreations.fr/categorie-produit/livrets/",),
        extraire=extraire_woocommerce,
    ),
)
