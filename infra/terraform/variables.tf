variable "region" {
  description = "Région Scaleway (Paris : données en France)"
  type        = string
  default     = "fr-par"
}

variable "zone" {
  description = "Zone Scaleway"
  type        = string
  default     = "fr-par-1"
}

variable "type_serveur" {
  description = "Gabarit du serveur. DEV1-S : 2 vCPU, 2 Go, suffisant pour le générateur"
  type        = string
  default     = "DEV1-S"
}

variable "taille_disque_go" {
  description = "Disque du serveur (système, Docker, livrets sources)"
  type        = number
  default     = 20
}

variable "cle_ssh_publique" {
  description = "Clé SSH publique de Birane (contenu de ~/.ssh/id_ed25519.pub)"
  type        = string
}

variable "ip_admin" {
  description = "Adresse IP autorisée en SSH, au format 1.2.3.4/32"
  type        = string
}

variable "domaine" {
  description = "Sous-domaine du générateur, à faire pointer sur l'IP du serveur"
  type        = string
  default     = "generateur.gemmw.fr"
}

variable "depot" {
  description = "Dépôt d'où l'image du générateur est construite sur le serveur"
  type        = string
  default     = "https://github.com/BiraneWANE/gemmw-data.git#main"
}
