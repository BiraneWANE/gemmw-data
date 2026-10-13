# gemmw-data

La partie data de [Gem'MW Éditions](https://payhip.com/GemMW), une petite maison d'édition de livrets d'activités pour les 2-3 ans, vendus en PDF sur Payhip et Etsy, bientôt en papier sur Amazon.

Ce dépôt contient tout ce qui tourne autour de la boutique sans être la boutique : le relevé des prix concurrents, l'entrepôt des ventes, le tableau de bord de marge, les modèles de prévision, et le générateur de livrets personnalisés au prénom de l'enfant. Les livrets eux-mêmes ne sont pas ici.

## Ce que ça fait aujourd'hui

- **Collecte** : chaque lundi, une action GitHub relève les prix des livrets concurrents (boutiques WooCommerce) et archive le relevé. `gemmw collecte`
- **Entrepôt** : un schéma SQLite (PostgreSQL plus tard, même schéma) pour l'historique des prix et les ventes, sans aucune donnée personnelle en clair.
- **Qualité** : lint (ruff), tests (pytest), secrets (gitleaks), le tout rejoué à chaque push.

## Ce qui arrive, dans l'ordre

| Étape | Quoi | Outils |
|---|---|---|
| 1 | Import des exports Payhip et Etsy dans l'entrepôt, contrôles d'entrée | pandas, Great Expectations |
| 2 | Tableau de bord : ventes, marge nette réelle après frais et TVA, prix concurrents | Streamlit |
| 3 | Générateur : un prénom entre, un PDF personnalisé sort, déclenché par la boutique | FastAPI, PyMuPDF, Docker |
| 4 | Infrastructure décrite en code sur un petit VPS | Terraform, Caddy |
| 5 | Prévision des ventes, segmentation des acheteuses | scikit-learn, MLflow |
| 6 | Assistants : réponses aux clientes, idées de contenu, aide à la création | LLM via LiteLLM, compteur de coût par conversation |

Le détail des choix et de ce qui a été écarté (Spark, Kafka, Kubernetes…) est dans [ARCHITECTURE.md](ARCHITECTURE.md). Le traitement des données personnelles est dans [GOUVERNANCE.md](GOUVERNANCE.md). Les décisions, une par fichier, sont dans [docs/decisions/](docs/decisions/).

## Démarrer

```bash
git clone https://github.com/BiraneWANE/gemmw-data.git
cd gemmw-data
cp .env.example .env
make install        # uv sync + hooks pre-commit
make test
make collecte       # écrit data/brut/releve-AAAA-MM-JJ.jsonl
```

Prérequis : Python 3.12 et [uv](https://docs.astral.sh/uv/).

## Arborescence

```
src/gemmw/
  collecte/        relevé des prix concurrents, un extracteur par site
  entrepot/        schéma et accès à la base
  tableau_de_bord/ l'application Streamlit (à venir)
  modeles/         prévision et segmentation (à venir)
  texte_image/     classement des commentaires, visuels (à venir)
  api/             le générateur de livrets (à venir)
tests/             un test par comportement, fixtures HTML figées
.github/workflows/ ci.yml (à chaque push), collecte.yml (chaque lundi)
docs/decisions/    une décision d'architecture par fichier
```

## Auteur

Birane WANE, architecte IA et concepteur développeur en science des données (RNCP 41993 et 35288). Le projet sert une vraie boutique, la mienne et celle de ma femme, ce qui change tout : chaque brique existe parce qu'une question concrète l'a demandée.

Licence MIT pour le code. Les livrets, les visuels et la marque Gem'MW restent la propriété de Gem'MW Éditions.
