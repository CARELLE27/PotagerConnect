# Retour d'expérience — PotagerConnect

> Template à compléter au fil du projet. À remplir dès qu'une difficulté survient,
> pas au J8 de mémoire.

## 1. Difficultés rencontrées et solutions

| # | Difficulté | Impact | Solution apportée | Jour |
|---|-----------|--------|-------------------|------|
| 1 | *(ex : CORS bloquant entre front et back)* | *(2h perdues)* | *(configurer allow_origins avec l'URL exacte du front)* | J3 |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |

## 2. Décisions de périmètre assumées

**Ce que nous avons volontairement exclu :**

- **Chat temps réel (WebSocket)** — aucun membre de l'équipe n'avait pratiqué la technologie. Sur 9 jours, un échec d'intégration aurait compromis la démonstration.
- **Paiement / facturation** — complexité juridique et technique sans rapport avec la valeur pédagogique du projet.
- **Application mobile native** — la PWA responsive couvre le besoin.

**Ce que ce choix nous a permis :** livrer un MVP complet, déployé, testé (>70% de couverture), monitoré et sécurisé, plutôt qu'un projet ambitieux à moitié fonctionnel.

## 3. Ce que nous referions autrement

- *(à compléter en rétrospective)*

## 4. Ce qui a bien fonctionné

- **Sprint 0 bloquant au J2** : personne n'a codé avant que Docker et la CI ne soient verts. Aucune galère d'intégration en fin de projet.
- **Règle MUST avant SHOULD** : le MVP était déployé au J5, ce qui a sécurisé la note plancher.
- **Code freeze au J8 matin** : aucune régression de dernière minute.

## 5. Métriques du projet

| Indicateur | Valeur |
|------------|--------|
| User stories livrées | ../17 |
| Couverture de tests | ..% |
| Nombre de commits | .. |
| Pull requests mergées | .. |
| Latence p95 sous charge (50 users) | .. ms |
| Temps de build de la pipeline | .. min |

## 6. Roadmap — potentiel d'évolution

*(Évalué au barème : « Potentiel d'évolution /5 »)*

**Court terme (v1.1)**
- Photos d'évolution des cultures (US-10)
- Forum d'entraide et troc de graines (US-15/16/17)

**Moyen terme (v2)**
- Notifications par email (récolte imminente, alerte gel)
- Export du planning en PDF
- Multi-jardins (une instance, plusieurs collectifs)

**Long terme**
- Application mobile (React Native, réutilisation de l'API REST)
- Reconnaissance de maladies des plantes par photo
- Scaling Kubernetes avec réplication horizontale du backend
