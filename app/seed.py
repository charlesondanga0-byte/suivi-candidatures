from app.db import connexion, init_db

DEMO = [
    ("Exemple SA", "Développeur Python junior", "Envoyée", "2026-10-28"),
    ("Réseaux Corp", "Technicien réseau", "Entretien", "2026-10-22"),
    ("Cloud Démo", "Support technique N2", "À envoyer", "2026-11-03"),
    ("Sécurité Test", "Analyste SOC junior", "Envoyée", "2026-10-30"),
    ("Données Fictives", "Assistant administrateur système", "Refus", "2026-10-15"),
]

if __name__ == "__main__":
    init_db()
    with connexion() as conn:
        conn.executemany(
            "INSERT INTO candidatures (entreprise, poste, statut, date_candidature) "
            "VALUES (?, ?, ?, ?)",
            DEMO,
        )
    print(f"{len(DEMO)} candidatures de démonstration ajoutées")
