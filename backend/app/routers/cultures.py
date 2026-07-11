from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Culture, Parcelle, RoleEnum, StatutCultureEnum, User
from app.plantes import get_plante, suggestions_du_mois
from app.schemas import CultureCreate, CultureOut

router = APIRouter(tags=["cultures"])


def _verifier_proprietaire(parcelle: Parcelle, user: User) -> None:
    """Un jardinier ne peut agir que sur SA parcelle. L'admin passe partout."""
    if user.role == RoleEnum.admin:
        return
    if parcelle.user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Cette parcelle ne vous appartient pas")


@router.post(
    "/parcelles/{parcelle_id}/cultures",
    response_model=CultureOut,
    status_code=status.HTTP_201_CREATED,
)
def creer_culture(
    parcelle_id: int,
    payload: CultureCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """US-07 : le jardinier declare ce qu'il plante. Feature metier coeur."""
    parcelle = db.get(Parcelle, parcelle_id)
    if parcelle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Parcelle introuvable")
    _verifier_proprietaire(parcelle, user)

    infos = get_plante(payload.nom_plante)
    famille = infos["famille"] if infos else None
    date_recolte = (
        payload.date_plantation + timedelta(days=infos["jours_recolte"]) if infos else None
    )

    culture = Culture(
        parcelle_id=parcelle.id,
        nom_plante=payload.nom_plante.strip().lower(),
        famille=famille,
        date_plantation=payload.date_plantation,
        date_recolte_prevue=date_recolte,
    )
    db.add(culture)
    db.commit()
    db.refresh(culture)
    return culture


@router.get("/parcelles/{parcelle_id}/cultures", response_model=list[CultureOut])
def liste_cultures(
    parcelle_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    parcelle = db.get(Parcelle, parcelle_id)
    if parcelle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Parcelle introuvable")
    _verifier_proprietaire(parcelle, user)
    return (
        db.query(Culture)
        .filter(Culture.parcelle_id == parcelle_id)
        .order_by(Culture.date_plantation.desc())
        .all()
    )


@router.patch("/cultures/{culture_id}/recolter", response_model=CultureOut)
def recolter(
    culture_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    culture = db.get(Culture, culture_id)
    if culture is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Culture introuvable")
    _verifier_proprietaire(culture.parcelle, user)

    culture.statut = StatutCultureEnum.recoltee
    db.commit()
    db.refresh(culture)
    return culture


@router.delete("/cultures/{culture_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_culture(
    culture_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    culture = db.get(Culture, culture_id)
    if culture is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Culture introuvable")
    _verifier_proprietaire(culture.parcelle, user)

    db.delete(culture)
    db.commit()


@router.get("/suggestions")
def suggestions(
    parcelle_id: int | None = Query(default=None),
    mois: int | None = Query(default=None, ge=1, le=12),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """US-08 / US-09 : plantes de saison, avec rotation des cultures.

    Si une parcelle est fournie, on exclut les familles deja cultivees dessus
    dans les 12 derniers mois.
    """
    mois = mois or date.today().month
    familles_a_eviter: set[str] = set()

    if parcelle_id is not None:
        parcelle = db.get(Parcelle, parcelle_id)
        if parcelle is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Parcelle introuvable")
        _verifier_proprietaire(parcelle, user)

        limite = date.today() - timedelta(days=365)
        cultures = (
            db.query(Culture)
            .filter(Culture.parcelle_id == parcelle_id, Culture.date_plantation >= limite)
            .all()
        )
        familles_a_eviter = {c.famille for c in cultures if c.famille}

    return {
        "mois": mois,
        "familles_evitees": sorted(familles_a_eviter),
        "suggestions": suggestions_du_mois(mois, familles_a_eviter),
    }
