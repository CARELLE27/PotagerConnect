"""Dependances d'authentification et de controle d'acces (RBAC)."""

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RoleEnum, User
from app.security import decode_token

security_logger = logging.getLogger("security")
bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token manquant")

    email = decode_token(creds.credentials, expected_type="access")
    if email is None:
        security_logger.warning("Token invalide ou expire presente")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token invalide ou expire")

    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Utilisateur introuvable")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """RBAC : seul un admin passe. Toute tentative est loguee (audit securite)."""
    if user.role != RoleEnum.admin:
        security_logger.warning(
            "Acces admin refuse pour l'utilisateur id=%s email=%s", user.id, user.email
        )
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Reserve aux responsables du jardin")
    return user
