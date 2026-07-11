"""Hachage bcrypt + emission / verification des JWT (access + refresh)."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": subject, "exp": expire, "type": token_type}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(subject: str) -> str:
    return _create_token(
        subject, timedelta(minutes=settings.access_token_expire_minutes), "access"
    )


def create_refresh_token(subject: str) -> str:
    return _create_token(subject, timedelta(days=settings.refresh_token_expire_days), "refresh")


def decode_token(token: str, expected_type: str = "access") -> str | None:
    """Renvoie le sujet (email) si le token est valide et du bon type, sinon None."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
    if payload.get("type") != expected_type:
        return None
    return payload.get("sub")
