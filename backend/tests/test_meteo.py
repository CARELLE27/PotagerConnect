"""US-11 / US-12 : meteo et conseils. L'appel a Open-Meteo est mocke (aucun reseau)."""

from unittest.mock import AsyncMock, patch

from app.routers.meteo import generer_conseils


def test_conseil_gel_si_temperature_negative():
    conseils = generer_conseils(temp_max=5, temp_min=-2, pluie_mm=0)
    assert any("Gel" in c for c in conseils)


def test_conseil_arrosage_si_chaud_et_sec():
    conseils = generer_conseils(temp_max=32, temp_min=18, pluie_mm=0)
    assert any("arrosez" in c.lower() for c in conseils)


def test_conseil_pas_d_arrosage_si_pluie():
    conseils = generer_conseils(temp_max=20, temp_min=12, pluie_mm=8)
    assert any("inutile d'arroser" in c.lower() for c in conseils)


def test_conseil_par_defaut_si_conditions_clementes():
    conseils = generer_conseils(temp_max=22, temp_min=14, pluie_mm=2)
    assert len(conseils) >= 1


def test_endpoint_meteo_mocke(client, auth_j1):
    faux_data = {
        "daily": {
            "time": ["2026-07-13", "2026-07-14", "2026-07-15"],
            "temperature_2m_max": [28.0, 30.0, 26.0],
            "temperature_2m_min": [15.0, 17.0, 14.0],
            "precipitation_sum": [0.0, 2.0, 10.0],
            "weather_code": [1, 3, 61],
        }
    }

    reponse_mock = AsyncMock()
    reponse_mock.json = lambda: faux_data
    reponse_mock.raise_for_status = lambda: None

    with patch("app.routers.meteo.httpx.AsyncClient") as MockClient:
        instance = MockClient.return_value.__aenter__.return_value
        instance.get = AsyncMock(return_value=reponse_mock)

        r = client.get("/meteo", headers=auth_j1)

    assert r.status_code == 200
    body = r.json()
    assert body["aujourd_hui"]["temp_max"] == 28.0
    assert len(body["conseils"]) >= 1
    assert len(body["previsions"]) == 3


def test_meteo_exige_authentification(client):
    assert client.get("/meteo").status_code == 401
