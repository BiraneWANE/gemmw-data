# Gouvernance des données

## Ce qu'on collecte, et ce qu'on ne collecte pas

**Prix concurrents.** Des pages publiques de boutiques, relevées une fois par semaine avec un User-Agent identifiable et deux secondes entre chaque requête. Aucune donnée personnelle. Le `robots.txt` de chaque site est respecté ; un site qui refuse les robots sort de la liste.

**Ventes.** Les exports Payhip et Etsy contiennent l'email de l'acheteuse. Il ne rentre jamais dans l'entrepôt : à l'import, il est remplacé par un haché SHA-256 salé, qui permet de reconnaître une cliente qui revient sans pouvoir retrouver qui elle est. Le sel est un secret hors dépôt. Les exports bruts restent sur le poste de travail, dans un dossier ignoré par git, et sont supprimés après import.

**Prénoms pour le générateur.** Le prénom de l'enfant arrive par la commande, sert à produire le PDF, et n'est pas conservé au-delà de la commande. Il n'est pas un identifiant.

## Base légale et droits

Gem'MW Éditions traite ces données au titre de l'exécution du contrat de vente (livraison du livret) et de son intérêt légitime (suivi de l'activité). Toute cliente peut demander l'accès, la rectification ou la suppression de ses données à l'adresse indiquée sur la boutique ; la suppression du haché dans l'entrepôt se fait en une requête.

## Conservation

| Donnée | Durée |
|---|---|
| Relevés de prix | Illimitée (données publiques, non personnelles) |
| Ventes dans l'entrepôt (hachées) | 5 ans, obligation comptable |
| Exports bruts avec emails | Supprimés après import |
| Journaux de l'API | 30 jours |
| Conversations avec les assistants | 90 jours, anonymisées |

## Assistants et règlement européen sur l'IA

Les assistants prévus (réponses aux clientes, idées de contenu) sont des usages à risque minimal au sens du règlement européen sur l'intelligence artificielle. Ils s'annoncent comme automatisés, ne prennent aucune décision concernant une personne, et une humaine relit tout message envoyé à une cliente. Chaque modèle utilisé a une fiche (model card) dans `docs/modeles/` indiquant ce sur quoi il a été évalué et ses limites connues.
