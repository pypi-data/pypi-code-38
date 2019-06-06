# encoding: utf-8
from __future__ import absolute_import, division, print_function

import fnmatch
import glob
import os.path
from collections import namedtuple
from functools import partial

from datapool.data_conversion import SUPPORTED_EXTENSIONS
from datapool.utils import iter_to_list
from datapool.yaml_stuff import load_yaml_and_bunchify

"""this module holds the configuration of the folder structure of the landing zone and
corresponding functions.

All modifications to the landing zone structure should be implemented here to have one
single point of configuration.

"""

site_pattern = "sites/*/site.yaml"
images_pattern = "sites/*/images/*.*"
parameters_yaml = "data/parameters.yaml"
source_type_pattern = "data/*/source_type.yaml"
source_pattern = "data/*/*/source.yaml"

scripts_pattern = "data/*/*/conversion.*"

source_type_based_scripts_pattern = "data/*/conversion.*"

raw_file_pattern = "data/*/*/raw_data/data*.raw"
source_type_related_raw_file_pattern = "data/*/raw_data/data*.raw"


all_file_patterns = [
    site_pattern,
    images_pattern,
    parameters_yaml,
    source_type_pattern,
    source_pattern,
    scripts_pattern,
    raw_file_pattern,
    source_type_based_scripts_pattern,
    source_type_related_raw_file_pattern,
]

tracking_sub_folder = "tracking"


lock_file = ".write_lock"

Handler = namedtuple("Handler", ["parser", "checker", "committer"])


def is_within_source_folder(path_of_file):

    d = os.path.dirname

    # we go three levels up first, so if we are in a source_type folder we are
    # already above "data":
    parent_parent = d(d(d(path_of_file)))

    while parent_parent != os.path.sep and parent_parent != "":
        if os.path.basename(parent_parent) == "data":
            return True
        parent_parent = d(parent_parent)
    return False


def relative_path_for_yaml(what, presets):
    try:
        if what == "site.yaml":
            return site_pattern.replace("*", presets["name"])
        elif what == "parameters.yaml":
            return parameters_yaml
        elif what == "source_type.yaml":
            return source_type_pattern.replace("*", presets["name"])
        elif what == "source.yaml":
            return source_pattern.replace("*", "{}").format(
                presets["source_type"], presets["name"]
            )
        raise NotImplementedError(what)
    except KeyError:
        return None


def ordered_fnmatch_patterns_for_update():
    """ordered list of glob patterns. order is important

    1. images
    2. sites
    3. source_types
    4. sources
    6. conversion scripts
    5. raw data
    """

    yield "."
    yield "sites"
    yield "sites/*"
    yield "sites/*/images/*"

    for pattern, __ in config():
        yield pattern

    yield "data/*/*"
    yield "data/*"
    yield "data"

    for extension in sorted(SUPPORTED_EXTENSIONS):
        yield "data/*/*/conversion{}".format(extension)

    yield "data/*/*/raw_data"
    yield "data/*/*/raw_data/data-*.raw"


def required_folders(root_folder):
    j = partial(os.path.join, root_folder)
    yield j("sites")
    yield j("data")

    # source types
    for folder in glob.glob(j("data", "*")):
        if os.path.isdir(folder):
            scripts = [f for f in os.listdir(folder) if f.startswith("conversion")]
            if scripts:
                yield os.path.join(folder, "raw_data")

    # sources
    for folder in glob.glob(j("data", "*", "*")):
        if os.path.isdir(folder):
            scripts = [f for f in os.listdir(folder) if f.startswith("conversion")]
            if scripts:
                yield os.path.join(folder, "raw_data")


def config():
    from .yaml_parsers import (
        parse_parameters,
        parse_site,
        parse_source_type,
        parse_source,
    )

    """
    order of file patterns matches !
    """

    from .site_and_picture_model import check, check_and_commit

    yield site_pattern, Handler(parse_site, check, check_and_commit)

    from .parameters_model import check, check_and_commit

    yield parameters_yaml, Handler(parse_parameters, check, check_and_commit)

    from .source_type_model import check, check_and_commit

    yield source_type_pattern, Handler(parse_source_type, check, check_and_commit)

    from .source_model import check, check_and_commit

    yield source_pattern, Handler(parse_source, check, check_and_commit)


def raw_file_pattern_for_script(script_path):
    folder = os.path.dirname(script_path)
    return os.path.join(folder, "raw_data", "data-*.raw")


def script_paths_for_raw_file(raw_file_path):
    folder = os.path.dirname(raw_file_path)
    parent_folder, __ = os.path.split(folder)
    pattern = os.path.join(parent_folder, "conversion.*")
    return glob.glob(pattern)


def source_yaml_path_for_script(script_path):
    folder = os.path.dirname(script_path)
    return os.path.join(folder, "source.yaml")


def source_type_yaml_for_source_yaml(source_yaml_path):
    folder = os.path.dirname(source_yaml_path)
    parent_folder, __ = os.path.split(folder)
    return os.path.join(parent_folder, "source_type.yaml")


"""
About mapping patterns,  parsers, checkers:

We use lazy initialization below to offer one single place of configuration without any
circular imports.

We could implement a class, but this would have only one instance which we only offer
static methods or would make use of the singleton pattern.  Instead we implement simple
functions and carefully use two global variables.

(If you consider modules and object / classes as namespaces both approaches are the same
on a conceptual level, only the syntax differs).
"""

_patterns_and_checkers = None
_inverted_patterns = None


def _setup():
    global _patterns_and_checkers
    global _inverted_patterns
    _patterns_and_checkers = []
    _inverted_patterns = {}
    for pattern, handler in config():
        _patterns_and_checkers.append((pattern, handler))
        _inverted_patterns[handler.parser] = pattern


def lookup_handler(rel_path):

    # to improve lookup speed
    if not rel_path.endswith(".yaml"):
        return None

    if _patterns_and_checkers is None:
        _setup()
    for pattern, handler in _patterns_and_checkers:
        if fnmatch.fnmatch(rel_path, pattern):
            return handler

    return None


def _lookup(attribute, rel_path):
    handler = lookup_handler(rel_path)
    return None if handler is None else getattr(handler, attribute)


lookup_parser = partial(_lookup, "parser")
lookup_checker = partial(_lookup, "checker")
lookup_committer = partial(_lookup, "committer")


def lookup_pattern(parser):
    if _inverted_patterns is None:
        _setup()
    return _inverted_patterns.get(parser)


def find_yamls(pattern, root, checker):

    full_pattern = os.path.join(root, pattern)
    for p in glob.glob(full_pattern):
        try:
            bunch = load_yaml_and_bunchify(p)
        except IOError:
            continue
        if checker(bunch):
            yield p


find_site_yaml = iter_to_list(partial(find_yamls, site_pattern))
find_source_yaml = iter_to_list(partial(find_yamls, source_pattern))
find_source_type_yaml = iter_to_list(partial(find_yamls, source_type_pattern))
find_parameters_yaml = iter_to_list(partial(find_yamls, parameters_yaml))
