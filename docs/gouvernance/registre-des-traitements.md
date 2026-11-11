# Registre des traitements

Tenu au titre de l'article 30 du RGPD. Le responsable du traitement est l'éditrice de la boutique (entreprise individuelle) ; le développeur agit pour son compte. Les coordonnées complètes figurent dans les mentions légales de la boutique, pas dans ce dépôt public.

Une précision de vocabulaire qui compte : un email haché avec un sel secret est une donnée **pseudonymisée**, pas anonyme. Celui qui détient le sel peut refaire le lien ; le RGPD continue donc de s'appliquer à la table `vente`, avec moins de risque.

## T1. Vente des livrets sur la boutique

| Rubrique | Contenu |
|---|---|
| Finalité | Encaisser la commande, livrer le PDF, envoyer la confirmation |
| Base légale | Exécution du contrat ; obligation légale pour les pièces comptables |
| Personnes | Acheteuses |
| Données | Prénom, nom, email, pays, contenu et montant de la commande, date de renonciation à la rétractation |
| Où | Base WooCommerce chez l'hébergeur (France). Hors de ce dépôt |
| Destinataires | Hébergeur ; Stripe et PayPal pour le paiement, responsables de leurs propres données bancaires |
| Transferts hors UE | Possibles chez Stripe et PayPal, encadrés par les clauses contractuelles types |
| Durée | 10 ans pour les pièces comptables (Code de commerce, L123-22) |
| Sécurité | HTTPS, accès administrateur nominatif, téléchargements servis par le serveur sans adresse publique du fichier |

## T2. Entrepôt d'analyse des ventes (ce dépôt)

| Rubrique | Contenu |
|---|---|
| Finalité | Suivre les ventes par plateforme, calculer la marge nette, mesurer l'effet des publications |
| Base légale | Intérêt légitime (pilotage de l'activité) |
| Personnes | Acheteuses Payhip, Etsy, boutique |
| Données | Identifiant pseudonymisé (SHA-256 salé de l'email), pays, produit, montants, date |
| Où | Fichier SQLite local, ignoré par git (`*.db`) |
| Minimisation | L'email n'entre jamais dans l'entrepôt ; l'export brut est supprimé après import |
| Durée | 5 ans, puis suppression des lignes |
| Sécurité | Sel stocké dans `.env`, jamais commité ; gitleaks en pre-commit ; contrôles d'entrée avant chargement |

## T3. Veille des prix concurrents

| Rubrique | Contenu |
|---|---|
| Finalité | Situer les prix de la boutique |
| Données | Titres, prix et adresses de pages produits publiques. Aucune donnée personnelle |
| Règles | `robots.txt` respecté, User-Agent identifiable, deux secondes entre deux requêtes |
| Durée | Illimitée (données publiques non personnelles) |

## T4. Générateur au prénom

| Rubrique | Contenu |
|---|---|
| Finalité | Produire un exemplaire du livret au prénom de l'enfant |
| Base légale | Exécution du contrat |
| Personnes | Enfants des acheteuses : données de mineurs, d'où une minimisation stricte |
| Données | Le prénom seul, sans âge, sans photo |
| Durée | Le générateur ne garde rien : ni le prénom, ni le PDF, ni trace dans ses journaux. La boutique garde le PDF personnalisé 30 jours (le temps du lien de téléchargement, 5 téléchargements au plus), puis l'efface chaque nuit. Le prénom reste dans la commande, avec la même durée que la commande (T1) |
| Sécurité | Appel en HTTPS avec une clé partagée, connue seulement du site et du serveur. Fichiers rangés dans un dossier fermé au public, servis par un lien signé avec la clé de la commande |

## T5. Formulaire de contact

| Rubrique | Contenu |
|---|---|
| Finalité | Répondre aux questions |
| Base légale | Intérêt légitime |
| Données | Prénom, email, message |
| Où | Boîte mail de la boutique, rien n'est stocké sur le site |
| Durée | 3 ans après le dernier échange |

## T6. Lettre d'information (à venir)

| Rubrique | Contenu |
|---|---|
| Finalité | Annoncer les nouveaux livrets |
| Base légale | **Consentement** : case non pré-cochée, désinscription en un clic dans chaque envoi |
| Données | Email, date et preuve du consentement |
| Durée | 3 ans après le dernier contact actif |
