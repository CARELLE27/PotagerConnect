import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Parcelle, RoleEnum, StatutParcelleEnum, User
from app.security import hash_password

engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    def _get_db():
        yield db

    app.dependency_overrides[get_db] = _get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def donnees(db):
    """1 admin, 2 jardiniers, 2 parcelles (une pour chaque jardinier)."""
    admin = User(email="admin@t.fr", nom="D", prenom="Marc",
                 role=RoleEnum.admin, password_hash=hash_password("Admin2026!"))
    j1 = User(email="j1@t.fr", nom="K", prenom="Aicha",
              role=RoleEnum.jardinier, password_hash=hash_password("Jardin2026!"))
    j2 = User(email="j2@t.fr", nom="P", prenom="Lea",
              role=RoleEnum.jardinier, password_hash=hash_password("Jardin2026!"))
    db.add_all([admin, j1, j2])
    db.flush()

    p_libre = Parcelle(numero="A-02", surface_m2=12.0, statut=StatutParcelleEnum.libre)
    p_j1 = Parcelle(numero="A-01", surface_m2=12.0,
                    statut=StatutParcelleEnum.attribuee, user_id=j1.id)
    db.add_all([p_libre, p_j1])
    db.commit()

    return {"admin": admin, "j1": j1, "j2": j2, "p_libre": p_libre, "p_j1": p_j1}


def token(client, email, mdp):
    r = client.post("/auth/login", json={"email": email, "password": mdp})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture()
def auth_admin(client, donnees):
    return {"Authorization": f"Bearer {token(client, 'admin@t.fr', 'Admin2026!')}"}


@pytest.fixture()
def auth_j1(client, donnees):
    return {"Authorization": f"Bearer {token(client, 'j1@t.fr', 'Jardin2026!')}"}


@pytest.fixture()
def auth_j2(client, donnees):
    return {"Authorization": f"Bearer {token(client, 'j2@t.fr', 'Jardin2026!')}"}
