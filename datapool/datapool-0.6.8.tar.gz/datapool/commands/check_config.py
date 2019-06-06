from ..logger import get_cmdline_logger, check_logging_config
from datapool.instance.config_handling import check_config as _check_config, read_config


def check_config(print_ok, print_err, verbose=False):
    """checks if current configuration is valid, eg if database access is possible, or
    if matlab can be started.
    """

    config = read_config()
    if config is None:
        print_err("- no config file found. please run 'pool init-config' first.")
        return 1

    if config is None:
        print_err("- no config file found. please run 'pool init-config' first.")
        return 1

    print_ok("- check settings in config file {}".format(config.__file__))
    try:
        check_logging_config(config)
    except Exception as e:
        print_err("- could not setup logger. hint: {}".format(e))
        return 1

    with get_cmdline_logger(verbose):
        overall_ok = True
        for ok, message in _check_config(config):
            if ok:
                print_ok(message)
            else:
                print_err(message)
                overall_ok = False
    if overall_ok:
        print_ok("+ all checks passed", fg="green")
    else:
        print_err("+ at least on check failed")
    return 0 if overall_ok else 1
