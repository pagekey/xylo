import click


@click.group()
def xylo():
    """Top-level CLI function."""

@xylo.command()
def new():
    print("new")

@xylo.command()
def dev():
    print("dev")

def cli_entrypoint():
    xylo()
