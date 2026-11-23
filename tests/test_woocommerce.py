import json

from gemmw.collecte.woocommerce import PAR_PAGE, ecrire, recuperer_commandes


class Reponse:
    def __init__(self, donnees):
        self.donnees = donnees

    def raise_for_status(self):
        pass

    def json(self):
        return self.donnees


def test_recupere_toutes_les_pages():
    appels = []

    def faux_get(url, params, auth, timeout):
        appels.append(params["page"])
        n = PAR_PAGE if params["page"] == 1 else 3
        return Reponse([{"id": params["page"] * 1000 + i} for i in range(n)])

    commandes = recuperer_commandes("https://exemple.test/", "ck", "cs", get=faux_get)
    assert appels == [1, 2]
    assert len(commandes) == PAR_PAGE + 3


def test_ecrit_un_fichier_json_date(tmp_path):
    from datetime import date

    chemin = ecrire([{"id": 1}], tmp_path, date(2026, 11, 23))
    assert chemin.name == "commandes-site-2026-11-23.json"
    assert json.loads(chemin.read_text(encoding="utf-8")) == [{"id": 1}]
