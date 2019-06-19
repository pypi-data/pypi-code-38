#!/usr/bin/python3

"""
The main module for devpipeline_git (a dev-pipeline plugin).  It provides git
support to dev-pipeline, and exposes the make_git function to create an Scm
that supports git.
"""


def _check_missing_value(configuration, key, error_fn):
    for name, component in configuration.items():
        if component.get("scm.tool") == "git":
            if key not in component:
                error_fn("{} doesn't specify {}".format(name, key))


def _check_missing_uri(configuration, error_fn):
    _check_missing_value(configuration, "git.uri", error_fn)


def _check_missing_revision(configuration, error_fn):
    _check_missing_value(configuration, "git.revision", error_fn)


_MAJOR = 0
_MINOR = 4
_PATCH = 3

_STRING = "{}.{}.{}".format(_MAJOR, _MINOR, _PATCH)
