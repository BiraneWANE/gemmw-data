"""Catalogue commun : une référence (SKU) par livret et par format, pour les trois boutiques.

Le site, Payhip et Etsy vendent les mêmes livrets sous des noms et des identifiants
différents. Le catalogue (produits.toml, versionné) les relie à une seule référence, ce qui
permet de compter les ventes d'un livret toutes boutiques confondues.
"""

from __future__ import annotations

import re
import tomllib
import unicodedata
from dataclasses import dataclass
from pathlib import Path

FICHIER = Path(__file__).parent / "produits.toml"
FORMATS = {"pdf", "plastifie", "kit"}


@dataclass(frozen=True)
class Produit:
    sku: str
    livret: str
    format: str
    prix_eur: float
    age: str
    site_id: int | None = None
    payhip: str = ""
    payhip_titre: str = ""
    etsy: str = ""


class CatalogueInvalide(ValueError):  # noqa: N818
    pass


def _normaliser(texte: str) -> str:
    """Minuscules, sans accents, apostrophes et espaces unifiés : pour comparer des titres."""
    texte = texte.replace("’", "'")
    texte = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", texte).strip()


def charger(fichier: Path = FICHIER) -> list[Produit]:
    """Lit le catalogue et vérifie qu'il est cohérent ; lève CatalogueInvalide sinon."""
    donnees = tomllib.loads(fichier.read_text(encoding="utf-8"))
    produits = [Produit(**p) for p in donnees.get("produit", [])]
    erreurs = verifier(produits)
    if erreurs:
        raise CatalogueInvalide(" ; ".join(erreurs))
    return produits


def verifier(produits: list[Produit]) -> list[str]:
    erreurs: list[str] = []
    for champ in ("sku", "payhip", "etsy", "site_id"):
        valeurs = [getattr(p, champ) for p in produits if getattr(p, champ)]
        doublons = sorted({str(v) for v in valeurs if valeurs.count(v) > 1})
        if doublons:
            erreurs.append(f"{champ} en double : {', '.join(doublons)}")
    for p in produits:
        if p.format not in FORMATS:
            erreurs.append(f"{p.sku} : format inconnu « {p.format} »")
        if p.prix_eur < 0:
            erreurs.append(f"{p.sku} : prix négatif")
        if not p.sku.startswith("GEMMW-"):
            erreurs.append(f"{p.sku} : la référence doit commencer par GEMMW-")
    return erreurs


class Index:
    """Retrouve la référence d'une vente à partir de ce que chaque boutique exporte."""

    def __init__(self, produits: list[Produit]) -> None:
        self.par_sku = {p.sku: p for p in produits}
        self.par_payhip = {p.payhip: p.sku for p in produits if p.payhip}
        self.par_titre = {_normaliser(p.payhip_titre): p.sku for p in produits if p.payhip_titre}
        self.par_etsy = {p.etsy: p.sku for p in produits if p.etsy}
        # Titre Etsy : on compare le début (Etsy coupe et ajoute des mots-clés)
        self.prefixes = sorted(
            ((_normaliser(p.livret), p.sku) for p in produits if p.etsy),
            key=lambda x: -len(x[0]),
        )

    def sku(self, plateforme: str, produit: str) -> str | None:
        produit = (produit or "").strip()
        if not produit:
            return None
        if plateforme == "site":
            skus = [s for s in produit.split("+") if s]
            return skus[0] if len(skus) == 1 and skus[0] in self.par_sku else None
        if plateforme == "payhip":
            return self.par_payhip.get(produit) or self.par_titre.get(_normaliser(produit))
        if plateforme == "etsy":
            if produit in self.par_sku:
                return produit
            if produit in self.par_etsy:
                return self.par_etsy[produit]
            texte = _normaliser(produit)
            return next((s for prefixe, s in self.prefixes if texte.startswith(prefixe)), None)
        return None
