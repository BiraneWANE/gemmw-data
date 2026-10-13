# Architecture

## Le principe

Une boutique de livrets PDF vend quelques dizaines d'exemplaires par mois. L'architecture est dimensionnée pour ça, et pour pouvoir grandir sans être réécrite. Chaque outil est là parce qu'une question concrète l'a demandé ; rien n'est là pour faire joli sur un CV.

## Le flux

```
Sites concurrents ──(requests + BeautifulSoup, chaque lundi)──▶ data/brut/*.jsonl
Exports Payhip / Etsy ──(import pandas + contrôles Great Expectations)──▶ entrepôt SQLite
                                                                            │
                                   ┌────────────────────────────────────────┤
                                   ▼                                        ▼
                        Tableau de bord Streamlit                 Modèles scikit-learn
                        (ventes, marge nette, prix)               (prévision, segments), suivis MLflow

Boutique WooCommerce ──(webhook commande)──▶ API FastAPI ──(PyMuPDF)──▶ PDF au prénom ──▶ mail à la cliente
```

## Les choix, et pourquoi

**SQLite d'abord, PostgreSQL ensuite.** Quelques milliers de lignes par an. SQLite tient sans serveur, se sauvegarde en copiant un fichier, et le schéma SQL est le même que celui qu'on migrera vers PostgreSQL (Neon ou Supabase) quand plusieurs services écriront en même temps.

**GitHub Actions comme ordonnanceur.** Une collecte par semaine ne justifie pas Airflow. Airflow est documenté ici pour dire ce qu'il apporterait (dépendances entre tâches, reprise, interface) et à partir de quand il deviendrait utile : quand il y aura plus de cinq tâches dépendantes les unes des autres. Pas avant.

**Great Expectations pour les contrôles d'entrée.** Les exports Payhip et Etsy changent de format sans prévenir. Les attentes (colonnes présentes, prix positifs, dates valides, pas de doublon de commande) sont versionnées avec le code et bloquent l'import quand elles échouent.

**FastAPI + PyMuPDF pour le générateur.** Le livret personnalisé est un PDF existant dans lequel on remplace du texte. PyMuPDF le fait en quelques millisecondes. Une seule route, un seul conteneur Docker, derrière Caddy pour le HTTPS.

**Terraform pour le VPS.** Un seul serveur, mais décrit en code : le recréer prend dix minutes, et ça documente ce qui tourne.

**LiteLLM devant les assistants.** Le fournisseur de modèle change (prix, qualité, disponibilité). Le code appelle une interface unique et le fournisseur est une variable d'environnement. Chaque conversation enregistre ses jetons et son coût, affichés dans le tableau de bord.

## Ce qui a été écarté

| Outil | Pourquoi pas |
|---|---|
| Spark | Des milliers de lignes, pas des milliards. pandas suffit avec une marge énorme |
| Kafka | Aucun flux temps réel. Les commandes arrivent par webhook, une à la fois |
| Snowflake, BigQuery | Un entrepôt payant pour quelques Mo n'a pas de sens |
| Kubernetes | Un conteneur sur un VPS. Docker Compose suffit |
| Airflow | Expliqué ci-dessus : utile à partir de cinq tâches dépendantes |

## Sécurité

Aucun secret dans le dépôt : `.env` est ignoré, gitleaks tourne avant chaque commit. Les clés d'API vivent dans les secrets GitHub Actions et dans le `.env` du serveur. Les emails des acheteuses ne quittent jamais Payhip et Etsy autrement que hachés (voir GOUVERNANCE.md).
