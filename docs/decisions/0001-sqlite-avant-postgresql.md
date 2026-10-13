# 0001. SQLite avant PostgreSQL

Date : 2026-10-12 · Statut : acceptée

## Contexte

L'entrepôt reçoit quelques milliers de lignes par an (relevés de prix hebdomadaires, ventes). Un seul processus y écrit à la fois pour l'instant.

## Décision

Démarrer sur SQLite, avec un schéma SQL standard qui ne dépend d'aucune extension. Migrer vers PostgreSQL (Neon ou Supabase, offres gratuites) quand l'API du générateur et la collecte écriront en même temps, ou quand le tableau de bord sera hébergé.

## Conséquences

Zéro serveur à gérer au départ, sauvegarde par copie de fichier. Le code d'accès passe par une seule fonction `ouvrir()` pour que le changement de moteur ne touche qu'un fichier. Les contraintes (`CHECK`, `UNIQUE`) sont dans le schéma, pas dans le code, pour qu'elles survivent à la migration.
