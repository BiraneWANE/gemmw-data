from pathlib import Path

from gemmw.entrepot import ouvrir
from gemmw.entrepot.ventes import charger, lire_etsy
from gemmw.tableau_de_bord.donnees import (
    dernier_releve,
    lire_releves,
    lire_ventes,
    resume_ventes,
)

RACINE = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"


def test_releves_exemple_se_lisent():
    releves = lire_releves([RACINE / "data" / "exemples"])
    assert len(releves) == 99
    assert releves["site"].nunique() == 2
    assert releves["en_promo"].sum() == 21
    assert len(dernier_releve(releves)) == 99


def test_dossier_vide_donne_tableau_vide(tmp_path):
    releves = lire_releves([tmp_path])
    assert releves.empty
    assert dernier_releve(releves).empty


def test_resume_ventes(tmp_path):
    db = tmp_path / "t.db"
    charger(ouvrir(db), lire_etsy(FIXTURES / "ventes" / "etsy_orders.csv", "sel"), "etsy")
    ventes = lire_ventes(db)
    r = resume_ventes(ventes)
    assert r["commandes"] == 2
    assert r["ca_ttc"] == 14.22
    assert r["net"] == 10.39  # 5.20 + 5.19, ce que la vendeuse touche vraiment
    assert r["clientes"] == 2
    assert r["retour"] == 0


def test_sans_base_resume_a_zero(tmp_path):
    assert resume_ventes(lire_ventes(tmp_path / "absente.db"))["commandes"] == 0
