"""Partage des recoltes - US-13 / US-14 (SHOULD, Sprint 2).

Un jardinier propose un surplus de recolte ; les autres peuvent le reserver.
Objectif social : eviter le gaspillage, renforcer l'entraide du collectif.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Recolte, StatutRecolteEnum, User
from app.schemas import RecolteCreate, RecolteOut

router = APIRouter(prefix="/recoltes", tags=["recoltes"])


@router.post("", response_model=RecolteOut, status_code=status.HTTP_201_CREATED)
def proposer_recolte(
    payload: RecolteCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """US-13 : proposer un surplus de recolte au partage."""
    recolte = Recolte(
        user_id=user.id,
        nom_produit=payload.nom_produit.strip(),
        quantite=payload.quantite.strip(),
    )
    db.add(recolte)
    db.commit()
    db.refresh(recolte)
    return recolte


@router.get("", response_model=list[RecolteOut])
def liste_recoltes(
    statut: StatutRecolteEnum | None = Query(default=None),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Liste des recoltes partagees, filtrable par statut (disponible / reservee)."""
    query = db.query(Recolte)
    if statut is not None:
        query = query.filter(Recolte.statut == statut)
    return query.order_by(Recolte.created_at.desc()).all()


@router.patch("/{recolte_id}/reserver", response_model=RecolteOut)
def reserver_recolte(
    recolte_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """US-14 : reserver un surplus disponible."""
    recolte = db.get(Recolte, recolte_id)
    if recolte is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Recolte introuvable")

    if recolte.statut == StatutRecolteEnum.reservee:
        raise HTTPException(status.HTTP_409_CONFLICT, "Cette recolte est deja reservee")

    if recolte.user_id == user.id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Vous ne pouvez pas reserver votre propre recolte"
        )

    recolte.statut = StatutRecolteEnum.reservee
    recolte.reserve_par = user.id
    db.commit()
    db.refresh(recolte)
    return recolte


@router.delete("/{recolte_id}", status_code=status.HTTP_204_NO_CONTENT)
def annuler_recolte(
    recolte_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Le proposeur peut retirer sa recolte tant qu'elle n'est pas reservee."""
    recolte = db.get(Recolte, recolte_id)
    if recolte is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Recolte introuvable")
    if recolte.user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Ce n'est pas votre recolte")
    if recolte.statut == StatutRecolteEnum.reservee:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Impossible de retirer une recolte deja reservee"
        )

    db.delete(recolte)
    db.commit()
