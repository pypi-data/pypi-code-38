#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cli command for gitlab_helper

These are the command, flags and arguements invoked by `glb`

Example:


        $ glb version

`main` is the entry point for all of the functions

Attributes:

    PROJECTS: ``dict``

used for flow control for the function to be run when creating a new project

   ADD_METHOD: ``dict``

used as flow control to get the function for `glb add` to add a project to
either new or existing repo

Todo:
    * better coverage
    * You have to also use ``sphinx.ext.todo`` extension
"""
import sys
import click

from .main import new_cli_project, add_new_project


PROJECTS: dict = {
    "python": {
        "types": {
            "cli": new_cli_project,
            "package": "package",
            "django": "django",
            "django-app": "django-app",
        }
    }
}

ADD_METHOD: dict = {"new": add_new_project, "existing": "existing project"}


@click.group()
def main(args=None):
    """Console script for glb."""
    pass


@main.command()
def version():
    """
    print the current version of gitlab-helper
    """
    from .__init__ import __version__

    print(__version__)


@main.command()
@click.argument("method")
@click.argument("name")
@click.argument("directory", default=".")
@click.option(
    "--replace-origin/--no-replace-origin",
    " -r/-R",
    default=True,
    show_default=False,
    help=(
        f"replace the orgin of the git repository with gitlab project repo "
        "url, defaults to being true"
    ),
)
@click.option(
    "--group",
    "-g",
    default=False,
    show_default=False,
    help="group to add/find project",
)
def add(method, name, directory, replace_origin, group):
    """
    add a  git repo to gitlab

    USAGE:

    add current directory to a new gitlab project named hello world

    \b
        glb add new hello-world .

    add current directory to a existing gitlab project named hello world

    \b
       glb add existing hello-world .

    """
    from .main import add_new_repo

    if group:
        print("group flag not implemented yet")
        return

    method_func = ADD_METHOD[method]
    project = method_func(name, group)
    repo = add_new_repo(directory)

    if not replace_origin:
        print("-R and --no-replace-origin not implemented yet")
        return

    repo.create_remote("origin", project.ssh_url_to_repo)
    files = repo.untracked_files  # retrieve a list of untracked files
    print(files)
    repo.index.add(files)
    repo.index.commit("init")
    repo.git.push("origin", "master")


@main.command()
@click.argument("project")
@click.argument("project_type")
@click.argument("name")
def new(project, project_type, name):
    """
    make a new project
    """
    project = PROJECTS[project]
    project_type = project["types"][project_type]
    project_type(name)
    return 0


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
    from .utils import my_groups, gid_from_value, clone_group_by_id

    my_groups = my_groups()
    my_groups_json = my_groups.json()
    gid = gid_from_value(attribute, my_groups_json)
    clone_group_by_id(gid)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
