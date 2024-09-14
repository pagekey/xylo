from pathlib import Path
import click
from cookiecutter.main import cookiecutter

@click.group()
def xylo():
    """Top-level CLI function."""

@xylo.command()
def new():
    print("new")
    templates_dir = Path(__file__).parent / "templates"
    cookiecutter(str(templates_dir))

@xylo.command()
def dev():
    print("dev")

@xylo.command()
def build():
    print("build")

def cli_entrypoint():
    xylo()
