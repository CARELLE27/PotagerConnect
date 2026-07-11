import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas import RefreshRequest, TokenPair, UserCreate, UserLogin, UserOut
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])
security_logger = logging.getLogger("security")


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """US-01 : inscription. Le mot de passe est hache en bcrypt, jamais stocke en clair."""
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Cet email est deja utilise")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        nom=payload.nom.strip(),
        prenom=payload.prenom.strip(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenPair)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """US-02 : connexion. Renvoie un access token et un refresh token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        security_logger.warning("Echec de connexion pour l'email %s", payload.email)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants invalides")

    return TokenPair(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Renouvelle l'access token a partir d'un refresh token valide."""
    email = decode_token(payload.refresh_token, expected_type="refresh")
    if email is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token invalide")

    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Utilisateur introuvable")

    return TokenPair(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    """Renvoie l'utilisateur courant : sert a afficher le header et adapter la navigation."""
    return user
