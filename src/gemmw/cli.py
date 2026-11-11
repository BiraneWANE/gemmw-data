"""Point d'entrée : `gemmw <commande>`."""

import logging
from pathlib import Path

import typer

from gemmw.collecte import lancer_collecte

app = typer.Typer(help="Outils data de Gem'MW Éditions", no_args_is_help=True)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s : %(message)s")


@app.command()
def collecte(sortie: Path = Path("data/brut")) -> None:  # noqa: B008
    """Relève les prix des livrets concurrents et les écrit dans SORTIE."""
    chemin = lancer_collecte(sortie)
    typer.echo(f"Relevé écrit : {chemin}")


@app.command()
def importer(
    fichier: Path,
    plateforme: str = typer.Option(..., help="payhip ou etsy"),
    verifier_seulement: bool = typer.Option(False, help="Contrôler sans charger"),
) -> None:
    """Importe un export CSV de ventes dans l'entrepôt, après contrôles d'entrée."""
    from gemmw.config import settings
    from gemmw.entrepot import ouvrir
    from gemmw.entrepot.controles import controler, tout_passe
    from gemmw.entrepot.ventes import LECTEURS, charger

    if not settings.sel_acheteuses:
        typer.echo("GEMMW_SEL_ACHETEUSES manquant dans .env : impossible de hacher les emails.")
        raise typer.Exit(code=2)
    if plateforme not in LECTEURS:
        typer.echo(f"Plateforme inconnue : {plateforme}. Choix : {', '.join(LECTEURS)}")
        raise typer.Exit(code=2)
    ventes = LECTEURS[plateforme](fichier, settings.sel_acheteuses)
    resultats = controler(ventes)
    for r in resultats:
        typer.echo(
            f"  {'ok ' if r.succes else 'KO '} {r.attente}"
            + (f" ({r.detail})" if r.detail and not r.succes else "")
        )
    if not tout_passe(resultats):
        typer.echo("Contrôles en échec : rien n'a été chargé.")
        raise typer.Exit(code=1)
    if verifier_seulement:
        typer.echo(f"{len(ventes)} vente(s) valides, non chargées (vérification seulement).")
        return
    rapport = charger(ouvrir(settings.db_path), ventes, plateforme)
    typer.echo(
        f"{rapport.plateforme} : {rapport.lues} lues, {rapport.inserees} nouvelles, "
        f"{rapport.ignorees} déjà connues."
    )


@app.command("controle-releve")
def controle_releve(fichier: Path) -> None:
    """Contrôle la qualité d'un relevé de prix. Code de sortie 1 si un contrôle échoue."""
    from gemmw.collecte.qualite import controler_releve, lire_releve, tout_passe
    from gemmw.collecte.sites import SITES

    resultats = controler_releve(lire_releve(fichier), tuple(s.nom for s in SITES))
    for r in resultats:
        typer.echo(
            f"  {'ok ' if r.succes else 'KO '} {r.attente}" + ("" if r.succes else f" ({r.detail})")
        )
    if not tout_passe(resultats):
        raise typer.Exit(code=1)


@app.command()
def alerte(
    fichier: Path,
    precedent: Path | None = typer.Option(  # noqa: B008
        None, help="Relevé de référence (sinon le plus récent du dossier)"
    ),
    resume: Path | None = typer.Option(  # noqa: B008
        None, help="Fichier où ajouter le rapport (ex. $GITHUB_STEP_SUMMARY)"
    ),
    telegram: bool = typer.Option(False, help="Envoyer le rapport sur Telegram si configuré"),
) -> None:
    """Compare un relevé au précédent et écrit ce qui a changé chez les concurrents."""
    from gemmw.collecte.alerte import comparer, en_texte, envoyer_telegram, releve_precedent
    from gemmw.collecte.qualite import lire_releve
    from gemmw.config import settings

    reference = precedent or releve_precedent(fichier.parent, fichier)
    if reference is None:
        typer.echo("Aucun relevé précédent : première collecte, pas de comparaison.")
        return
    rapport = comparer(lire_releve(reference), lire_releve(fichier))
    texte = en_texte(rapport)
    typer.echo(texte)
    if resume:
        with resume.open("a", encoding="utf-8") as f:
            f.write("\n" + texte + "\n")
    if telegram and not rapport.vide:
        if settings.telegram_bot_token and settings.telegram_chat_id:
            envoyer_telegram(texte, settings.telegram_bot_token, settings.telegram_chat_id)
            typer.echo("Rapport envoyé sur Telegram.")
        else:
            typer.echo("Telegram non configuré : rapport non envoyé.")


@app.command()
def generer(livret: Path, prenom: str, sortie: Path | None = None) -> None:  # noqa: B008
    """Écrit le prénom à la place des repères PRENOM d'un livret (test en local)."""
    from gemmw.api.generateur import PrenomInvalide, compter_reperes, personnaliser

    source = livret.read_bytes()
    if compter_reperes(source) == 0:
        typer.echo("Aucun repère PRENOM dans ce livret.")
        raise typer.Exit(1)
    try:
        pdf = personnaliser(source, prenom)
    except PrenomInvalide as e:
        typer.echo(f"Prénom refusé : {e}")
        raise typer.Exit(2) from e
    cible = sortie or livret.with_name(f"{livret.stem}_{prenom.strip().lower()}.pdf")
    cible.write_bytes(pdf)
    typer.echo(f"Livret écrit : {cible}")


@app.command()
def version() -> None:
    from gemmw import __version__

    typer.echo(__version__)


if __name__ == "__main__":
    app()
