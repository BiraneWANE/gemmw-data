"""Contrôles d'entrée sur un tableau de ventes, avant chargement.

Chaque contrôle est une attente simple sur les données ; un seul échec bloque l'import et dit
pourquoi. C'est volontairement sans dépendance : Great Expectations viendra quand il y aura
plusieurs sources et un besoin de rapport ; le vocabulaire (attente, résultat) est le même.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from gemmw.entrepot.ventes import COLONNES

PLATEFORMES = {"payhip", "etsy", "amazon", "site"}
PRIX_MAX_PLAUSIBLE = 500.0


@dataclass(frozen=True)
class Resultat:
    attente: str
    succes: bool
    detail: str = ""


def controler(ventes: pd.DataFrame) -> list[Resultat]:
    resultats: list[Resultat] = []

    manquantes = [c for c in COLONNES if c not in ventes.columns]
    resultats.append(
        Resultat("colonnes attendues présentes", not manquantes, ", ".join(manquantes))
    )
    if manquantes:
        return resultats  # inutile d'aller plus loin

    doublons = ventes.duplicated(subset=["plateforme", "commande_ref"]).sum()
    resultats.append(Resultat("aucune commande en double", doublons == 0, f"{doublons} doublon(s)"))

    negatifs = (ventes["prix_ttc_eur"] <= 0).sum()
    resultats.append(Resultat("prix strictement positifs", negatifs == 0, f"{negatifs} ligne(s)"))

    enormes = (ventes["prix_ttc_eur"] > PRIX_MAX_PLAUSIBLE).sum()
    resultats.append(
        Resultat(f"prix sous {PRIX_MAX_PLAUSIBLE:.0f} €", enormes == 0, f"{enormes} ligne(s)")
    )

    frais_trop = (ventes["frais_eur"] > ventes["prix_ttc_eur"]).sum()
    resultats.append(
        Resultat("frais inférieurs au prix", frais_trop == 0, f"{frais_trop} ligne(s)")
    )

    dates = pd.to_datetime(ventes["vendue_le"], errors="coerce")
    invalides = dates.isna().sum()
    futur = (dates > pd.Timestamp.now()).sum()
    resultats.append(Resultat("dates valides", invalides == 0, f"{invalides} invalide(s)"))
    resultats.append(Resultat("aucune date dans le futur", futur == 0, f"{futur} ligne(s)"))

    inconnues = set(ventes["plateforme"]) - PLATEFORMES
    resultats.append(Resultat("plateforme connue", not inconnues, ", ".join(sorted(inconnues))))

    vides = ventes["acheteuse_hash"].str.len().ne(64).sum()
    resultats.append(Resultat("acheteuse hachée (64 caractères)", vides == 0, f"{vides} ligne(s)"))
    return resultats


def tout_passe(resultats: list[Resultat]) -> bool:
    return all(r.succes for r in resultats)
