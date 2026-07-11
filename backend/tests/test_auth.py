"""US-01 / US-02 / US-03 : inscription, connexion, RBAC."""

from app.models import User


def test_le_mot_de_passe_n_est_jamais_stocke_en_clair(client, db):
    r = client.post("/auth/register", json={
        "email": "nouveau@t.fr", "password": "MotDePasse1!", "nom": "N", "prenom": "P"})
    assert r.status_code == 201

    user = db.query(User).filter(User.email == "nouveau@t.fr").first()
    assert user.password_hash != "MotDePasse1!"
    assert user.password_hash.startswith("$2")  # bcrypt


def test_email_deja_utilise_est_refuse(client, donnees):
    r = client.post("/auth/register", json={
        "email": "j1@t.fr", "password": "MotDePasse1!", "nom": "X", "prenom": "Y"})
    assert r.status_code == 409


def test_mot_de_passe_trop_court_est_refuse(client):
    r = client.post("/auth/register", json={
        "email": "court@t.fr", "password": "abc", "nom": "X", "prenom": "Y"})
    assert r.status_code == 422


def test_mauvais_mot_de_passe_renvoie_401(client, donnees):
    r = client.post("/auth/login", json={"email": "j1@t.fr", "password": "faux"})
    assert r.status_code == 401


def test_login_renvoie_access_et_refresh_token(client, donnees):
    r = client.post("/auth/login", json={"email": "j1@t.fr", "password": "Jardin2026!"})
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert "refresh_token" in r.json()


def test_route_protegee_sans_token_renvoie_401(client):
    assert client.get("/auth/me").status_code == 401


def test_un_refresh_token_ne_sert_pas_d_access_token(client, donnees):
    r = client.post("/auth/login", json={"email": "j1@t.fr", "password": "Jardin2026!"})
    refresh = r.json()["refresh_token"]
    r2 = client.get("/auth/me", headers={"Authorization": f"Bearer {refresh}"})
    assert r2.status_code == 401


def test_refresh_renouvelle_l_access_token(client, donnees):
    r = client.post("/auth/login", json={"email": "j1@t.fr", "password": "Jardin2026!"})
    r2 = client.post("/auth/refresh", json={"refresh_token": r.json()["refresh_token"]})
    assert r2.status_code == 200
    assert "access_token" in r2.json()
