"""
Module for wrappers around ConfigParser for writing config files.
"""

import ConfigParser

from lib5c.util.system import check_outdir


def write_config(outfile, name, data):
    """
    Writes key-value data to a simple config file.

    Parameters
    ----------
    outfile : str
        File to write to.
    name : str
        Section name for the config.
    data : dict
        The data to write in the config.
    """
    check_outdir(outfile)

    # create config
    config = ConfigParser.RawConfigParser()
    config.optionxform = str
    config.add_section(name)
    for k, v in data.items():
        config.set(name, k, v)

    # write config
    with open(outfile, 'w') as handle:
        config.write(handle)
