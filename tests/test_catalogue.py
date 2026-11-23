from pathlib import Path

import pytest

from gemmw.catalogue import CatalogueInvalide, Index, Produit, charger, verifier
from gemmw.entrepot import ouvrir
from gemmw.entrepot.controles import controler, tout_passe
from gemmw.entrepot.ventes import charger as charger_ventes
from gemmw.entrepot.ventes import lire_site, rattacher_au_catalogue

FIXTURES = Path(__file__).parent / "fixtures" / "ventes"
SEL = "sel-de-test"


def test_le_catalogue_versionne_est_coherent():
    produits = charger()
    skus = {p.sku for p in produits}
    assert "GEMMW-INVARIABLES-01" in skus
    assert len(skus) == len(produits)
    # chaque livret payant existe au moins en PDF
    livrets_pdf = {p.livret for p in produits if p.format == "pdf"}
    assert {p.livret for p in produits} <= livrets_pdf


def test_verifier_signale_doublons_et_formats():
    a = Produit("GEMMW-A-01", "A", "pdf", 5.9, "2 ans", payhip="X")
    b = Produit("GEMMW-A-01", "B", "poster", -1, "2 ans", payhip="X")
    erreurs = verifier([a, b])
    assert any("sku en double" in e for e in erreurs)
    assert any("payhip en double" in e for e in erreurs)
    assert any("format inconnu" in e for e in erreurs)
    assert any("prix négatif" in e for e in erreurs)


def test_catalogue_invalide_leve_une_erreur(tmp_path):
    fichier = tmp_path / "produits.toml"
    fichier.write_text(
        '[[produit]]\nsku = "MAUVAIS"\nlivret = "x"\nformat = "pdf"\nprix_eur = 1.0\nage = ""\n',
        encoding="utf-8",
    )
    with pytest.raises(CatalogueInvalide):
        charger(fichier)


@pytest.mark.parametrize(
    ("plateforme", "produit", "attendu"),
    [
        ("site", "GEMMW-AVENT-PAP", "GEMMW-AVENT-PAP"),
        ("site", "GEMMW-AUTOMNE-01+GEMMW-COULEURS-01", None),  # panier de deux livrets
        ("payhip", "nsAqU", "GEMMW-INVARIABLES-01"),
        (
            "payhip",
            "Mes premières couleurs avec Talo, dès 2 ans (PDF à imprimer)",
            "GEMMW-COULEURS-01",
        ),
        (
            "payhip",
            "mes premieres couleurs avec talo,  des 2 ans (pdf a imprimer)",
            "GEMMW-COULEURS-01",
        ),
        ("etsy", "4610140244", "GEMMW-COMPTE-01"),
        ("etsy", "Mon calendrier de l’Avent avec Talo : 24 activités, gommettes", "GEMMW-AVENT-01"),
        ("etsy", "Un livret inconnu", None),
        ("amazon", "GEMMW-AVENT-01", None),
    ],
)
def test_index_retrouve_la_reference(plateforme, produit, attendu):
    assert Index(charger()).sku(plateforme, produit) == attendu


def test_site_garde_les_commandes_payees_et_hache_les_emails():
    ventes = lire_site(FIXTURES / "site_commandes.json", SEL)
    assert ventes["commande_ref"].tolist() == ["2001", "2002", "2005"]  # ni 0 €, ni remboursée
    assert ventes["prix_ttc_eur"].tolist() == [5.90, 36.80, 11.80]
    assert ventes["vendue_le"].tolist() == ["2026-11-20", "2026-11-21", "2026-11-22"]
    assert ventes["acheteuse_hash"].iloc[0] == ventes["acheteuse_hash"].iloc[1]  # même cliente
    assert "example.org" not in ventes.to_string()
    assert tout_passe(controler(ventes))


def test_import_site_puis_rattachement(tmp_path):
    conn = ouvrir(tmp_path / "test.db")
    ventes = lire_site(FIXTURES / "site_commandes.json", SEL)
    charger_ventes(conn, ventes, "site")
    assert rattacher_au_catalogue(conn, charger()) == 2
    lignes = dict(conn.execute("SELECT commande_ref, sku FROM vente").fetchall())
    assert lignes == {"2001": "GEMMW-INVARIABLES-01", "2002": "GEMMW-AVENT-PAP", "2005": None}
    assert conn.execute("SELECT COUNT(*) FROM produit").fetchone()[0] == len(charger())
    # relancer ne change rien
    assert rattacher_au_catalogue(conn, charger()) == 0


def test_ancienne_base_sans_colonne_sku_est_migree(tmp_path):
    import sqlite3

    chemin = tmp_path / "ancienne.db"
    ancienne = sqlite3.connect(chemin)
    ancienne.execute(
        "CREATE TABLE vente (id INTEGER PRIMARY KEY, plateforme TEXT, commande_ref TEXT,"
        " vendue_le TEXT, produit TEXT, prix_ttc_eur REAL, frais_eur REAL, tva_eur REAL,"
        " acheteuse_hash TEXT, pays TEXT)"
    )
    ancienne.commit()
    ancienne.close()
    conn = ouvrir(chemin)
    colonnes = {c[1] for c in conn.execute("PRAGMA table_info(vente)")}
    assert "sku" in colonnes
