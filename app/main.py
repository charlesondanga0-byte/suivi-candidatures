from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE = Path(__file__).resolve().parent.parent

app = FastAPI(title="Suivi de candidatures")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


@app.get("/")
def accueil():
    return FileResponse(BASE / "static" / "index.html")


@app.get("/sante")
def sante():
    return {"statut": "ok"}
