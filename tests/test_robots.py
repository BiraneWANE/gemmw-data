from gemmw.collecte import Robots


def test_robots_illisible_vaut_autorisation(monkeypatch):
    """Un robots.txt qui ne répond pas ne bloque pas la collecte (délai et User-Agent restent)."""
    import urllib.robotparser as rp

    def read_qui_echoue(self):
        raise OSError("réseau coupé")

    monkeypatch.setattr(rp.RobotFileParser, "read", read_qui_echoue)
    assert Robots().autorise("https://exemple.fr/categorie-produit/x/") is True
