"""Table de reference des plantes : famille, saison de semis, duree avant recolte.

Sert a deux choses :
  - calculer automatiquement date_recolte_prevue (US-07)
  - proposer des suggestions de saison + rotation des cultures (US-08 / US-09)
"""

PLANTES: dict[str, dict] = {
    "tomate": {"famille": "solanacees", "mois_semis": [4, 5, 6], "jours_recolte": 90},
    "pomme de terre": {"famille": "solanacees", "mois_semis": [3, 4, 5], "jours_recolte": 100},
    "aubergine": {"famille": "solanacees", "mois_semis": [4, 5], "jours_recolte": 110},
    "poivron": {"famille": "solanacees", "mois_semis": [4, 5], "jours_recolte": 100},
    "courgette": {"famille": "cucurbitacees", "mois_semis": [5, 6], "jours_recolte": 60},
    "concombre": {"famille": "cucurbitacees", "mois_semis": [5, 6], "jours_recolte": 65},
    "potiron": {"famille": "cucurbitacees", "mois_semis": [5, 6], "jours_recolte": 120},
    "haricot": {"famille": "legumineuses", "mois_semis": [5, 6, 7], "jours_recolte": 60},
    "pois": {"famille": "legumineuses", "mois_semis": [3, 4, 10], "jours_recolte": 80},
    "feve": {"famille": "legumineuses", "mois_semis": [2, 3, 11], "jours_recolte": 100},
    "carotte": {"famille": "apiacees", "mois_semis": [3, 4, 5, 6, 7], "jours_recolte": 90},
    "radis": {"famille": "brassicacees", "mois_semis": [3, 4, 5, 6, 7, 8, 9], "jours_recolte": 30},
    "chou": {"famille": "brassicacees", "mois_semis": [4, 5, 6], "jours_recolte": 100},
    "navet": {"famille": "brassicacees", "mois_semis": [3, 4, 8, 9], "jours_recolte": 60},
    "salade": {"famille": "asteracees", "mois_semis": [3, 4, 5, 6, 7, 8], "jours_recolte": 45},
    "epinard": {"famille": "chenopodiacees", "mois_semis": [3, 4, 8, 9], "jours_recolte": 50},
    "poireau": {"famille": "amaryllidacees", "mois_semis": [3, 4, 5], "jours_recolte": 150},
    "oignon": {"famille": "amaryllidacees", "mois_semis": [3, 4, 9], "jours_recolte": 120},
    "ail": {"famille": "amaryllidacees", "mois_semis": [10, 11], "jours_recolte": 240},
}


def get_plante(nom: str) -> dict | None:
    return PLANTES.get(nom.strip().lower())


def suggestions_du_mois(mois: int, familles_a_eviter: set[str] | None = None) -> list[dict]:
    """US-09 : plantes de saison, en excluant les familles deja cultivees (rotation)."""
    familles_a_eviter = familles_a_eviter or set()
    resultat = []
    for nom, infos in PLANTES.items():
        if mois not in infos["mois_semis"]:
            continue
        if infos["famille"] in familles_a_eviter:
            continue
        resultat.append({"nom_plante": nom, **infos})
    return sorted(resultat, key=lambda p: p["nom_plante"])
