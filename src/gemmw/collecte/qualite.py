"""Contrôles de qualité d'un relevé de prix, avant de s'en servir.

Un relevé est un fichier JSON lines écrit par `lancer_collecte`. On vérifie qu'il est
exploitable : assez de lignes, champs obligatoires présents, prix plausibles, pas de doublon,
et chaque site suivi présent. Un relevé en échec ne doit pas déclencher d'alerte de prix :
une page qui a changé de balisage ferait croire que tous les produits ont disparu.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

CHAMPS_OBLIGATOIRES = ("releve_le", "site", "titre", "prix_eur", "url")
PRIX_MIN_EUR = 0.5
PRIX_MAX_EUR = 200.0


@dataclass(frozen=True)
class Resultat:
    attente: str
    succes: bool
    detail: str = ""


def lire_releve(chemin: Path) -> list[dict]:
    lignes = []
    for i, brut in enumerate(chemin.read_text(encoding="utf-8").splitlines(), start=1):
        if not brut.strip():
            continue
        try:
            lignes.append(json.loads(brut))
        except json.JSONDecodeError as e:
            raise ValueError(f"ligne {i} illisible : {e}") from e
    return lignes


def controler_releve(
    lignes: list[dict], sites_attendus: tuple[str, ...] = (), minimum: int = 5
) -> list[Resultat]:
    res: list[Resultat] = []
    res.append(
        Resultat(f"au moins {minimum} produits", len(lignes) >= minimum, f"{len(lignes)} lus")
    )

    manquants = [
        i
        for i, ligne in enumerate(lignes, 1)
        if any(ligne.get(c) in (None, "") for c in CHAMPS_OBLIGATOIRES)
    ]
    res.append(Resultat("champs obligatoires remplis", not manquants, f"lignes {manquants[:10]}"))

    hors_bornes = [
        ligne.get("url", "?")
        for ligne in lignes
        if not isinstance(ligne.get("prix_eur"), int | float)
        or not PRIX_MIN_EUR <= ligne["prix_eur"] <= PRIX_MAX_EUR
    ]
    res.append(
        Resultat(
            f"prix entre {PRIX_MIN_EUR} et {PRIX_MAX_EUR} €",
            not hors_bornes,
            f"{len(hors_bornes)} hors bornes, ex. {hors_bornes[:3]}",
        )
    )

    promos_incoherentes = [
        ligne.get("url", "?")
        for ligne in lignes
        if ligne.get("prix_initial_eur") is not None
        and isinstance(ligne.get("prix_eur"), int | float)
        and ligne["prix_initial_eur"] <= ligne["prix_eur"]
    ]
    res.append(
        Resultat(
            "prix barré supérieur au prix actuel",
            not promos_incoherentes,
            f"ex. {promos_incoherentes[:3]}",
        )
    )

    doublons = [
        u
        for u, n in Counter((ligne.get("site"), ligne.get("url")) for ligne in lignes).items()
        if n > 1
    ]
    res.append(Resultat("aucun produit en double", not doublons, f"ex. {doublons[:3]}"))

    if sites_attendus:
        presents = {ligne.get("site") for ligne in lignes}
        absents = [s for s in sites_attendus if s not in presents]
        res.append(Resultat("chaque site suivi est présent", not absents, f"absents : {absents}"))
    return res


def tout_passe(resultats: list[Resultat]) -> bool:
    return all(r.succes for r in resultats)
