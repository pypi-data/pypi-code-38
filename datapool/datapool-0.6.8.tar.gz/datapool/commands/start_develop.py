import os
import shutil
from os.path import exists

from datapool.instance.config_handling import read_config

from ..landing_zone import LandingZone
from ..logger import get_cmdline_logger


def _setup_landing_zone(
    development_landing_zone,
    operational_landing_zone,
    is_first_time,
    reset,
    print_ok,
    print_err,
):

    print_ok("- setup development landing zone")
    if exists(development_landing_zone):
        if not reset:
            print_err("  - folder {} already exists.".format(development_landing_zone))
            return 1
        else:
            try:
                shutil.rmtree(development_landing_zone)
            except Exception as e:
                print_err(
                    "  - could not delete folder {}".format(
                        os.path.abspath(development_landing_zone)
                    )
                )
                print_err("  - error message is: {}".format(e))
                return 1

    try:
        if is_first_time:
            print_ok(
                "- operational landing zone is empty. you might use 'pool create-example' "
                "to see how to setup an initial landing zone."
            )
            LandingZone.create_empty(development_landing_zone)
        else:
            print_ok("- copy files from operational landing zone.")
            LandingZone.create_from(development_landing_zone, operational_landing_zone)
    except IOError as e:
        print_err("- something went wrong: {}".format(e))
        return 1
    return 0


def start_develop(development_landing_zone, reset, verbose, print_ok, print_err):
    """Creates local landing zone for integrating new devices, conversion scripts etc.
    either the configured operational landing zone is cloned or example files are
    written to the local landing zone.

    Also creates a local sqlite database.

    if "reset" is True existing folders and database will be overwritten.
    """

    config = read_config(DEVELOPZONE=development_landing_zone)
    if config is None:
        print_err("- no config file found. please run 'pool init-config' first.")
        return 1

    operational_landing_zone = config.landing_zone.folder

    if not exists(operational_landing_zone):
        print_err(
            "+ configured landing zone {} does not exist".format(
                operational_landing_zone
            )
        )
        return 1

    try:
        files = os.listdir(operational_landing_zone)
        files = [f for f in files if not f.startswith(".")]
        is_first_time = files == []
    except IOError as e:
        print_err("+ can not read {}: {}".format(operational_landing_zone, e))
        return 1

    with get_cmdline_logger(verbose):
        exit_code = _setup_landing_zone(
            development_landing_zone,
            operational_landing_zone,
            is_first_time,
            reset,
            print_ok,
            print_err,
        )

    if exit_code:
        print_err("+ setup failed")
    else:
        print_ok("+ setup done", fg="green")
    return exit_code
