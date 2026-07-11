# Guide administrateur — installation, configuration, maintenance

## 1. Installation en production

### Prérequis serveur
- Ubuntu 22.04+ avec Docker et Docker Compose
- Un nom de domaine pointant sur l'IP du serveur
- Ports ouverts : **22 (SSH), 80, 443** — et rien d'autre

### Étapes

```bash
git clone <url-du-repo> /srv/potagerconnect
cd /srv/potagerconnect

cp .env.example .env
openssl rand -hex 32     # → coller dans SECRET_KEY
nano .env                # renseigner tous les mots de passe

docker compose up -d --build
docker compose exec backend python -m app.seed
```

### HTTPS (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d potagerconnect.example.fr
```

Certbot installe un renouvellement automatique. Vérifier :

```bash
sudo certbot renew --dry-run
```

## 2. Variables d'environnement

| Variable | Rôle | Obligatoire |
|----------|------|-------------|
| `SECRET_KEY` | Signature des JWT | ✅ **Oui** |
| `POSTGRES_PASSWORD` | Mot de passe BDD | ✅ Oui |
| `DATABASE_URL` | Connexion BDD | ✅ Oui |
| `CORS_ORIGINS` | Domaines autorisés | ✅ Oui |
| `GRAFANA_PASSWORD` | Admin Grafana | ✅ Oui |

⚠️ Le fichier `.env` n'est **jamais** commité. Vérifier : `git check-ignore .env`

## 3. Monitoring

| Outil | URL | Rôle |
|-------|-----|------|
| Prometheus | `:9090` | Collecte des métriques |
| Grafana | `:3000` | Dashboards |
| Alertmanager | `:9093` | Notifications |

### Dashboards à créer dans Grafana
- **Système** : CPU, RAM, disque, réseau (source : node-exporter)
- **Applicatif** : requêtes/sec, latence p95, codes HTTP, taux d'erreur 5xx

### Alertes configurées
| Alerte | Seuil | Sévérité |
|--------|-------|----------|
| `ServiceDown` | Backend injoignable > 1 min | Critique |
| `TauxErreur5xxEleve` | > 5% d'erreurs sur 5 min | Critique |
| `LatenceElevee` | p95 > 1 s pendant 5 min | Avertissement |
| `MemoireSaturee` | RAM > 90% pendant 5 min | Avertissement |

**Tester une alerte** (à faire avant la soutenance) :
```bash
docker compose stop backend
# → l'alerte ServiceDown doit se déclencher au bout d'une minute
docker compose start backend
```

## 4. Sauvegarde et restauration

### Sauvegarde quotidienne

```bash
docker compose exec -T db pg_dump -U potager potagerconnect \
  | gzip > /srv/backups/potager_$(date +%F).sql.gz
```

Cron, tous les jours à 3h :
```cron
0 3 * * * cd /srv/potagerconnect && docker compose exec -T db pg_dump -U potager potagerconnect | gzip > /srv/backups/potager_$(date +\%F).sql.gz
```

**Rétention :** 7 sauvegardes quotidiennes + 4 hebdomadaires.
**Hors site :** copier vers un stockage objet (S3 / Azure Blob).

### Restauration

```bash
gunzip -c /srv/backups/potager_2026-07-01.sql.gz \
  | docker compose exec -T db psql -U potager potagerconnect
```

## 5. Plan de reprise d'activité (PRA)

| Scénario | Procédure | Objectif |
|----------|-----------|----------|
| Conteneur planté | `docker compose restart <service>` | RTO < 2 min |
| Corruption BDD | Restaurer le dernier dump | RTO < 30 min, RPO < 24 h |
| Perte du serveur | Reprovisionner, `git clone`, restaurer le dump | RTO < 2 h |
| Déploiement défectueux | Rollback : redéployer l'image du SHA précédent | RTO < 5 min |

## 6. Rollback d'un déploiement

Chaque image est taguée avec le SHA du commit. Pour revenir en arrière :

```bash
export TAG=<sha-precedent>
docker compose pull && docker compose up -d
```

## 7. Maintenance courante

```bash
docker compose logs -f backend      # suivre les logs
docker compose ps                   # état des services
curl -f https://<domaine>/api/health   # sonde applicative
docker system prune -a              # nettoyer les images inutilisées
```
