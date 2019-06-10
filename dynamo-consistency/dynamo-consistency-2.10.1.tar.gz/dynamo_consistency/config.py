"""
Small module to get information from the config.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""


import os
import logging
import json

from . import opts


LOG = logging.getLogger(__name__)
LOCATION = opts.CONFIG or 'consistency_config.json'
"""
The string giving the location of the configuration JSON file.
Generally, you want to set this value of the module before calling
:py:func:`config_dict` to get your configuration.
"""

LOADER = json
"""
A module that uses the load function on a file descriptor to return a dictionary.
(Examples are the ``json`` and ``yaml`` modules.)
If your ``LOCATION`` is not a JSON file, you'll want to change this
also before calling :py:func:`config_dict`.
"""

DIRECTORYLIST = None
"""
If this is set to a list of directories, it overrides the
``DirectoryList`` set in the configuration file.
This prevents the tool from attempting to list directories that are not there.
"""

CONFIG = None

SITE = None
"""
A global place that stores a site that has been picked.
Set in :py:func:`dynamo_consistency.picker.pick_site`.
"""

def config_dict():
    """
    This only loads the configuration file the first time it is called

    :returns: the configuration file in a dictionary
    :rtype: str
    :raises IOError: when it cannot find the configuration file
    """

    # pylint: disable=global-statement

    global CONFIG
    global LOCATION
    global DIRECTORYLIST

    if CONFIG is None:

        location = LOCATION

        # If not there, fall back to the test directory
        # This is mostly so that Travis-CI finds a configuration on it's own
        if not os.path.exists(location):
            LOG.warning('Could not find file at %s. '
                        'Set the value of config.CONFIG_FILE to avoid receiving this message',
                        location)
            location = os.path.join(os.path.dirname(__file__),
                                    LOCATION)
            LOG.warning('Falling back to test configuration: %s', location)

        # If file exists, load it
        if os.path.exists(location):
            LOCATION = location
            with open(location, 'r') as config:
                LOG.debug('Opening config: %s', location)
                CONFIG = LOADER.load(config)
        else:
            raise IOError('Could not load config at %s' % location)

        # Overwrite any values with environment variables
        for key in CONFIG.keys():
            CONFIG[key] = os.environ.get(key, CONFIG[key])

    # If DIRECTORYLIST set, overwrite previous entry
    if DIRECTORYLIST:
        CONFIG['DirectoryList'] = DIRECTORYLIST
        # Only do this writing once
        DIRECTORYLIST = None

    return CONFIG


def vardir(directory):
    """
    Gets the full path to a sub directory inside of **VarLocation**
    and creates an empty directory if needed.

    :param str directory: A desired sub-directory
    :returns: Path to configured sub-directory
    :rtype: str
    """

    output = os.path.join(config_dict()['VarLocation'], directory)

    if not os.path.exists(output):
        os.makedirs(output)

    return output
