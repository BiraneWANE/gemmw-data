# Journal

Une entrée par séance de travail : ce qui a été fait, ce qui a été décidé et pourquoi.

## 2026-11-23

- Catalogue commun (`src/gemmw/catalogue/`) : 12 références, une par livret et par format, reliées au site (WooCommerce), à Payhip et à Etsy ; contrôles de cohérence (doublons, formats, prix). Table `produit` et colonne `vente.sku` dans l'entrepôt, avec migration des bases existantes.
- Rattachement automatique des ventes au catalogue après chaque import : par référence pour le site, par code ou titre pour Payhip, par identifiant ou début de titre pour Etsy. Une vente non rattachée reste visible (« à rattacher »).
- Import des commandes de la boutique du site : collecte par l'API REST WooCommerce (`gemmw commandes-site`), lecture JSON, commandes à 0 € et remboursées écartées.
- Tableau de bord : ventes par livret toutes boutiques confondues.
- Constat : les livrets plastifiés de l'automne et de « Je compte » ne sont vendus que sur le site, pas sur Payhip.

## 2026-11-18

- Générateur au prénom : les pointillés sous le repère PRENOM sont gardés (ligne « Ce livret appartient à : »).

## 2026-11-10

- Gouvernance des données : registre des traitements, durées de conservation, accès.
- Collecte : six contrôles de qualité du relevé, alerte quand un concurrent change ses prix (résumé de l'action, Telegram en option), relevé précédent gardé en cache.
- Collecte Etsy via l'API officielle v3, sautée sans clé.
- Générateur au prénom : remplacement des repères PRENOM (couleur du fond prise autour du repère, phrase réécrite quand le repère est au milieu d'un texte), service FastAPI protégé par une clé, image Docker construite et démarrée par la CI.
- Infrastructure du générateur en code (`infra/`) : serveur Scaleway à Paris, pare-feu, Docker Compose et Caddy pour le HTTPS ; Terraform vérifié par la CI (format et validation). Décision 0004, proposée.
- Décision : le prénom n'est jamais enregistré ; les livrets sources sont montés dans le conteneur, jamais copiés dans l'image.

## 2026-10-12

- Squelette du dépôt : structure `src/`, `uv`, `ruff`, `pytest`, `pre-commit` avec `gitleaks`, intégration continue et collecte hebdomadaire sur GitHub Actions.
- Premier extracteur WooCommerce et schéma de l'entrepôt, avec tests sur fixtures figées.
- Décision : SQLite avant PostgreSQL, GitHub Actions avant Airflow (voir `docs/decisions/`).
