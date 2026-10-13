from pathlib import Path

from gemmw.collecte.sites import extraire_woocommerce

FIXTURES = Path(__file__).parent / "fixtures"


def test_extraction_woocommerce_liste():
    html = (FIXTURES / "woocommerce_liste.html").read_text(encoding="utf-8")
    produits = extraire_woocommerce(html)
    assert [p.titre for p in produits] == ["Imagier de l'automne", "Mes couleurs"]
    assert [p.prix_eur for p in produits] == [6.90, 4.50]
    assert all(p.url.startswith("https://") for p in produits)


def test_page_vide_ne_plante_pas():
    assert extraire_woocommerce("<html></html>") == []
