# Infrastructure du générateur

Un serveur chez Scaleway (Paris, données en France), décrit en Terraform :
une IP publique, un pare-feu (SSH depuis l'IP de Birane seulement, 80 et 443 ouverts),
et Docker installé au démarrage. Les livrets sources sont posés dans /srv/gemmw/livrets.
Le générateur tourne derrière Caddy, qui gère le HTTPS tout seul.

Le choix de Scaleway est expliqué dans `docs/decisions/0004-scaleway-pour-le-generateur.md`.
Changer d'hébergeur ne touche que `terraform/` : `docker-compose.yml` et `Caddyfile` restent.

## Créer le serveur

```bash
export SCW_ACCESS_KEY=... SCW_SECRET_KEY=... SCW_DEFAULT_PROJECT_ID=...
cd infra/terraform
terraform init
terraform plan  -var "cle_ssh_publique=$(cat ~/.ssh/id_ed25519.pub)" -var "ip_admin=$(curl -s ifconfig.me)/32"
terraform apply -var "cle_ssh_publique=$(cat ~/.ssh/id_ed25519.pub)" -var "ip_admin=$(curl -s ifconfig.me)/32"
```

## Après la création (une seule fois)

1. Dans cPanel o2switch > Zone DNS : enregistrement A `generateur` vers l'`ip_publique` affichée.
2. Sur le serveur : ajouter `GEMMW_API_CLE=...` dans `/opt/gemmw/.env`.
3. Copier les livrets : `scp livrets/*.pdf root@IP:/srv/gemmw/livrets/`.
4. `cd /opt/gemmw && docker compose up -d --build`, puis vérifier `https://generateur.gemmw.fr/sante`.

Les clés et les livrets ne passent jamais par Terraform ni par GitHub.

## Mettre à jour le générateur

`cd /opt/gemmw && docker compose up -d --build` reconstruit l'image depuis la branche main.
