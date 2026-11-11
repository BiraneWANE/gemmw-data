terraform {
  required_version = ">= 1.6"
  required_providers {
    scaleway = {
      source  = "scaleway/scaleway"
      version = "~> 2.40"
    }
  }
}

# Identifiants lus dans l'environnement, jamais dans le code :
# SCW_ACCESS_KEY, SCW_SECRET_KEY, SCW_DEFAULT_PROJECT_ID
provider "scaleway" {
  region = var.region
  zone   = var.zone
}
