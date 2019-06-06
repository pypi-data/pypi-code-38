# encoding: utf-8
from __future__ import absolute_import, division, print_function

from sqlalchemy.orm import sessionmaker

from datapool.database import create_session
from datapool.errors import ConsistencyError
from datapool.logger import logger
from datapool.utils import iter_to_list, update_and_report_change

from .converters import domain_object_to_dbo
from .db_objects import ParameterDbo

NOT_ALLOWED_TO_CHANGE_PARAMETER = ("name",)


def check_and_commit(parameters, engine, session=None):
    exceptions = check(parameters, engine, session)
    if exceptions:
        raise exceptions[0]
    return commit(parameters, engine, session)


@iter_to_list
def commit(parameters, engine, session=None):

    if session is None:
        session = create_session(engine)

    parameter_dbos = _fetch_existing_parameter_dbos(session)
    added, __, existing = _check_differences(parameter_dbos, parameters)

    yield from _update_parameters(existing)

    for parameter in sorted(added, key=lambda p: p.name):
        yield _commit(parameter, session)

    yield from added

    session.commit()


def _update_parameters(existing):
    # only descriptions may be updated
    for parameter_dbo, parameter_yaml in existing:
        yield from update_and_report_change(
            parameter_dbo, parameter_yaml, "description"
        )


@iter_to_list
def check(parameters, engine, session=None):
    if session is None:
        session = create_session(engine)

    parameter_dbos = _fetch_existing_parameter_dbos(session)
    yield from _determine_and_check_differences(parameter_dbos, parameters)


def _fetch_existing_parameter_dbos(session):
    return session.query(ParameterDbo).all()


@iter_to_list
def _determine_and_check_differences(parameter_dbos, parameters_from_landing_zone):

    added, removed, existing = _check_differences(
        parameter_dbos, parameters_from_landing_zone
    )
    if removed:
        yield from _report_removed(removed)

    yield from _check_for_modifications(existing)


def _check_differences(parameter_dbos, parameters_from_landing_zone):

    parameters = parameters_from_landing_zone
    dbos = {dbo.name: dbo for dbo in parameter_dbos}
    parameters = {parameter.name: parameter for parameter in parameters}

    # we sort because regression tests might depend on name orderings:
    new_names = sorted(parameters.keys() - dbos.keys())
    missing_names = sorted(dbos.keys() - parameters.keys())
    common_names = sorted(dbos.keys() & parameters.keys())

    added = (parameters[name] for name in new_names)
    removed_dbos = [dbos[name] for name in missing_names]
    existing = [(dbos[name], parameters[name]) for name in common_names]
    return added, removed_dbos, existing


def _report_removed(removed_dbos):
    from .pretty_printers import pretty_log  # local import avoids circular import

    error = logger().error
    error("detected removed parameters:")
    for removed_dbo in removed_dbos:
        pretty_log(error, removed_dbo)
        yield ConsistencyError("parameter {} was removed".format(removed_dbo.name))


def _check_for_modifications(existing):
    from .pretty_printers import pretty_log  # local import avoids circular import

    error = logger().error
    for parameter_dbo, parameter in existing:
        ok = _check_for_parameter_modifications(parameter_dbo, parameter)
        if not ok:
            error("detected parameter modifications. existing parameter:")
            pretty_log(error, parameter_dbo)
            error("detected parameter modifications. modified parameter:")
            pretty_log(error, parameter)
            yield ConsistencyError("parameter {} was modified".format(parameter.name))


def _commit(parameter, session):
    logger().info("called _commit for parameter {}".format(parameter.name))
    parameter_row = domain_object_to_dbo(parameter)
    logger().debug("add new parameter row {}".format(parameter_row))
    session.add(parameter_row)
    return parameter_row


def _check_for_parameter_modifications(parameter_dbo, parameter_from_landing_zone):
    parameter = parameter_from_landing_zone
    return all(
        getattr(parameter, field) == getattr(parameter_dbo, field)
        for field in NOT_ALLOWED_TO_CHANGE_PARAMETER
    )
