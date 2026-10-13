"""Point d'entrée : `gemmw <commande>`."""

from pathlib import Path

import typer

from gemmw.collecte import lancer_collecte

app = typer.Typer(help="Outils data de Gem'MW Éditions", no_args_is_help=True)


@app.command()
def collecte(sortie: Path = Path("data/brut")) -> None:  # noqa: B008
    """Relève les prix des livrets concurrents et les écrit dans SORTIE."""
    chemin = lancer_collecte(sortie)
    typer.echo(f"Relevé écrit : {chemin}")


@app.command()
def version() -> None:
    from gemmw import __version__

    typer.echo(__version__)
