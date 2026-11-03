import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PAR_DEFAUT = Path(__file__).resolve().parent.parent / "candidatures.db"


def chemin_db():
    return os.environ.get("DB_PATH", str(DB_PAR_DEFAUT))


@contextmanager
def connexion():
    conn = sqlite3.connect(chemin_db())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with connexion() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS candidatures (
                id INTEGER PRIMARY KEY,
                entreprise TEXT NOT NULL,
                poste TEXT NOT NULL,
                lien TEXT,
                statut TEXT NOT NULL DEFAULT 'À envoyer',
                date_candidature TEXT NOT NULL,
                notes TEXT
            )
            """
        )
