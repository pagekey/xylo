import os
from pathlib import Path
import threading
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
    if not Path(".xylo").exists():
        clean_xylo()
    t1 = threading.Thread(target=frontend_thread, args=())
    t1.start()

    t2 = threading.Thread(target=backend_thread, args=())
    t2.start()

    t1.join()
    t2.join()


def backend_thread():
    print("running backend...")

def frontend_thread():
    config = load_config("xylo.yaml")
    original_dir = os.getcwd()
    generate_code()
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


def generate_code():
    config = load_config("xylo.yaml")
    for name, page in config.pages.items():
        page_file = Path(".xylo") / "frontend" / "app" / Path("./" + page.path) / "page.tsx"
        os.makedirs(page_file.parent, exist_ok=True)
        with open(page_file, 'w') as f:
            module, function = page.component.split(":")
            import_stmt = "import {" + function + "}" + f" from '{module}';\n"
            f.write(import_stmt)
            f.write("export default function() {\n")
            f.write(f"    return <{function} />;\n")
            f.write("}\n")


def clean_xylo():
    os.system("rm -rf .xylo")
    dot_xylo = str(TEMPLATES_DIR / "{{cookiecutter.name}}" / ".xylo")
    os.system(f"cp -r {dot_xylo} .")


def cli_entrypoint():
    xylo()
