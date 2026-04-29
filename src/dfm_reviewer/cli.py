import typer

app = typer.Typer(help="Mechanical DFM review workbench.")


@app.callback()
def main() -> None:
    """Run the Mechanical DFM reviewer CLI."""
