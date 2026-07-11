"""Donnees de demonstration : 1 admin, 3 jardiniers, 12 parcelles, quelques cultures.

Usage : docker compose exec backend python -m app.seed
Idempotent : ne cree rien si les utilisateurs existent deja.
"""

from datetime import date, timedelta

from app.database import Base, SessionLocal, engine
from app.models import Culture, Parcelle, RoleEnum, StatutCultureEnum, StatutParcelleEnum, User
from app.plantes import get_plante
from app.security import hash_password

COMPTES = [
    ("marc.dupont@potager.fr", "Marc", "Dupont", RoleEnum.admin, "Admin2026!"),
    ("aicha.kone@potager.fr", "Aicha", "Kone", RoleEnum.jardinier, "Jardin2026!"),
    ("lea.perrin@potager.fr", "Lea", "Perrin", RoleEnum.jardinier, "Jardin2026!"),
    ("sam.traore@potager.fr", "Sam", "Traore", RoleEnum.jardinier, "Jardin2026!"),
]


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Base deja peuplee, rien a faire.")
            return

        users = {}
        for email, prenom, nom, role, mdp in COMPTES:
            u = User(
                email=email,
                prenom=prenom,
                nom=nom,
                role=role,
                password_hash=hash_password(mdp),
            )
            db.add(u)
            users[email] = u
        db.flush()

        attributions = {1: "aicha.kone@potager.fr", 3: "lea.perrin@potager.fr",
                        5: "sam.traore@potager.fr", 7: "aicha.kone@potager.fr"}

        parcelles = {}
        for i in range(1, 13):
            proprietaire = users.get(attributions.get(i))
            p = Parcelle(
                numero=f"A-{i:02d}",
                surface_m2=10.0 + (i % 4) * 2.5,
                statut=StatutParcelleEnum.attribuee if proprietaire else StatutParcelleEnum.libre,
                pos_x=(i - 1) % 4,
                pos_y=(i - 1) // 4,
                user_id=proprietaire.id if proprietaire else None,
            )
            db.add(p)
            parcelles[i] = p
        db.flush()

        demo_cultures = [
            (1, "tomate", 58, StatutCultureEnum.en_cours),
            (1, "radis", 98, StatutCultureEnum.recoltee),
            (3, "courgette", 50, StatutCultureEnum.en_cours),
            (7, "salade", 30, StatutCultureEnum.en_cours),
        ]
        for num, plante, jours, statut in demo_cultures:
            plantation = date.today() - timedelta(days=jours)
            infos = get_plante(plante)
            db.add(
                Culture(
                    parcelle_id=parcelles[num].id,
                    nom_plante=plante,
                    famille=infos["famille"],
                    date_plantation=plantation,
                    date_recolte_prevue=plantation + timedelta(days=infos["jours_recolte"]),
                    statut=statut,
                )
            )

        db.commit()
        print("Donnees de demonstration creees.")
        print("  Admin      : marc.dupont@potager.fr / Admin2026!")
        print("  Jardiniere : aicha.kone@potager.fr / Jardin2026!")
    finally:
        db.close()


if __name__ == "__main__":
    run()
