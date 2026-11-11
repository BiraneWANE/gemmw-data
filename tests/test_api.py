import pymupdf
import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from gemmw.api.app import app  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    doc = pymupdf.open()
    doc.new_page().insert_text((72, 100), "Coucou PRENOM !", fontsize=18)
    (tmp_path / "automne.pdf").write_bytes(doc.tobytes())
    monkeypatch.setenv("GEMMW_LIVRETS_DIR", str(tmp_path))
    monkeypatch.setenv("GEMMW_API_CLE", "cle-de-test")
    return TestClient(app)


def test_sante(client):
    assert client.get("/sante").json() == {"ok": True}


def test_cle_obligatoire(client):
    r = client.post("/livrets/automne/personnaliser", json={"prenom": "Lina"})
    assert r.status_code == 401


def test_generation(client):
    h = {"X-Gemmw-Cle": "cle-de-test"}
    assert client.get("/livrets", headers=h).json() == {"automne": {"reperes": 1}}
    r = client.post("/livrets/automne/personnaliser", json={"prenom": "lina"}, headers=h)
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert "Lina" in pymupdf.open(stream=r.content, filetype="pdf")[0].get_text()


def test_erreurs(client):
    h = {"X-Gemmw-Cle": "cle-de-test"}
    assert (
        client.post(
            "/livrets/inconnu/personnaliser", json={"prenom": "Lina"}, headers=h
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/livrets/automne/personnaliser", json={"prenom": "L1na"}, headers=h
        ).status_code
        == 422
    )
    assert client.post(
        "/livrets/../personnaliser", json={"prenom": "Lina"}, headers=h
    ).status_code in (400, 404)
