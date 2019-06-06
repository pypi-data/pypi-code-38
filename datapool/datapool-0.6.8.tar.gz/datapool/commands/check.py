import contextlib
import fnmatch
import glob
import os
import shutil
import tempfile
import time
from os.path import exists, join

import datapool.instance.db_objects
from datapool.data_conversion import ConversionRunner
from datapool.instance.config_handling import (config_for_develop_db,
                                               read_config)
from datapool.instance.domain_objects_checker import DomainObjectsChecker
from datapool.instance.landing_zone_structure import (all_file_patterns,
                                                      required_folders,
                                                      source_type_yaml_for_source_yaml,
                                                      source_yaml_path_for_script)
from datapool.instance.signal_model import (check_fields,
                                            check_signals_against_db,
                                            check_signals_uniqueness)
from datapool.instance.uniform_file_format import to_signals
from datapool.instance.yaml_parsers import parse_source

from ..database import check_if_tables_exist, connect_to_db, copy_db, setup_db
from ..errors import (DataPoolException, InvalidLandingZone,
                      InvalidOperationError)
from ..landing_zone import LandingZone
from ..logger import get_cmdline_logger
from ..utils import enumerate_filename, print_signals


def _setup(print_err, landing_zone, **kw):

    config = read_config(**kw)
    if config is None:
        print_err("- no config file found. please run 'pool init-config' first.")
        return None, None

    if not exists(landing_zone):
        print_err("  - folder {} does not exist".format(landing_zone))
        return None, None
    try:
        lz = LandingZone(landing_zone)
    except InvalidLandingZone as e:
        print_err("  - landing zone at {} invalid. reason: {}".format(landing_zone, e))
        return None, None
    return config, lz


def check(landing_zone, result_folder, verbose, print_ok, print_err, run_twice=True):

    config, lz = _setup(print_err, landing_zone)
    if config is None or lz is None:
        return 1

    print_ok(
        "- check names and places of changed files at landing zone {}".format(
            landing_zone
        )
    )
    all_changed_files = set(lz.list_new_and_changed_files())
    __, unknown_files = lz.separate_allowed_files(all_changed_files)

    if not unknown_files:
        print_ok("- all filenames comply specification.")
    else:
        for unknown_file in unknown_files:
            print_err("- do not know how to handle file at {}".format(unknown_file))

    with get_cmdline_logger(verbose):
        with _setup_test_db(
            landing_zone, config, verbose, print_ok, print_err
        ) as engine:

            folders_ok = _run_folder_checks(lz, print_ok, print_err)
            if folders_ok:
                print_ok("+ folder structure is ok")
            else:
                print_err("+ folder structure is corrupted")

            files_ok = _run_file_checks(lz, print_ok, print_err)
            if files_ok:
                print_ok("+ file names and their locations are ok")
            else:
                print_err("+ invalid file names or misplaced files found")

            yamls_ok = _run_yaml_checks(lz, engine, print_ok, print_err, verbose)
            if yamls_ok:
                print_ok("- all yaml are ok")
            else:
                print_err("+ detected problems in yaml files")

            found_errors = not (folders_ok and files_ok and yamls_ok)

            if not found_errors:

                print_ok("")
                print_ok("- check scripts landing zone at {}".format(landing_zone))
                found_errors = _run_script_checks(
                    lz,
                    engine,
                    config,
                    result_folder,
                    verbose,
                    run_twice,
                    print_ok,
                    print_err,
                )

    if found_errors:
        print_err("")
        print_err("+ checks failed. please fix this.")
        return 1

    print_ok("")
    print_ok("- all scripts checked")
    print_ok("+ congratulations: all checks succeeded.", fg="green")
    return 0


def _run_script_checks(
    lz, engine, config, result_folder, verbose, run_twice, print_ok, print_err
):

    runner = ConversionRunner(config)
    result_folder = _setup_result_folder(result_folder, print_ok, print_err)

    changed_files = lz.list_new_and_changed_files()

    all_signals = []
    found_errors = False

    def _check(script_path, data_path, read_source):

        nonlocal found_errors

        if script_path not in changed_files:
            print_ok(
                "- skip conversion of {} by {}. script is unchanged".format(
                    data_path, script_path
                )
            )
            return

        if data_path is None:
            found_errors = True
            print_err(
                "- conversion script changed but no raw data file for {}".format(
                    script_path
                )
            )
            return

        print_ok("")
        print_ok("- check {} on {}".format(script_path, data_path))

        if read_source:
            source = _load_source(lz, script_path, print_err)
            if source is None:
                found_errors = True
                return
            allowed_sources = None
        else:
            source = None
            allowed_sources = _allowed_sources(lz, script_path, print_err)

        for i in range(2 if run_twice else 1):
            do_backup = i == 0

            ok, needed_conv, signals = _check_conversion(
                runner,
                lz,
                script_path,
                data_path,
                verbose,
                result_folder,
                source,
                allowed_sources,
                do_backup,
                print_ok,
                print_err,
            )
            if i == 0:
                if signals is not None:
                    all_signals.extend(signals)

            if not ok:
                found_errors = True
                return
            else:
                print_ok(
                    "  - {} conversion needed {:.0f} msec".format(
                        "first" if i == 0 else "second", needed_conv * 1000
                    )
                )

    for script_path, data_path in lz.source_type_based_conversion_scripts_and_data():
        _check(script_path, data_path, False)

    for script_path, data_path in lz.conversion_scripts_and_data():
        _check(script_path, data_path, True)

    if found_errors:
        return found_errors

    print_ok("")
    print_ok("- check signals integrity")
    found_errors = _report(check_signals_uniqueness(all_signals), print_err)
    if not found_errors:
        print_ok("- check signals against db")
        found_errors = _report(check_signals_against_db(all_signals, engine), print_err)
    return found_errors


def _load_source(lz, script_path, print_err):
    source_path = source_yaml_path_for_script(script_path)

    source = None
    for result in parse_source(lz.root_folder, source_path):
        if isinstance(result, DataPoolException):
            print_err("  - parsing {}: {}".format(source_path, result))
        else:
            source = result

    return source


def _allowed_sources(lz, script_path, print_err):
    # assumes that the script is related to source_type, not source.

    source_path = source_yaml_path_for_script(script_path)
    source_type_folder = os.path.dirname(source_path)

    source_names = set()
    for abs_source_path in glob.glob(
        os.path.join(lz.root_folder, source_type_folder, "*", "source.yaml")
    ):
        source_path = os.path.relpath(abs_source_path, lz.root_folder)
        for result in parse_source(lz.root_folder, source_path):
            if isinstance(result, DataPoolException):
                print_err("  - parsing {}: {}".format(source_path, result))
            else:
                source_names.add(result["name"])
    return source_names


def _check_conversion(
    runner,
    lz,
    script_path,
    data_path,
    verbose,
    result_folder,
    source,
    allowed_sources,
    backup_results,
    print_ok,
    print_err,
):

    # check exclusive or for source and allowed_sources
    assert source is not None or allowed_sources is not None
    assert source is None or allowed_sources is None

    signals = None

    must_specify_source = source is None

    started = time.time()
    for result in runner.check_conversion(
        lz.p(script_path),
        lz.p(data_path),
        status_callback=False,
        verbose=verbose,
        must_specify_source=must_specify_source,
    ):
        if isinstance(result, Exception):
            print_err("  - {}".format(result))
        else:
            output_file, rows = result
            signals = to_signals(rows)

    if signals is None:
        return False, 0, signals

    needed_conv = time.time() - started

    if source is not None:
        for signal_ in signals:
            signal_.source = source.name

    if allowed_sources is not None:
        reported = set()
        for signal_ in signals:
            if signal_.source in reported:
                continue
            if signal_.source not in allowed_sources:
                print_err(
                    (
                        "  - {} source entry '{}' is not allowed "
                        "for the corresponding source type"
                    ).format(script_path, signal_.source)
                )
                reported.add(signal_.source)
        if reported:
            return False, 0, signals

    if backup_results:
        _backup_results(result_folder, output_file, signals, script_path, print_ok)

    has_errors = _report(check_fields(signals), print_err)
    return not has_errors, needed_conv, signals


def _report(check_iter, print_err):
    error_count = 0
    has_errors = False
    exceptions = [result for result in check_iter if isinstance(result, Exception)]
    MAX_ERR = 10
    for exception in exceptions:
        print_err("  - {}".format(exception))
        error_count += 1
        has_errors = True
        if error_count > MAX_ERR:
            print_err(
                "  - too many errors, skipped {} errors.".format(
                    len(exceptions) - MAX_ERR
                )
            )
            break
    return has_errors


def _setup_result_folder(result_folder, print_ok, print_err):

    if not result_folder:
        result_folder = tempfile.mkdtemp()
    else:
        if os.path.exists(result_folder):
            if not os.path.isdir(result_folder):
                print_err(
                    "+ given path {} exists but is not a folder".format(result_folder)
                )
                return 1
        else:
            os.makedirs(result_folder)
            print_ok("- created folder {}".format(result_folder))

    return result_folder


def _backup_results(result_folder, output_file, signals, script, print_ok):
    script_folder_name = os.path.basename(os.path.dirname(script))
    csv_path = join(result_folder, script_folder_name) + ".csv"
    txt_path = join(result_folder, script_folder_name) + ".txt"

    csv_path, txt_path = enumerate_filename(csv_path, txt_path)
    shutil.copy(output_file, csv_path)
    print_ok("  - wrote conversion result as csv to {}".format(csv_path))
    with open(txt_path, "w") as fh:
        print_signals(signals, file=fh)
    print_ok("  - wrote conversion result as txt to {}".format(txt_path))


@contextlib.contextmanager
def _setup_test_db(landing_zone, config, verbose, print_ok, print_err):

    config_develop_db, path = config_for_develop_db(landing_zone)

    if os.path.exists(path):
        os.unlink(path)

    ok = False
    try:
        ok = check_if_tables_exist(config.db)
    except InvalidOperationError:
        print_err("- could not connect to productive db.")
    if not ok:
        print_err(
            "- setup fresh development db. productive does not exist or is empty."
        )
        setup_db(config_develop_db, verbose=verbose)

    else:
        print_ok("- copy meta data from productive db")
        for table_name in copy_db(
            config.db,
            config_develop_db,
            delete_existing=True,
            dont_copy=set(_tables_to_skip_for_copy()),
            verbose=verbose,
        ):
            print_ok("  - copy table {}".format(table_name))

    engine = connect_to_db(config_develop_db)

    yield engine

    os.unlink(path)
    engine.dispose()


def _tables_to_skip_for_copy():
    dbos = datapool.instance.db_objects
    for dbo in (
        dbos.QualityDbo,
        dbos.SignalQualityDbo,
        dbos.SignalCommentAssociation,
        dbos.SignalSignalQualityAssociation,
        dbos.CommentDbo,
        dbos.SignalDbo,
        dbos.ProjectDbo,
    ):
        yield dbo.__tablename__


def _run_folder_checks(lz, print_ok, print_err):
    print_ok("")
    print_ok("- check folder structure")
    ok = True
    for folder in required_folders(lz.root_folder):
        rel_folder = os.path.relpath(folder, lz.root_folder)
        if not os.path.exists(folder):
            print_err("  - {} does not exist".format(rel_folder))
            ok = False
        elif not os.path.isdir(folder):
            rel_folder = os.path.relpath(folder, lz.root_folder)
            print_err("  - {} is not a folder".format(rel_folder))
            ok = False
        else:
            print_ok("  - {} exists and is a folder".format(rel_folder))

    return ok


def _run_file_checks(lz, print_ok, print_err):

    # we assume that folder structure itself is valid, we only check
    # files by their name and location within the folder structure.
    print_ok("")
    print_ok("- check files")
    ok = True
    for path in glob.glob(os.path.join(lz.root_folder, "**"), recursive=True):
        if os.path.isdir(path):
            continue
        rel_path = os.path.relpath(path, lz.root_folder)
        for pattern in all_file_patterns:
            if fnmatch.fnmatch(rel_path, pattern):
                break
        else:
            print_err("  - {} not allowed".format(rel_path))
            ok = False
    return ok


def _run_yaml_checks(lz, engine, print_ok, print_err, verbose):

    new_yamls = []
    for rel_path in lz.list_all_files():
        if not rel_path.endswith(".yaml"):
            continue
        new_yamls.append(rel_path)

    print_ok("")
    if not new_yamls:
        print_ok("- no yaml files detected. skip checks.")
        return True

    print_ok("- detected {} yaml files:".format(len(new_yamls)))
    for rel_path in new_yamls:
        print_ok("  - {}".format(lz.p(rel_path)))

    print_ok("")
    print_ok("- check yaml files")
    checker = DomainObjectsChecker(lz.root_folder, new_yamls)
    ok = True
    for error in checker.check_all(engine):
        print_err("  - got error: {}".format(error))
        ok = False

    return ok
