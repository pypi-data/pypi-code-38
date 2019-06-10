
import click
import yaml

from .generate import generate_menu


def generate_digest(items):
    for i in items:
        if isinstance(i, str):
            yield from generate_menu(i)
        elif isinstance(i, dict):
            yield from generate_menu(**i)
        else:
            raise ValueError("Item should be either string or dict")


@click.command()
@click.argument("config", type=click.File())
def print_digest(config):
    """
    Print digest of daily menus for a list of places configured in a YAML file.
    """
    c = yaml.safe_load(config)
    menu = c.get("menu", [])
    for line in generate_digest(menu):
        print(line)
