from os.path import abspath, exists

from ..logger import get_cmdline_logger


def init_config(landing_zone, sqlite_db, reset, print_ok, print_err, verbose=False):
    """setup minimal landing zone and create default configuration """

    from datapool.instance.config_handling import init_config as init_config_

    with get_cmdline_logger(verbose):

        if not exists(landing_zone):
            print_err("+ folder {} does not exist".format(landing_zone))
            return 1
        print_ok("- guess settings")
        try:
            landing_zone = abspath(landing_zone)
            config_folder, messages = init_config_(
                landing_zone, sqlite_db, overwrite=reset
            )
            for message in messages:
                print_err("  - {}".format(message))
            print_ok("- created config files at {}".format(config_folder))
            print_ok(
                "  please edit these files and adapt the data base configuration to your setup"
            )
        except Exception as e:
            print_err("+ something went wrong: {}".format(e))
            return 1

        return 0
