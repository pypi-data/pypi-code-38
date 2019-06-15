# -*- coding: utf-8 -*-

"""Console script for glb."""
import sys
import click
from .settings import PROJECTS

# from settings import PYTHON_PROJECT_TYPES


@click.group()
def main(args=None):
    """Console script for glb."""
    pass


@main.command()
@click.argument("project")
@click.argument("project_type")
@click.argument("name")
def new(project, project_type, name):
    """
    make a new project
    """
    project = PROJECTS()[project]
    project_type = project["types"][project_type]
    project_type(name)


# @click.group()
# @new.command()
# @click.option("--name", "-n", required=True)
# @click.option("--group", "-g", default=False, show_default=False)
# def project(name, group):
#     pass


# @project.command()
# def python(project_type):
#     print(PYTHON_PROJECT_TYPES[project_type])


@main.command()
@click.argument("value")
def token(value):
    """
    set gitlab private token
    """
    # TODO

    print("TODO")


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
