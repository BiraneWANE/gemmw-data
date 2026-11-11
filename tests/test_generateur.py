import pymupdf
import pytest

from gemmw.api.generateur import PrenomInvalide, compter_reperes, nettoyer_prenom, personnaliser


def livret_test(texte="Bravo PRENOM, tu as fini !", fond=(1, 0.976, 0.92)) -> bytes:
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.draw_rect(page.rect, color=None, fill=fond)
    page.insert_text((100, 200), texte, fontsize=20, color=(0.3, 0.4, 0.3))
    page2 = doc.new_page(width=595, height=842)
    page2.insert_text((100, 300), "Une page sans repère.", fontsize=14)
    return doc.tobytes()


@pytest.mark.parametrize(
    ("brut", "propre"),
    [("lina", "Lina"), ("  marie-lou ", "Marie-Lou"), ("ÉLOÏSE", "Éloïse"), ("o'neil", "O'Neil")],
)
def test_nettoyer_prenom(brut, propre):
    assert nettoyer_prenom(brut) == propre


@pytest.mark.parametrize("brut", ["", "Lina2", "<script>", "A" * 21])
def test_prenom_refuse(brut):
    with pytest.raises(PrenomInvalide):
        nettoyer_prenom(brut)


def test_le_repere_est_remplace():
    source = livret_test()
    assert compter_reperes(source) == 1
    sortie = personnaliser(source, "lina")
    doc = pymupdf.open(stream=sortie, filetype="pdf")
    texte = doc[0].get_text()
    assert "PRENOM" not in texte
    assert "Lina" in texte
    assert "tu as fini" in texte
    assert doc.page_count == 2


def test_prenom_long_reste_lisible():
    sortie = personnaliser(livret_test(), "Marie-Charlotte")
    assert "Marie-Charlotte" in pymupdf.open(stream=sortie, filetype="pdf")[0].get_text()


def test_livret_sans_repere():
    with pytest.raises(ValueError):
        personnaliser(livret_test("Pas de repère ici"), "Lina")


def _page_avec(*lignes):
    doc = pymupdf.open()
    page = doc.new_page(width=420, height=595)
    page.draw_rect(page.rect, color=None, fill=(1, 0.976, 0.92))
    for x, y, texte in lignes:
        page.insert_text((x, y), texte, fontsize=16, fontname="helv")
    return doc.tobytes()


def test_prenom_dans_une_phrase_sans_trou():
    pdf = personnaliser(_page_avec((60, 300, "Bravo PRENOM, tu as fini !")), "lina")
    with pymupdf.open(stream=pdf, filetype="pdf") as doc:
        texte = " ".join(doc[0].get_text().split())
    assert "Bravo Lina, tu as fini !" in texte
    assert "PRENOM" not in texte


def test_phrase_centree_reste_centree():
    t = "Joyeux automne PRENOM !"
    x = (420 - pymupdf.get_text_length(t, "helv", 16)) / 2
    pdf = personnaliser(_page_avec((x, 300, t)), "Marie-Charlotte")
    with pymupdf.open(stream=pdf, filetype="pdf") as doc:
        (zone,) = doc[0].search_for("Joyeux automne Marie-Charlotte !")
    assert abs((zone.x0 + zone.x1) / 2 - 210) < 3


def test_fond_pris_autour_du_repere_et_pas_sur_le_texte():
    pdf = personnaliser(_page_avec((60, 300, "Bravo PRENOM")), "Lina")
    with pymupdf.open(stream=pdf, filetype="pdf") as doc:
        pix = doc[0].get_pixmap(clip=pymupdf.Rect(150, 302, 200, 306), dpi=72)
    assert all(abs(a - b) <= 2 for a, b in zip(pix.pixel(10, 1)[:3], (255, 249, 235), strict=True))
