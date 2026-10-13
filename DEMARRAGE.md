# Mise en ligne, pas à pas (à supprimer une fois fait)

Durée : 1 h 30 à 2 h. Prérequis sur le PC : Git, Python 3.12, uv (`powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`).

1. Dézipper dans `C:\Users\bwane\Desktop\DATA\gemmw-data` (ou ailleurs, sans espace ni accent dans le chemin).
2. Sur github.com, connecté en BiraneWANE : New repository, nom `gemmw-data`, public, **sans** README ni .gitignore ni licence (ils sont déjà là). Create.
3. Dans un terminal, à la racine du dossier :
   ```
   git init -b main
   uv sync --group dev
   uv run pre-commit install
   uv run pytest
   git add .
   git commit -m "Squelette du dépôt : structure, CI, collecte, entrepôt"
   git remote add origin https://github.com/BiraneWANE/gemmw-data.git
   git push -u origin main
   ```
   Au `git commit`, les hooks pre-commit tournent une première fois (ruff, gitleaks) ; s'ils modifient un fichier, refaire `git add .` et `git commit`.
4. Sur GitHub, onglet Actions : le workflow CI doit passer au vert en 1 à 2 minutes. Puis « Collecte hebdomadaire », bouton « Run workflow », pour vérifier que la collecte tourne et dépose son artefact.
5. Onglet Settings → General : décrire le dépôt en une ligne, ajouter les topics `python`, `data-engineering`, `scraping`, `fastapi`, `streamlit`. Épingler le dépôt sur le profil.
6. Relire le README et le mettre dans vos mots. Supprimer ce fichier, commit, push.

Ce qui ne doit JAMAIS être ajouté au dépôt : le `.env`, les PDF des livrets, les exports Payhip/Etsy avec les emails. Le `.gitignore` les bloque, gitleaks vérifie les clés, mais la règle reste la vôtre.
