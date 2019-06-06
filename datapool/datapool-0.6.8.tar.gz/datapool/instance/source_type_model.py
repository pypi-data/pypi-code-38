# encoding: utf-8
from __future__ import absolute_import, division, print_function

from sqlalchemy.orm import sessionmaker

from datapool.database import create_session
from datapool.errors import ConsistencyError
from datapool.logger import logger
from datapool.utils import iter_to_list, update_and_report_change

from .converters import domain_object_to_dbo
from .db_objects import SourceTypeDbo


def check_and_commit(source_type, engine, session=None):
    if session is None:
        session = create_session(engine)
    exceptions = check(source_type, engine, session)
    if exceptions:
        raise exceptions[0]
    return commit(source_type, engine, session)


@iter_to_list
def commit(source_type, engine, session=None):
    logger().debug("called commit for source_type {}".format(source_type.name))

    if session is None:
        session = create_session(engine)

    # we yield dbos which usually get invalid (expire) after commit, then attributes can not be
    # accessed any more and eg pretty_printing in tests fails. we disable this:
    session.expire_on_commit = False

    source_type_dbos = fetch_existing_source_type_dbos(session)
    added, __, existing = check_differences(source_type_dbos, source_type)

    yield from _update(existing)

    assert len(added) in (0, 1), len(added)
    if added:
        yield _commit(added[0], session)

    session.commit()


def _update(existing):

    for (dbo, from_lz) in existing:
        yield from update_and_report_change(dbo, from_lz, "description")
        lookup = {item.numerical_value: item for item in from_lz.special_values}
        for dbo_sv in dbo.special_values:
            new_sv = lookup[dbo_sv.numerical_value]
            yield from update_and_report_change(dbo_sv, new_sv, "description")


@iter_to_list
def check(source_type, engine, session=None):
    if session is None:
        session = create_session(engine)
    source_type_dbos = fetch_existing_source_type_dbos(session)
    yield from _determine_and_check_differences(source_type_dbos, source_type)


def fetch_existing_source_type_dbos(session):
    assert session is not None
    return session.query(SourceTypeDbo).all()


@iter_to_list
def _determine_and_check_differences(source_type_dbos, source_type_from_landing_zone):

    added, removed, existing = check_differences(
        source_type_dbos, source_type_from_landing_zone
    )
    yield from _check_for_modifications(existing)


def check_differences(source_type_dbos, source_type_from_landing_zone):

    source_types = [source_type_from_landing_zone]
    dbos = {dbo.name: dbo for dbo in source_type_dbos}
    source_types = {source_type.name: source_type for source_type in source_types}

    # we sort because regression tests might depend on name orderings:
    new_names = sorted(source_types.keys() - dbos.keys())
    missing_names = sorted(dbos.keys() - source_types.keys())
    common_names = sorted(dbos.keys() & source_types.keys())

    added = [source_types[name] for name in new_names]
    removed_dbos = [dbos[name] for name in missing_names]
    existing = [(dbos[name], source_types[name]) for name in common_names]
    return added, removed_dbos, existing


def _report_removed(removed_dbos):
    from .pretty_printers import pretty_log  # local import avoids circular import

    error = logger().error
    error("detected removed source types:")
    for removed_dbo in removed_dbos:
        pretty_log(error, removed_dbo)
        yield ConsistencyError("source_type {} was removed".format(removed_dbo.name))


def _check_for_modifications(existing):
    from .pretty_printers import pretty_log  # local import avoids circular import

    error = logger().error
    for source_type_dbo, source_type in existing:
        ok_1 = _check_for_source_type_modifications(source_type_dbo, source_type)
        ok_2 = _check_for_special_values_modifications(source_type_dbo, source_type)
        if not (ok_1 and ok_2):
            error("detected source_type modifications. existing source_type:")
            pretty_log(error, source_type_dbo)
            error("detected source_type modifications. modified source_type:")
            pretty_log(error, source_type)
            yield ConsistencyError(
                "source_type {} was modified".format(source_type.name)
            )


def _commit(source_type, session):
    logger().info("called _commit for source_type {}".format(source_type.name))
    source_type_row = domain_object_to_dbo(source_type)
    logger().debug("add new source_type row {}".format(source_type_row))
    session.add(source_type_row)
    return source_type_row


def _check_for_source_type_modifications(
    source_type_dbo, source_type_from_landing_zone
):
    return source_type_dbo.name == source_type_from_landing_zone.name


def _check_for_special_values_modifications(
    source_type_dbo, source_type_from_landing_zone
):
    special_values_in_db = {
        sv.categorical_value: sv for sv in source_type_dbo.special_values
    }
    special_values_from_lz = {
        sv.categorical_value: sv for sv in source_type_from_landing_zone.special_values
    }

    removed = special_values_in_db.keys() - special_values_from_lz.keys()

    existing_categorical_values = (
        special_values_in_db.keys() & special_values_from_lz.keys()
    )

    def neq(sv1, sv2):
        return (
            sv1.categorical_value != sv2.categorical_value
            or sv1.numerical_value != sv2.numerical_value
        )

    modified = any(
        neq(special_values_in_db[cv], special_values_from_lz[cv])
        for cv in existing_categorical_values
    )

    return not removed and not modified
