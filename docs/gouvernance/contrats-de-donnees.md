# Contrats de données

Un contrat de données dit ce qu'une table promet à ceux qui la lisent : schéma, qualité, fraîcheur, sensibilité. Les attentes ci-dessous sont celles que vérifie `src/gemmw/entrepot/controles.py` avant tout chargement ; une seule qui échoue bloque l'import.

## `vente`

| Clause | Valeur |
|---|---|
| Producteur | Import des exports Payhip et Etsy (`gemmw importer`), plus tard la boutique WooCommerce |
| Consommateurs | Tableau de bord, futurs modèles de prévision et de segmentation |
| Fréquence | Manuelle, à chaque export ; cible : chaque semaine |
| Clé | (`plateforme`, `commande_ref`) unique. Un import rejoué ne crée pas de doublon |
| Sensibilité | Donnée personnelle pseudonymisée (`acheteuse_hash`) |

| Colonne | Type | Attente |
|---|---|---|
| `plateforme` | texte | parmi payhip, etsy, amazon, site |
| `commande_ref` | texte | non vide |
| `vendue_le` | date ISO | valide, jamais dans le futur |
| `produit` | texte | non vide |
| `prix_ttc_eur` | réel | strictement positif, sous 500 € |
| `frais_eur` | réel | inférieur au prix |
| `tva_eur` | réel | 0 en franchise en base, sauf TVA collectée par la plateforme |
| `acheteuse_hash` | texte | exactement 64 caractères hexadécimaux |
| `pays` | texte | code pays ou vide |

## `releve_prix`

| Clause | Valeur |
|---|---|
| Producteur | Collecte hebdomadaire (GitHub Actions, le lundi) |
| Consommateurs | Tableau de bord, position de prix |
| Fraîcheur | Un relevé de moins de 8 jours ; au-delà, le tableau de bord le signale |
| Sensibilité | Publique, non personnelle |
| Règle | Ajout seul, jamais de mise à jour : l'historique est la valeur de la table |

| Colonne | Type | Attente |
|---|---|---|
| `releve_le` | date ISO | date de la collecte |
| `site` | texte | un site de la liste de collecte |
| `titre` | texte | non vide |
| `prix_eur` | réel | positif ou nul (contrainte `CHECK` en base) |
| `url` | texte | adresse de la page produit |
| `format` | texte | « pdf », « papier » ou vide |

## Changer un contrat

Ajouter une colonne facultative ne casse rien. Renommer, retirer ou changer le sens d'une colonne demande une décision écrite dans `docs/decisions/`, la mise à jour de ce fichier et celle des contrôles, dans le même commit.
