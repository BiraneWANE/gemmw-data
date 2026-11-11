import json

from gemmw.collecte.alerte import comparer, en_texte, releve_precedent
from gemmw.collecte.qualite import controler_releve, lire_releve, tout_passe


def ligne(url, prix, site="A", titre=None, initial=None):
    return {
        "releve_le": "2026-11-09T06:17:00+00:00",
        "site": site,
        "titre": titre or url,
        "prix_eur": prix,
        "url": url,
        "prix_initial_eur": initial,
    }


def test_releve_valide_passe_tous_les_controles():
    lignes = [ligne(f"u{i}", 5.0 + i) for i in range(6)]
    assert tout_passe(controler_releve(lignes, ("A",)))


def test_releve_vide_ou_casse_echoue():
    res = controler_releve([ligne("u1", 0.0), ligne("u1", 6.0)], ("A", "B"))
    echecs = {r.attente for r in res if not r.succes}
    assert "au moins 5 produits" in echecs
    assert "aucun produit en double" in echecs
    assert "chaque site suivi est présent" in echecs
    assert any(e.startswith("prix entre") for e in echecs)


def test_promo_incoherente_detectee():
    lignes = [ligne(f"u{i}", 6.0) for i in range(5)] + [ligne("p", 9.0, initial=8.0)]
    res = {r.attente: r.succes for r in controler_releve(lignes)}
    assert res["prix barré supérieur au prix actuel"] is False


def test_comparer_detecte_changements():
    avant = [ligne("a", 10.0), ligne("b", 5.0), ligne("c", 7.0), ligne("d", 8.0)]
    apres = [ligne("a", 12.0), ligne("b", 5.1), ligne("d", 6.0, initial=8.0), ligne("e", 4.0)]
    r = comparer(avant, apres)
    assert [v[1]["url"] for v in r.variations] == ["a", "d"]  # b : +2 %, sous le seuil
    assert [x["url"] for x in r.nouveaux] == ["e"]
    assert [x["url"] for x in r.retires] == ["c"]
    assert [x["url"] for x in r.promos_debut] == ["d"]
    texte = en_texte(r)
    assert "10,00 € -> 12,00 € (hausse)" in texte
    assert "Nouveaux produits" in texte and "Produits retirés" in texte


def test_rien_na_change():
    r = comparer([ligne("a", 10.0)], [ligne("a", 10.0)])
    assert r.vide
    assert "rien n'a changé" in en_texte(r)


def test_releve_precedent_et_lecture(tmp_path):
    for jour in ("2026-11-02", "2026-11-09"):
        (tmp_path / f"releve-{jour}.jsonl").write_text(
            json.dumps(ligne("a", 10.0)) + "\n", encoding="utf-8"
        )
    actuel = tmp_path / "releve-2026-11-09.jsonl"
    assert releve_precedent(tmp_path, actuel).name == "releve-2026-11-02.jsonl"
    assert lire_releve(actuel)[0]["prix_eur"] == 10.0
