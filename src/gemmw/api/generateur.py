"""Générateur au prénom : remplace le repère PRENOM d'un livret PDF par le prénom de l'enfant.

Dans le livret, Sabrina écrit le mot PRENOM (en capitales, sans accent) partout où le prénom
doit apparaître. Pour chaque repère trouvé, on efface le mot en le recouvrant de la couleur du
fond, puis on écrit le prénom sur la même ligne de base, avec la même taille et la même couleur.
Un prénom trop long pour la place disponible est écrit un peu plus petit.
"""

from __future__ import annotations

import os
import re
import unicodedata
from collections import Counter

import pymupdf

REPERE = "PRENOM"
LONGUEUR_MAX = 20
_AUTORISE = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$")


class PrenomInvalide(ValueError):  # noqa: N818
    pass


def nettoyer_prenom(brut: str) -> str:
    """« marie-lou » -> « Marie-Lou ». Refuse les chiffres, symboles et prénoms trop longs."""
    p = unicodedata.normalize("NFC", " ".join(brut.split()))
    if not p:
        raise PrenomInvalide("Le prénom est vide.")
    if len(p) > LONGUEUR_MAX:
        raise PrenomInvalide(f"Le prénom dépasse {LONGUEUR_MAX} caractères.")
    if not _AUTORISE.match(p):
        raise PrenomInvalide(
            "Le prénom ne doit contenir que des lettres, espaces, tirets ou apostrophes."
        )
    return re.sub(r"(^|[ \-'])(\w)", lambda m: m.group(1) + m.group(2).upper(), p.lower())


def _couleur_fond(page: pymupdf.Page, zone: pymupdf.Rect) -> tuple[float, float, float]:
    """La couleur la plus fréquente autour du repère : c'est le fond, pas les lettres."""
    autour = pymupdf.Rect(zone.x0 - 4, zone.y0 - 3, zone.x1 + 4, zone.y1 + 3) & page.rect
    pix = page.get_pixmap(clip=autour, dpi=72, alpha=False)
    n = pix.n
    data = pix.samples
    compte = Counter(tuple(data[i : i + 3]) for i in range(0, len(data) - n + 1, n))
    r, g, b = compte.most_common(1)[0][0]
    return (r / 255, g / 255, b / 255)


def _span_de(page_spans: list[dict], zone: pymupdf.Rect) -> dict:
    """Le morceau de texte qui contient ce repère (taille, couleur, ligne de base, voisins)."""
    for span in page_spans:
        if REPERE in span["text"] and pymupdf.Rect(span["bbox"]).intersects(zone):
            return span
    return {"size": 12, "color": 0, "text": REPERE, "origin": (zone.x0, zone.y1 - 2)}


def _spans(page: pymupdf.Page) -> list[dict]:
    return [
        span
        for bloc in page.get_text("dict")["blocks"]
        for ligne in bloc.get("lines", [])
        for span in ligne["spans"]
    ]


def _police() -> pymupdf.Font:
    """Helvetica par défaut, ou la police du livret si GEMMW_POLICE pointe vers un .ttf/.otf."""
    fichier = os.environ.get("GEMMW_POLICE")
    if fichier and os.path.isfile(fichier):
        return pymupdf.Font(fontfile=fichier)
    return pymupdf.Font("helv")


def compter_reperes(pdf: bytes) -> int:
    with pymupdf.open(stream=pdf, filetype="pdf") as doc:
        return sum(len(p.search_for(REPERE)) for p in doc)


def personnaliser(pdf: bytes, prenom: str) -> bytes:
    """Renvoie le PDF avec chaque repère PRENOM remplacé. Lève une erreur s'il n'y en a aucun.

    Repère seul dans sa zone de texte : le prénom est centré à sa place.
    Repère dans une phrase : la phrase est réécrite avec le prénom dedans, au même endroit
    (centrée si elle l'était sur la page), pour ne laisser ni trou ni chevauchement.
    """
    prenom = nettoyer_prenom(prenom)
    police = _police()
    doc = pymupdf.open(stream=pdf, filetype="pdf")
    total = 0
    for page in doc:
        zones = page.search_for(REPERE)
        if not zones:
            continue
        spans = _spans(page)
        a_ecrire = []
        deja = set()
        for zone in zones:
            span = _span_de(spans, zone)
            avant, _, apres = span["text"].partition(REPERE)
            couleur = span["color"]
            rgb = tuple(((couleur >> d) & 255) / 255 for d in (16, 8, 0))
            seul = not avant.strip() and not apres.strip()
            cadre = zone if seul or "bbox" not in span else pymupdf.Rect(span["bbox"])
            if id(span) in deja:
                continue
            deja.add(id(span))
            page.add_redact_annot(cadre, fill=_couleur_fond(page, cadre))
            texte = prenom if seul else span["text"].replace(REPERE, prenom)
            a_ecrire.append((cadre, float(span["size"]), rgb, span["origin"][1], texte, seul))
            total += span["text"].count(REPERE)
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)
        milieu_page = (page.rect.x0 + page.rect.x1) / 2
        for cadre, taille, couleur, base, texte, seul in a_ecrire:
            centre = (cadre.x0 + cadre.x1) / 2
            centree = seul or abs(centre - milieu_page) < 6
            if seul:
                largeur_dispo = max(cadre.width * 2.2, cadre.width + 40)
            elif centree:
                largeur_dispo = page.rect.width - 40
            else:
                largeur_dispo = page.rect.x1 - cadre.x0 - 20
            while police.text_length(texte, fontsize=taille) > largeur_dispo and taille > 6:
                taille -= 0.5
            largeur = police.text_length(texte, fontsize=taille)
            x = centre - largeur / 2 if centree else cadre.x0
            ecrit = pymupdf.TextWriter(page.rect, color=couleur)
            ecrit.append((x, base), texte, font=police, fontsize=taille)
            ecrit.write_text(page)
    if total == 0:
        doc.close()
        raise ValueError(f"Aucun repère {REPERE} dans ce livret.")
    sortie = doc.tobytes(garbage=3, deflate=True)
    doc.close()
    return sortie
