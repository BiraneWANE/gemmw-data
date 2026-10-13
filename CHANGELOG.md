# Journal

Une entrée par séance de travail : ce qui a été fait, ce qui a été décidé et pourquoi.

## 2026-10-13

- Dépôt mis en ligne sur GitHub, intégration continue au vert.
- Extracteur confronté aux vraies pages : trois balisages WooCommerce (classique, thème Flatsome, grille maison), prix barrés, fourchettes de prix, pagination, vérification du robots.txt. Deux pages réelles figées comme fixtures.
- Première collecte réelle : 99 produits sur deux sites, 21 en promotion ; un exemple conservé dans `data/exemples/`.
- Deux défauts trouvés grâce aux données réelles, pas aux tests : le lien « page/1/ » relu comme page suivante, et les packs présents dans plusieurs catégories. Corrigés, avec un test chacun.
- Windows (Smart App Control) bloque les lanceurs `.exe` non signés créés par uv : les commandes passent par `python -m gemmw.cli`. Version de Python épinglée à 3.12 (`.python-version`).

## 2026-10-12

- Squelette du dépôt : structure `src/`, `uv`, `ruff`, `pytest`, `pre-commit` avec `gitleaks`, intégration continue et collecte hebdomadaire sur GitHub Actions.
- Premier extracteur WooCommerce et schéma de l'entrepôt, avec tests sur fixtures figées.
- Décision : SQLite avant PostgreSQL, GitHub Actions avant Airflow (voir `docs/decisions/`).
