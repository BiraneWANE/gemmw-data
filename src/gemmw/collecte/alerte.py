"""Alerte de prix : compare deux relevés et dit ce qui a changé chez les concurrents.

On compare le relevé du jour au précédent, produit par produit (clé : site + url) :
nouveaux produits, produits retirés, changements de prix au-delà d'un seuil, et début ou
fin de promotion. Le résultat est un petit rapport en texte, lisible par une personne, qu'on
peut écrire dans le résumé GitHub Actions ou envoyer sur Telegram.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import requests

SEUIL_VARIATION = 0.05  # 5 % : en dessous, on ne dérange personne


@dataclass
class Rapport:
    nouveaux: list[dict] = field(default_factory=list)
    retires: list[dict] = field(default_factory=list)
    variations: list[tuple[dict, dict]] = field(default_factory=list)
    promos_debut: list[dict] = field(default_factory=list)
    promos_fin: list[dict] = field(default_factory=list)

    @property
    def vide(self) -> bool:
        return not any(
            (self.nouveaux, self.retires, self.variations, self.promos_debut, self.promos_fin)
        )


def _cle(ligne: dict) -> tuple[str, str]:
    return (ligne.get("site", ""), ligne.get("url", ""))


def comparer(avant: list[dict], apres: list[dict], seuil: float = SEUIL_VARIATION) -> Rapport:
    a = {_cle(x): x for x in avant}
    b = {_cle(x): x for x in apres}
    r = Rapport()
    r.nouveaux = [b[k] for k in b.keys() - a.keys()]
    r.retires = [a[k] for k in a.keys() - b.keys()]
    for k in a.keys() & b.keys():
        p0, p1 = a[k].get("prix_eur"), b[k].get("prix_eur")
        if p0 and p1 and abs(p1 - p0) / p0 >= seuil:
            r.variations.append((a[k], b[k]))
        promo0 = a[k].get("prix_initial_eur") is not None
        promo1 = b[k].get("prix_initial_eur") is not None
        if promo1 and not promo0:
            r.promos_debut.append(b[k])
        elif promo0 and not promo1:
            r.promos_fin.append(b[k])
    for liste in (r.nouveaux, r.retires, r.promos_debut, r.promos_fin):
        liste.sort(key=lambda x: (x.get("site", ""), x.get("titre", "")))
    r.variations.sort(key=lambda v: (v[1].get("site", ""), v[1].get("titre", "")))
    return r


def _eur(x: float) -> str:
    return f"{x:.2f} €".replace(".", ",")


def en_texte(r: Rapport, titre: str = "Prix des concurrents") -> str:
    if r.vide:
        return f"{titre} : rien n'a changé depuis le dernier relevé."
    lignes = [f"{titre} : ce qui a changé depuis le dernier relevé", ""]
    if r.variations:
        lignes.append("Prix modifiés :")
        for v0, v1 in r.variations:
            sens = "hausse" if v1["prix_eur"] > v0["prix_eur"] else "baisse"
            lignes.append(
                f"- {v1['site']} · {v1['titre']} : {_eur(v0['prix_eur'])} -> "
                f"{_eur(v1['prix_eur'])} ({sens})"
            )
        lignes.append("")
    if r.promos_debut:
        lignes.append("Nouvelles promotions :")
        lignes += [
            f"- {x['site']} · {x['titre']} : {_eur(x['prix_eur'])} au lieu de "
            f"{_eur(x['prix_initial_eur'])}"
            for x in r.promos_debut
        ]
        lignes.append("")
    if r.promos_fin:
        lignes.append("Promotions terminées :")
        lignes += [f"- {x['site']} · {x['titre']} : {_eur(x['prix_eur'])}" for x in r.promos_fin]
        lignes.append("")
    if r.nouveaux:
        lignes.append("Nouveaux produits :")
        lignes += [f"- {x['site']} · {x['titre']} : {_eur(x['prix_eur'])}" for x in r.nouveaux]
        lignes.append("")
    if r.retires:
        lignes.append("Produits retirés :")
        lignes += [f"- {x['site']} · {x['titre']}" for x in r.retires]
    return "\n".join(lignes).rstrip()


def releve_precedent(dossier: Path, actuel: Path) -> Path | None:
    """Le relevé le plus récent du dossier, autre que `actuel` (les noms sont datés)."""
    autres = sorted(p for p in dossier.glob("releve-*.jsonl") if p.resolve() != actuel.resolve())
    return autres[-1] if autres else None


def envoyer_telegram(texte: str, jeton: str, chat_id: str) -> None:
    url = f"https://api.telegram.org/bot{jeton}/sendMessage"
    reponse = requests.post(url, data={"chat_id": chat_id, "text": texte[:4000]}, timeout=30)
    reponse.raise_for_status()
