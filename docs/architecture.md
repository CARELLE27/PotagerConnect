# Documentation technique — PotagerConnect

## 1. Vue d'ensemble

```
┌──────────────────┐      HTTPS       ┌──────────────────┐
│   Navigateur     │ ───────────────► │  Nginx (reverse  │
└──────────────────┘                  │  proxy + SPA)    │
                                      └────────┬─────────┘
                                    /api/      │        / (static)
                                               ▼
                                      ┌──────────────────┐
                                      │  FastAPI         │
                                      │  JWT + RBAC      │
                                      └────────┬─────────┘
                                               │ SQLAlchemy
                                               ▼
                                      ┌──────────────────┐
                                      │  PostgreSQL 16   │
                                      │  (volume Docker) │
                                      └──────────────────┘

Observabilité :  FastAPI /metrics ──► Prometheus ──► Grafana
                                          └────────► Alertmanager ──► Slack/mail
```

## 2. Justification des choix technologiques

*(À argumenter en soutenance — 5 minutes sur l'architecture)*

| Choix | Alternative écartée | Justification |
|-------|---------------------|---------------|
| FastAPI | Flask, Django | Validation Pydantic intégrée, doc OpenAPI automatique, typage natif |
| PostgreSQL | MongoDB | Le domaine est fortement relationnel : User → Parcelle → Culture |
| SQLAlchemy 2.0 | Requêtes SQL brutes | Protège nativement de l'injection SQL, migrations gérées |
| JWT stateless | Sessions serveur | Scalabilité horizontale, pas d'état partagé entre réplicas |
| Nginx | Serveur Vite en prod | Sert les fichiers statiques, applique les headers de sécurité |
| Open-Meteo | OpenWeatherMap | Gratuit, **sans clé API** : rien à gérer en secret |
| Pas de WebSocket | Chat temps réel | Hors périmètre — décision de scope sur 9 jours |

## 3. Modèle de données

| Table | Champs | Relations |
|-------|--------|-----------|
| `users` | id, email (unique), password_hash, nom, prenom, role, is_active, created_at | 1—N `parcelles` |
| `parcelles` | id, numero (unique), surface_m2, statut, pos_x, pos_y, user_id (FK, nullable) | N—1 `users`, 1—N `cultures` |
| `cultures` | id, parcelle_id (FK), nom_plante, famille, date_plantation, date_recolte_prevue, statut | N—1 `parcelles` |
| `recoltes` | id, user_id (FK), nom_produit, quantite, statut, reserve_par (FK, nullable) | N—1 `users` |

**Énumérations :** `role` (jardinier / admin), `statut` parcelle (libre / attribuee), `statut` culture (en_cours / recoltee), `statut` récolte (disponible / reservee).

## 4. Logique métier notable

**Calcul automatique de la date de récolte** — à la création d'une culture, `app/plantes.py` fournit la durée moyenne avant récolte de la plante ; `date_recolte_prevue = date_plantation + jours_recolte`. Une plante inconnue est acceptée sans date prévue.

**Rotation des cultures** — `GET /suggestions?parcelle_id=X` exclut les plantes dont la famille botanique a déjà été cultivée sur cette parcelle dans les 12 derniers mois. Bonne pratique agronomique réelle : éviter d'épuiser le sol et de favoriser les maladies.

## 5. Sécurité — couches successives

1. **Nginx** : HTTPS (Let's Encrypt), CSP, HSTS, X-Frame-Options
2. **Pydantic** : validation et typage de toute entrée
3. **`get_current_user`** : le JWT doit être valide, de type `access`, et l'utilisateur actif
4. **`require_admin`** : RBAC sur les routes de gestion
5. **`_verifier_proprietaire`** : un jardinier n'agit que sur sa parcelle
6. **SQLAlchemy** : requêtes paramétrées, pas d'injection SQL possible
7. **Logs d'audit** : chaque 401/403 est tracé dans le logger `security`

## 6. Déploiement

Voir `docs/guide-admin.md`.

## 7. Migrations

Le seed (`app/seed.py`) appelle `Base.metadata.create_all()` pour le développement.
**Pour la production**, initialiser Alembic :

```bash
cd backend
alembic init migrations
alembic revision --autogenerate -m "schema initial"
alembic upgrade head
```
