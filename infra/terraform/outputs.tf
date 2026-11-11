output "ip_publique" {
  description = "À mettre dans un enregistrement A pour le sous-domaine (cPanel o2switch > Zone DNS)"
  value       = scaleway_instance_ip.publique.address
}

output "connexion_ssh" {
  value = "ssh root@${scaleway_instance_ip.publique.address}"
}
