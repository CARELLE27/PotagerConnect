"""US-13 / US-14 : proposer et reserver une recolte partagee."""


def test_un_jardinier_propose_une_recolte(client, auth_j1):
    r = client.post("/recoltes", json={"nom_produit": "Tomates", "quantite": "2 kg"},
                    headers=auth_j1)
    assert r.status_code == 201
    assert r.json()["statut"] == "disponible"
    assert r.json()["nom_produit"] == "Tomates"


def test_la_recolte_apparait_dans_la_liste(client, auth_j1):
    client.post("/recoltes", json={"nom_produit": "Courgettes", "quantite": "1 kg"},
                headers=auth_j1)
    r = client.get("/recoltes", headers=auth_j1)
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_filtrer_par_statut_disponible(client, auth_j1):
    client.post("/recoltes", json={"nom_produit": "Radis", "quantite": "1 botte"},
                headers=auth_j1)
    r = client.get("/recoltes?statut=disponible", headers=auth_j1)
    assert all(x["statut"] == "disponible" for x in r.json())


def test_un_autre_jardinier_reserve_une_recolte(client, auth_j1, auth_j2):
    rec = client.post("/recoltes", json={"nom_produit": "Salades", "quantite": "3"},
                      headers=auth_j1).json()
    r = client.patch(f"/recoltes/{rec['id']}/reserver", headers=auth_j2)
    assert r.status_code == 200
    assert r.json()["statut"] == "reservee"


def test_on_ne_reserve_pas_sa_propre_recolte(client, auth_j1):
    rec = client.post("/recoltes", json={"nom_produit": "Fraises", "quantite": "500 g"},
                      headers=auth_j1).json()
    r = client.patch(f"/recoltes/{rec['id']}/reserver", headers=auth_j1)
    assert r.status_code == 400


def test_une_recolte_reservee_ne_peut_pas_etre_reservee_a_nouveau(client, auth_j1, auth_j2):
    rec = client.post("/recoltes", json={"nom_produit": "Pommes", "quantite": "2 kg"},
                      headers=auth_j1).json()
    client.patch(f"/recoltes/{rec['id']}/reserver", headers=auth_j2)
    r = client.patch(f"/recoltes/{rec['id']}/reserver", headers=auth_j2)
    assert r.status_code == 409


def test_le_proposeur_retire_sa_recolte_non_reservee(client, auth_j1):
    rec = client.post("/recoltes", json={"nom_produit": "Poireaux", "quantite": "4"},
                      headers=auth_j1).json()
    r = client.delete(f"/recoltes/{rec['id']}", headers=auth_j1)
    assert r.status_code == 204


def test_on_ne_retire_pas_la_recolte_d_un_autre(client, auth_j1, auth_j2):
    rec = client.post("/recoltes", json={"nom_produit": "Carottes", "quantite": "1 kg"},
                      headers=auth_j1).json()
    r = client.delete(f"/recoltes/{rec['id']}", headers=auth_j2)
    assert r.status_code == 403
