"""
Summary:
    Project-level Defaults and Settings:  ec2tools

    - **Local Default Settings**: Local defaults for your specific installation are derived from settings found in:

Module Attributes:
    - user_home (TYPE str):
        $HOME environment variable, present for most Unix and Unix-like POSIX systems
    - config_dir (TYPE str):
        directory name default for stsaval config files (.stsaval)
    - config_path (TYPE str):
        default for stsaval config files, includes config_dir (~/.stsaval)
"""
import os
import inspect
import logging
from ec2tools import __version__
from pyaws.script_utils import get_os, os_parityPath, read_local_config


logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)

# --  project-level DEFAULTS  ------------------------------------------------


try:

    env_info = get_os(detailed=True)
    OS = env_info['os_type']
    user_home = env_info['HOME'] or os.getenv('HOME')

except KeyError as e:
    logger.critical(
        '%s: %s variable is required and not found in the environment' %
        (inspect.stack()[0][3], str(e)))
    raise e

else:
    # project
    PACKAGE = 'ec2tools'
    LICENSE = 'GPL-3'
    LICENSE_DESC = 'General Public License Version 3'

    # configuration info
    config_file = 'configuration.json'
    config_root = os_parityPath(user_home + '/' + '.config')
    config_dir = os_parityPath(config_root + '/' + PACKAGE)
    config_filepath = os_parityPath(config_dir + '/' + config_file)
    launchconfig_dir = os_parityPath(config_dir + '/launchconfigs')
    userdata_dir = os_parityPath(config_dir + '/userdata')

    # logging parameters
    enable_logging = True
    log_mode = 'STREAM'
    log_filename = PACKAGE + '.log'
    log_dir = os_parityPath(user_home + '/' + 'logs')
    log_path = os_parityPath(log_dir + '/' + log_filename)

    seed_config = {
        "PROJECT": {
            "PACKAGE": PACKAGE,
            "CONFIG_VERSION": __version__,
            "HOME": user_home,

        },
        "LOGGING": {
            "ENABLE_LOGGING": enable_logging,
            "LOG_FILENAME": log_filename,
            "LOG_PATH": log_path,
            "LOG_MODE": log_mode,
            "SYSLOG_FILE": False
        },
        "CONFIG": {
            "CONFIG_ROOT": config_root,
            "CONFIG_DIR": config_dir,
            "CONFIG_FILE": config_filepath,
            "LAUNCHCONFIG_DIR": launchconfig_dir,
            "USERDATA_DIR": userdata_dir
        }
    }

    try:

        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            os.chmod(config_dir, 0o755)

        elif os.path.exists(config_filepath):
            # parse config file
            local_config = read_local_config(cfg=config_filepath)
            # fail to read, set to default config
            if not local_config:
                local_config = seed_config

        elif not os.path.exists(config_filepath):
            local_config = seed_config

    except OSError as e:
        logger.exception(
            '%s: Error when attempting to access or create local log and config %s' %
            (inspect.stack()[0][3], str(e))
        )
        raise e
