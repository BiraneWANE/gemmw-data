"""L'interface du générateur : la boutique envoie un prénom, reçoit le livret personnalisé.

    GET  /sante                              -> {"ok": true}
    GET  /livrets                            -> les références disponibles et leur nombre de repères
    POST /livrets/{reference}/personnaliser  -> le PDF, corps JSON {"prenom": "Lina"}

Les livrets sources sont des PDF rangés dans GEMMW_LIVRETS_DIR (un fichier par référence,
ex. automne.pdf). Les appels doivent porter l'en-tête X-Gemmw-Cle, égal à GEMMW_API_CLE :
seule la boutique connaît cette clé. Aucun prénom n'est enregistré.
"""

from __future__ import annotations

import os
import re
import secrets
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from gemmw.api.generateur import PrenomInvalide, compter_reperes, personnaliser

app = FastAPI(title="Générateur de livrets au prénom", version="0.1.0")
_REF = re.compile(r"^[a-z0-9-]{1,40}$")


def _dossier() -> Path:
    return Path(os.environ.get("GEMMW_LIVRETS_DIR", "data/livrets"))


def verifier_cle(x_gemmw_cle: str = Header(default="")) -> None:
    attendue = os.environ.get("GEMMW_API_CLE", "")
    if not attendue or not secrets.compare_digest(x_gemmw_cle, attendue):
        raise HTTPException(status_code=401, detail="Clé absente ou incorrecte.")


class Demande(BaseModel):
    prenom: str


@app.get("/sante")
def sante() -> dict:
    return {"ok": True}


@app.get("/livrets", dependencies=[Depends(verifier_cle)])
def livrets() -> dict:
    return {
        p.stem: {"reperes": compter_reperes(p.read_bytes())}
        for p in sorted(_dossier().glob("*.pdf"))
    }


@app.post("/livrets/{reference}/personnaliser", dependencies=[Depends(verifier_cle)])
def generer(reference: str, demande: Demande) -> Response:
    if not _REF.match(reference):
        raise HTTPException(status_code=400, detail="Référence invalide.")
    chemin = _dossier() / f"{reference}.pdf"
    if not chemin.exists():
        raise HTTPException(status_code=404, detail="Livret inconnu.")
    try:
        pdf = personnaliser(chemin.read_bytes(), demande.prenom)
    except PrenomInvalide as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{reference}-personnalise.pdf"'},
    )
