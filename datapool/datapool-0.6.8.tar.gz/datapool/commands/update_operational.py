import time

from datapool.instance.config_handling import read_config

from ..errors import DataPoolException, InvalidLandingZone
from ..landing_zone import LandingZone, write_lock
from ..utils import is_server_running
from .check import check


def update_operational(
    development_landing_zone, verbose, overwrite, copy_raw, print_ok, print_err
):

    config = read_config()
    if config is None:
        print_err("- no config file found. please run 'pool init-config' first.")
        return 1

    operational_landing_zone = config.landing_zone.folder
    if not is_server_running(config):
        print_err("- datapool server is not running.")
        return 1

    print_ok("- datapool server is running.")

    try:
        lz = LandingZone(development_landing_zone)
    except InvalidLandingZone as e:
        print_err(
            "  - landing zone at {} invalid. reason: {}".format(
                development_landing_zone, e
            )
        )
        return 1

    messages = []

    try:
        messages = lz.check_before_update_operational(operational_landing_zone)
    except DataPoolException as e:
        print_err("+ {}".format(e))
        return 1

    if messages:
        for message in messages:
            print_err("  - problem: {}".format(message))
            print_ok("  - will ignore these and overwrite existing files")
    else:
        print_ok("- development landing zone seems to be sane.")

    with write_lock(operational_landing_zone) as got_lock:

        if not got_lock:
            print_err(
                "+ {} is locked. maybe somebody else works on it simultaneously ?".format(
                    operational_landing_zone
                )
            )
            return 1

        exit_code = check(
            development_landing_zone, None, verbose, print_ok, print_err, False
        )
        if exit_code != 0:
            print_err("+ don't update {}".format(operational_landing_zone))
            return 1

        try:
            files_generator = lz.update_operational(
                operational_landing_zone,
                copy_raw,
                raw_file_patterns=(
                    "data/*/*/raw_data/data*.raw",
                    "data/*/raw_data/data*.raw",
                ),
                delay=0.5,
            )
        except DataPoolException as e:
            print_err("- update failed:")
            print_err("- {}".format(e))
            return 1

        num_files = 0
        for action, file in files_generator:
            print_ok("- {} {}".format(action, file))
            time.sleep(.5)
            num_files += 1
        print_ok(
            "+ copied/created {} files/folders to/in {}".format(
                num_files, operational_landing_zone
            ),
            fg="green",
        )
        return 0
