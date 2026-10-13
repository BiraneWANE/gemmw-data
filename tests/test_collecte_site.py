from gemmw.collecte import Robots, collecter_site
from gemmw.collecte.sites import Produit, Site


def test_un_produit_dans_deux_categories_est_releve_une_fois(monkeypatch):
    import gemmw.collecte as c

    pages = {
        "https://x.fr/cat-a/": "A",
        "https://x.fr/cat-b/": "B",
    }
    monkeypatch.setattr(c, "telecharger", lambda url: pages[url])
    monkeypatch.setattr(c.settings, "delai_entre_requetes_s", 0)
    monkeypatch.setattr(Robots, "autorise", lambda self, url: True)

    commun = Produit(titre="Pack", prix_eur=49.9, url="https://x.fr/produit/pack/")
    seul = Produit(titre="Livret", prix_eur=6.5, url="https://x.fr/produit/livret/")
    site = Site(
        nom="x",
        urls=tuple(pages),
        extraire=lambda html: [commun, seul] if html == "A" else [commun],
    )
    releve = collecter_site(site, Robots())
    assert [p.url for _, p in releve] == [commun.url, seul.url]
