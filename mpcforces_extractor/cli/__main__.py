import typer
from mpcforces_extractor.cli.extract import extractor_cmd
from mpcforces_extractor.cli.visualize import visualize_cmd

app = typer.Typer(no_args_is_help=True)
app.add_typer(extractor_cmd)
app.add_typer(visualize_cmd)

if __name__ == "__main__":
    app()
