# encoding: utf-8
from __future__ import absolute_import, division, print_function

import datetime
from collections import Counter
from functools import wraps
from os.path import abspath, basename, dirname, exists, join

from datapool.errors import ConsistencyError, DataPoolException
from datapool.logger import logger
from datapool.utils import is_number, iter_to_list
from datapool.yaml_stuff import (check_yaml_fields_exist, is_datetime,
                                 load_yaml_and_bunchify, parse_datetime)

from .domain_objects import (DomainObject, Parameter, ParameterAveraging,
                             Parameters, Picture, Site, Source, SourceType,
                             SpecialValueDefinition)
from .landing_zone_structure import source_type_yaml_for_source_yaml


def _load_yaml(*pathes):

    path = join(*pathes)
    logger().info("load {}".format(path))
    data = load_yaml_and_bunchify(path)
    if data is None:
        msg = "file {} is empty".format(path)
        logger().warning(msg)
        raise ConsistencyError(msg)
    return data


def log(exceptions, rel_path):
    for e in exceptions:
        logger().warning("{}: {}".format(rel_path, e))
        yield e


def check_result_attribute_types(function):
    @wraps(function)
    def wrapped(landing_zone_folder, rel_path, *a, **kw):
        for result in function(landing_zone_folder, rel_path, *a, **kw):
            if isinstance(result, DomainObject):
                try:
                    result.check_attributes()
                except DataPoolException as e:
                    yield ConsistencyError(
                        "parsing {} failed: '{}'".format(rel_path, e)
                    )
            yield result

    wrapped.function = function
    return wrapped


@check_result_attribute_types
def parse_site(landing_zone_folder, rel_path):
    """ Make sure that 'pictures' is always present in site
    """

    path = join(landing_zone_folder, rel_path)
    try:
        site = _load_yaml(path)
    except ConsistencyError as e:
        yield e
        return

    if "pictures" not in site:
        site.pictures = []

    if "postcode" not in site:
        site.postcode = None

    if "description" not in site:
        site.description = None

    site_folder = dirname(path)
    exceptions = check_site_yaml(site, rel_path)
    exceptions += check_pictures(site, site_folder)
    if exceptions:
        yield from log(exceptions, rel_path)
        return

    # we transform our site Bunch so that it corresponds to the data resp. dbo objects
    # attributes:

    folder = dirname(abspath(path))

    exceptions = []
    for i, picture in enumerate(site.pictures):
        path = join(folder, picture.path)
        if "timestamp" in picture:
            if not is_datetime(picture.timestamp):
                e = ConsistencyError("date entry is not a valid date".format(i))
                exceptions.append(e)
                continue
            picture.timestamp = parse_datetime(picture.timestamp)
        else:
            picture.timestamp = None

        not_allowed = picture.keys() - set(("timestamp", "path", "description"))
        for name in not_allowed:
            exceptions.append(
                ConsistencyError(
                    "field named '{}' not allowed for pictures".format(name)
                )
            )

        with open(path, "rb") as fh:
            picture.data = fh.read()

        picture.filename = basename(picture.path)
        del picture.path

    if exceptions:
        yield from log(exceptions, rel_path)
        return

    site.pictures = [Picture(p) for p in site.pictures]

    site.coord_x = str(site.coordinates.x)
    site.coord_y = str(site.coordinates.y)
    site.coord_z = str(site.coordinates.z)
    del site.coordinates

    # now we can initialize our data object:
    yield Site(site, rel_path)


@check_result_attribute_types
def parse_parameters(landing_zone_folder, rel_path, P=Parameter, PS=Parameters):

    try:
        parameters = _load_yaml(landing_zone_folder, rel_path)
    except ConsistencyError as e:
        yield e
        return

    logger().info("number of parameters found: {}".format(len(parameters)))

    result = []
    for parameter in parameters:
        exceptions = check_parameters_yaml(parameter, rel_path)
        if exceptions:
            yield from log(exceptions, rel_path)
            continue

        # now we can initialize our data object:
        result.append(P(parameter))

    yield PS(result, rel_path)


@check_result_attribute_types
def parse_source(landing_zone_folder, rel_path, T=Source, ST=SourceType):

    try:
        source = _load_yaml(landing_zone_folder, rel_path)
    except ConsistencyError as e:
        yield e
        return

    exceptions = []

    averaging = []
    for i, avg in enumerate(source.get("averaging", [])):
        if not isinstance(avg, dict):
            exceptions.append(
                ConsistencyError("aveaging entry {} is not a mapping".format(i))
            )
            continue
        avg.integration_time = avg.get("integration_time") or None
        avg.integration_angle = avg.get("integration_angle") or None
        avg.integration_length_x = avg.get("integration_length_x") or None
        avg.integration_length_y = avg.get("integration_length_y") or None
        averaging.append(ParameterAveraging(avg))

    source.averaging = averaging

    if source.serial is not None:
        source.serial = str(source.serial)

    results = parse_source_type(
        landing_zone_folder, source_type_yaml_for_source_yaml(rel_path), ST
    )
    source_type = None
    for result in results:
        if isinstance(result, SourceType):
            source_type = result
        else:
            exceptions.append(result)

    source.source_type = source_type.name

    excs = check_source_yaml(source, rel_path)

    exceptions.extend(excs)

    if exceptions:
        yield from log(exceptions, rel_path)
        return

    yield T(source, rel_path)


@check_result_attribute_types
@iter_to_list
def parse_source_type(
    landing_zone_folder, rel_path, ST=SourceType, SV=SpecialValueDefinition
):

    try:
        source_type = _load_yaml(landing_zone_folder, rel_path)
    except ConsistencyError as e:
        yield e
        return

    if "special_values" in source_type:
        ok = []
        for i, sv in enumerate(source_type["special_values"]):
            if not isinstance(sv, dict):
                e = ConsistencyError(
                    "entry {} of 'special_values' in {} does not consist of "
                    "key-value pairs".format(i, rel_path)
                )
                yield from log([e], rel_path)
                continue
            if "description" not in sv or sv.description is None:
                sv.description = ""
            ok.append(sv)
        source_type.special_values = [SV(sv) for sv in ok]
    else:
        source_type.special_values = []

    excs = check_source_type_yaml(source_type, rel_path)
    if excs:
        yield from log(excs, rel_path)
        return

    yield ST(source_type, rel_path)


@iter_to_list
def check_site_yaml(site, rel_path):
    check_attributes = [
        "name",
        "coordinates",
        "coordinates.x",
        "coordinates.y",
        "coordinates.z",
        "street",
        "city",
        "pictures",
    ]
    yield from check_yaml_fields_exist(site, rel_path, check_attributes)


@iter_to_list
def check_pictures(site, site_folder):

    for i, picture in enumerate(site.pictures):

        if "path" not in picture:
            yield ConsistencyError("picture no {} has no field 'path'".format(i + 1))
        elif not picture.path:
            yield ConsistencyError(
                "entry 'path' of picture no {} is empty".format(i + 1)
            )
        else:
            path = join(site_folder, picture.path)
            if not exists(path):
                yield ConsistencyError("picture {} does not exist".format(picture.path))

        if "description" not in picture:
            picture.description = None


@iter_to_list
def check_parameters_yaml(parameters, rel_path):
    check_attributes = ["name", "unit", "description"]
    yield from check_yaml_fields_exist(parameters, rel_path, check_attributes)
    if "name" in parameters and parameters.name is None:
        yield ConsistencyError("field 'name' has no value")
    if "unit" in parameters and parameters.unit is None:
        yield ConsistencyError("field 'unit' has no value")


@iter_to_list
def check_source_yaml(source, rel_path):
    for name in ["name", "description", "serial", "manufacturer", "manufacturing_date"]:
        if name not in source:
            yield ConsistencyError("field '{}' is not set in {}".format(name, rel_path))
            continue
        if source[name] in (None, ""):
            yield ConsistencyError("field '{}' is empty in {}".format(name, rel_path))

    if "manufacturing_date" in source:
        if isinstance(source.manufacturing_date, datetime.datetime):
            yield ConsistencyError("entry manufacturing_date is not a pure date")
        elif not isinstance(source.manufacturing_date, datetime.date):
            yield ConsistencyError("entry manufacturing_date is not a valid date")

    yield from _check_averaging_settings(source)


def _check_averaging_settings(source):
    if not isinstance(source.averaging, list):
        yield ConsistencyError("avaraging section is not a list of mappings")
        return

    ok = []
    for i, averaging in enumerate(source.averaging):
        if not isinstance(averaging, dict):
            yield ConsistencyError("enty {} in averaging is not mapping".format(i))
        elif "parameter" not in averaging:
            yield ConsistencyError(
                "item {} listed in avaraging section has no entry 'parameter'".format(i)
            )
        else:
            ok.append(averaging)

    parameter_name_counts = Counter((averaging.parameter for averaging in ok))
    for name, count in parameter_name_counts.items():
        if count > 1:
            yield ConsistencyError(
                "parameter '{}' is listed {} times in averaging section".format(
                    name, count
                )
            )

    for averaging in sorted(ok, key=lambda avg: avg.parameter):

        if averaging.parameter is None:
            yield ConsistencyError("missing value for 'parameter' in averaging section")

        not_nones = sum(
            1
            for k, v in averaging.items()
            if k.startswith("integration") and v is not None
        )
        if not_nones == 0:
            yield ConsistencyError(
                "at least one averaging value must be set for '{}'".format(
                    averaging.parameter
                )
            )

        for unit in ("length_x", "length_y", "angle", "time"):
            field_name = "integration_{}".format(unit)
            value = averaging.get(field_name)
            if value is not None:
                if not is_number(value):
                    yield ConsistencyError(
                        "averaging setting '{}' of '{}' is not a number: '{}'".format(
                            field_name, averaging.parameter, value
                        )
                    )


@iter_to_list
def check_source_type_yaml(source_type, rel_path):
    for name in ("name", "description"):
        if name not in source_type:
            yield ConsistencyError("field '{}' is not set in {}".format(name, rel_path))
            continue
        if not source_type[name]:
            yield ConsistencyError("field '{}' is empty in {}".format(name, rel_path))

    yield from _check_special_values_section(source_type.special_values, rel_path)


def _check_special_values_section(special_values, rel_path):

    numerical_values = []
    categorical_values = []
    for i, entry in enumerate(special_values):
        if not isinstance(entry, dict):
            yield ConsistencyError(
                "entry {} of special_value section in {} does not consist of "
                "key-value pairs".format(i, rel_path)
            )
            continue

        if "numerical_value" not in entry:
            yield ConsistencyError(
                "field 'numerical_value' is empty in entry {} of special_value "
                "section of {}".format(i, rel_path)
            )
        else:
            if not is_number(entry.numerical_value):
                yield ConsistencyError(
                    "value '{}' specified by field 'numerical_value' in {} is "
                    "not a number".format(entry.numerical_value, rel_path)
                )
            numerical_values.append(entry.numerical_value)

        if "categorical_value" not in entry:
            yield ConsistencyError(
                "field 'categorical_value' is empty in entry {} of "
                "special_value section of {}".format(i, rel_path)
            )
        else:
            categorical_values.append(entry.categorical_value)

        not_allowed = entry.keys() - set(
            ("numerical_value", "categorical_value", "description", "_rel_path")
        )
        for name in not_allowed:
            yield ConsistencyError(
                "field '{}' not allowed in entry {} of special_value section "
                "in {}".format(name, i, rel_path)
            )

    for name, count in Counter(numerical_values).items():
        if count > 1:
            yield ConsistencyError(
                "numerical_value '{}' not unique in special_value section of {}".format(
                    name, rel_path
                )
            )

    for value, count in Counter(categorical_values).items():
        if count > 1:
            yield ConsistencyError(
                "categorical_value '{}' not unique in special_value section of "
                "{}".format(value, rel_path)
            )
