"""
Read configuration file

@author: Miroslaw Janiewicz
@contact: Miroslaw.Janiewicz@gmail.com
@version: 0.2
@status: development

This is Yet Another Simple Configuration Parser module
for INI style configurations files.

parser.py [path to/name of an INI config file] [section.option to be fetched]

The script takes two arguments

The first argument is a name of configuration file  or full path to a
configuration file (see below for "Configuration File" section for more details)
The second argument may be "--list-all" to obtain a list of all available option
or a key of specific option to get value for this option only (run first with
"--list-all" to see what exactly can be used here).

If an option doesn't belong to any of the sections in the configuration file
then it should be addresses with \"default\" section, i.e:\n\
    default.[myoption]

Configuration File
If absolute path is provided to a configuration file then only that file is
read but if only a name of configuration file is given then script will attempt
to read a file by that name in following locations and order:
- /etc/[config file name]
- ~/[config file name]
- directory from which the script has been ran.
The configuration may contain sections in [section] format.

Sample configuration file:

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
file also was found. This way it allows to fine tune the configuration by placin
general config in /etc and then user specific in his home dir followed by one it
the script's run directory.
"""
from __future__ import print_function


from builtins import str
from builtins import object
class _ConfigurationData(object):
    """
    Provide tools to store dynamically created attributes.

    This class allows to create dynamically custom attributes
    and then iterate over them using keys, values or both.

    Public methods:
    keys()
    iteritems()
    next()
    """
    def __init__(self):
        """Initialize class."""
        self.prefix = '____'

    def __setitem__(self, key=None, value=None):
        """
        Set/create attribute to value.

        @param key: string - a name of the attribute to set/update
        @param value: value to be set for the key attribute
        """
        setattr(self, self.prefix+key, value)

    def __getitem__(self, key=None):
        """Provide the item[key] fetch style for dynamically set arguments."""
        return getattr(self, key)

    def __getattr__(self, key=None):
        """
        Provide a method to fetch arguments set dynamically.

        This is useful where trying to print value like class.value
        where dynamically set attribute 'value' is really prefixed i.e.
        it's real name is '____value'.

        @raise AttributeError: if requested attribute wasn't found
        """

        if key == 'prefix':
            raise AttributeError("Preventing infinite recursion!")
        try:
            return self.__dict__[self.prefix+key]
        except KeyError:
            raise AttributeError("Attribute " + key +
                                 " (" + self.prefix + key + ") " + "not found!")

    def keys(self):
        """
        Return all keys as dictionary.

        Custom keys method that fetches all keys of dynamically set attributes.

        @return: list of keys for dynamically set attributes
        @rtype: list
        """
        import re
        self.keys_list = []
        for item in self.__dict__:
            r = re.match('^'+self.prefix+'([a-z-_]+)'+'$', item)
            if r:
                self.keys_list.append(r.group(1))
        return self.keys_list

    def iteritems(self):
        """
        Return a touple of (key, value) pair.

        Custom iteritems method that fetches all (keys,values)
        of dynamically set attributes.
        """
        items = []
        for k in list(self.keys()):
            v = self[k]
            items.append((k, v))
        return items

    def __iter__(self):
        """Iterate over saved attributes."""
        list(self.keys())
        self.keys_list.reverse()
        return self

    def __next__(self):
        """
        Provide next item for iteration.

        Iterator's 'next' method.

        @return: next value for the iterator
        @rtype: whatever values where set to be

        @raise StopIteration: when there is nothing more to iterate over
        """
        v = self.keys_list
        try:
            item = v.pop()
            return self[item]
        except:
            raise StopIteration


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class ConfigurationFileError(Error):
    """This is raised when configuration file can't be found"""
    pass


class ConfigurationParseError(Error):
    """
    This is raised when the content of a configuration file
    can't be parsed
    """
    pass


class Parser(_ConfigurationData):
    """
    Read and parse INI style configuration file.

    This class does all the work of locating and parsing the configuration file
    given.
    This class also extends _ConfigurationData class which is providing means
    to dynamically set custom attributes for parsed configuration's sections
    and variables, i.e. if

    p = Parser()

    then sample config could be reached by

    p.zabbix.username

    'zabbix' here is a section from configuration file and 'username' is actual
    name of configuration option.

    Public methods:
    print_all()
    """

    def __init__(self,
                 configuration_file_name=None,
                 defaults={},
                 delimiter='='):
        """
        Read and parse configuration file.

        @param configuration_file_name: string - name of a file with
        configuration to be read; by default this will search for the file
        in scripts dir, then in user home dir and finally in /etc/
        @param defaults: dictionary - default values to be returned in case
        when configuration file is not specifying optional parameters
        """
        import os

        # set prefix that will be added to all dynamically added attributes
        self.prefix = '____'
        self.delimiter = str(delimiter)

        if configuration_file_name is None:
            raise ConfigurationFileError("You need to provide configuration \
file name or full path")
        else:
            configuration_file_name = os.path.expanduser(
                configuration_file_name)

        # set path separator
        DS = os.path.sep
        self.defaults = defaults

        # let's see if given configuration file name is an absolute path -
        # if it is we want to check that file only if not we will
        # go for a couple of locations
        self.search_config_files = []
        if os.path.isabs(configuration_file_name) is False:
            self.search_config_files.append(DS + 'etc' + DS +
                                            configuration_file_name)
            self.search_config_files.append(os.path.expanduser('~') + DS +
                                            configuration_file_name)
            self.search_config_files.append(os.path.abspath(os.path.curdir) +
                                            DS + configuration_file_name)
        else:
            self.search_config_files.append(configuration_file_name)

        self._parse_configuration_file()

    def _parse_defaults(self):
        """
        Parse any received default configuration data.

        @note: The defaults are passed on to constructor of the class.

        @raise ConfigurationParseError: when provided defaults are not
        of the required format (dictionary)
        @raise ConfigurationParseError: when key in provided defaults is not
        containing dot (.) separator for section.option
        """
        if not isinstance(self.defaults, dict):
            raise ConfigurationParseError("Default values are not of the \
required type - expected a dictionary")

        for conf_path, conf_value in self.defaults.items():
            try:
                conf_section, conf_name = conf_path.split('.')
            except ValueError:
                raise ConfigurationParseError(
                    'A "." was expected in the key \'' +
                    conf_path +
                    '\' but none found!')
            # need to make sure that an attribute for any section
            # is set only once
            try:
                getattr(self, conf_section)
            except AttributeError:
                self[conf_section] = _ConfigurationData()
            self[conf_section][conf_name] = conf_value

    def _parse_configuration_file(self):
        """
        Parse configuration from file.

        Parsed configuration is available through the arguments
        of the instance of Parser class:
        Parser.section_name.option_name

        @raise ConfigurationFileError: when none of configuration files exist
        @raise ConfigurationParseError: when at least one line of configuration
        file is not in supported format
        """
        import os
        import re

        # this will hold a list of configuration files that actually exist
        config = []

        # lets filter out configurations that do exist
        for config_file in self.search_config_files:
            if os.path.exists(config_file):
                config.append(config_file)

        if len(config) == 0:
            raise ConfigurationFileError('No configuration file exist')

        # first lets grab all defaults and then we will overwrite values
        # with those from the config file
        self._parse_defaults()
        # set default section name and assign it
        default_section_name = 'default'
        section_name = default_section_name
        for c in config:
            f = open(c, 'r')
            for l in f.readlines():
                l = l.strip()
                # eliminating comments and empty lines
                if not re.match('^(#).*$', l) and l is not '':
                    r = re.match('^\[([a-z-_]+)\]$', l)
                    if r is not None:  # obviously the line is a section name
                        section_name = r.group(1)
                        # need to make sure that an attribute for
                        # any section is set only once
                        try:
                            getattr(self, section_name)
                        except AttributeError:
                            self[section_name] = _ConfigurationData()
                    else:  # option line
                        # check if any section was already set
                        # and set default if not
                        if section_name == default_section_name:
                            # need to make sure that default
                            # section is created only once
                            try:
                                getattr(self, default_section_name)
                            except AttributeError:
                                self[section_name] = _ConfigurationData()
                        try:
                            k, v = l.split(self.delimiter, 1)
                        except ValueError:
                            raise ConfigurationParseError("At least one line of\
 configuration file in not supported format!")
                        self[section_name][k.strip()] = v.strip()

    def _format(self, fmt=None):
        """
        Prepapre config data for display or to be saved back to a file

        @param fmt: string - for what outout data should be formatted;
        possible values are "save" and "print"
        @raise ValueError if no format specified
        """
        import re
        out_save = []
        out_print = []
        self._parse_configuration_file()

        for item in self.__dict__:
            r = re.match(self.prefix+'([a-z\_]+)', item)
            if r:
                section_name = r.group(1)
                out_save.append('['+section_name+']')
                for k, v in self[section_name].iteritems():
                    out_save.append(k+'='+str(v))
                    out_print.append(section_name + '.' + k + ' = ' + str(v))
        if fmt == 'save':
            return out_save
        elif fmt == 'print':
            return out_print
        else:
            raise ValueError

    def print_all(self):
        """
        Prints to the screen all available
        configuration keys along with their values.

        This is convenience method.
        """
        prt = self._format('print')
        print('\n'.join(prt))

    def save(self, file_name=None):
        """
        Save configuration details to a file
        """
        cfg = self._format('save')
        try:
            open(file_name, 'w').write('\n'.join(cfg))
        except:
            raise ConfigurationFileError("Can't save to the file:"+file_name)


def main():
    import sys
    if len(sys.argv) == 2 and sys.argv[1] in ['help', '--help', '-h']:
        print("Configuration parser - help")
        print(__doc__)
    elif len(sys.argv) == 3 and sys.argv[2] == '--print-all':
        conf = sys.argv[1]
        try:
            p = Parser(conf)
        except ConfigurationParseError as e:
            print("ERROR:", e)
        except ConfigurationFileError as e:
            print("ERROR:", e)
        else:
            p.print_all()
    elif len(sys.argv) < 3:
        print("Usage:\n", sys.argv[0], "[full path|only name of an INI style \
config file] [section.variable to fetch|--print-all]")
        sys.exit(1)
    else:
        try:
            conf = sys.argv[1]
            section, variable = str(sys.argv[2]).split('.')
            p = Parser(conf, defaults={}, delimiter='=')
        except ValueError:
            print("There was an ERROR when parsing the configuration file or\
options you provided.\n\
Make sure that configuration file is in format \"key=value\" \
with optional \"[section]\" grouping.\n\
If any variable doesn't belong to any of the sections then it should be \
addresses with \"default\" section, i.e:\n\
default.[myoption]")
            sys.exit(1)
        except IndexError:
            raise

        print(p[section][variable])
