import typer
from mpcforces_extractor.cli.extract import extractor_cmd

app = typer.Typer(no_args_is_help=True)
app.add_typer(extractor_cmd)

if __name__ == "__main__":
    app()
