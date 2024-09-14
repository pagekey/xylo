import os
from pathlib import Path
import threading
import click
from cookiecutter.main import cookiecutter
from xylo.config import load_config
import multiprocessing


TEMPLATES_DIR = Path(__file__).parent / "templates"


@click.group()
def xylo():
    """Self-hosted application toolkit."""

@xylo.command()
def new():
    name = input("Name for your app (my-app): ")
    if len(name) < 1:
        name = "my-app"
    cookiecutter(
        str(TEMPLATES_DIR),
        extra_context={"name": name, "name_with_underscores": name.replace("-", "_")},
        no_input=True,
    )
    ignore_file = Path(name) / ".ignore"
    ignore_file.rename(Path(name) / ".gitignore")



@xylo.command()
def dev():
    # check if nextjs app generated yet
    if not Path(".xylo").exists():
        clean_xylo()

    # Start separate processes to manage front/backend.
    frontend_process = multiprocessing.Process(target=run_frontend, args=(), kwargs={})
    frontend_process.start()
    backend_process = multiprocessing.Process(target=run_backend, args=(), kwargs={})
    backend_process.start()

    # Block waiting for the processes.
    try:
        frontend_process.join()
        backend_process.join()
    except KeyboardInterrupt:
        frontend_process.kill()
        backend_process.kill()
    print("Killed background processes.")


def run_backend():
    print("running backend...")
    config = load_config("xylo.yaml")
    original_dir = os.getcwd()
    generate_code()
    if not Path(".xylo/backend/venv").exists():
        os.system("python3 -m venv .xylo/backend/venv")
    os.system(".xylo/backend/venv/bin/pip install pip --upgrade")
    os.system(".xylo/backend/venv/bin/pip install -e xylo/backend")
    os.chdir(".xylo/backend")
    os.system("venv/bin/python3 server.py")

def run_frontend():
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
            f.write('"use client"\n')
            import_stmt = "import {" + function + "}" + f" from '{module}';\n"
            f.write(import_stmt)
            f.write("export default function() {\n")
            f.write(f"    return <{function} />;\n")
            f.write("}\n")
    server_file = Path(".xylo") / "backend" / "server.py"
    os.makedirs(server_file.parent, exist_ok=True)
    with open(server_file, 'w') as f:
        f.write("from flask import Flask\n")
        f.write("from flask_cors import CORS\n")
        f.write("app = Flask(__name__)\n")
        f.write("CORS(app)\n")
        for name, route in config.routes.items():
            module, function = route.handler.split(":")
            f.write(f"from {module} import {function}\n")
            f.write(f"@app.route('{route.path}')\n")
            f.write(f"def route_{name.replace('-', '_')}():\n")
            f.write(f"    return {function}()\n")
        f.write("if __name__ == '__main__':\n")
        f.write("    app.run(debug=True)")


def clean_xylo():
    os.system("rm -rf .xylo")
    dot_xylo = str(TEMPLATES_DIR / "{{cookiecutter.name}}" / ".xylo")
    os.system(f"cp -r {dot_xylo} .")


def cli_entrypoint():
    xylo()
