import os
from pathlib import Path
import click
from cookiecutter.main import cookiecutter
from xylo.config import load_config


TEMPLATES_DIR = Path(__file__).parent / "templates"


@click.group()
def xylo():
    """Top-level CLI function."""

@xylo.command()
def new():
    name = input("Name for your app (my-app): ")
    if len(name) < 1:
        name = "my-app"
    cookiecutter(
        str(TEMPLATES_DIR),
        extra_context={"name": name},
        no_input=True,
    )
    ignore_file = Path(name) / ".ignore"
    ignore_file.rename(Path(name) / ".gitignore")



@xylo.command()
def dev():
    # check if nextjs app generated yet
    config = load_config("xylo.yaml")
    print("Config: ",config)
    if not Path(".xylo").exists():
        clean_xylo()
    original_dir = os.getcwd()
    os.chdir("xylo/frontend")
    os.system("npm i")
    os.system("npm run build")
    os.system("npm link")
    os.chdir(original_dir)
    os.chdir(".xylo/frontend")
    if not Path("node_modules").exists():
        os.system("npm i")
    os.system(f"npm link {config.name}-frontend")
    os.system("npm run dev")
    os.chdir(original_dir)

@xylo.command()
def build():
    print("build")

@xylo.command()
def clean():
    clean_xylo()

def clean_xylo():
    os.system("rm -rf .xylo")
    dot_xylo = str(TEMPLATES_DIR / "{{cookiecutter.name}}" / ".xylo")
    os.system(f"cp -r {dot_xylo} .")


def cli_entrypoint():
    xylo()
