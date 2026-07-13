"""US-15 / US-16 / US-17 : forum d'entraide et troc."""


def test_creer_un_post_entraide(client, auth_j1):
    r = client.post("/forum", json={
        "titre": "Mes tomates jaunissent", "contenu": "Que faire ?", "type": "entraide"},
        headers=auth_j1)
    assert r.status_code == 201
    assert r.json()["type"] == "entraide"
    assert r.json()["nb_commentaires"] == 0


def test_creer_un_post_troc(client, auth_j1):
    r = client.post("/forum", json={
        "titre": "Echange graines de courgettes", "contenu": "Contre des tomates",
        "type": "troc"}, headers=auth_j1)
    assert r.status_code == 201
    assert r.json()["type"] == "troc"


def test_liste_des_posts(client, auth_j1):
    client.post("/forum", json={"titre": "A", "contenu": "aaa", "type": "entraide"},
                headers=auth_j1)
    client.post("/forum", json={"titre": "B", "contenu": "bbb", "type": "troc"},
                headers=auth_j1)
    r = client.get("/forum", headers=auth_j1)
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_filtrer_les_posts_par_type(client, auth_j1):
    client.post("/forum", json={"titre": "A", "contenu": "aaa", "type": "entraide"},
                headers=auth_j1)
    client.post("/forum", json={"titre": "B", "contenu": "bbb", "type": "troc"},
                headers=auth_j1)
    r = client.get("/forum?type=troc", headers=auth_j1)
    assert all(p["type"] == "troc" for p in r.json())


def test_commenter_un_post(client, auth_j1, auth_j2):
    post = client.post("/forum", json={"titre": "Aide", "contenu": "?", "type": "entraide"},
                       headers=auth_j1).json()
    r = client.post(f"/forum/{post['id']}/commentaires",
                    json={"contenu": "Essaie d'arroser moins"}, headers=auth_j2)
    assert r.status_code == 201
    assert r.json()["contenu"] == "Essaie d'arroser moins"


def test_le_detail_montre_les_commentaires(client, auth_j1, auth_j2):
    post = client.post("/forum", json={"titre": "Aide", "contenu": "?", "type": "entraide"},
                       headers=auth_j1).json()
    client.post(f"/forum/{post['id']}/commentaires", json={"contenu": "Conseil 1"},
                headers=auth_j2)
    r = client.get(f"/forum/{post['id']}", headers=auth_j1)
    assert r.status_code == 200
    assert len(r.json()["commentaires"]) == 1


def test_l_auteur_supprime_son_post(client, auth_j1):
    post = client.post("/forum", json={"titre": "X", "contenu": "y", "type": "entraide"},
                       headers=auth_j1).json()
    r = client.delete(f"/forum/{post['id']}", headers=auth_j1)
    assert r.status_code == 204


def test_on_ne_supprime_pas_le_post_d_un_autre(client, auth_j1, auth_j2):
    post = client.post("/forum", json={"titre": "X", "contenu": "y", "type": "entraide"},
                       headers=auth_j1).json()
    r = client.delete(f"/forum/{post['id']}", headers=auth_j2)
    assert r.status_code == 403
