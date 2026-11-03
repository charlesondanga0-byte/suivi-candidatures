import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.db import connexion, init_db
from app.models import CandidatureIn, Statut
from app.seed import inserer_demo

BASE = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if os.environ.get("DEMO_MODE") == "1":
        inserer_demo()
    yield


app = FastAPI(title="Suivi de candidatures", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

COLONNES = "entreprise, poste, lien, statut, date_candidature, notes"


def valeurs(c: CandidatureIn):
    d = c.model_dump(mode="json")
    return (
        d["entreprise"], d["poste"], d["lien"],
        d["statut"], d["date_candidature"], d["notes"],
    )


@app.get("/")
def accueil():
    return FileResponse(BASE / "static" / "index.html")


@app.get("/sante")
def sante():
    return {"statut": "ok"}


@app.get("/api/candidatures")
def lister(statut: Optional[Statut] = None):
    requete = "SELECT * FROM candidatures"
    params = []
    if statut:
        requete += " WHERE statut = ?"
        params.append(statut)
    requete += " ORDER BY date_candidature DESC, id DESC"
    with connexion() as conn:
        return [dict(ligne) for ligne in conn.execute(requete, params)]


@app.get("/api/candidatures/{id_}")
def lire(id_: int):
    with connexion() as conn:
        ligne = conn.execute(
            "SELECT * FROM candidatures WHERE id = ?", (id_,)
        ).fetchone()
        if ligne is None:
            raise HTTPException(status_code=404, detail="Candidature introuvable")
        return dict(ligne)


@app.post("/api/candidatures", status_code=201)
def creer(c: CandidatureIn):
    with connexion() as conn:
        curseur = conn.execute(
            f"INSERT INTO candidatures ({COLONNES}) VALUES (?, ?, ?, ?, ?, ?)",
            valeurs(c),
        )
        ligne = conn.execute(
            "SELECT * FROM candidatures WHERE id = ?", (curseur.lastrowid,)
        ).fetchone()
        return dict(ligne)


@app.put("/api/candidatures/{id_}")
def modifier(id_: int, c: CandidatureIn):
    with connexion() as conn:
        curseur = conn.execute(
            "UPDATE candidatures SET entreprise = ?, poste = ?, lien = ?, "
            "statut = ?, date_candidature = ?, notes = ? WHERE id = ?",
            (*valeurs(c), id_),
        )
        if curseur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Candidature introuvable")
        ligne = conn.execute(
            "SELECT * FROM candidatures WHERE id = ?", (id_,)
        ).fetchone()
        return dict(ligne)


@app.delete("/api/candidatures/{id_}", status_code=204)
def supprimer(id_: int):
    with connexion() as conn:
        curseur = conn.execute("DELETE FROM candidatures WHERE id = ?", (id_,))
        if curseur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Candidature introuvable")
    return Response(status_code=204)


@app.get("/api/stats")
def stats():
    with connexion() as conn:
        lignes = conn.execute(
            "SELECT statut, COUNT(*) AS n FROM candidatures GROUP BY statut"
        ).fetchall()
    par_statut = {ligne["statut"]: ligne["n"] for ligne in lignes}
    return {"total": sum(par_statut.values()), "par_statut": par_statut}
