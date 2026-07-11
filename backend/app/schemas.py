from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import RoleEnum, StatutCultureEnum, StatutParcelleEnum, StatutRecolteEnum


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    nom: str = Field(min_length=1, max_length=100)
    prenom: str = Field(min_length=1, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    nom: str
    prenom: str
    role: RoleEnum


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class CultureCreate(BaseModel):
    nom_plante: str = Field(min_length=1, max_length=100)
    date_plantation: date


class CultureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parcelle_id: int
    nom_plante: str
    famille: str | None
    date_plantation: date
    date_recolte_prevue: date | None
    statut: StatutCultureEnum


class ParcelleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    surface_m2: float
    statut: StatutParcelleEnum
    pos_x: int
    pos_y: int
    user_id: int | None
    jardinier_nom: str | None = None


class ParcelleDetail(ParcelleOut):
    cultures: list[CultureOut] = []


class AttributionRequest(BaseModel):
    user_id: int


class RecolteCreate(BaseModel):
    nom_produit: str = Field(min_length=1, max_length=100)
    quantite: str = Field(min_length=1, max_length=50)


class RecolteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    nom_produit: str
    quantite: str
    statut: StatutRecolteEnum
    reserve_par: int | None
    created_at: datetime
