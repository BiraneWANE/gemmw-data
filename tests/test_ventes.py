from pathlib import Path

from gemmw.entrepot import ouvrir
from gemmw.entrepot.controles import controler, tout_passe
from gemmw.entrepot.ventes import charger, hacher_email, lire_etsy, lire_payhip

FIXTURES = Path(__file__).parent / "fixtures" / "ventes"
SEL = "sel-de-test"


def test_hachage_stable_et_insensible_a_la_casse():
    assert hacher_email("Anna@Example.org ", SEL) == hacher_email("anna@example.org", SEL)
    assert hacher_email("anna@example.org", SEL) != hacher_email("anna@example.org", "autre sel")
    assert len(hacher_email("x@y.z", SEL)) == 64


def test_payhip_garde_les_payees_et_hache_les_emails():
    ventes = lire_payhip(FIXTURES / "payhip_export.csv", SEL)
    assert len(ventes) == 3  # la remboursée est écartée
    assert set(ventes["plateforme"]) == {"payhip"}
    assert ventes["prix_ttc_eur"].tolist() == [5.90, 5.90, 5.90]
    assert ventes["frais_eur"].tolist() == [0.57, 0.57, 0.57]
    assert "a.test@example.org" not in ventes.to_string()
    # la même acheteuse revient : même haché, deux commandes distinctes
    assert ventes["acheteuse_hash"].nunique() == 2
    assert ventes["commande_ref"].nunique() == 3
    assert ventes["vendue_le"].tolist() == ["2026-10-02", "2026-10-05", "2026-10-09"]


def test_etsy_ecarte_les_annulees_et_calcule_les_frais():
    ventes = lire_etsy(FIXTURES / "etsy_orders.csv", SEL)
    assert len(ventes) == 2
    assert ventes["commande_ref"].tolist() == ["3412345678", "3412345690"]
    assert ventes["tva_eur"].tolist() == [1.18, 1.24]
    assert ventes["frais_eur"].tolist() == [0.70, 0.71]  # total - net - TVA reversée
    assert ventes["pays"].tolist() == ["France", "Belgium"]
    assert ventes["produit"].tolist() == ["AUTOMNE-PDF", "COULEURS-PDF"]


def test_controles_passent_sur_les_fixtures():
    for ventes in (
        lire_payhip(FIXTURES / "payhip_export.csv", SEL),
        lire_etsy(FIXTURES / "etsy_orders.csv", SEL),
    ):
        resultats = controler(ventes)
        assert tout_passe(resultats), [r for r in resultats if not r.succes]


def test_controles_detectent_un_prix_negatif_et_un_doublon():
    ventes = lire_payhip(FIXTURES / "payhip_export.csv", SEL)
    ventes.loc[0, "prix_ttc_eur"] = -1
    ventes.loc[1, "commande_ref"] = ventes.loc[2, "commande_ref"]
    echecs = {r.attente for r in controler(ventes) if not r.succes}
    # un prix négatif rend aussi les frais supérieurs au prix : trois attentes tombent
    assert echecs == {
        "prix strictement positifs",
        "aucune commande en double",
        "frais inférieurs au prix",
    }


def test_chargement_ignore_les_commandes_deja_connues(tmp_path):
    conn = ouvrir(tmp_path / "t.db")
    ventes = lire_etsy(FIXTURES / "etsy_orders.csv", SEL)
    premier = charger(conn, ventes, "etsy")
    second = charger(conn, ventes, "etsy")
    assert (premier.inserees, premier.ignorees) == (2, 0)
    assert (second.inserees, second.ignorees) == (0, 2)
    assert conn.execute("SELECT COUNT(*) FROM vente").fetchone()[0] == 2
