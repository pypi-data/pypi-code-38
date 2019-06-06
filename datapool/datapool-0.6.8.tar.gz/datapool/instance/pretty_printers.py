# encoding: utf-8
from __future__ import absolute_import, division, print_function

import importlib
import io
import sys
from functools import singledispatch

from .db_objects import (
    ParameterAveragingDbo,
    ParameterDbo,
    PictureDbo,
    SiteDbo,
    SourceDbo,
    SourceTypeDbo,
    SpecialValueDefinitionDbo,
)
from .domain_objects import (
    Parameter,
    ParameterAveraging,
    Parameters,
    Picture,
    Site,
    Source,
    SourceType,
    SpecialValueDefinition,
)


def pretty_log(log_function, what, indent=""):

    lines = pretty_str(what, indent).split("\n")
    # pretty_prints a final "\n" which produces an empty line in the logs, so we remove
    # trailing empty lines:
    if lines[-1] == "":
        lines = lines[:-1]
    for line in lines:
        log_function(line)


def pretty_str(what, indent=""):
    file = io.StringIO()
    pretty_print(what, file=file, indent=indent)
    return file.getvalue()


"""
we use single dispatch on first argument to find appropriate pretty printing function.
see https://docs.python.org/3/library/functools.html#functools.singledispatch
"""


@singledispatch
def pretty_print(what, file=sys.stdout, indent=""):
    raise RuntimeError("single dispatch on pretty_print for {!r} failed".format(what))


def fields(dbo):
    names = dir(dbo)
    return {name: getattr(dbo, name) for name in names if not name.startswith("_")}


def _pretty_print_site(type_name, dd, file, indent):

    lines = ""
    lines += "{indent}{type_name} {name}:\n"
    lines += "{indent}    street      : {street!r}\n"
    lines += "{indent}    city        : {city!r}\n"
    lines += "{indent}    x, y, z     : {coord_x!r}, {coord_y!r}, {coord_z!r}\n"
    lines += "{indent}    description : {description}\n"

    pictures = dd["pictures"]
    if not pictures:
        lines += "{indent}    pictures    : none\n"

    txt = lines.rstrip().format(indent=indent, type_name=type_name, **dd)
    print(txt, file=file)
    for p in dd["pictures"]:
        pretty_print(p, file=file, indent=indent + "    ")


def _pretty_print_picture(type_name, dd, file, indent):

    lines = ""
    lines += "{indent}{type_name}:\n"
    lines += "{indent}    filename    : {filename!r}\n"
    lines += "{indent}    timestamp   : {timestamp!r}\n"
    lines += "{indent}    filesize    : {filesize!r}\n"
    lines += "{indent}    description : {description!r}\n"

    txt = lines.rstrip().format(
        indent=indent, type_name=type_name, filesize=len(dd["data"]), **dd
    )
    print(txt, file=file)


def _pretty_print_parameter(type_name, dd, file, indent):

    lines = ""
    lines += "{indent}{type_name}:\n"
    lines += "{indent}    name        : {name!r}\n"
    lines += "{indent}    description : {description!r}\n"
    lines += "{indent}    unit        : {unit!r}\n"

    txt = lines.rstrip().format(indent=indent, type_name=type_name, **dd)
    print(txt, file=file)


def _pretty_print_parameter_averaging(type_name, dd, file, indent):

    lines = ""
    lines += "{indent}{type_name}:\n"
    lines += "{indent}    parameter            : {parameter!r}\n"
    lines += "{indent}    integration_length_x : {integration_length_x!r}\n"
    lines += "{indent}    integration_length_y : {integration_length_y!r}\n"
    lines += "{indent}    integration_angle    : {integration_angle!r}\n"
    lines += "{indent}    integration_time     : {integration_time!r}\n"

    txt = lines.rstrip().format(indent=indent, type_name=type_name, **dd)
    print(txt, file=file)


def _pretty_print_source(type_name, dd, file, indent):

    lines = ""
    lines += "{indent}{type_name}:\n"
    lines += "{indent}    name               : {name!r}\n"
    lines += "{indent}    description        : {description!r}\n"
    lines += "{indent}    serial             : {serial!r}\n"
    lines += "{indent}    manufacturer       : {manufacturer!r}\n"
    lines += "{indent}    manufacturing_date : {manufacturing_date!r}\n"
    lines += "{indent}    type               : {source_type!r}\n"

    txt = lines.rstrip().format(indent=indent, type_name=type_name, **dd)
    print(txt, file=file)
    for avg in dd["averaging"]:
        pretty_print(avg, file=file, indent=indent + "    ")


def _pretty_print_source_type(type_name, dd, file, indent):

    lines = ""
    lines += "{indent}{type_name}:\n"
    lines += "{indent}    name        : {name!r}\n"
    lines += "{indent}    description : {description!r}\n"

    txt = lines.rstrip().format(indent=indent, type_name=type_name, **dd)
    print(txt, file=file)
    for sv in dd["special_values"]:
        pretty_print(sv, file=file, indent=indent + "    ")


def _pretty_print_special_value_definition(type_name, dd, file, indent):

    lines = ""
    lines += "{indent}{type_name}:\n"
    lines += "{indent}    categorical_value : {categorical_value!r}\n"
    lines += "{indent}    numerical_value   : {numerical_value!r}\n"
    lines += "{indent}    description       : {description!r}\n"

    txt = lines.rstrip().format(indent=indent, type_name=type_name, **dd)
    print(txt, file=file)


def _pretty_print_parameters(type_name, parameters, file, indent):

    all_lines = ""
    all_lines += "{indent}{type_name}:\n"
    for parameter in parameters:

        lines = ""
        lines += "{indent}    name        : {parameter.name!r}\n"
        lines += "{indent}    description : {parameter.description!r}\n"
        lines += "{indent}    unit        : {parameter.unit!r}\n\n"
        txt = lines.format(indent=indent, parameter=parameter)
        all_lines += txt

    txt = all_lines.rstrip().format(indent=indent, type_name=type_name)
    print(txt, file=file)


@pretty_print.register(Site)
def pretty_print_site(site, file=sys.stdout, indent=""):
    _pretty_print_site("Site", site, file, indent)


@pretty_print.register(SiteDbo)
def pretty_print_site_dbo(site, file=sys.stdout, indent=""):
    attributes = fields(site)
    attributes["pictures"] = site.pictures
    _pretty_print_site("SiteDbo", attributes, file, indent)


@pretty_print.register(Picture)
def pretty_print_picture(picture, file=sys.stdout, indent=""):
    _pretty_print_picture("Picture", picture, file, indent)


@pretty_print.register(PictureDbo)
def pretty_print_picture_dbo(picture, file=sys.stdout, indent=""):
    _pretty_print_picture("PictureDbo", fields(picture), file, indent)


@pretty_print.register(Parameter)
def pretty_print_parameter(parameter, file=sys.stdout, indent=""):
    _pretty_print_parameter("Parameter", parameter, file, indent)


@pretty_print.register(Parameters)
def pretty_print_parameters(parameters, file=sys.stdout, indent=""):
    _pretty_print_parameters("Parameters", parameters, file, indent)


@pretty_print.register(ParameterDbo)
def pretty_print_parameter_dbo(parameter, file=sys.stdout, indent=""):
    _pretty_print_parameter("ParameterDbo", fields(parameter), file, indent)


@pretty_print.register(ParameterAveragingDbo)
def pretty_print_parameter_averaging_dbo(
    parameter_averaging, file=sys.stdout, indent=""
):
    dd = fields(parameter_averaging)
    dd["parameter"] = dd["parameter"].name
    _pretty_print_parameter_averaging("ParameterAveragingDbo", dd, file, indent)


@pretty_print.register(ParameterAveraging)
def pretty_print_parameter_averaging(parameter_averaging, file=sys.stdout, indent=""):
    parameter_averaging = parameter_averaging.copy()
    if isinstance(parameter_averaging.parameter, ParameterDbo):
        parameter_averaging.parameter = parameter_averaging.parameter.name
    _pretty_print_parameter_averaging(
        "ParameterAveraging", parameter_averaging, file, indent
    )


@pretty_print.register(Source)
def pretty_print_source(source, file=sys.stdout, indent=""):
    _pretty_print_source("Source", source, file, indent)


@pretty_print.register(SourceDbo)
def pretty_print_source_dbo(source, file=sys.stdout, indent=""):
    dd = fields(source)
    dd["source_type"] = source.source_type.name
    _pretty_print_source("SourceDbo", dd, file, indent)


@pretty_print.register(SourceType)
def pretty_print_source_type(source_type, file=sys.stdout, indent=""):
    _pretty_print_source_type("SourceType", source_type, file, indent)


@pretty_print.register(SourceTypeDbo)
def pretty_print_source_type_dbo(source_type, file=sys.stdout, indent=""):
    _pretty_print_source_type("SourceTypeDbo", fields(source_type), file, indent)


@pretty_print.register(SpecialValueDefinitionDbo)
def pretty_print_special_value_definition_dbo(source_type, file=sys.stdout, indent=""):
    _pretty_print_special_value_definition(
        "SpecialValueDefinitionDbo", fields(source_type), file, indent
    )


@pretty_print.register(SpecialValueDefinition)
def pretty_print_special_value_definition(source_type, file=sys.stdout, indent=""):
    _pretty_print_special_value_definition(
        "SpecialValueDefinition", source_type, file, indent
    )
