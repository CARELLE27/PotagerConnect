"""US-04 / US-05 / US-06 : carte, attribution, RBAC."""


def test_un_jardinier_ne_peut_pas_lister_toutes_les_parcelles(client, auth_j1):
    assert client.get("/parcelles", headers=auth_j1).status_code == 403


def test_l_admin_voit_toutes_les_parcelles(client, auth_admin):
    r = client.get("/parcelles", headers=auth_admin)
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_mes_parcelles_ne_renvoie_que_les_siennes(client, auth_j1, donnees):
    r = client.get("/parcelles/mes-parcelles", headers=auth_j1)
    assert r.status_code == 200
    assert [p["numero"] for p in r.json()] == ["A-01"]


def test_un_jardinier_sans_parcelle_recoit_une_liste_vide(client, auth_j2):
    r = client.get("/parcelles/mes-parcelles", headers=auth_j2)
    assert r.json() == []


def test_un_jardinier_ne_peut_pas_attribuer_une_parcelle(client, auth_j1, donnees):
    r = client.patch(f"/parcelles/{donnees['p_libre'].id}/attribuer",
                     json={"user_id": donnees["j1"].id}, headers=auth_j1)
    assert r.status_code == 403


def test_l_admin_attribue_une_parcelle_libre(client, auth_admin, donnees):
    r = client.patch(f"/parcelles/{donnees['p_libre'].id}/attribuer",
                     json={"user_id": donnees["j2"].id}, headers=auth_admin)
    assert r.status_code == 200
    assert r.json()["statut"] == "attribuee"
    assert r.json()["jardinier_nom"] == "Lea P"


def test_attribuer_une_parcelle_deja_attribuee_renvoie_409(client, auth_admin, donnees):
    r = client.patch(f"/parcelles/{donnees['p_j1'].id}/attribuer",
                     json={"user_id": donnees["j2"].id}, headers=auth_admin)
    assert r.status_code == 409


def test_un_jardinier_ne_consulte_pas_la_parcelle_d_un_autre(client, auth_j2, donnees):
    r = client.get(f"/parcelles/{donnees['p_j1'].id}", headers=auth_j2)
    assert r.status_code == 403
