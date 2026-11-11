# Accès et rôles

Principe : chacun accède à ce dont son rôle a besoin, rien de plus. Les comptes sont nominatifs, jamais partagés, avec la double authentification quand le service la propose.

| Ressource | Éditrice | Développeur | GitHub Actions | Assistants IA |
|---|---|---|---|---|
| Comptes Payhip, Etsy, Amazon | Propriétaire | Sur invitation, le temps d'une tâche | Aucun | Aucun |
| Administration de la boutique (WordPress) | Administratrice | Administrateur | Aucun | Aucun |
| Comptes Stripe et PayPal | Propriétaire | Aucun | Aucun | Aucun |
| Hébergement (cPanel) | Titulaire | Administrateur | Aucun | Aucun |
| Exports de ventes avec emails | Les télécharge | Les importe, puis les supprime | Aucun | Aucun |
| Sel de hachage (`.env`) | Aucun | Seul détenteur | Aucun | Aucun |
| Entrepôt SQLite (pseudonymisé) | Lecture via le tableau de bord | Lecture et écriture | Aucun | Aucun |
| Dépôt GitHub | Lecture | Propriétaire | Lecture du code | Aucun |
| Relevés de prix | Lecture | Lecture et écriture | Écriture (artefact CI) | Lecture |

## Secrets

- Les secrets vivent dans `.env` en local et dans les secrets chiffrés de GitHub pour la CI. Aucun secret dans le code ni dans l'historique git.
- La CI ne reçoit aucun secret lié aux clientes : elle ne fait que la collecte publique.
- Si un secret fuit, on le révoque d'abord, puis on nettoie l'historique.

## Revue

Une fois par trimestre, on relit cette table, on retire les accès devenus inutiles, et on note la revue dans le journal des décisions (`docs/decisions/`).
