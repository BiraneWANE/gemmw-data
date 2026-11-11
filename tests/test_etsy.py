from gemmw.collecte.etsy import annonce_vers_produit, collecter_etsy, rechercher


class FausseReponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


def annonce(i, devise="EUR", montant=590):
    return {
        "listing_id": i,
        "title": f"Livret {i}",
        "url": f"https://www.etsy.com/listing/{i}/livret?ref=x",
        "price": {"amount": montant, "divisor": 100, "currency_code": devise},
    }


def test_conversion_annonce():
    p = annonce_vers_produit(annonce(1))
    assert p.prix_eur == 5.90
    assert p.url == "https://www.etsy.com/listing/1/livret"
    assert annonce_vers_produit(annonce(2, devise="USD")) is None


def test_recherche_avec_requete_simulee():
    appels = []

    def faux_get(url, headers, params, timeout):
        appels.append((headers["x-api-key"], params["keywords"]))
        return FausseReponse({"count": 2, "results": [annonce(1), annonce(2, devise="USD")]})

    produits = rechercher("imagier", "cle-test", get=faux_get, pause_s=0)
    assert [p.titre for p in produits] == ["Livret 1"]
    assert appels == [("cle-test", "imagier")]


def test_sans_cle_la_collecte_est_sautee():
    assert collecter_etsy("", ("imagier",)) == []
