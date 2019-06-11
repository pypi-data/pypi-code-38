"""
    {{ angreal._cleaned_name }}.cli
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    {{ angreal._cleaned_name}}'s command line interface

"""

import click


@click.group()
def main():
    """
    The main entry point for {{angreal.name}}
    :return:
    """
    pass


@main.command()
def subcommand():
    """
    This is a sub command on the main entry point group
    :return:
    """
    pass