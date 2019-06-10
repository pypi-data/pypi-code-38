# -*- coding: utf-8 -*-

"""Console script for glb."""
import sys
import click


@click.group()
def main(args=None):
    """Console script for glb."""
    click.echo(
        f"glb are some quick an easy python scripts for managing some gitlab "
        f"actions that I commonly do"
    )
    click.echo("See click documentation at http://click.pocoo.org/")
    return 0


@main.command()
@click.argument("value")
def token(value):
    """
    set gitlab private token
    """
    # TODO
    import os

    print(os.environ)


@main.command()
@click.argument("attribute")
def clone(attribute):
    """
    attempt to clone all of a groups projects, given a atrribute that is a
     value of one of your group's attributes
    """
    from .glb import my_groups, gid_from_value, clone_group_by_id

    my_groups = my_groups()
    my_groups_json = my_groups.json()
    gid = gid_from_value(attribute, my_groups_json)
    clone_group_by_id(gid)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
