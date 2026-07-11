import enum
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RoleEnum(str, enum.Enum):
    jardinier = "jardinier"
    admin = "admin"


class StatutParcelleEnum(str, enum.Enum):
    libre = "libre"
    attribuee = "attribuee"


class StatutCultureEnum(str, enum.Enum):
    en_cours = "en_cours"
    recoltee = "recoltee"


class StatutRecolteEnum(str, enum.Enum):
    disponible = "disponible"
    reservee = "reservee"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    prenom: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name="role_enum"), default=RoleEnum.jardinier, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    parcelles: Mapped[list["Parcelle"]] = relationship(back_populates="jardinier")

    @property
    def nom_complet(self) -> str:
        return f"{self.prenom} {self.nom}"


class Parcelle(Base):
    __tablename__ = "parcelles"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    surface_m2: Mapped[float] = mapped_column(Float, nullable=False)
    statut: Mapped[StatutParcelleEnum] = mapped_column(
        Enum(StatutParcelleEnum, name="statut_parcelle_enum"),
        default=StatutParcelleEnum.libre,
        nullable=False,
    )
    pos_x: Mapped[int] = mapped_column(Integer, default=0)
    pos_y: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    jardinier: Mapped["User | None"] = relationship(back_populates="parcelles")
    cultures: Mapped[list["Culture"]] = relationship(
        back_populates="parcelle", cascade="all, delete-orphan"
    )


class Culture(Base):
    __tablename__ = "cultures"

    id: Mapped[int] = mapped_column(primary_key=True)
    parcelle_id: Mapped[int] = mapped_column(ForeignKey("parcelles.id"), nullable=False)
    nom_plante: Mapped[str] = mapped_column(String(100), nullable=False)
    famille: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_plantation: Mapped[date] = mapped_column(Date, nullable=False)
    date_recolte_prevue: Mapped[date | None] = mapped_column(Date, nullable=True)
    statut: Mapped[StatutCultureEnum] = mapped_column(
        Enum(StatutCultureEnum, name="statut_culture_enum"),
        default=StatutCultureEnum.en_cours,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    parcelle: Mapped["Parcelle"] = relationship(back_populates="cultures")


class Recolte(Base):
    """Partage des recoltes - US-13 / US-14 (SHOULD, Sprint 2)."""

    __tablename__ = "recoltes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    nom_produit: Mapped[str] = mapped_column(String(100), nullable=False)
    quantite: Mapped[str] = mapped_column(String(50), nullable=False)
    statut: Mapped[StatutRecolteEnum] = mapped_column(
        Enum(StatutRecolteEnum, name="statut_recolte_enum"),
        default=StatutRecolteEnum.disponible,
        nullable=False,
    )
    reserve_par: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
