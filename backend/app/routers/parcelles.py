from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_admin
from app.models import Parcelle, RoleEnum, StatutParcelleEnum, User
from app.schemas import AttributionRequest, ParcelleDetail, ParcelleOut, UserOut

router = APIRouter(prefix="/parcelles", tags=["parcelles"])


def _to_out(p: Parcelle) -> ParcelleOut:
    return ParcelleOut(
        id=p.id,
        numero=p.numero,
        surface_m2=p.surface_m2,
        statut=p.statut,
        pos_x=p.pos_x,
        pos_y=p.pos_y,
        user_id=p.user_id,
        jardinier_nom=p.jardinier.nom_complet if p.jardinier else None,
    )


@router.get("", response_model=list[ParcelleOut])
def liste_parcelles(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    """US-04 : carte de toutes les parcelles. Reserve au responsable."""
    parcelles = db.query(Parcelle).order_by(Parcelle.numero).all()
    return [_to_out(p) for p in parcelles]


@router.get("/mes-parcelles", response_model=list[ParcelleOut])
def mes_parcelles(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """US-06 : le jardinier ne voit que SES parcelles."""
    parcelles = (
        db.query(Parcelle).filter(Parcelle.user_id == user.id).order_by(Parcelle.numero).all()
    )
    return [_to_out(p) for p in parcelles]


@router.get("/{parcelle_id}", response_model=ParcelleDetail)
def detail_parcelle(
    parcelle_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    parcelle = db.get(Parcelle, parcelle_id)
    if parcelle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Parcelle introuvable")

    # Controle d'acces : un jardinier ne consulte que sa propre parcelle.
    if user.role != RoleEnum.admin and parcelle.user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Cette parcelle ne vous appartient pas")

    base = _to_out(parcelle)
    return ParcelleDetail(**base.model_dump(), cultures=parcelle.cultures)


@router.patch("/{parcelle_id}/attribuer", response_model=ParcelleOut)
def attribuer(
    parcelle_id: int,
    payload: AttributionRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """US-05 : le responsable attribue une parcelle libre a un jardinier."""
    parcelle = db.get(Parcelle, parcelle_id)
    if parcelle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Parcelle introuvable")
    if parcelle.statut == StatutParcelleEnum.attribuee:
        raise HTTPException(status.HTTP_409_CONFLICT, "Cette parcelle est deja attribuee")

    jardinier = db.get(User, payload.user_id)
    if jardinier is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Jardinier introuvable")

    parcelle.user_id = jardinier.id
    parcelle.statut = StatutParcelleEnum.attribuee
    db.commit()
    db.refresh(parcelle)
    return _to_out(parcelle)


@router.patch("/{parcelle_id}/liberer", response_model=ParcelleOut)
def liberer(
    parcelle_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)
):
    parcelle = db.get(Parcelle, parcelle_id)
    if parcelle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Parcelle introuvable")

    parcelle.user_id = None
    parcelle.statut = StatutParcelleEnum.libre
    db.commit()
    db.refresh(parcelle)
    return _to_out(parcelle)


users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("", response_model=list[UserOut])
def liste_jardiniers(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Peuple la modale d'attribution cote frontend. Admin uniquement."""
    return db.query(User).filter(User.role == RoleEnum.jardinier).order_by(User.nom).all()
