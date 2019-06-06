# read in config
from __future__ import absolute_import, print_function, division
import configobj
import pkg_resources
import os
import validate

from hcam_widgets.misc import createJSON, saveJSON


def check_user_dir(g):
    """
    Check directories exist for saving apps/configs etc. Create if not.
    """
    dirs = [os.path.expanduser('~/.hdriver')]
    if 'app_directory' in g.cpars:
        dirs.append(os.path.expanduser(g.cpars['app_directory']))
    if 'log_file_directory' in g.cpars:
        dirs.append(os.path.expanduser(g.cpars['log_file_directory']))
    for direc in dirs:
        if not os.path.exists(direc):
            try:
                os.mkdir(direc)
            except Exception as err:
                g.clog.warn('Failed to make directory ' + str(err))


def load_config(g):
    """
    Populate application level globals from config file
    """
    configspec_file = pkg_resources.resource_filename('hcam_drivers',
                                                      'data/configspec.ini')
    # try and load config file.
    # look in the following locations in order
    # - ~/.hdriver directory
    # - package resources
    paths = []
    paths.append(os.path.expanduser('~/.hdriver/'))
    resource_dir = pkg_resources.resource_filename('hcam_drivers', 'data')
    paths.append(resource_dir)

    # now load config file
    config = configobj.ConfigObj({}, configspec=configspec_file)
    for loc in paths:
        try:
            with open(os.path.join(loc, "config")) as source:
                config = configobj.ConfigObj(source, configspec=configspec_file)
            break
        except IOError:
            pass

    # validate ConfigObj, filling defaults from configspec if missing from config file
    validator = validate.Validator()
    result = config.validate(validator)
    if result is not True:
        g.clog.warn('Config file validation failed')

    # now update globals with config
    g.cpars.update(config)


def write_config(g):
    """
    Dump application level globals to config file
    """
    configspec_file = pkg_resources.resource_filename('hcam_drivers',
                                                      'data/configspec.ini')
    config = configobj.ConfigObj({}, configspec=configspec_file)
    config.update(g.cpars)
    config.filename = os.path.expanduser('~/.hdriver/config')
    try:
        config.write()
    except Exception as err:
        g.clog.warn("Could not write config file:\n" + str(err))


def dump_app(g):
    """
    Dump current application settings to backup
    """
    json_string = createJSON(g, full=False)
    saveJSON(g, json_string, backup=True)

