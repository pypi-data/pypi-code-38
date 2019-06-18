# -*- coding: utf-8 -*-

"""Main module."""

import requests
from packaging import version


def get_versions(package_name):
    r = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    try:
        versions = [version.parse(k) for k in r.json()['releases'].keys()]
    except KeyError:
        return []
    return versions
