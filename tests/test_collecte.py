from pathlib import Path

from gemmw.collecte.sites import extraire_woocommerce, pages_woocommerce

FIXTURES = Path(__file__).parent / "fixtures"


def test_extraction_woocommerce_classique():
    html = (FIXTURES / "woocommerce_liste.html").read_text(encoding="utf-8")
    produits = extraire_woocommerce(html)
    assert [p.titre for p in produits] == ["Imagier de l'automne", "Mes couleurs"]
    assert [p.prix_eur for p in produits] == [6.90, 4.50]
    assert all(p.prix_initial_eur is None for p in produits)


def test_extraction_theme_flatsome_page_reelle():
    """Page figée de mespetitslivrets.fr (catégorie 18 mois - 3 ans), relevée le 13 octobre 2026."""
    html = (FIXTURES / "mespetitslivrets_categorie.html").read_text(encoding="utf-8")
    produits = extraire_woocommerce(html)
    assert len(produits) == 12
    assert all(p.url.startswith("https://mespetitslivrets.fr/produit/") for p in produits)
    assert all(p.prix_eur > 0 for p in produits)
    promo = next(p for p in produits if p.titre.startswith("Défi Été"))
    assert promo.prix_eur == 13.90
    assert promo.prix_initial_eur == 17.90
    plein_tarif = next(p for p in produits if "Partie 1" in p.titre)
    assert plein_tarif.prix_eur == 12.90
    assert plein_tarif.prix_initial_eur is None


def test_extraction_grille_maison_page_reelle():
    """Page figée de clesskidscreations.fr (livrets d'activités), relevée le 13 octobre 2026."""
    html = (FIXTURES / "clesskids_categorie.html").read_text(encoding="utf-8")
    produits = extraire_woocommerce(html)
    assert len(produits) == 20
    assert all(p.url.startswith("https://clesskidscreations.fr/produit/") for p in produits)
    fourchette = next(p for p in produits if p.titre == "Les chiffres")
    assert fourchette.prix_eur == 13.00  # « 13,00 € – 15,00 € » : on garde le plus bas
    assert fourchette.prix_initial_eur is None
    promo = next(p for p in produits if p.titre == "Les émotions")
    assert promo.prix_eur == 7.20
    assert promo.prix_initial_eur == 16.00


def test_pagination_detectee():
    html = (FIXTURES / "mespetitslivrets_categorie.html").read_text(encoding="utf-8")
    url = "https://mespetitslivrets.fr/categorie-produit/livrets-dactivites/livrets-18-mois-3-ans/"
    pages = pages_woocommerce(html, url)
    assert pages == [url + "page/2/", url + "page/3/"]


def test_pagination_ignore_le_retour_a_la_page_1():
    url = "https://x.fr/categorie-produit/livrets/page/2/"
    html = (
        '<a class="page-numbers" href="/categorie-produit/livrets/page/1/">1</a>'
        '<a class="page-numbers" href="/categorie-produit/livrets/page/3/">3</a>'
    )
    assert pages_woocommerce(html, url) == ["https://x.fr/categorie-produit/livrets/page/3/"]


def test_page_vide_ne_plante_pas():
    assert extraire_woocommerce("<html></html>") == []
    assert pages_woocommerce("<html></html>", "https://x.fr/") == []
