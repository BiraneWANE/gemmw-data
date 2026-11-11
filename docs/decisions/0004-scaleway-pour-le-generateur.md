# 0004. Un petit serveur Scaleway pour le générateur

Date : 2026-11-10 · Statut : proposée

## Contexte

Le site est sur un hébergement mutualisé o2switch, qui ne fait pas tourner de conteneur.
Le générateur au prénom a besoin d'un endroit où son conteneur tourne en permanence,
appelable en HTTPS par la boutique. Il traite des prénoms d'enfants : on veut les données en France.

## Décision

Un serveur Scaleway DEV1-S (2 vCPU, 2 Go) à Paris, créé par Terraform, avec Docker Compose
et Caddy pour le HTTPS. Le prix affiché par Scaleway le 10 novembre 2026 est d'environ 6 € par mois ;
il est à revérifier sur scaleway.com au moment de créer le serveur.

Écartés : Kubernetes (un seul conteneur), un hébergeur hors Union européenne,
et Hetzner, moins cher, mais dont les gabarits et les prix ont changé plusieurs fois en 2026
et dont les centres de données sont en Allemagne et en Finlande.

## Conséquences

Une dépense fixe d'environ 6 € par mois, à décider par Birane avant tout `terraform apply`.
Changer d'hébergeur ne touche que `infra/terraform/`. À revoir si le générateur doit tenir
beaucoup plus de commandes, ou si le tableau de bord rejoint le même serveur.
