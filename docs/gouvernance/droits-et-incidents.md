# Droits des personnes et incidents

## Une cliente exerce ses droits

1. La demande arrive par l'adresse de contact de la boutique. Réponse sous un mois au plus (article 12 du RGPD).
2. Accès ou rectification : on lui transmet ce que la boutique détient sur elle (commande, email).
3. Effacement : on supprime ce qui n'est pas soumis à une obligation légale. Les factures restent 10 ans, mais dans l'entrepôt d'analyse on retrouve ses lignes en recalculant le haché de son email avec le sel, puis on les supprime :

```sql
DELETE FROM vente WHERE acheteuse_hash = :hash;
```

4. On note la date de la demande et de la réponse, sans recopier les données.

## Une fuite ou une perte de données

1. Contenir : révoquer le secret ou l'accès en cause, couper le service si besoin.
2. Évaluer : quelles données, combien de personnes, quel risque pour elles.
3. Notifier la CNIL sous 72 heures si la fuite présente un risque pour les personnes (article 33). Prévenir les personnes elles-mêmes si le risque est élevé (article 34).
4. Documenter l'incident dans `docs/decisions/`, même s'il n'est pas notifié : ce qui s'est passé, ce qui a été fait, ce qui change.

Rappel de ce que ce dépôt ne contient jamais : emails, exports bruts, PDF vendus, sel de hachage, clés d'API.
