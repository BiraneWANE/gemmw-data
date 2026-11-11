# gemmw-data

La partie data de [Gem'MW Éditions](https://payhip.com/GemMW), une petite maison d'édition de livrets d'activités pour les 2-3 ans, vendus en PDF sur Payhip et Etsy, bientôt en papier sur Amazon.

Ce dépôt contient tout ce qui tourne autour de la boutique sans être la boutique : le relevé des prix concurrents, l'entrepôt des ventes, le tableau de bord de marge, les modèles de prévision, et le générateur de livrets personnalisés au prénom de l'enfant. Les livrets eux-mêmes ne sont pas ici.

## Ce que ça fait aujourd'hui

- **Collecte** : chaque lundi, une action GitHub relève les prix des livrets concurrents (boutiques WooCommerce, et annonces Etsy via l'API officielle quand une clé est fournie) et archive le relevé. `uv run python -m gemmw.cli collecte`
- **Contrôle et alerte** : le relevé passe six contrôles de qualité (nombre de produits, champs remplis, prix plausibles, promotions cohérentes, doublons, sites présents), puis il est comparé à celui de la semaine précédente : changements de prix, promotions, nouveaux produits et produits retirés, écrits dans le résumé de l'action et envoyés sur Telegram si c'est configuré. `uv run python -m gemmw.cli controle-releve <relevé>` puis `uv run python -m gemmw.cli alerte <relevé>`
- **Entrepôt** : un schéma SQLite (PostgreSQL plus tard, même schéma) pour l'historique des prix et les ventes, sans aucune donnée personnelle en clair.
- **Import des ventes** : exports Payhip et Etsy vers l'entrepôt, emails hachés, neuf contrôles d'entrée. `uv run python -m gemmw.cli importer <export.csv> --plateforme payhip|etsy`
- **Tableau de bord** : ventes, marge nette après frais et TVA, et position de Gem'MW face aux prix concurrents. `uv run streamlit run src/gemmw/tableau_de_bord/app.py`
- **Générateur au prénom** : dans le livret, le mot PRENOM marque chaque endroit où le prénom de l'enfant doit apparaître. Le générateur l'efface et écrit le prénom à sa place, même taille, même couleur, sur la même ligne (la phrase est réécrite pour ne laisser ni trou ni chevauchement). Il tourne en service web (FastAPI, dans un conteneur Docker) appelé par la boutique, avec une clé partagée ; aucun prénom n'est enregistré. Essai en local : `uv run python -m gemmw.cli generer livret.pdf "Marie-Lou"`
- **Qualité** : lint (ruff), tests (pytest), secrets (gitleaks), le tout rejoué à chaque push.

## Ce qui arrive, dans l'ordre

| Étape | Quoi | Outils |
|---|---|---|
| 1 | Brancher le générateur sur la boutique, au paiement | webhook de la boutique |
| 2 | Créer le serveur du générateur (code prêt dans `infra/`, hébergeur à valider) | Terraform, Caddy |
| 3 | Prévision des ventes, segmentation des acheteuses | scikit-learn, MLflow |
| 4 | Assistants : réponses aux clientes, idées de contenu, aide à la création | LLM via LiteLLM, compteur de coût par conversation |

Le détail des choix et de ce qui a été écarté (Spark, Kafka, Kubernetes…) est dans [ARCHITECTURE.md](ARCHITECTURE.md). Le traitement des données personnelles est dans [GOUVERNANCE.md](GOUVERNANCE.md). Les décisions, une par fichier, sont dans [docs/decisions/](docs/decisions/).

## Démarrer

```bash
git clone https://github.com/BiraneWANE/gemmw-data.git
cd gemmw-data
cp .env.example .env
make install        # uv sync + hooks pre-commit
make test
uv run python -m gemmw.cli collecte   # écrit data/brut/releve-AAAA-MM-JJ.jsonl
uv run python -m gemmw.cli controle-releve data/brut/releve-AAAA-MM-JJ.jsonl
uv run python -m gemmw.cli alerte data/brut/releve-AAAA-MM-JJ.jsonl   # compare au relevé précédent
```

Prérequis : Python 3.12 et [uv](https://docs.astral.sh/uv/).

### Le générateur en service

```bash
uv sync --extra api
GEMMW_API_CLE=une-longue-cle GEMMW_LIVRETS_DIR=livrets uv run uvicorn gemmw.api.app:app
# ou dans Docker (les livrets sont montés, jamais copiés dans l'image)
docker build -t gemmw-generateur .
docker run -p 8000:8000 -e GEMMW_API_CLE=une-longue-cle -v "$PWD/livrets:/livrets:ro" gemmw-generateur
```

| Appel | Réponse |
|---|---|
| `GET /sante` | `{"ok": true}` |
| `GET /livrets` | les livrets disponibles et leur nombre de repères PRENOM |
| `POST /livrets/{reference}/personnaliser` avec `{"prenom": "Lina"}` | le PDF personnalisé |

Les deux derniers demandent l'en-tête `X-Gemmw-Cle`. Le prénom est vérifié (20 caractères au plus, lettres, espaces, tirets, apostrophes) et mis en forme (« marie-lou » donne « Marie-Lou »). Par défaut le prénom est écrit en Helvetica ; `GEMMW_POLICE` peut pointer vers le fichier de police du livret pour qu'il s'y fonde.

## Arborescence

```
src/gemmw/
  collecte/        relevé des prix concurrents, un extracteur par site
  entrepot/        schéma et accès à la base
  tableau_de_bord/ l'application Streamlit et sa couche de lecture
  modeles/         prévision et segmentation (à venir)
  texte_image/     classement des commentaires, visuels (à venir)
  api/             le générateur de livrets au prénom et son service web
tests/             un test par comportement, fixtures HTML figées
infra/             le serveur du générateur : Terraform (Scaleway), Docker Compose, Caddy
.github/workflows/ ci.yml (à chaque push), collecte.yml (chaque lundi)
docs/decisions/    une décision d'architecture par fichier
```

## Auteur

Birane WANE, architecte IA et concepteur développeur en science des données (RNCP 41993 et 35288). Le projet sert une vraie boutique, celle d'une cliente, ce qui change tout : chaque brique existe parce qu'une question concrète l'a demandée.

Licence MIT pour le code. Les livrets, les visuels et la marque Gem'MW restent la propriété de Gem'MW Éditions.
