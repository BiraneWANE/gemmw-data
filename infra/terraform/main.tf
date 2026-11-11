# Un seul serveur, décrit en code : le recréer prend dix minutes et ce fichier dit ce qui tourne.

resource "scaleway_iam_ssh_key" "admin" {
  name       = "gemmw-admin"
  public_key = var.cle_ssh_publique
}

resource "scaleway_instance_ip" "publique" {}

resource "scaleway_instance_security_group" "web" {
  name                    = "gemmw-web"
  inbound_default_policy  = "drop"
  outbound_default_policy = "accept"

  inbound_rule {
    action   = "accept"
    port     = 22
    ip_range = var.ip_admin
  }

  inbound_rule {
    action = "accept"
    port   = 80
  }

  inbound_rule {
    action = "accept"
    port   = 443
  }
}

resource "scaleway_instance_server" "generateur" {
  name              = "gemmw-generateur"
  type              = var.type_serveur
  image             = "debian_bookworm"
  ip_id             = scaleway_instance_ip.publique.id
  security_group_id = scaleway_instance_security_group.web.id
  tags              = ["gemmw", "generateur"]

  root_volume {
    size_in_gb = var.taille_disque_go
  }

  user_data = {
    cloud-init = templatefile("${path.module}/cloud-init.yaml", {
      domaine   = var.domaine
      depot     = var.depot
      compose   = file("${path.module}/../docker-compose.yml")
      caddyfile = file("${path.module}/../Caddyfile")
    })
  }

  depends_on = [scaleway_iam_ssh_key.admin]
}
