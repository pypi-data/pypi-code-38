# -*- coding: utf-8 -*-

"""Module providing access to all known dataset definitions."""

from __future__ import absolute_import, division, print_function

import hashlib
import os
import pkg_resources
import py
import textwrap
import yaml

_hashinfo_formatversion = 1


def _load_yml_definitions():
    """
    Read dataset .yml files from definitions/ and hashinfo/ directories.
    This is done once during the module import stage.
    """
    global definition, fileinfo_dirty
    definition = {}
    fileinfo_dirty = set()
    for definition_file in pkg_resources.resource_listdir("dials_data", "definitions"):
        if definition_file.endswith(".yml"):
            dataset_definition = pkg_resources.resource_string(
                "dials_data", "definitions/" + definition_file
            )
            dataset_name = definition_file[:-4]
            definition[dataset_name] = yaml.safe_load(dataset_definition)
            dhash = hashlib.sha256()
            dhash.update(dataset_definition)
            definition[dataset_name]["hash"] = dhash.hexdigest()
            h_file = "hashinfo/" + definition_file
            if not pkg_resources.resource_exists("dials_data", h_file):
                fileinfo_dirty.add(dataset_name)
                continue
            hashinfo = yaml.safe_load(
                pkg_resources.resource_stream("dials_data", h_file)
            )
            if (
                hashinfo["definition"] == definition[dataset_name]["hash"]
                and hashinfo["formatversion"] == _hashinfo_formatversion
            ):
                definition[dataset_name]["hashinfo"] = hashinfo
            else:
                fileinfo_dirty.add(dataset_name)


_load_yml_definitions()


def create_integrity_record(dataset_name):
    """
    Generate a dictionary for the integrity information of a specific dataset.
    """
    return {
        "definition": definition[dataset_name]["hash"],
        "formatversion": _hashinfo_formatversion,
    }


def repository_location():
    """
    Returns an appropriate location where the downloaded regression data should
    be stored.

    In order of evaluation:
    * If the environment variable DIALS_DATA is set and exists or can be
      created then use that location
    * If a Diamond Light Source specific path exists then use that location
    * If the environment variable LIBTBX_BUILD is set and the directory
      'dials_data' exists or can be created underneath that location then
      use that.
    * Use ~/.cache/dials_data if it exists or can be created
    * Otherwise fail with a RuntimeError
    """
    if os.getenv("DIALS_DATA"):
        try:
            repository = py.path.local(os.getenv("DIALS_DATA"))
            repository.ensure(dir=1)
            return repository
        except Exception:
            pass
    try:
        repository = py.path.local("/dls/science/groups/scisoft/DIALS/dials_data")
        if repository.check(dir=1):
            return repository
    except Exception:
        pass
    if os.getenv("LIBTBX_BUILD"):
        try:
            repository = py.path.local(os.getenv("LIBTBX_BUILD")).join("dials_data")
            repository.ensure(dir=1)
            return repository
        except Exception:
            pass
    repository = (
        py.path.local(os.path.expanduser("~")).join(".cache").join("dials_data")
    )
    try:
        repository.ensure(dir=1)
        return repository
    except Exception:
        raise RuntimeError(
            "Could not determine regression data location. Use environment variable DIALS_DATA"
        )


def get_resident_size(ds):
    if ds in fileinfo_dirty:
        return 0
    return sum(item["size"] for item in definition[ds]["hashinfo"]["verify"])


def _human_readable(num, suffix="B"):
    for unit in ("", "k", "M", "G"):
        if num < 10:
            return "%.1f%s%s" % (num, unit, suffix)
        if num < 1024:
            return "%.0f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.0f%s%s" % (num, "T", suffix)


def list_known_definitions(ds_list, quiet=False):
    indent = " " * 4
    for shortname in sorted(ds_list):
        if quiet:
            print(shortname)
            continue
        dataset = definition[shortname]
        if shortname in fileinfo_dirty:
            size_information = "unverified dataset"
        else:
            size_information = _human_readable(get_resident_size(shortname))
        print(
            "{shortname}: {dataset[name]} ({size_information})".format(
                shortname=shortname, dataset=dataset, size_information=size_information
            )
        )
        print(
            "{indent}{author} ({license})".format(
                author=dataset.get("author", "unknown author"),
                indent=indent,
                license=dataset.get("license", "unknown license"),
            )
        )
        if dataset.get("url"):
            print("{indent}{dataset[url]}".format(indent=indent, dataset=dataset))
        print(
            "\n{}\n".format(
                textwrap.fill(
                    dataset["description"],
                    initial_indent=indent,
                    subsequent_indent=indent,
                )
            )
        )
