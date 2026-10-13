# 0002. GitHub Actions avant Airflow

Date : 2026-10-12 · Statut : acceptée

## Contexte

Le référentiel RNCP 41993 cite Airflow pour l'orchestration. Le besoin réel est une collecte par semaine et, plus tard, un import d'exports après chaque relevé.

## Décision

Ordonnancer avec GitHub Actions (cron dans le dépôt, gratuit, journaux conservés). Ne pas installer Airflow tant qu'il n'y a pas au moins cinq tâches dépendantes les unes des autres avec un besoin de reprise sur échec.

## Conséquences

Pas de serveur d'orchestration à maintenir. Le jour où Airflow devient utile, chaque étape est déjà une commande `gemmw <étape>` indépendante, donc un DAG se résume à les enchaîner.
