def exemple(**changements):
    donnees = {
        "entreprise": "Exemple SA",
        "poste": "Développeur Python",
        "statut": "Envoyée",
        "date_candidature": "2026-11-01",
    }
    donnees.update(changements)
    return donnees


def test_sante(client):
    reponse = client.get("/sante")
    assert reponse.status_code == 200
    assert reponse.json() == {"statut": "ok"}


def test_creer_puis_lire(client):
    reponse = client.post("/api/candidatures", json=exemple())
    assert reponse.status_code == 201
    cree = reponse.json()

    lu = client.get(f"/api/candidatures/{cree['id']}")
    assert lu.status_code == 200
    assert lu.json()["entreprise"] == "Exemple SA"


def test_statut_invalide_refuse(client):
    reponse = client.post("/api/candidatures", json=exemple(statut="Peut-être"))
    assert reponse.status_code == 422


def test_entreprise_vide_refusee(client):
    reponse = client.post("/api/candidatures", json=exemple(entreprise=""))
    assert reponse.status_code == 422


def test_lien_dangereux_refuse(client):
    reponse = client.post(
        "/api/candidatures", json=exemple(lien="javascript:alert(1)")
    )
    assert reponse.status_code == 422


def test_lien_https_accepte(client):
    reponse = client.post(
        "/api/candidatures", json=exemple(lien="https://exemple.com/offre")
    )
    assert reponse.status_code == 201


def test_modifier(client):
    id_ = client.post("/api/candidatures", json=exemple()).json()["id"]
    reponse = client.put(
        f"/api/candidatures/{id_}", json=exemple(statut="Entretien")
    )
    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "Entretien"


def test_supprimer(client):
    id_ = client.post("/api/candidatures", json=exemple()).json()["id"]
    assert client.delete(f"/api/candidatures/{id_}").status_code == 204
    assert client.get(f"/api/candidatures/{id_}").status_code == 404


def test_candidature_inconnue_renvoie_404(client):
    assert client.get("/api/candidatures/999").status_code == 404
    assert client.put("/api/candidatures/999", json=exemple()).status_code == 404
    assert client.delete("/api/candidatures/999").status_code == 404


def test_filtre_par_statut(client):
    client.post("/api/candidatures", json=exemple(statut="Envoyée"))
    client.post("/api/candidatures", json=exemple(statut="Refus"))
    reponse = client.get("/api/candidatures", params={"statut": "Refus"})
    assert reponse.status_code == 200
    assert len(reponse.json()) == 1
    assert reponse.json()[0]["statut"] == "Refus"


def test_stats(client):
    client.post("/api/candidatures", json=exemple(statut="Envoyée"))
    client.post("/api/candidatures", json=exemple(statut="Envoyée"))
    client.post("/api/candidatures", json=exemple(statut="Refus"))
    stats = client.get("/api/stats").json()
    assert stats["total"] == 3
    assert stats["par_statut"] == {"Envoyée": 2, "Refus": 1}
