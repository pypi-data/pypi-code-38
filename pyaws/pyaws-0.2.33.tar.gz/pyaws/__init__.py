import os
from pyaws._version import __version__ as version
from pyaws import environment


__author__ = 'Blake Huber'
__version__ = version
__credits__ = []
__license__ = "GPL-3.0"
__maintainer__ = "Blake Huber"
__email__ = "blakeca00@gmail.com"
__status__ = "Development"


## the following imports require __version__  ##

from pyaws.colors import Colors
from pyaws import logd 

PACKAGE = 'pyaws'
enable_logging = True
log_mode = 'STREAM'          # log to cloudwatch logs
log_filename = 'pyaws.log'
log_dir = os.getenv('HOME') + '/logs'
log_path = log_dir + '/' + log_filename


log_config = {
    "PROJECT": {
        "PACKAGE": PACKAGE,
        "CONFIG_VERSION": __version__,
    },
    "LOGGING": {
        "ENABLE_LOGGING": enable_logging,
        "LOG_FILENAME": log_filename,
        "LOG_DIR": log_dir,
        "LOG_PATH": log_path,
        "LOG_MODE": log_mode,
        "SYSLOG_FILE": False
    }
}

# shared, global logger object
logger = logd.getLogger(__version__)
