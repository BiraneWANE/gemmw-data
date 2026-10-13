# 0003. Contrôles d'entrée maison avant Great Expectations

Date : 2026-10-13 · Statut : acceptée

## Contexte

Les exports Payhip et Etsy changent de format sans prévenir et peuvent contenir des lignes
annulées, remboursées ou incohérentes. Il faut des contrôles avant tout chargement. Le référentiel
cite Great Expectations, un cadre complet (attentes versionnées, rapports HTML, profilage).

## Décision

Écrire les attentes en Python pur dans `entrepot/controles.py` : une fonction, une liste de
résultats, un échec bloque l'import. Adopter Great Expectations quand il y aura au moins trois
sources et un besoin de rapport partagé, c'est-à-dire avec Amazon et le site.

## Conséquences

Zéro dépendance supplémentaire, lecture en une page, tests unitaires directs. Le vocabulaire
(attente, résultat, suite) est celui de Great Expectations, pour que la migration soit une
transcription et non une réécriture.
