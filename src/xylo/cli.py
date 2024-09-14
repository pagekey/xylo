import os
from pathlib import Path
import click
from cookiecutter.main import cookiecutter

@click.group()
def xylo():
    """Top-level CLI function."""

@xylo.command()
def new():
    templates_dir = Path(__file__).parent / "templates"
    name = input("Name for your app (my-app): ")
    if len(name) < 1:
        name = "my-app"
    cookiecutter(
        str(templates_dir),
        extra_context={"name": name},
        no_input=True,
    )
    ignore_file = Path(name) / ".ignore"
    ignore_file.rename(Path(name) / ".gitignore")



@xylo.command()
def dev():
    # check if nextjs app generated yet
    os.chdir(".xylo/frontend")
    if not Path("node_modules").exists():
        os.system("npm i")
    os.system("npm run dev")
    os.chdir("../..")

@xylo.command()
def build():
    print("build")

def cli_entrypoint():
    xylo()
