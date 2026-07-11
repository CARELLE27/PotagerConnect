# 🌱 PotagerConnect

Plateforme de gestion de jardins partagés communautaires.
Projet 3PRJ3 — École IT — B3 Unité 3.

**Impact social :** promouvoir l'agriculture urbaine, organiser le partage des récoltes, recréer du lien social autour de la nature.

---

## Stack technique

| Couche | Techno | Pourquoi |
|--------|--------|----------|
| Frontend | React 18 + Vite | SPA, exigé au programme (2WEB1/2WEB2) |
| Backend | FastAPI (Python 3.11) | API REST, validation Pydantic native, doc OpenAPI auto |
| BDD | PostgreSQL 16 + SQLAlchemy | Relationnel, adapté au modèle parcelles/cultures |
| Auth | JWT (access + refresh) + bcrypt | Exigence sécurité 3SEC3 |
| Conteneurisation | Docker + docker compose | Exigé |
| CI/CD | GitLab CI *(et GitHub Actions)* | Lint + tests + build + deploy |
| Monitoring | Prometheus + Grafana + Alertmanager | Exigence 3MON3 |
| Reverse proxy | Nginx (headers de sécurité) | HTTPS, CSP, HSTS |

---

## Prérequis

- Docker et Docker Compose
- (dev backend seul) Python 3.11
- (dev frontend seul) Node 20

---

## Installation

```bash
git clone <url-du-repo>
cd potagerconnect

cp .env.example .env
# Générer une vraie clé secrète :
openssl rand -hex 32
# ...et la coller dans SECRET_KEY du fichier .env

docker compose up --build
```

Peupler la base avec les données de démonstration :

```bash
docker compose exec backend python -m app.seed
```

## Accès

| Service | URL |
|---------|-----|
| Application | http://localhost:5173 |
| API + doc OpenAPI | http://localhost:8000/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

## Comptes de démonstration

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| Responsable (admin) | marc.dupont@potager.fr | `Admin2026!` |
| Jardinière | aicha.kone@potager.fr | `Jardin2026!` |
| Jardinière | lea.perrin@potager.fr | `Jardin2026!` |

> Comptes de démo uniquement. À supprimer avant toute mise en production réelle.

---

## Lancer les tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest            # couverture minimale exigée : 70%
ruff check .      # linting
```

Les tests tournent sur SQLite en mémoire : aucune base externe, aucun appel réseau. La CI est donc reproductible.

---

## Structure du projet

```
potagerconnect/
├── backend/
│   ├── app/
│   │   ├── config.py          Variables d'environnement (aucun secret en dur)
│   │   ├── database.py        Session SQLAlchemy
│   │   ├── models.py          User, Parcelle, Culture, Recolte
│   │   ├── schemas.py         Validation Pydantic (entrées/sorties)
│   │   ├── security.py        bcrypt + JWT (access & refresh)
│   │   ├── deps.py            get_current_user, require_admin (RBAC)
│   │   ├── plantes.py         Table de référence : familles, saisons, rotations
│   │   ├── seed.py            Données de démonstration
│   │   └── routers/           auth.py, parcelles.py, cultures.py
│   ├── tests/                 Tests unitaires et d'intégration
│   └── Dockerfile             Multi-stage, non-root, healthcheck
├── frontend/
│   ├── src/pages/             Login, CarteParcelles, MaParcelle
│   ├── src/context/           AuthContext
│   ├── src/api.js             Client HTTP
│   ├── Dockerfile             Build Vite → Nginx
│   └── nginx.conf             Headers de sécurité + proxy /api
├── monitoring/                Prometheus, Alertmanager, Grafana
├── loadtest/charge.js         Test de charge k6
├── docker-compose.yml
├── .gitlab-ci.yml
└── docs/                      Doc technique, guides, REX
```

---

## Endpoints de l'API

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| POST | `/auth/register` | — | Inscription (bcrypt) |
| POST | `/auth/login` | — | Connexion → access + refresh token |
| POST | `/auth/refresh` | — | Renouveler l'access token |
| GET | `/auth/me` | JWT | Utilisateur courant |
| GET | `/parcelles` | **admin** | Carte de toutes les parcelles |
| GET | `/parcelles/mes-parcelles` | JWT | Uniquement ses parcelles |
| GET | `/parcelles/{id}` | JWT + owner | Détail + cultures |
| PATCH | `/parcelles/{id}/attribuer` | **admin** | Attribuer à un jardinier |
| PATCH | `/parcelles/{id}/liberer` | **admin** | Libérer une parcelle |
| GET | `/users` | **admin** | Liste des jardiniers |
| POST | `/parcelles/{id}/cultures` | JWT + owner | Déclarer une culture |
| GET | `/parcelles/{id}/cultures` | JWT + owner | Cultures de la parcelle |
| PATCH | `/cultures/{id}/recolter` | JWT + owner | Marquer comme récoltée |
| DELETE | `/cultures/{id}` | JWT + owner | Supprimer |
| GET | `/suggestions` | JWT | Plantes de saison + rotation |
| GET | `/health` | — | Sonde de liveness |
| GET | `/metrics` | — | Métriques Prometheus |

Documentation interactive complète : `/docs` (OpenAPI généré automatiquement).

---

## Sécurité

- Mots de passe hachés en **bcrypt**, jamais stockés en clair
- **JWT** access token (30 min) + **refresh token** (7 jours), typés et non interchangeables
- **RBAC** : `require_admin` sur toutes les routes de gestion
- **Vérification de propriété** : un jardinier ne peut agir que sur sa parcelle (403 sinon)
- Validation et sanitisation des entrées via Pydantic
- Headers de sécurité Nginx : CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- Conteneur backend en **utilisateur non-root**
- Logs d'audit des tentatives d'accès refusées et des échecs de connexion
- Aucun secret dans le code : tout passe par les variables d'environnement

---

## Périmètre volontairement exclu (WON'T HAVE)

Décision de scope assumée, sur 9 jours de projet :

- ❌ Chat / messagerie temps réel (WebSocket)
- ❌ Paiement ou transaction monétaire
- ❌ Application mobile native
- ❌ Notifications push
- ❌ Reconnaissance de plantes par IA

**Pourquoi :** livrer un MVP complet, déployé, monitoré et sécurisé vaut mieux qu'un projet ambitieux à moitié fonctionnel. Voir `docs/retour-experience.md`.

---

## Licence

Projet pédagogique — École IT, 2025-2026.
