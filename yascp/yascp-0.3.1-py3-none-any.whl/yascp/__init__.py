"""
Read configuration file

@author: Miroslaw Janiewicz
@contact: Miroslaw.Janiewicz@gmail.com
@version: 0.2
@status: development

This is yet another simple module to read configuration file and feed it to the script.
This allows bypass installing 3rd party libs to do the same job and was very
valuable lesson of Python programming for the author.

The Configuration parser is designed to work with INI style configuration files.

parser.py [path to/name of an INI config file] [section.option to be fetched]

The script takes two arguments

The first argument is a name of configuration file  or full path to a
configuration file (see below for "Configuration File" section for more details).
The second argument may be "--list-all" to obtain a list of all available options
or a key of specific option to get value for this option only (run first with
"--list-all" to see what exactly can be used here).

If an option doesn't belong to any of the sections in the configuration file
then it should be addresses with \"default\" section, i.e:\n\
    default.[myoption]

Configuration File
If absolute path is provided to a configuration file then only that file is read but
if only a name of configuration file is given then script will attempt to read
a file by that name in following locations and order:
- /etc/[config file name]
- ~/[config file name]
- directory from which the script has been ran.
The configuration may contain sections in [section] format. Sample configuration file:

[database]
login = user
password = topsecret
host = example.com
port = 3306

[backend_api]
login = api_user
password = api_password
url = http://example.com:9080


Any options set in earlier configuration (like in /etc/) will be overridden
should it also be specified in any following locations where the configuration
file also was found. This way it allows to fine tune the configuration by placing
general config in /etc and then user specific in his home dir followed by one it
the script's run directory.
"""
from __future__ import absolute_import
from . import parser

__all__ = ['parser']