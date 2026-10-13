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


@app.command()
def version() -> None:
    from gemmw import __version__

    typer.echo(__version__)


if __name__ == "__main__":
    app()
