# encoding: utf-8
from __future__ import absolute_import, division, print_function

from sqlalchemy.orm import sessionmaker

from datapool.database import create_session
from datapool.errors import ConsistencyError
from datapool.logger import logger
from datapool.utils import iter_to_list, update_and_report_change

from .converters import domain_object_to_dbo
from .db_objects import ParameterDbo, SourceDbo, SourceTypeDbo


def check_and_commit(source, engine, session=None):
    if source.serial is not None:
        source.serial = str(source.serial)
    if session is None:
        session = create_session(engine)
    exceptions = check(source, engine, session)
    if exceptions:
        raise exceptions[0]
    return commit(source, engine, session)


@iter_to_list
def commit(source, engine, session=None):
    logger().debug("called commit for source {}".format(source.name))

    if session is None:
        session = create_session(engine)

    if source.serial is not None:
        source.serial = str(source.serial)

    existing_source_dbo = (
        session.query(SourceDbo).filter(SourceDbo.name == source.name).first()
    )
    if existing_source_dbo is not None:
        logger().debug(
            "source with same name {} already exists".format(existing_source_dbo)
        )
        to_create, __, __ = _determine_averaging_differences(
            existing_source_dbo, source
        )
        _add_new_averagings(existing_source_dbo, to_create, session)
        yield from _update(existing_source_dbo, source)

    else:

        source_type = (
            session.query(SourceTypeDbo)
            .filter(SourceTypeDbo.name == source.source_type)
            .first()
        )

        source.source_type = source_type

        source_without_averaging = source.copy()
        del source_without_averaging.averaging

        source_dbo = domain_object_to_dbo(source_without_averaging)
        session.add(source_dbo)

        _add_new_averagings(source_dbo, source.averaging, session)

        logger().debug("add new source_dbo {}".format(source_dbo))
        # session.add(source_dbo)

    session.commit()
    yield find_by_name(session, source.name)


def _update(existing_source_dbo, source):
    for name in ("description", "serial", "manufacturer", "manufacturing_date"):
        yield from update_and_report_change(existing_source_dbo, source, name)


def find_by_name(session, source_name):
    return session.query(SourceDbo).filter(SourceDbo.name == source_name).first()


@iter_to_list
def check(source, engine, session=None):

    if session is None:
        session = create_session(engine)

    yield from _check_if_referenced_parameters_are_valid(session, source)
    yield from _check_if_referenced_source_type_is_valid(session, source)

    # check if the source.name already exists.
    existing_source_dbo = find_by_name(session, source.name)
    if existing_source_dbo is not None:
        yield from _check_for_modifications(source, existing_source_dbo)
    else:
        # if the source is new and has a serial number, the pair (serieal, source_type) should be
        # unique:
        if source.serial is not None:
            yield from _check_unique_serial(session, source)


def _check_if_referenced_parameters_are_valid(session, source):

    for averaging in sorted(source.averaging, key=lambda avg: avg.parameter):
        dbo = (
            session.query(ParameterDbo)
            .filter(ParameterDbo.name == averaging.parameter)
            .first()
        )
        if dbo is None:
            yield ConsistencyError(
                "parameter name '{}' in averaging section not in db".format(
                    averaging.parameter
                )
            )


def _check_if_referenced_source_type_is_valid(session, source):

    dbo = (
        session.query(SourceTypeDbo)
        .filter(SourceTypeDbo.name == source.source_type)
        .first()
    )
    if dbo is None:
        yield ConsistencyError("source type '{}' not in db".format(source.source_type))


@iter_to_list
def _check_unique_serial(session, source):
    dbo = (
        session.query(SourceDbo)
        .filter(
            SourceDbo.serial == str(source.serial),
            SourceDbo.source_type.has(name=source.source_type),
        )
        .first()
    )
    if dbo is not None:
        yield ConsistencyError(
            "combination source_type '{}' serial '{}' already exists".format(
                source.serial, source.source_type
            )
        )


def _check_for_modifications(source, source_dbo):

    yield from _check_for_averaging_modifications(source, source_dbo)

    # if exists, the source_type must remain the same
    if source_dbo.source_type.name != source.source_type:

        from .pretty_printers import pretty_log  # local import avoids circular import

        error = logger().error
        error("detected source modifications. existing source:")
        pretty_log(error, source_dbo)
        error("detected source modifications. modified source:")
        pretty_log(error, source)
        yield ConsistencyError(
            "detected invalid source modifiations, see log for details"
        )


def _check_for_averaging_modifications(source, source_dbo):
    from .pretty_printers import pretty_log  # local import avoids circular import

    to_create, dbos_to_drop, dbos_already_existing = _determine_averaging_differences(
        source_dbo, source
    )

    if dbos_to_drop:
        for dbo in sorted(dbos_to_drop, key=lambda dbo: dbo.parameter.name):
            logger().error(
                "detected removed averaging settings of '{}' for source '{}':".format(
                    dbo.parameter, source.name
                )
            )
            pretty_log(logger().error, dbo)
        yield ConsistencyError(
            "some averaging settings for source '{}' were removed.".format(source.name)
        )

    source_averaging = {avg.parameter: avg for avg in source.averaging}
    for dbo in sorted(dbos_already_existing, key=lambda dbo: dbo.parameter.name):
        avg = source_averaging[dbo.parameter.name]
        if any(
            (
                avg.integration_time != dbo.integration_time,
                avg.integration_length_x != dbo.integration_length_x,
                avg.integration_length_y != dbo.integration_length_y,
                avg.integration_angle != dbo.integration_angle,
            )
        ):
            logger().error(
                "detected modification in averaging settings of '{}' for source '{}':".format(
                    dbo.parameter, source.name
                )
            )
            logger().error("existing averaging:")
            pretty_log(logger().error, dbo)
            logger().error("modified averaging:")
            pretty_log(logger().error, avg)


def _determine_averaging_differences(source_dbo, source):

    existing_averagings = {avg.parameter.name: avg for avg in source_dbo.averaging}
    new_averagings = {avg.parameter: avg for avg in source.averaging}

    to_create_keys = set(new_averagings) - set(existing_averagings)
    to_drop_keys = set(existing_averagings) - set(new_averagings)
    existing_keys = set(new_averagings) & set(existing_averagings)

    to_create = list(map(new_averagings.get, to_create_keys))
    to_drop = list(map(existing_averagings.get, to_drop_keys))
    dbos_existing = list(map(existing_averagings.get, existing_keys))

    return to_create, to_drop, dbos_existing


def _add_new_averagings(source_dbo, to_create, session):
    from .pretty_printers import pretty_log  # local import avoids circular import

    for averaging in to_create:
        averaging.parameter = (
            session.query(ParameterDbo)
            .filter(ParameterDbo.name == averaging.parameter)
            .first()
        )
        averaging.source = source_dbo
        dbo = domain_object_to_dbo(averaging)
        session.add(dbo)
        logger().debug("added new averaging:")
        pretty_log(logger().debug, averaging)
