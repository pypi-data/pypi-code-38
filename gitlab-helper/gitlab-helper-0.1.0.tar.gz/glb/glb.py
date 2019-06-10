# -*- coding: utf-8 -*-

"""Main module."""
from git import Repo
import os
import requests
from .exceptions import TokenError, GroupNotFound

from .settings import gl, GITLAB_API_BASE_URL, GITLAB_AUTH_HEADER


def with_auth(func):
    """
    wrap a function that requires a token with_auth to raise token errors if
    misconfigured
    """

    def wrapper():
        from .settings import GITLAB_TOKEN

        if not GITLAB_TOKEN:
            raise TokenError(
                f"Token hasn't been defined, make sure that you set the "
                f"GITLAB_PRIVATE_TOKEN environment variable"
            )
        return func()

    return wrapper


def clone_group_by_id(gid: int):
    projects = gl.groups.get(gid).projects.list()
    cwd = os.getcwd() + "/"
    [Repo.clone_from(p.ssh_url_to_repo, cwd + p.name) for p in projects]


@with_auth
def my_groups():
    """
    owned defaults to true because normally searching for my own groups
    """

    search_url = GITLAB_API_BASE_URL + "groups"
    r = requests.get(search_url, headers=GITLAB_AUTH_HEADER)
    r.raise_for_status()
    return r


def gid_from_value(attribute: str, groups: list) -> int:
    """Exract the group id from a list of groups whose values match an attribute


    Args:
        attribute (str): the value to match on.
        groups (list): list of groups to match on

    Returns:
        int: when group is found, otherwise, raises and exception
    """
    for group in groups:
        if attribute in group.values():
            return group["id"]
    raise GroupNotFound(
        f"No groups in {groups} found with attribute containing {attribute}"
    )
