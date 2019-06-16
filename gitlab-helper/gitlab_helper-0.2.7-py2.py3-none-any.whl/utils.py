# -*- coding: utf-8 -*-

from git import Repo
from git.exc import InvalidGitRepositoryError
import os
import requests
from cookiecutter.main import cookiecutter


def with_auth(func, *args, **kwargs):
    """
    wrap a function that requires a token with_auth to raise token errors if
    misconfigured
    """

    def wrapper(*args, **kwargs):
        from .settings import GITLAB_TOKEN
        from .exceptions import TokenError

        if not GITLAB_TOKEN:
            raise TokenError(
                f"Token hasn't been defined, make sure that you set the "
                f"GITLAB_PRIVATE_TOKEN environment variable"
            )
        return func(*args, **kwargs)

    return wrapper


def is_git_repo(path):
    """
    is this directory a git repo?
    """
    try:
        Repo(path).git_dir
        return True
    except InvalidGitRepositoryError:
        return False


def clone_group_by_id(gid: int):
    from .settings import gl

    projects = gl.groups.get(gid).projects.list()
    cwd = os.getcwd() + "/"
    [Repo.clone_from(p.ssh_url_to_repo, cwd + p.name) for p in projects]


@with_auth
def my_groups():
    """
    owned defaults to true because normally searching for my own groups
    """
    from .settings import GITLAB_API_BASE_URL, GITLAB_AUTH_HEADER

    search_url = GITLAB_API_BASE_URL + "groups"
    r = requests.get(search_url, headers=GITLAB_AUTH_HEADER)
    r.raise_for_status()
    return r


def add_new_repo(directory: str) -> Repo:
    """
    creates new repo in directory and adds all files as initial commit if one
    doesn't exists. if an exisiting repo is found, returns that repo
    """
    repo_path = os.getcwd() + "/" + directory

    if is_git_repo(repo_path):
        repo = Repo(repo_path)
    else:
        repo = Repo.init(repo_path)
    return repo


def create_project(name: str):
    """
    create project on gitlab
    """
    from .settings import gl

    return gl.projects.create({"name": name})


def add_new_project(name: str, group):
    """
    add a new project to gitlab
    """
    if group:
        print("-g flag not implemented")
        return
    return create_project(name)


@with_auth
def new_cli_project_repo(name: str):
    project = create_project(name)
    cwd = os.getcwd() + "/"
    repo = Repo.init(os.path.join(cwd, name))
    repo.create_remote("origin", project.ssh_url_to_repo)
    files = repo.untracked_files  # retrieve a list of untracked files
    print(files)

    repo.index.add(files)
    repo.index.commit("init")
    repo.git.push("origin", "master")


def new_cli_project(name):
    cookiecutter(
        "https://github.com/audreyr/cookiecutter-pypackage.git",
        no_input=True,
        extra_context={
            "full_name": "Robert Wendt",
            "email": "rwendt1337@gmail.com",
            "github_username": "reedrichards",
            "project_name": name,
            "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '_').replace('-', '_') }}",  # noqa: E501
            "project_short_description": "",
            "pypi_username": "{{ cookiecutter.github_username }}",
            "version": "0.1.0",
            "use_pytest": "y",
            "use_pypi_deployment_with_travis": "n",
            "add_pyup_badge": "n",
            "command_line_interface": "Click",
            "create_author_file": "y",
            "open_source_license": "BSD license",
        },
    )
    new_cli_project_repo(name)


def gid_from_value(attribute: str, groups: list) -> int:
    """Exract the group id from a list of groups whose values match an attribute


    Args:
        attribute (str): the value to match on.
        groups (list): list of groups to match on

    Returns:
        int: when group is found, otherwise, raises and exception
    """
    from .exceptions import GroupNotFound

    for group in groups:
        if attribute in group.values():
            return group["id"]
    raise GroupNotFound(
        f"No groups in {groups} found with attribute containing {attribute}"
    )
