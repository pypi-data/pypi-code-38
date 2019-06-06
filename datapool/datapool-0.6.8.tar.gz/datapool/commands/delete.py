import functools
import itertools
import json
import os
from datetime import datetime

from sqlalchemy.orm import sessionmaker

from datapool.instance.pretty_printers import pretty_str

from ..database import (InvalidOperationError, check_if_tables_exist,
                        connect_to_db, filters_to_sqlalchemy_expression)
from ..instance.config_handling import read_config
from ..instance.db_objects import (ParameterDbo, SignalCommentAssociation,
                                   SignalDbo, SignalSignalQualityAssociation,
                                   SiteDbo, SourceDbo, SourceTypeDbo)
from ..instance.landing_zone_structure import (find_parameters_yaml,
                                               find_site_yaml,
                                               find_source_type_yaml,
                                               find_source_yaml,
                                               tracking_sub_folder)
from ..landing_zone import write_lock
from ..logger import get_cmdline_logger
from ..utils import format_table


class FailedError(Exception):
    pass


def convert_failed_error_to_return_code(function):
    @functools.wraps(function)
    def wrapped(*a, **kw):
        try:
            return_code = function(*a, **kw)
            return 0 if return_code is None else return_code
        except FailedError:
            return 1

    return wrapped


@convert_failed_error_to_return_code
def delete_signals(do_delete, max_rows, filters, print_ok, print_err):

    with get_cmdline_logger(verbose=False):
        session, config = _setup_session(print_err)

        filter_expression, messages = filters_to_sqlalchemy_expression(filters)
        if messages:
            for message in messages:
                print_err("- {}".format(message))
            return 1

        q = (
            session.query(SignalDbo)
            .outerjoin(SignalDbo.site)  # site might be null !
            .join(SignalDbo.source)
            .join(SignalDbo.parameter)
            .filter(filter_expression)
            .order_by(SignalDbo.timestamp)
        )

        if max_rows:
            _print_signals(q, max_rows, print_ok)

        if not do_delete:
            print_ok("- use '--force --force' to delete signals.")
            return 0

        signal_ids_query = q.with_entities(SignalDbo.signal_id)

        _delete_associations(session, signal_ids_query)

        del_q = session.query(SignalDbo).filter(
            SignalDbo.signal_id.in_(signal_ids_query.subquery())
        )
        count = del_q.delete(synchronize_session="fetch")
        session.commit()
        print_ok("- deleted {} rows".format(count))
        if config.backup_landing_zone:
            _record_delete(
                    "delete_signals",
                config, (do_delete, max_rows, filters)
            )
            print_ok("- recorded deletion")
        return 0


def _tracking_sub_folder(config):
    folder = os.path.join(config.backup_landing_zone.folder, tracking_sub_folder)
    return folder


def _record_delete(what, config, args):
    target_folder = _tracking_sub_folder(config)
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    file_name = "{}.json.{}".format(what, datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    with open(os.path.join(target_folder, file_name), "w") as fh:
        fh.write(json.dumps(args))


def _setup_session(print_err):
    config = read_config()
    if config is None:
        print_err("- no config file found. please run 'pool init-config' first.")
        raise FailedError()

    try:
        engine = connect_to_db(config.db)
    except InvalidOperationError as e:
        print_err("- {}".format(e))
        raise FailedError()

    if not check_if_tables_exist(config.db):
        print_err("- database not initialized, run 'pool init-db' first")
        raise FailedError()

    session = sessionmaker(bind=engine)()
    return session, config


def _print_signals(q, max_rows, print_ok):
    num_signals = q.count()
    print_ok("- deletion affects {} signal(s)".format(num_signals))
    if not num_signals:
        return

    rows = [dbo.resolved_columns() for dbo in q.limit(max_rows)]
    header = SignalDbo.resolved_column_names()
    table = format_table(header, rows)
    print_ok("")
    header, delim, *rows = table.split("\n")
    print_ok("  " + header)
    print_ok("  " + delim)
    for row in rows:
        print_ok("  " + row)
    if num_signals > max_rows:
        print_ok("  ... skipped {} signals".format(num_signals - max_rows))
    print_ok("")


@convert_failed_error_to_return_code
def delete_meta(do_delete, max_rows, what, name, print_ok, print_err):
    assert what in ("site", "source", "source_type", "parameter")

    with get_cmdline_logger(verbose=False):

        session, config = _setup_session(print_err)
        landing_zone_root = config.landing_zone.folder

        function = {
            "site": _delete_site,
            "source": _delete_source,
            "source_type": _delete_source_type,
            "parameter": _delete_parameter,
        }[what]

        signals_before = _count_signals(session)

        with write_lock(landing_zone_root) as got_lock:

            if not got_lock:
                print_err(
                    "+ {} is locked. maybe somebody else works on it simultaneously ?".format(
                        landing_zone_root
                    )
                )
                return 1

            exit_code = function(
                session,
                name,
                do_delete,
                max_rows,
                landing_zone_root,
                print_ok,
                print_err,
            )

        if not exit_code:
            session = sessionmaker(bind=session.bind)()
            signals_after = _count_signals(session)
            print_ok(
                "- this operation deleted {} signals".format(
                    signals_before - signals_after
                )
            )
            if do_delete and config.backup_landing_zone:
                _record_delete(
                        "delete_meta",
                    config,
                    (do_delete, max_rows, what, name),
                )
                print_ok("- recorded deletion.")

        if not do_delete:
            print_ok("- use '--force --force' to delete {}".format(name))
        return exit_code


def _delete_source(
    session, name, do_delete, max_rows, landing_zone_root, print_ok, print_err
):
    source = _check_one_exists(
        "source", session, SourceDbo, SourceDbo.name, name, print_err
    )

    print_ok("- following source found in database:")
    print_ok(pretty_str(source, indent="  "))

    yaml_path = _find_unique(
        landing_zone_root, find_source_yaml, _match_name(name), print_err
    )
    if max_rows:
        _list_matching_signals(
            session,
            SourceDbo,
            SignalDbo.source_id == source.source_id,
            max_rows,
            print_ok,
        )
    _list_affected_files(yaml_path, print_ok, print_err)

    if not do_delete:
        return 0

    _delete_related_signals(
        session, SourceDbo, SignalDbo.source_id == source.source_id, print_ok
    )
    for averaging in source.averaging:
        session.delete(averaging)
    session.delete(source)
    _remove_yaml_including_folders(yaml_path, print_ok, print_err)
    session.commit()
    return 0


def _delete_source_type(
    session, name, do_delete, max_rows, landing_zone_root, print_ok, print_err
):
    source_type = _check_one_exists(
        "source_type", session, SourceTypeDbo, SourceTypeDbo.name, name, print_err
    )

    print_ok("- following source type found in database:")
    print_ok(pretty_str(source_type, indent="  "))

    if source_type.sources:
        print_err(
            "can not delete this source type, please delete the following sources first:"
        )
        for source in source_type.sources:
            print_err("  " + source.name)
        return 1

    yaml_path = _find_unique(
        landing_zone_root, find_source_type_yaml, _match_name(name), print_err
    )
    _list_affected_files(yaml_path, print_ok, print_err)

    if not do_delete:
        return 0

    session.delete(source_type)
    _remove_yaml_including_folders(yaml_path, print_ok, print_err)
    session.commit()
    return 0


def _delete_site(
    session, name, do_delete, max_rows, landing_zone_root, print_ok, print_err
):

    site = _check_one_exists("site", session, SiteDbo, SiteDbo.name, name, print_err)

    print_ok("- following site found in database:")
    print_ok(pretty_str(site, indent="  "))

    yaml_path = _find_unique(
        landing_zone_root, find_site_yaml, _match_name(name), print_err
    )
    if max_rows:
        _list_matching_signals(
            session, SiteDbo, SiteDbo.name == name, max_rows, print_ok
        )
    _list_affected_files(yaml_path, print_ok, print_err)

    if not do_delete:
        return 0

    # delete in right order:
    for picture in site.pictures:
        session.delete(picture)
    _delete_related_signals(
        session, SiteDbo, SignalDbo.site_id == site.site_id, print_ok
    )
    session.delete(site)

    _remove_yaml_including_folders(yaml_path, print_ok, print_err)
    session.commit()
    return 0


def _delete_parameter(
    session, name, do_delete, max_rows, landing_zone_root, print_ok, print_err
):
    parameter = _check_one_exists(
        "parameter", session, ParameterDbo, ParameterDbo.name, name, print_err
    )

    print_ok("- following parameter found in database:")
    print_ok(pretty_str(parameter, indent="  "))

    if parameter.averaging:
        print_err(
            "- the following source(s) have averaging setttings refering to '{}'".format(
                name
            )
        )
        for averaging in parameter.averaging:
            print_err(" - {}".format(averaging.source.name))
        return 1

    yaml_path = _find_unique(
        landing_zone_root, find_parameters_yaml, lambda obj: True, print_err
    )

    if max_rows:
        _list_matching_signals(
            session, ParameterDbo, ParameterDbo.name == name, max_rows, print_ok
        )

    if not do_delete:
        return 0

    _delete_related_signals(
        session,
        ParameterDbo,
        SignalDbo.parameter_id == parameter.parameter_id,
        print_ok,
    )
    session.delete(parameter)
    _rewrite_yaml_with_parameter_removed(name, yaml_path)
    session.commit()
    return 0


def _rewrite_yaml_with_parameter_removed(name, yaml_path):
    # ruamel.yaml preserves layout of input file when dumping, see
    # https://stackoverflow.com/questions/20805418/pyyaml-dump-format#answer-36760452
    from ruamel import yaml

    parameters = yaml.load(open(yaml_path).read(), Loader=yaml.RoundTripLoader)

    parameters = [p for p in parameters if p["name"] != name]
    with open(yaml_path, "w") as fh:
        print(yaml.dump(parameters, Dumper=yaml.RoundTripDumper), end="", file=fh)


def _check_one_exists(what, session, dbo, field, name, print_err):
    dbos = session.query(dbo).filter(field == name).all()
    num_found = len(dbos)
    if not num_found:
        print_err("- no {} named '{}' in database".format(what, name))
        raise FailedError()
    if num_found > 1:
        print_err("- multiple {}s named '{}' in database".format(what, name))
        raise FailedError()
    return dbos[0]


def _match_name(name):
    return lambda obj: obj.name == name


def _find_unique(root, find_function, checker, print_err):
    p = find_function(root, checker)
    if len(p) == 1:
        return p[0]
    if not p:
        print_err("- cound not find readable and matching yaml file in {}".format(root))
    if len(p) > 1:
        print_err("- found multiple yaml files in {}".format(root))
        for pi in p:
            print_err("  {}".format(pi))
    raise FailedError()


def _list_matching_signals(session, joined_dbo, dbo_filter, max_rows, print_ok):

    q = session.query(SignalDbo).join(joined_dbo).filter(dbo_filter)
    _print_signals(q, max_rows, print_ok)


def _count_signals(session):
    return session.query(SignalDbo).count()


def _iter_yaml_including_folders(yaml_path):
    folder = os.path.dirname(yaml_path)
    # bottom up traversal to make sure folders and files are removed before # parents:
    for base_path, directories, files in reversed(list(os.walk(folder, topdown=True))):
        for file_ in sorted(files):
            yield "file", os.path.join(base_path, file_)
        for directory in sorted(directories):
            yield "folder", os.path.join(base_path, directory)
    yield "folder", folder


def _remove_yaml_including_folders(yaml_path, print_ok, print_err):
    handlers = {"file": os.remove, "folder": os.rmdir}

    for type_, path in _iter_yaml_including_folders(yaml_path):
        try:
            handlers[type_](path)
            print_ok("- removed {}".format(path))
        except IOError as e:
            print_err(
                "- could not remove {}, reason: {}".format(os.path.abspath(path), e)
            )
            raise FailedError()


def _list_affected_files(yaml_path, print_ok, print_err):
    print_ok("- the following files and folders will be deleted in this order:")
    for type_, path in _iter_yaml_including_folders(yaml_path):
        print_ok("  {}".format(path + ("" if type_ == "file" else "/")))


def _delete_related_signals(session, join_dbo, filter_, print_ok):
    signal_ids_query = session.query(SignalDbo.signal_id).join(join_dbo).filter(filter_)
    _delete_associations(session, signal_ids_query)

    del_q = session.query(SignalDbo).filter(
        SignalDbo.signal_id.in_(signal_ids_query.subquery())
    )

    count = del_q.delete(synchronize_session="fetch")
    print_ok("- deleted {} rows from table 'signal'".format(count))


def _delete_associations(session, signal_ids_query):
    for association in (
        session.query(SignalCommentAssociation)
        .filter(SignalCommentAssociation.signal_id.in_(signal_ids_query.subquery()))
        .all()
    ):
        session.delete(association)

    for association in (
        session.query(SignalSignalQualityAssociation)
        .filter(
            SignalSignalQualityAssociation.signal_id.in_(signal_ids_query.subquery())
        )
        .all()
    ):
        session.delete(association)
