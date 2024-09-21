import os
from pathlib import Path
import subprocess
import sys
import click
from cookiecutter.main import cookiecutter
from xylo.config import load_config
import multiprocessing
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


TEMPLATES_DIR = Path(__file__).parent / "templates"


class FrontendWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        try:
            if not event.is_directory:
                print(f'Modified: {event.src_path}')
                subprocess.run(['npm', 'run', 'build'], cwd='xylo/frontend')
                print("built")
        except:
            print("Warning: error occurred in frontend watcher")

    def on_created(self, event):
        if not event.is_directory:
            print(f'Created: {event.src_path}')
    
    def on_deleted(self, event):
        if not event.is_directory:
            print(f'Deleted: {event.src_path}')


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
    frontend_process = multiprocessing.Process(target=dev_frontend, args=(), kwargs={})
    frontend_process.start()
    backend_process = multiprocessing.Process(target=dev_backend, args=(), kwargs={})
    backend_process.start()

    # Watch for changes to frontend
    path = "xylo/frontend/src"
    event_handler = FrontendWatcher()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    # Block waiting for the processes.
    try:
        frontend_process.join()
        backend_process.join()
    except KeyboardInterrupt:
        frontend_process.kill()
        backend_process.kill()
        observer.stop()
    observer.join()
    print("Killed background processes.")


def dev_backend():
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

def dev_frontend():
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
    clean_xylo()
    generate_code()
    build_frontend()
    build_backend()


def build_frontend():
    config = load_config("xylo.yaml")
    original_dir = os.getcwd()
    os.chdir("xylo/frontend")
    os.system("npm i")
    os.system("npm run build")
    os.system("npm link")
    os.chdir(original_dir)
    os.chdir(".xylo/frontend")
    os.system("npm i")
    os.system(f"npm link {config.name}-frontend")
    os.system("npm run build")
    os.system("mkdir ../../dist")
    os.system("mv out ../../dist/frontend")
    os.chdir(original_dir)


def build_backend():
    # config = load_config("xylo.yaml")
    # original_dir = os.getcwd()
    os.system("cp -r xylo/backend dist/backend")
    os.system("rm -rf dist/backend/.venv")
    os.system("cp .xylo/backend/server.py dist/backend/src")


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
            f.write(f"export default function {function}GeneratedPage()" + " {\n")
            f.write(f"    return <{function} />;\n")
            f.write("}\n")
    server_file = Path(".xylo") / "backend" / "server.py"
    os.makedirs(server_file.parent, exist_ok=True)
    with open(server_file, 'w') as f:
        f.write("from flask import Flask, request\n")
        f.write("from flask_cors import CORS\n")
        f.write("app = Flask(__name__)\n")
        f.write("CORS(app)\n")
        for name, route in config.routes.items():
            module, function = route.handler.split(":")
            if route.method:
                method_str = f", methods=['{route.method}']"
            else:
                method_str = ""
            f.write(f"import {module}\n")
            f.write(f"@app.route('{route.path}'{method_str})\n")
            f.write(f"def route_{name.replace('-', '_')}():\n")
            f.write(f"    if request.is_json:\n")
            f.write(f"        body = request.get_json()\n")
            f.write(f"    else:\n")
            f.write("        body = {}\n")
            f.write(f"    return {module}.{function}(body)\n")
        f.write("if __name__ == '__main__':\n")
        f.write("    app.run(debug=True)")


def clean_xylo():
    os.system("rm -rf .xylo")
    dot_xylo = str(TEMPLATES_DIR / "{{cookiecutter.name}}" / ".xylo")
    os.system(f"cp -r {dot_xylo} .")


def cli_entrypoint():
    xylo()


@xylo.group()
def run():
    """Run a Xylo app component in production."""


from http.server import HTTPServer, SimpleHTTPRequestHandler

@run.command()
def frontend():
    """Serve frontend static files."""
    if not Path("index.html").exists():
        print("You're not in a valid Xylo frontend build. Please cd to the dist/frontend directory.")
        sys.exit(1)
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Serving on port {server_address[1]}...")
    httpd.serve_forever()

@run.command()
def backend():
    """Run the backend."""
    if not Path("src/server.py").exists():
        print("You're not in a valid Xylo backend build. Please cd to the dist/backend directory.")
        sys.exit(1)
    os.system("poetry install")
    os.system("poetry run python src/server.py")
