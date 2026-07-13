"""US-10 : photos d'evolution des cultures."""

# Une mini image PNG 1x1 encodee en base64 (data URL)
IMG = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


def _creer_culture(client, headers, parcelle_id):
    return client.post(f"/parcelles/{parcelle_id}/cultures",
                       json={"nom_plante": "tomate", "date_plantation": "2026-05-12"},
                       headers=headers).json()


def test_ajouter_une_photo_a_sa_culture(client, auth_j1, donnees):
    culture = _creer_culture(client, auth_j1, donnees["p_j1"].id)
    r = client.post(f"/cultures/{culture['id']}/photos",
                    json={"image_base64": IMG, "legende": "Semaine 1"}, headers=auth_j1)
    assert r.status_code == 201
    assert r.json()["legende"] == "Semaine 1"


def test_lister_les_photos_d_une_culture(client, auth_j1, donnees):
    culture = _creer_culture(client, auth_j1, donnees["p_j1"].id)
    client.post(f"/cultures/{culture['id']}/photos", json={"image_base64": IMG},
                headers=auth_j1)
    r = client.get(f"/cultures/{culture['id']}/photos", headers=auth_j1)
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_on_n_ajoute_pas_de_photo_sur_la_culture_d_un_autre(client, auth_j1, auth_j2, donnees):
    culture = _creer_culture(client, auth_j1, donnees["p_j1"].id)
    r = client.post(f"/cultures/{culture['id']}/photos", json={"image_base64": IMG},
                    headers=auth_j2)
    assert r.status_code == 403


def test_supprimer_une_photo(client, auth_j1, donnees):
    culture = _creer_culture(client, auth_j1, donnees["p_j1"].id)
    photo = client.post(f"/cultures/{culture['id']}/photos", json={"image_base64": IMG},
                        headers=auth_j1).json()
    r = client.delete(f"/photos/{photo['id']}", headers=auth_j1)
    assert r.status_code == 204
