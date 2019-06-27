from __future__ import print_function

import os

from setuptools_scm.version import guess_next_simple_semver

SEMVER_MINOR = 2
SEMVER_PATCH = 3
SEMVER_LEN = 3


def format_next_version(
    guess_next, version=None, fmt="{guessed}-beta.{distance}", **kw
):
    guessed = guess_next(version.tag, **kw)
    branch = os.environ.get("BRANCH_NAME", version.branch)

    if branch == "master":
        fmt = "{guessed}"
    elif branch == "release":
        fmt = "{guessed}-rc.{distance}"
    elif branch.startswith("feature"):
        fmt = "{guessed}-alpha.{distance}"
    elif branch.startswith("PR"):
        target_branch = os.environ.get("CHANGE_TARGET")

        if target_branch == "master":
            fmt = "{guessed}"
        elif target_branch == "release":
            fmt = "{guessed}-rc.{distance}"
        elif target_branch == "develop":
            fmt = "{guessed}-alpha.{distance}"

    return version.format_with(fmt, guessed=guessed)


def get_local_empty(version):
    return ""


def guess_next_semver_version(version):
    if version.exact:
        return guess_next_simple_semver(version.tag, retain=SEMVER_LEN, increment=False)
    else:
        if version.branch is not None and "feature" in version.branch:
            return format_next_version(
                guess_next_simple_semver, version=version, retain=SEMVER_MINOR
            )
        else:
            return format_next_version(
                guess_next_simple_semver, version=version, retain=SEMVER_PATCH
            )
