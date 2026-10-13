"""Un extracteur par type de boutique. Chacun ne fait qu'une chose : HTML -> liste de produits.

Les deux concurrents suivis tournent sous WooCommerce, mais avec trois balisages différents :
le classique (`li.product`), le thème Flatsome (`div.product-small.box`) et une grille maison
(`li.ckc-pcv2-card`). L'extracteur WooCommerce gère les trois, ainsi que le prix barré des
promotions (`del` = prix initial, `ins` = prix actuel), la fourchette de prix des produits
variables (« 13,00 € – 15,00 € », on garde le plus bas) et la pagination des catégories.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag


@dataclass(frozen=True)
class Produit:
    titre: str
    prix_eur: float
    url: str
    prix_initial_eur: float | None = None  # renseigné seulement en promotion
    format: str = ""  # "pdf", "papier", ... quand la page le dit


@dataclass(frozen=True)
class Site:
    nom: str
    urls: tuple[str, ...]
    extraire: Callable[[str], list[Produit]]
    pages_suivantes: Callable[[str, str], list[str]] | None = None


CARTES = "li.product, div.product-small.box, li.ckc-pcv2-card"
TITRE = ".woocommerce-loop-product__title, .product-title, .ckc-pcv2-card__name, h2, h3, h4"
LIEN = (
    "a.woocommerce-LoopProduct-link, a.woocommerce-loop-product__link, "
    ".product-title a, .ckc-pcv2-card__name a, a[href*='/produit/']"
)
PRIX = ".price, .ckc-pcv2-card__price"


def extraire_woocommerce(html: str) -> list[Produit]:
    soupe = BeautifulSoup(html, "html.parser")
    produits: list[Produit] = []
    vus: set[str] = set()
    for carte in soupe.select(CARTES):
        lien = carte.select_one(LIEN)
        titre = carte.select_one(TITRE)
        prix = carte.select_one(PRIX)
        if not (lien and titre and prix):
            continue
        url = lien.get("href", "")
        if not url or url in vus:
            continue
        actuel, initial = _prix_woocommerce(prix)
        if actuel is None:
            continue
        vus.add(url)
        produits.append(
            Produit(
                titre=titre.get_text(" ", strip=True),
                prix_eur=actuel,
                url=url,
                prix_initial_eur=initial,
            )
        )
    return produits


def pages_woocommerce(html: str, url_page: str) -> list[str]:
    """Les autres pages de la même catégorie (`.../page/2/`), sans doublon ni retour en arrière."""
    soupe = BeautifulSoup(html, "html.parser")
    pages: list[str] = []
    for a in soupe.select(".page-numbers a, a.page-number, a.page-numbers"):
        href = urljoin(url_page, a.get("href", ""))
        if "/page/" not in href or href.rstrip("/").endswith("/page/1"):
            continue  # pas une page suivante, ou retour à la première page
        if href != url_page and href not in pages:
            pages.append(href)
    return pages


def _prix_woocommerce(bloc: Tag) -> tuple[float | None, float | None]:
    """Retourne (prix actuel, prix initial). Le prix initial n'existe qu'en promotion."""
    ins = bloc.select_one("ins .amount")
    sup = bloc.select_one("del .amount")
    if ins:
        return _nombre(ins.get_text()), _nombre(sup.get_text()) if sup else None
    valeurs = [v for v in (_nombre(m.get_text()) for m in bloc.select(".amount")) if v is not None]
    if not valeurs:
        return None, None
    # Un produit variable affiche une fourchette "13,00 € – 15,00 €" : on garde le prix le plus bas
    return min(valeurs), None


def _nombre(texte: str) -> float | None:
    chiffres = "".join(c for c in texte if c.isdigit() or c in ",.")
    if not chiffres:
        return None
    return float(chiffres.replace(",", "."))


SITES: tuple[Site, ...] = (
    Site(
        nom="mespetitslivrets",
        urls=(
            "https://mespetitslivrets.fr/categorie-produit/livrets-dactivites/livrets-bebes/",
            "https://mespetitslivrets.fr/categorie-produit/livrets-dactivites/livrets-18-mois-3-ans/",
            "https://mespetitslivrets.fr/categorie-produit/livrets-dactivites/livrets-3-6-ans/",
        ),
        extraire=extraire_woocommerce,
        pages_suivantes=pages_woocommerce,
    ),
    Site(
        nom="clesskidscreations",
        urls=(
            "https://clesskidscreations.fr/categorie-produit/livrets-dactivites/",
            "https://clesskidscreations.fr/categorie-produit/imagiers/",
        ),
        extraire=extraire_woocommerce,
        pages_suivantes=pages_woocommerce,
    ),
)
