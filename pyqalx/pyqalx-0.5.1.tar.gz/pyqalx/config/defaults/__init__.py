import logging
import os


TOKEN = ""
"""API token"""

LOGGING_LEVEL = logging._levelToName[logging.ERROR]
"""Level that we should log at by default. """

LOG_FILE_PATH = os.path.join(os.path.expanduser("~"), '.qalx.log')
"""The path where log files will be stored.
 
 .. note::
    The default value is evaluated on our build system. 
    Your default location will be ~/.qalx.log or %USERPROFILE%/.qalx.log"""

UNPACK_SET = True
"""Should the items in a set be de-referenced?"""

UNPACK_GROUP = False
"""Should the sets in a group be de-referenced?"""

UNPACK_BOT = True
"""Should the workers in a bot be de-referenced?"""

MSG_BLACKOUTSECONDS = 30
"""After this time in seconds the message will be returned to the queue if it has not been deleted.

.. note::
    Workers automatically issue a heartbeat to the queue while the job is being processed to keep extending 
    the blackout during processing
"""