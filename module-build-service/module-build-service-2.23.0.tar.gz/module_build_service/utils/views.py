# -*- coding: utf-8 -*-
# Copyright (c) 2018  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Ralph Bean <rbean@redhat.com>
#            Matt Prahl <mprahl@redhat.com>
#            Jan Kaluza <jkaluza@redhat.com>
import re
import copy
from functools import wraps
from datetime import datetime

from flask import request, url_for, Response
from sqlalchemy.sql.sqltypes import Boolean as sqlalchemy_boolean
from sqlalchemy.orm import aliased
import sqlalchemy

from module_build_service import models, api_version, conf, db
from module_build_service.errors import ValidationError, NotFound
from .general import scm_url_schemes


def get_scm_url_re():
    """
    Returns a regular expression for SCM URL extraction and validation.
    """
    schemes_re = "|".join(map(re.escape, scm_url_schemes(terse=True)))
    regex = (
        r"(?P<giturl>(?P<scheme>(?:" + schemes_re + r"))://(?P<host>[^/]+)?"
        r"(?P<repopath>/[^\?]+))(?:\?(?P<modpath>[^#]+)?)?#(?P<revision>.+)"
    )
    return re.compile(regex)


def pagination_metadata(p_query, api_version, request_args):
    """
    Returns a dictionary containing metadata about the paginated query.
    This must be run as part of a Flask request.
    :param p_query: flask_sqlalchemy.Pagination object
    :param api_version: an int of the API version
    :param request_args: a dictionary of the arguments that were part of the
    Flask request
    :return: a dictionary containing metadata about the paginated query
    """
    request_args_wo_page = dict(copy.deepcopy(request_args))
    # Remove pagination related args because those are handled elsewhere
    # Also, remove any args that url_for accepts in case the user entered
    # those in
    for key in ["page", "per_page", "endpoint"]:
        if key in request_args_wo_page:
            request_args_wo_page.pop(key)
    for key in request_args:
        if key.startswith("_"):
            request_args_wo_page.pop(key)

    pagination_data = {
        "page": p_query.page,
        "pages": p_query.pages,
        "per_page": p_query.per_page,
        "prev": None,
        "next": None,
        "total": p_query.total,
        "first": url_for(
            request.endpoint,
            api_version=api_version,
            page=1,
            per_page=p_query.per_page,
            _external=True,
            **request_args_wo_page
        ),
        "last": url_for(
            request.endpoint,
            api_version=api_version,
            page=p_query.pages,
            per_page=p_query.per_page,
            _external=True,
            **request_args_wo_page
        ),
    }

    if p_query.has_prev:
        pagination_data["prev"] = url_for(
            request.endpoint,
            api_version=api_version,
            page=p_query.prev_num,
            per_page=p_query.per_page,
            _external=True,
            **request_args_wo_page
        )
    if p_query.has_next:
        pagination_data["next"] = url_for(
            request.endpoint,
            api_version=api_version,
            page=p_query.next_num,
            per_page=p_query.per_page,
            _external=True,
            **request_args_wo_page
        )

    return pagination_data


def _add_order_by_clause(flask_request, query, column_source):
    """
    Orders the given SQLAlchemy query based on the GET arguments provided.

    :param flask_request: a Flask request object
    :param query: a SQLAlchemy query object
    :param column_source: a SQLAlchemy database model
    :return: a SQLAlchemy query object
    """
    order_by = flask_request.args.getlist("order_by")
    order_desc_by = flask_request.args.getlist("order_desc_by")
    # Default to ordering by ID in descending order
    descending = True
    requested_order = ["id"]

    if order_by and order_desc_by:
        raise ValidationError("You may not specify both order_by and order_desc_by")
    elif order_by:
        descending = False
        requested_order = order_by
    elif order_desc_by:
        descending = True
        requested_order = order_desc_by

    column_dict = dict(column_source.__table__.columns)
    order_args = []
    for column_name in requested_order:
        if column_name not in column_dict:
            raise ValidationError(
                'An invalid ordering key of "{}" was supplied'.format(column_name))
        column = column_dict[column_name]
        # If the version column is provided, cast it as an integer so the sorting is correct
        if column_name == "version":
            column = sqlalchemy.cast(column, sqlalchemy.BigInteger)
        if descending:
            column = column.desc()

        order_args.append(column)

    return query.order_by(*order_args)


def str_to_bool(value):
    """
    Parses a string to determine its boolean value
    :param value: a string
    :return: a boolean
    """
    return value.lower() in ["true", "1"]


def filter_component_builds(flask_request):
    """
    Returns a flask_sqlalchemy.Pagination object based on the request parameters
    :param request: Flask request object
    :return: flask_sqlalchemy.Pagination
    """
    search_query = dict()
    for key in request.args.keys():
        # Search by state will be handled separately
        if key == "state":
            continue
        # Only filter on valid database columns
        if key in models.ComponentBuild.__table__.columns.keys():
            if isinstance(models.ComponentBuild.__table__.columns[key].type, sqlalchemy_boolean):
                search_query[key] = str_to_bool(flask_request.args[key])
            else:
                search_query[key] = flask_request.args[key]

    # Multiple states can be supplied => or-ing will take place
    states = flask_request.args.getlist("state")
    search_states = []
    for state in states:
        if state.isdigit():
            search_states.append(state)
        else:
            try:
                import koji
            except ImportError:
                raise ValidationError("Cannot filter by state names because koji isn't installed")

            if state.upper() in koji.BUILD_STATES:
                search_states.append(koji.BUILD_STATES[state.upper()])
            else:
                raise ValidationError("Invalid state was supplied: %s" % state)

    # Allow the user to specify the module build ID with a more intuitive key name
    if "module_build" in flask_request.args:
        search_query["module_id"] = flask_request.args["module_build"]

    query = models.ComponentBuild.query

    if search_query:
        query = query.filter_by(**search_query)
    if search_states:
        query = query.filter(models.ComponentBuild.state.in_(search_states))

    query = _add_order_by_clause(flask_request, query, models.ComponentBuild)

    page = flask_request.args.get("page", 1, type=int)
    per_page = flask_request.args.get("per_page", 10, type=int)
    return query.paginate(page, per_page, False)


def filter_module_builds(flask_request):
    """
    Returns a flask_sqlalchemy.Pagination object based on the request parameters
    :param request: Flask request object
    :return: flask_sqlalchemy.Pagination
    """
    search_query = dict()
    special_columns = set((
        "time_submitted",
        "time_modified",
        "time_completed",
        "state",
        "stream_version_lte",
        "virtual_stream",
    ))
    columns = models.ModuleBuild.__table__.columns.keys()
    for key in set(request.args.keys()) - special_columns:
        # Only filter on valid database columns but skip columns that are treated specially or
        # ignored
        if key in columns:
            search_query[key] = flask_request.args[key]

    # Multiple states can be supplied => or-ing will take place
    states = flask_request.args.getlist("state")
    search_states = []
    for state in states:
        if state.isdigit():
            search_states.append(state)
        else:
            if state in models.BUILD_STATES:
                search_states.append(models.BUILD_STATES[state])
            else:
                raise ValidationError("Invalid state was supplied: %s" % state)

    nsvc = flask_request.args.get("nsvc", None)
    if nsvc:
        nsvc_parts = nsvc.split(":")
        query_keys = ["name", "stream", "version", "context"]
        for key, part in zip(query_keys, nsvc_parts):
            search_query[key] = part

    rpm = flask_request.args.get("rpm", None)
    koji_tags = []
    if rpm:
        if conf.system == "koji":
            # we are importing the koji builder here so we can search for the rpm metadata
            # from koji. If we imported this regulary we would have gotten a circular import error.
            from module_build_service.builder.KojiModuleBuilder import KojiModuleBuilder  # noqa

            koji_tags = KojiModuleBuilder.get_rpm_module_tag(rpm)
        else:
            raise ValidationError("Configured builder does not allow to search by rpm binary name!")

    query = models.ModuleBuild.query

    if search_query:
        query = query.filter_by(**search_query)
    if search_states:
        query = query.filter(models.ModuleBuild.state.in_(search_states))
    if koji_tags:
        query = query.filter(models.ModuleBuild.koji_tag.in_(koji_tags)).filter_by(**search_query)

    # This is used when filtering the date request parameters, but it is here to avoid recompiling
    utc_iso_datetime_regex = re.compile(
        r"^(?P<datetime>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.\d+)?(?:Z|[-+]00(?::00)?)?$")

    # Filter the query based on date request parameters
    for item in ("submitted", "modified", "completed"):
        for context in ("before", "after"):
            request_arg = "%s_%s" % (item, context)  # i.e. submitted_before
            iso_datetime_arg = request.args.get(request_arg, None)

            if iso_datetime_arg:
                iso_datetime_matches = re.match(utc_iso_datetime_regex, iso_datetime_arg)

                if not iso_datetime_matches or not iso_datetime_matches.group("datetime"):
                    raise ValidationError(
                        'An invalid Zulu ISO 8601 timestamp was provided for the "%s" parameter'
                        % request_arg
                    )
                # Converts the ISO 8601 string to a datetime object for SQLAlchemy to use to filter
                item_datetime = datetime.strptime(
                    iso_datetime_matches.group("datetime"), "%Y-%m-%dT%H:%M:%S")
                # Get the database column to filter against
                column = getattr(models.ModuleBuild, "time_" + item)

                if context == "after":
                    query = query.filter(column >= item_datetime)
                elif context == "before":
                    query = query.filter(column <= item_datetime)

    # Multiple virtual_streams can be supplied for "or" logic filtering
    virtual_streams = flask_request.args.getlist("virtual_stream")
    query = models.ModuleBuild._add_virtual_streams_filter(db.session, query, virtual_streams)

    stream_version_lte = flask_request.args.get("stream_version_lte")
    if stream_version_lte is not None:
        invalid_error = (
            "An invalid value of stream_version_lte was provided. It must be an "
            "integer or float greater than or equal to 10000."
        )
        try:
            stream_version_lte = float(stream_version_lte)
        except (TypeError, ValueError):
            raise ValidationError(invalid_error)

        if stream_version_lte < 10000:
            raise ValidationError(invalid_error)

        query = models.ModuleBuild._add_stream_version_lte_filter(
            db.session, query, stream_version_lte)

    br_joined = False
    module_br_alias = None
    for item in (
        "base_module_br",
        "name",
        "stream",
        "version",
        "context",
        "stream_version",
        "stream_version_lte",
        "stream_version_gte",
    ):
        if item == "base_module_br":
            request_arg_name = item
        else:
            request_arg_name = "base_module_br_{}".format(item)
        request_arg = flask_request.args.get(request_arg_name)

        if not request_arg:
            continue

        if not br_joined:
            module_br_alias = aliased(models.ModuleBuild, name="module_br")
            # Shorten this table name for clarity in the query below
            mb_to_br = models.module_builds_to_module_buildrequires
            # The following joins get added:
            # JOIN module_builds_to_module_buildrequires
            #     ON module_builds_to_module_buildrequires.module_id = module_builds.id
            # JOIN module_builds AS module_br
            #     ON module_builds_to_module_buildrequires.module_buildrequire_id = module_br.id
            query = query.join(mb_to_br, mb_to_br.c.module_id == models.ModuleBuild.id).join(
                module_br_alias, mb_to_br.c.module_buildrequire_id == module_br_alias.id)
            br_joined = True

        if item == "base_module_br":
            try:
                name, stream, version, context = flask_request.args["base_module_br"].split(":")
            except ValueError:
                raise ValidationError(
                    'The filter argument for "base_module_br" must be in the format of N:S:V:C')
            query = query.filter(
                module_br_alias.name == name,
                module_br_alias.stream == stream,
                module_br_alias.version == version,
                module_br_alias.context == context,
            )
        elif item.endswith("_lte"):
            column = getattr(module_br_alias, item[:-4])
            query = query.filter(column <= request_arg)
        elif item.endswith("_gte"):
            column = getattr(module_br_alias, item[:-4])
            query = query.filter(column >= request_arg)
        else:
            column = getattr(module_br_alias, item)
            query = query.filter(column == request_arg)

    query = _add_order_by_clause(flask_request, query, models.ModuleBuild)

    page = flask_request.args.get("page", 1, type=int)
    per_page = flask_request.args.get("per_page", 10, type=int)
    return query.paginate(page, per_page, False)


def cors_header(allow="*"):
    """
    A decorator that sets the Access-Control-Allow-Origin header to the desired value on a Flask
    route
    :param allow: a string of the domain to allow. This defaults to '*'.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            rv = func(*args, **kwargs)
            if rv:
                # If a tuple was provided, then the Flask Response should be the first object
                if isinstance(rv, tuple):
                    response = rv[0]
                else:
                    response = rv
                # Make sure we are dealing with a Flask Response object
                if isinstance(response, Response):
                    response.headers.add("Access-Control-Allow-Origin", allow)
            return rv

        return wrapper

    return decorator


def validate_api_version():
    """
    A decorator that validates the requested API version on a route
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            req_api_version = kwargs.get("api_version", 1)
            if req_api_version > api_version or req_api_version < 1:
                raise NotFound("The requested API version is not available")
            return func(*args, **kwargs)

        return wrapper

    return decorator
