-- Historique des prix concurrents : une ligne par produit et par relevé, jamais mise à jour.
CREATE TABLE IF NOT EXISTS releve_prix (
    id          INTEGER PRIMARY KEY,
    releve_le   TEXT NOT NULL,
    site        TEXT NOT NULL,
    titre       TEXT NOT NULL,
    prix_eur    REAL NOT NULL CHECK (prix_eur >= 0),
    url         TEXT NOT NULL,
    format      TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_releve_site_date ON releve_prix (site, releve_le);

-- Ventes Gem'MW, importées des exports Payhip et Etsy. Aucune donnée personnelle :
-- l'acheteuse est réduite à un identifiant haché (voir GOUVERNANCE.md).
CREATE TABLE IF NOT EXISTS vente (
    id              INTEGER PRIMARY KEY,
    plateforme      TEXT NOT NULL CHECK (plateforme IN ('payhip', 'etsy', 'amazon', 'site')),
    commande_ref    TEXT NOT NULL,
    vendue_le       TEXT NOT NULL,
    produit         TEXT NOT NULL,
    prix_ttc_eur    REAL NOT NULL,
    frais_eur       REAL NOT NULL DEFAULT 0,
    tva_eur         REAL NOT NULL DEFAULT 0,
    acheteuse_hash  TEXT NOT NULL,
    pays            TEXT,
    UNIQUE (plateforme, commande_ref)
);
