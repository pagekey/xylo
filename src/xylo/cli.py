from pathlib import Path
import click


@click.group()
def xylo():
    """Top-level CLI function."""

@xylo.command()
def new():
    print("new")
    templates = Path(__file__).parent / "templates" / "frontend"
    for file in templates.iterdir():
        print(file)

@xylo.command()
def dev():
    print("dev")

@xylo.command()
def build():
    print("build")

def cli_entrypoint():
    xylo()
