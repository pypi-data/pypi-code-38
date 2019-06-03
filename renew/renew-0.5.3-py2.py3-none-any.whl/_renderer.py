import os
import re

import six

PY_IDENTIFIER_VALIDATOR = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE)
PY_FILE_HEADER = """\
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file has been created with renew.
# A py-pickling tool: https://pypi.org/project/renew/

"""


def validate_output_path(output_file_path):
    target_dir = os.path.dirname(output_file_path)
    if not os.path.isdir(target_dir):
        raise ValueError("Target dir does not exist: {}".format(target_dir))


def validate_objects(objects):
    for i, item in enumerate(objects):
        if not isinstance(item, tuple):
            msg = "Expecting item number {} to be tuple, got {}."
            raise TypeError(msg.format(i, type(item).__name__))
        if len(item) != 2:
            raise TypeError("Expecting tuples with two items, got {} at item number {}".format(len(item), i))
        name, obj = item
        if not isinstance(name, six.string_types):
            msg = "Expecting first item in tuple to be a string, got {} at item number {}"
            raise TypeError(msg.format(type(name).__name__, i))
        if not PY_IDENTIFIER_VALIDATOR.match(name):
            raise ValueError("{} is not a valid python identifier - given at item number {}".format(name, i))


def validate_dependency(dependency):
    fail_msg = "Expecting string or tuple with two string items, got {}."
    assert isinstance(dependency, tuple), fail_msg.format(type(dependency).__name__)
    assert len(dependency) == 2, fail_msg.format("tuple with {} items.".format(len(dependency)))

    cannot_be_empty = "Dependency cannot be an empty string."
    source, name = dependency
    if source is not None:
        assert isinstance(source, six.string_types), fail_msg.format("source of type {}".format(type(source)))
        assert source, cannot_be_empty + " Got empty source."

    assert isinstance(name, six.string_types), fail_msg.format("name of type {}".format(type(source)))
    assert name, cannot_be_empty + " Got empty namespace."


def build_imports(dependencies):
    if not dependencies:
        return ""

    def make_statement(src, namespace):
        if src:
            return "from {} import {}\n".format(src, namespace)
        else:
            return "import {}\n".format(namespace)

    return "".join(make_statement(*d) for d in sorted(dependencies, key=lambda x: x[0] or x[1])) + "\n"
