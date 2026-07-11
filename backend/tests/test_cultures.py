"""US-07 : declarer une culture (feature metier coeur) + US-08/09 suggestions."""

from datetime import date


def test_un_jardinier_declare_une_culture_sur_sa_parcelle(client, auth_j1, donnees):
    r = client.post(f"/parcelles/{donnees['p_j1'].id}/cultures",
                    json={"nom_plante": "Tomate", "date_plantation": "2026-05-12"},
                    headers=auth_j1)
    assert r.status_code == 201
    body = r.json()
    assert body["nom_plante"] == "tomate"
    assert body["famille"] == "solanacees"
    # 90 jours apres le 12/05 -> calcul automatique de la date de recolte
    assert body["date_recolte_prevue"] == "2026-08-10"


def test_la_culture_apparait_dans_la_liste_apres_creation(client, auth_j1, donnees):
    client.post(f"/parcelles/{donnees['p_j1'].id}/cultures",
                json={"nom_plante": "radis", "date_plantation": "2026-04-02"}, headers=auth_j1)
    r = client.get(f"/parcelles/{donnees['p_j1'].id}/cultures", headers=auth_j1)
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_un_jardinier_ne_plante_pas_sur_la_parcelle_d_un_autre(client, auth_j2, donnees):
    r = client.post(f"/parcelles/{donnees['p_j1'].id}/cultures",
                    json={"nom_plante": "tomate", "date_plantation": "2026-05-12"},
                    headers=auth_j2)
    assert r.status_code == 403


def test_date_de_plantation_obligatoire(client, auth_j1, donnees):
    r = client.post(f"/parcelles/{donnees['p_j1'].id}/cultures",
                    json={"nom_plante": "tomate"}, headers=auth_j1)
    assert r.status_code == 422


def test_plante_inconnue_acceptee_sans_date_de_recolte(client, auth_j1, donnees):
    r = client.post(f"/parcelles/{donnees['p_j1'].id}/cultures",
                    json={"nom_plante": "plante exotique", "date_plantation": "2026-05-12"},
                    headers=auth_j1)
    assert r.status_code == 201
    assert r.json()["date_recolte_prevue"] is None


def test_marquer_une_culture_comme_recoltee(client, auth_j1, donnees):
    c = client.post(f"/parcelles/{donnees['p_j1'].id}/cultures",
                    json={"nom_plante": "radis", "date_plantation": "2026-04-02"},
                    headers=auth_j1).json()
    r = client.patch(f"/cultures/{c['id']}/recolter", headers=auth_j1)
    assert r.status_code == 200
    assert r.json()["statut"] == "recoltee"


def test_une_plante_hors_saison_n_est_jamais_suggeree(client, auth_j1):
    r = client.get("/suggestions?mois=1", headers=auth_j1)
    assert r.status_code == 200
    noms = [s["nom_plante"] for s in r.json()["suggestions"]]
    assert "tomate" not in noms  # la tomate se seme en avril-juin


def test_les_suggestions_changent_selon_le_mois(client, auth_j1):
    mai = client.get("/suggestions?mois=5", headers=auth_j1).json()["suggestions"]
    janvier = client.get("/suggestions?mois=1", headers=auth_j1).json()["suggestions"]
    assert len(mai) > len(janvier)


def test_rotation_la_famille_deja_cultivee_est_exclue(client, auth_j1, donnees):
    client.post(f"/parcelles/{donnees['p_j1'].id}/cultures",
                json={"nom_plante": "tomate", "date_plantation": str(date.today())},
                headers=auth_j1)
    r = client.get(f"/suggestions?mois=5&parcelle_id={donnees['p_j1'].id}", headers=auth_j1)
    noms = [s["nom_plante"] for s in r.json()["suggestions"]]
    assert "solanacees" in r.json()["familles_evitees"]
    assert "aubergine" not in noms  # meme famille que la tomate
