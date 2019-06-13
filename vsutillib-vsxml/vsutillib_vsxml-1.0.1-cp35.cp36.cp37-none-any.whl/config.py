"""
vsutillib version and configuration constants

config can be use by other applications

import vsutillib.config as config

config.init(configFile='appName-config.xml',
            filesRoot='.appName',
            logFile='file.log',
            name='appName',
            version='1.0')

and

config.close()

config.data is files.ConfigurationSettings class instance

before application exit
"""

import logging
import sys
from pathlib import Path

from vsutillib.files import ConfigurationSettings
from vsutillib.log import LogRotateFileHandler

data = ConfigurationSettings()  # pylint: disable=invalid-name

__VERSION = (1, 0, '1')

VERSION = ".".join(map(str, __VERSION))
AUTHOR = "Efrain Vergara"
EMAIL = "akai10tsuki@gmail.com"

COPYRIGHT = "2018-2019, Efrain Vergara"
LICENSE = "MIT"
DESCRIPTION = 'Library module with miscellaneous convenience functions and classes'
NAME = "vsutillib"
KEYWORDS = 'mkv multimedia video audio configuration'
REQUIRED = [
    'vsutillib-files>=1.0.1',
    'vsutillib-log>=1.0.1',
    'vsutillib-macos>=1.0.1',
    'vsutillib-media>=1.0.1',
    'vsutillib-mkv>=1.0.1'
    'vsutillib-network>=1.0.1',
    'vsutillib-process>=1.0.1',
    'vsutillib-pyqt>=1.0.1',
    'vsutillib-scripts>=1.0.1'
    'vsutillib-vsxml>=1.0.1',
]
URL = 'https://github.com/akai10tsuki/vsutillib'
PYPI = 'https://pypi.org/project/mkvbatchmultiplex/'
PROJECTURLS = {
    'Bug Reports': 'https://pypi.org/project/vsutillib/#files',
    'Source': 'https://pypi.org/project/vsutillib/#files',
}

IMAGEFILESPATH = ""
FILESROOT = ".vsutillib"
LOGFILE = "vsutillib.log"
CONFIGFILE = "config.xml"

__version__ = VERSION


def init(filesRoot=None,
         configFile=None,
         logFile=None,
         name=None,
         version=None):
    """
    configures the system to save application configuration to xml file

    Args:
        filesRoot (str, optional): root folder on ~ for files. Defaults to [.vsutillib].
        configFile (str, optional): name of configuration file. Defaults to [config.xml].
        logFile (str, optional): name of logging file. Defaults to [vsutillib.log].
        name (str, optional): name of application. Defaults to [vsutillib].
        version (str, optional): appplication version . Defaults to [vsutillib version].
    """

    if filesRoot is None:
        filesPath = Path(Path.home(), FILESROOT)
    else:
        filesPath = Path(Path.home(), filesRoot)

    filesPath.mkdir(parents=True, exist_ok=True)

    if configFile is None:
        cfgFile = Path(filesPath, CONFIGFILE)
    else:
        cfgFile = Path(filesPath, configFile)

    data.setConfigFile(cfgFile)
    data.readFromFile()

    if logFile is None:
        loggingFile = Path(filesPath, LOGFILE)
    else:
        loggingFile = Path(filesPath, logFile)

    loghandler = LogRotateFileHandler(loggingFile, backupCount=10)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s %(message)s")
    loghandler.setFormatter(formatter)

    logging.getLogger('').setLevel(logging.DEBUG)
    logging.getLogger('').addHandler(loghandler)
    logging.info("App Start.")
    logging.info("Python: %s", sys.version)

    if name is None:
        appName = NAME
    else:
        appName = name

    if version is None:
        appVersion = VERSION
    else:
        appVersion = version

    logging.info("%s-%s", appName, appVersion)


def close():
    """
    save configuration to file and write end message to log file
    """
    data.saveToFile()

    logging.info("App End.")
