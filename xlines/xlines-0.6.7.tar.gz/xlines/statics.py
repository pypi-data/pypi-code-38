"""
Summary:
    xlines Project-level Defaults and Settings

Module Attributes:
    - user_home (TYPE str):
        $HOME environment variable, present for most Unix and Unix-like POSIX systems
    - config_dir (TYPE str):
        directory name default for stsaval config files (.stsaval)
    - config_path (TYPE str):
        default for stsaval config files, includes config_dir (~/.stsaval)
    - key_deprecation (TYPE str):
        Deprecation logic that xlines uses when 2 keys exist for a user.
"""

import os
import inspect
import logging
from xlines.common import read_local_config, get_os, os_parityPath
from xlines._version import __version__

logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)


# --  project-level DEFAULTS  ------------------------------------------------


try:

    env_info = get_os(detailed=True)
    OS = env_info['os_type']
    user_home = env_info['HOME']

except KeyError as e:
    logger.critical(
        '%s: %s variable is required and not found in the environment' %
        (inspect.stack()[0][3], str(e)))
    raise e
else:
    # local vars -- this section executes as default; if windows, execute diff
    # section with appropriate pathnames

    # project
    PACKAGE = 'xlines'
    LICENSE = 'GPL v3'
    LICENSE_DESC = 'General Public License v3'
    version = __version__

    # config parameters
    config_dir = '.config'
    config_subdir = PACKAGE
    config_filename = 'xlinesconf.json'
    config_dirpath = user_home + '/' + config_dir + '/' + config_subdir
    config_path = config_dirpath + '/' + config_filename

    # output format
    count_column_width = 7                                    # characters
    min_buffer_chars = 6                                      # characters
    min_width = 80 - count_column_width - min_buffer_chars    # characters
    count_threshold = 1000                                    # number of lines of text

    # exclusions
    ext_filename = 'exclusions.list'
    dir_filename = 'directories.list'

    # logging parameters
    enable_logging = False
    log_mode = 'FILE'
    log_filename = 'xlines.log'
    log_dir = user_home + '/' + 'logs'
    log_path = log_dir + '/' + log_filename

    if OS == 'Windows':
        config_path = os_parityPath(config_path)
        log_path = os_parityPath(log_path)

    seed_config = {
        "PROJECT": {
            "PACKAGE": PACKAGE,
            "PACKAGE_VERSION": version,
            "HOME": user_home
        },
        "CONFIG": {
            "CONFIG_DATE": "",
            "CONFIG_FILENAME": config_filename,
            "CONFIG_DIR": config_dirpath,
            "CONFIG_SUBDIR": config_subdir,
            "CONFIG_PATH": config_path
        },
        "EXCLUSIONS": {
            "EX_FILENAME": ext_filename,
            "EX_DIR_FILENAME": dir_filename,
            "EX_EXT_PATH": config_dirpath + '/' + ext_filename,
            "EX_DIR_PATH": config_dirpath + '/' + dir_filename
        },
        "LOGGING": {
            "ENABLE_LOGGING": enable_logging,
            "LOG_FILENAME": log_filename,
            "LOG_PATH": log_path,
            "LOG_MODE": log_mode,
            "SYSLOG_FILE": False
        },
        "OUTPUT": {
            "MIN_WIDTH": min_width,
            "COUNT_COLUMN_WIDTH": count_column_width,
            "COUNT_HI_THRESHOLD": count_threshold,
            "BUFFER":  min_buffer_chars
        }
    }

try:
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
        os.chmod(log_dir, 0o755)
    if os.path.exists(config_path):
        # parse config file
        local_config = read_local_config(cfg=config_path)
        # fail to read, set to default config
        if not local_config:
            local_config = seed_config
    else:
        local_config = seed_config

except OSError as e:
    logger.exception(
        '%s: Error when attempting to access or create local log and config %s' %
        (inspect.stack()[0][3], str(e))
    )
    raise e
