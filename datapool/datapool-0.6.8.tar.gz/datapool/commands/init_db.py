from datapool.instance.config_handling import read_config

from ..database import check_if_tables_exist, setup_db, setup_fresh_db
from ..errors import InvalidOperationError
from ..logger import get_cmdline_logger


def init_db(reset, verbose, print_ok, print_err):
    """creates empty tables in configured database, can be used to delete data from an
    existing database.
    """

    with get_cmdline_logger(verbose):

        config = read_config()
        if config is None:
            print_err("+ no config file found. please run 'pool init' first.")
            return 1

        try:
            already_exists = check_if_tables_exist(config.db)
        except InvalidOperationError as e:
            print_err("+ can not check database: {}".format(e))
            return 1
        if already_exists:
            if reset:
                setup_fresh_db(config.db, verbose=verbose)
            else:
                print_err(
                    "+ database is already initialized, use --force TWICE to setup a "
                    "fresh and empty database. YOU WILL LOOSE ALL EXISTING DATA !!!"
                )
                return 1
        else:
            setup_db(config.db, verbose=verbose)

        print_ok("+ intialized db", fg="green")
        return 0
