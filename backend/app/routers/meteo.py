"""Meteo locale + conseils de jardinage automatises - US-11 / US-12 (SHOULD).

Utilise Open-Meteo : API REST gratuite, sans cle d'authentification.
Les conseils sont generes cote serveur selon les conditions du jour.
"""

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.deps import get_current_user
from app.models import User

router = APIRouter(prefix="/meteo", tags=["meteo"])

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def generer_conseils(temp_max: float, temp_min: float, pluie_mm: float) -> list[str]:
    """Regles simples de jardinage selon la meteo du jour."""
    conseils: list[str] = []

    if temp_min <= 0:
        conseils.append("Gel prevu : protegez vos plants sensibles (voile d'hivernage).")
    if temp_max >= 30 and pluie_mm < 1:
        conseils.append("Forte chaleur et temps sec : arrosez tot le matin ou en soiree.")
    if pluie_mm >= 5:
        conseils.append("Pluie prevue : inutile d'arroser aujourd'hui.")
    elif pluie_mm < 1 and temp_max < 30:
        conseils.append("Temps sec : pensez a verifier l'humidite du sol.")

    if not conseils:
        conseils.append("Conditions clementes : journee ideale pour jardiner.")
    return conseils


@router.get("")
async def meteo(_: User = Depends(get_current_user)):
    """Meteo du jour au jardin + conseils. US-11 et US-12."""
    params = {
        "latitude": settings.jardin_latitude,
        "longitude": settings.jardin_longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
        "timezone": "auto",
        "forecast_days": 3,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            reponse = await client.get(OPEN_METEO_URL, params=params)
            reponse.raise_for_status()
            data = reponse.json()
    except (httpx.HTTPError, httpx.TimeoutException):
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Service meteo indisponible pour le moment. Reessayez plus tard.",

        ) from None


    daily = data.get("daily", {})
    temp_max = daily.get("temperature_2m_max", [None])[0]
    temp_min = daily.get("temperature_2m_min", [None])[0]
    pluie = daily.get("precipitation_sum", [0])[0] or 0

    if temp_max is None or temp_min is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Donnees meteo incompletes.")

    previsions = []
    for i in range(len(daily.get("time", []))):
        previsions.append({
            "date": daily["time"][i],
            "temp_max": daily["temperature_2m_max"][i],
            "temp_min": daily["temperature_2m_min"][i],
            "pluie_mm": daily["precipitation_sum"][i],
            "code": daily["weather_code"][i],
        })

    return {
        "jardin": settings.jardin_nom,
        "aujourd_hui": {
            "temp_max": temp_max,
            "temp_min": temp_min,
            "pluie_mm": pluie,
        },
        "conseils": generer_conseils(temp_max, temp_min, pluie),
        "previsions": previsions,
    }
