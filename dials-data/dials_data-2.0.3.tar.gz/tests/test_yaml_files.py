# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import pkg_resources
import pytest
import string
import yaml

definition_yamls = {
    fn
    for fn in pkg_resources.resource_listdir("dials_data", "definitions")
    if fn.endswith(".yml")
}
hashinfo_yamls = {
    fn
    for fn in pkg_resources.resource_listdir("dials_data", "hashinfo")
    if fn.endswith(".yml")
}


def is_valid_name(filename):
    if not filename.endswith(".yml") or len(filename) <= 4:
        return False
    allowed_characters = frozenset(string.ascii_letters + string.digits + "_")
    return all(c in allowed_characters for c in filename[:-4])


@pytest.mark.parametrize("yaml_file", definition_yamls)
def test_yaml_file_is_valid_definition(yaml_file):
    assert is_valid_name(yaml_file)
    definition = yaml.safe_load(
        pkg_resources.resource_stream("dials_data", "definitions/" + yaml_file).read()
    )
    fields = set(definition)
    required = set(("name", "data", "description"))
    optional = set(("license", "url", "author"))
    assert fields >= required, "Required fields missing: " + str(
        sorted(required - fields)
    )
    assert fields <= (required | optional), "Unknown fields present: " + str(
        sorted(fields - required - optional)
    )


@pytest.mark.parametrize("yaml_file", hashinfo_yamls)
def test_yaml_file_is_valid_hashinfo(yaml_file):
    assert is_valid_name(yaml_file)
    assert (
        yaml_file in definition_yamls
    ), "hashinfo file present without corresponding definition file"
    hashinfo = yaml.safe_load(
        pkg_resources.resource_stream("dials_data", "hashinfo/" + yaml_file).read()
    )
    fields = set(hashinfo)
    required = set(("definition", "formatversion", "verify"))
    assert fields >= required, "Required fields missing: " + str(
        sorted(required - fields)
    )
    assert fields <= required, "Unknown fields present: " + str(
        sorted(fields - required)
    )
