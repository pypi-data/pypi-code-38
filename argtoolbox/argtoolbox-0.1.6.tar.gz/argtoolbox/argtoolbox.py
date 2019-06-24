#! /usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK


# This file is part of argtoolbox.
#
# argtoolbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# argtoolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LinShare user cli.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014 Frédéric MARTIN
#
# Contributors list:
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#

from __future__ import unicode_literals

import os
import sys
import logging
import base64
import copy
from ordereddict import OrderedDict
import ConfigParser
import argparse
import types
import locale

# -----------------------------------------------------------------------------
# global logger variable
#log = logging.getLogger('argtoolbox')
#log.setLevel(logging.INFO)
#log.setLevel(logging.DEBUG)
# logger formats
DEFAULT_LOGGING_FORMAT = logging.Formatter(
    "%(asctime)s %(levelname)-8s: %(message)s", "%H:%M:%S")
DEBUG_LOGGING_FORMAT = logging.Formatter(
    "%(asctime)s %(levelname)-8s %(module)s:%(name)s:%(funcName)s:%(lineno)d:%(message)s",
    "%H:%M:%S")
# logger handlers
# pylint: disable-msg=C0103
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setFormatter(DEFAULT_LOGGING_FORMAT)

# debug mode
# if you need debug during class construction, file config loading, ...,
# you need to modify the logger level here.
#log.addHandler(streamHandler)
#log.setLevel(logging.DEBUG)
#streamHandler.setFormatter(DEBUG_LOGGING_FORMAT)


# -----------------------------------------------------------------------------
class DefaultHook(object):
    """
    This class does nothing. This is the default class for creating your own
    hook. After reading an option from the config file, you can apply a
    postprocessing, like the base64 decoding or every thing you want.
    """

    def __init__(self):
        pass

    def __call__(self, elt):
        pass


# -----------------------------------------------------------------------------
class Base64ElementHook(DefaultHook):
    """This hook is used as a post reading processing in order to convert
    base64 data stored into the config file into plain text data."""
    def __init__(self, warning=False):
        super(Base64ElementHook, self).__init__()
        self.warning = warning

    def __call__(self, elt):
        if elt.value:
            try:
                data = base64.b64decode(elt.value)
                elt.value = data
            except TypeError as ex:
                # pylint: disable-msg=W0621
                log = logging.getLogger('argtoolbox')
                if self.warning:
                    log.warn("current field '%(name)s' is not \
stored in the configuration file with \
base64 encoding",
                             {"name": getattr(elt, "_name")})
                else:
                    log.error("current field '%(name)s' is not stored in the \
configuration file with base64 encoding", {"name":
                              getattr(elt, "_name")})
                    raise ex


# -----------------------------------------------------------------------------
class SectionHook(object):
    """
    The SectionHook class is used during the configuration reloading
    process. After the parsing of CLI arguments, all section hooks are
    applied.
    This hook lets you modify the attribute called "self.section".
    The hook is looking for a CLI argument in "args" using "opt_name" as the
    argument name. Then, the value is stored into section.attribute.

    """
    def __init__(self, section, attribute, opt_name):
        if not issubclass(section.__class__, _AbstractSection):
            raise TypeError("First argument should be a subclass of _Section.")
        self.section = section

        if not isinstance(attribute, types.UnicodeType):
            raise TypeError("Second argument should be a string, "
                            + "attribute name.")
        self.attribute = attribute

        if not isinstance(opt_name, types.UnicodeType):
            raise TypeError("Third argument should be a string, option name.")
        self.opt_name = opt_name

    def __call__(self, args):
        # looking for a specific opt_name in command line args
        value = getattr(args, self.opt_name)
        # if defined, we set this value to a attribute of input Section.
        if value is not None:
            setattr(self.section, self.attribute, value)


# -----------------------------------------------------------------------------
class Config(object):
    # pylint: disable-msg=R0902
    """This is the entry point, this class will contains all Section and
     Elements."""

    def __init__(self, prog_name, config_file=None, desc=None,
                 mandatory=False, use_config_file=True):
        self.prog_name = prog_name
        self.config_file = config_file
        self.use_config_file = use_config_file
        self._desc = desc
        self.mandatory = mandatory

        self.sections = OrderedDict()
        self._default_section = self.add_section(SimpleSection("DEFAULT"))
        self.parser = None
        self.file_parser = ConfigParser.SafeConfigParser()

    def add_section(self, section):
        """Add a new Section object to the config. Should be a subclass of
        _AbstractSection."""
        if not issubclass(section.__class__, _AbstractSection):
            raise TypeError("argument should be a subclass of Section")
        self.sections[section.get_key_name()] = section
        return section

    def get_section(self, name):
        if name.lower() == "default":
            return self._default_section
        return self.sections.get(name)

    def get_default_section(self):
        """This method will return default section object"""
        return self._default_section

    def load(self, exit_on_failure=False):
        """One you have added all your configuration data (Section, Element,
        ...) you need to load data from the config file."""
        if self.use_config_file:
            self._load(exit_on_failure)

    def _load(self, exit_on_failure):
        """One you have added all your configuration data (Section, Element,
        ...) you need to load data from the config file."""
        # pylint: disable-msg=W0621
        log = logging.getLogger('argtoolbox')
        discoveredFileList = []
        if self.config_file:
            if isinstance(self.config_file, types.UnicodeType):
                discoveredFileList = self.file_parser.read(self.config_file)
            else:
                discoveredFileList = self.file_parser.readfp(
                    self.config_file,
                    "file descriptor")
        else:
            defaultFileList = []
            defaultFileList.append(self.prog_name + ".cfg")
            defaultFileList.append(
                os.path.expanduser('~/.' + self.prog_name + '.cfg'))
            defaultFileList.append('/etc/' + self.prog_name + '.cfg')
            log.debug("defaultFileList: " + str(defaultFileList))
            discoveredFileList = self.file_parser.read(defaultFileList)

        log.debug("discoveredFileList: " + str(discoveredFileList))

        if self.mandatory and len(discoveredFileList) < 1:
            msg = "The required config file was missing."
            msg += " Default config files : " + str(defaultFileList)
            log.error(msg)
            raise EnvironmentError(msg)

        log.debug("loading configuration ...")
        if exit_on_failure:
            for s in self.sections.values():
                log.debug("loading section : " + s.get_section_name())
                try:
                    s.load(self.file_parser)
                except ValueError:
                    sys.exit(1)
        else:
            for s in self.sections.values():
                log.debug("loading section : " + s.get_section_name())
                s.load(self.file_parser)

        log.debug("configuration loaded.")

    def get_parser(self, **kwargs):
        """This method will create and return a new parser with prog_name,
        description, and a config file argument.
        """
        self.parser = argparse.ArgumentParser(prog=self.prog_name,
                                              description=self._desc,
                                              add_help=False, **kwargs)
        # help is removed because parser.parse_known_args() show help,
        # often partial help. help action will be added during
        # reloading step for parser.parse_args()
        if self.use_config_file:
            self.parser.add_argument('--config-file',
                                     action="store",
                                     help="Other configuration file.")
        return self.parser

    def reload(self, hooks=None):
        """This method will reload the configuration using input argument
        from the command line interface.
        1. pasing arguments
        2. applying hooks
        3. addding help argument
        4. reloading configuration using cli argument like a configuration
        file name.
        """
        #from argcomplete import debug
        # Parsing the command line looking for the previous options like
        # configuration file name or server section. Extra arguments
        # will be store into argv.
        args = None

        if os.environ.get('_ARGCOMPLETE'):
            # During argcomplete completion, parse_known_args will return an
            # empty Namespace. In this case, we feed the previous function with
            # data comming from the input completion data
            compline = os.environ.get('COMP_LINE')
            args = self.parser.parse_known_args(compline.split()[1:])[0]
        else:
            args = self.parser.parse_known_args()[0]
        if hooks is not None:
            if isinstance(hooks, list):
                for h in hooks:
                    if isinstance(h, SectionHook):
                        h(args)
            else:
                if isinstance(hooks, SectionHook):
                    hooks(args)

        # After the first argument parsing, for configuration reloading,
        # we can add the help action.
        self.parser.add_argument('-h', '--help', action='help',
                                 default=argparse.SUPPRESS,
                                 help='show this help message and exit')

        # Reloading
        if self.use_config_file:
            # pylint: disable-msg=W0621
            log = logging.getLogger('argtoolbox')
            log.debug("reloading configuration ...")
            if args.config_file:
                self.file_parser = ConfigParser.SafeConfigParser()
                discoveredFileList = self.file_parser.read(args.config_file)
                log.debug("discoveredFileList: " + str(discoveredFileList))
            for s in self.sections.values():
                log.debug("loading section : " + s.get_section_name())
                s.reset()
                s.load(self.file_parser)
            log.debug("configuration reloaded.")

    def __getattr__(self, name):
        if name.lower() == "default":
            return self._default_section
        s = self.sections.get(name)
        if s is not None:
            return s
        else:
            raise AttributeError("'%(class)s' object has no attribute \
'%(name)s'" % {"name": name, "class": self.__class__.__name__})

    def __str__(self):
        res = []
        res.append("Configuration of %(prog_name)s : " % self.__dict__)
        for s in self.sections.values():
            res.append("".join(s.get_representation("\t")))
        return "\n".join(res)

    def write_default_config_file(self, output, comments=True):
        """This method write a sample file, with attributes, descriptions,
        sample values, required flags, using the configuration object
        properties.
        """
        if self.use_config_file:
            # pylint: disable-msg=W0621
            log = logging.getLogger('argtoolbox')
            with open(output, 'w') as f:
                if comments:
                    f.write("#####################################\n")
                    f.write("# Description :\n")
                    f.write("# -------------\n# ")
                    for i in self._desc.split('\n'):
                        f.write("# ")
                        f.write(i)
                        f.write("\n")
                    f.write("\n\n")

                for s in self.sections.values():
                    log.debug("loading section : " + s.get_section_name())
                    s.write_config_file(f, comments)
            log.debug("config file generation completed : " + str(output))


# -----------------------------------------------------------------------------
class _AbstractSection(object):
    """This class is the parent class of all Section classes. You can not use
    it, you must implement abstract methods.
    """

    def __init__(self, desc=None, prefix=None,
                 suffix=None, required=False):
        self._name = None
        self._desc = desc
        self._prefix = prefix
        self._suffix = suffix
        self._required = required

    def get_key_name(self):
        """This method return the name of the section, it Should be unique
        because it is used as a key or identifier."""
        return self._name

    def get_section_name(self):
        """This method build the current section name that the program will
        looking for into the configuration file.
        The format is [<prefix>-]<name>[-<suffix>].
        """
        a = []
        if self._prefix:
            a.append(self._prefix)
        a.append(str(self._name))
        if self._suffix:
            a.append(self._suffix)
        return "-".join(a)

    # pylint: disable-msg=W0613
    # pylint: disable-msg=R0201
    def load(self, file_parser):
        """ This method must be implemented by the subclass. This method should
        read and load all section elements.
        """
        raise NotImplementedError("You must implement this method.")

    def get_representation(self, prefix="", suffix="\n"):
        """return the string representation of the current object."""
        res = prefix + "Section " + self.get_section_name().upper() + suffix
        return res

    def __str__(self):
        return "".join(self.get_representation())

    def write_config_file(self, f, comments):
        """This method write a sample file, with attributes, descriptions,
        sample values, required flags, using the configuration object
        properties.
        """
        if comments:
            f.write("#####################################\n")
            f.write("# Section : ")
            f.write("#".join(self.get_representation()) + "\n")
            f.write("#####################################\n")
        f.write("[" + self._name + "]\n")
        if self._desc and comments:
            f.write("# Description : ")
            for i in self._desc.split('\n'):
                f.write("# ")
                f.write(i)
                f.write("\n")
            f.write("\n")


# -----------------------------------------------------------------------------
class _Section(_AbstractSection):
    """Simple abstract section object, container for Elements"""
    def __init__(self, *args, **kwargs):
        super(_Section, self).__init__(*args, **kwargs)
        self.elements = OrderedDict()

    def add_element(self, elt):
        """Helper to add a element to the current section. The Element name
        will be used as an identifier."""
        if not isinstance(elt, Element):
            raise TypeError("argument should be a subclass of Element")
        self.elements[elt.get_name()] = elt
        return elt

    def add_element_list(self, elt_list, **kwargs):
        """Helper to add a list of similar elements to the current section.
        Element names will be used as an identifier."""
        for e in elt_list:
            self.add_element(Element(e, **kwargs))

    def count(self):
        """This method will return the number of Element in the current
        Section"""
        return len(self.elements)

    def reset(self):
        for e in self.elements.values():
            e.reset()

    def load(self, file_parser):
        section = self.get_section_name()
        try:
            for e in self.elements.values():
                e.load(file_parser, section)
        except ConfigParser.NoSectionError as e:
            # pylint: disable-msg=W0621
            log = logging.getLogger('argtoolbox')
            if self._required:
                log.error("Required section : " + section)
                raise ValueError(e)
            else:
                log.debug("Missing section : " + section)

    def __getattr__(self, name):
        e = self.elements.get(name)
        if e is not None:
            return e
        else:
            raise AttributeError("'%(class)s' object has no attribute \
'%(name)s'" % {"name": name, "class": self.__class__.__name__})

    def get_element(self, name):
        return self.elements.get(name)

    def write_config_file(self, f, comments):
        """This method write a sample file, with attributes, descriptions,
        sample values, required flags, using the configuration object
        properties.
        """
        if len(self.elements) < 1:
            return
        super(_Section, self).write_config_file(f, comments)

        for e in self.elements.values():
            e.write_config_file(f, comments)
        f.write("\n")


# -----------------------------------------------------------------------------
class SimpleSection(_Section):
    """A simple section object. This class is used to declare a section that
    should be into the configuration file.
    Then you need to add Elements to this section.

    mysection = SimpleSection("section_1")
    """

    def __init__(self, name, *args, **kwargs):
        super(SimpleSection, self).__init__(*args, **kwargs)
        self._name = name

    def get_representation(self, prefix="", suffix="\n"):
        res = []
        if self.count() > 0:
            res.append(prefix + "Section "
                       + self.get_section_name().upper() + suffix)
            for elt in self.elements.values():
                res.append("".join(elt.get_representation(prefix)))
        return res


# -----------------------------------------------------------------------------
class SubSection(_Section):
    """ TODO """

    def get_representation(self, prefix="", suffix="\n"):
        res = []
        if self.count() > 0:
            res.append(prefix + "SubSection : "
                       + self.get_section_name().upper() + suffix)
            for elt in self.elements.values():
                res.append("".join(elt.get_representation(prefix)))
        return res

    def __copy__(self):
        newone = type(self)()
        newone.__dict__.update(self.__dict__)
        self.elements = OrderedDict()
        return newone

    # pylint: disable-msg=W0613
    def __deepcopy__(self, *args):
        newone = type(self)()
        newone.__dict__.update(self.__dict__)
        newone.elements = OrderedDict()
        for e in self.elements.values():
            newone.add_element(copy.deepcopy(e))
        return newone


# -----------------------------------------------------------------------------
class ListSection(_AbstractSection):
    """ TODO """
    def __init__(self, name, *args, **kwargs):
        super(ListSection, self).__init__(*args, **kwargs)
        self.elements = OrderedDict()
        self._name = name

    def load(self, file_parser):

        section = self.get_section_name()
        try:

            # TODO : ? : data = data.decode(locale.getpreferredencoding())
            for key in [item for item in file_parser.options(section)
                        if item not in file_parser.defaults().keys()]:
                self.elements[key] = file_parser.get(section, key)
        except ConfigParser.NoSectionError as e:
            # pylint: disable-msg=W0621
            log = logging.getLogger('argtoolbox')
            if self._required:
                log.error("Required section : " + section)
                raise ValueError(e)
            else:
                log.debug("Missing section : " + section)

    def reset(self):
        for e in self.elements.values():
            e.reset()

    def get_representation(self, prefix="", suffix="\n"):
        res = []
        res.append(prefix + "Section " + self._name + suffix)

        for key, val in self.elements.items():
            a = []
            a.append(prefix)
            a.append(" - " + str(key) + " : " + str(val))
            a.append(suffix)
            res.append("".join(a))
        return res


# -----------------------------------------------------------------------------
# warning| [R0902, Element] Too many instance attributes (13/7)
# pylint: disable-msg=R0902
class Element(object):
    """
    An Element could represent a option into the configuration file, this
    class lets you configure many requirements like default value, data
    type, if the option is mandatory, etc.
    You can also defined if element could be supply by the command line
    interface, default options for the cli, etc.
    """

    # pylint: disable-msg=R0913
    def __init__(self, name, e_type=str, required=False, default=None,
                 conf_hidden=False, conf_required=False, desc=None,
                 hooks=None, hidden=False, e_type_exclude=False):
        """Information about how to declare a element which will be load from a
        configuration file.

    Keyword Arguments:

    - name    -- name of the attribute store into the configuration file.

    - e_type -- Data type of the attribute.

    - e_type_exclude -- Do not export data type to argparse. Example there is a
    conflict between type=int and action=count for argparse parameters.

    - conf_required -- The current attribute must be present in the
    configuration file.

    - required -- The current attribute must be present into command line
    arguments except if it is present into configuration file.

    - default -- Default value used if the attribute is not set in
    configuration file.
        This value is also used during configuration file generation.
        ex: 'attribute = $default_value' or  ';attribute = $default_value'
        if this attribute is mandatory.

    - desc -- Description used into the configuration file and argparse.

    - conf_hidden -- The current attribute will not be used during
    configuration file generation.

    - hidden -- The current attribute will not be print on console
    (ex password)

    - hooks -- one hook or a list of hook. Should be an instance of
    DefaultHook. The hook will be apply to the element value once read
    from config file.

    """

        self._name = name
        self.e_type = e_type
        self.e_type_exclude = e_type_exclude
        self._required = required
        self.default = default
        self._desc = desc
        self.conf_hidden = conf_hidden
        self.conf_required = conf_required
        self._desc_for_config = None
        self._desc_for_argparse = None
        self._value = None
        self.hidden = hidden

        if hooks is None:
            hooks = []

        if isinstance(hooks, list):
            for h in hooks:
                if not isinstance(h, DefaultHook):
                    raise TypeError("Hook argument should be a subclass"
                                    + " of DefaultHook")
            self.hooks = hooks
        else:
            if isinstance(hooks, DefaultHook):
                self.hooks = [hooks]
            else:
                raise TypeError(
                    "Hook argument should be a subclass of DefaultHook")

    @property
    def value(self):
        """TODO"""
        if self._value is None:
            return self.default
        return self._value

    @value.setter
    def value(self, value):
        """TODO"""
        self._value = value

    def get_name(self):
        """This method will return the name of the current element"""
        return self._name

    def get_representation(self, prefix="", suffix="\n"):
        """This method build a array that will contain the string
        representation of the current object. Every lines could be
        prefixed and suffixed.
        """
        res = []
        if self.hidden:
            res.append(prefix + " - " + str(self._name)
                       + " : xxxxxxxx" + suffix)
        else:
            default = self.default
            if default is None:
                default = " - "
            a = prefix + " - "
            a += str(self._name) + " : "
            if isinstance(default, types.UnicodeType):
                a += default
            else:
                a += str(default)
            a += suffix
            res.append(a)
        return res

    def __str__(self):
        return "".join(self.get_representation())

    def __copy__(self):
        newone = type(self)(self._name)
        newone.__dict__.update(self.__dict__)
        #self.elements = OrderedDict()
        return newone

    def post_load(self):
        """Every element hooks are applied by this method, just after the
        loading process.
        """
        for h in self.hooks:
            h(self)

    def load(self, file_parser, section_name):
        """The current element is loaded from the configuration file,
        all constraints and requirements are checked.
        Then element hooks are applied.
        """
        self._load(file_parser, section_name)
        self.post_load()

    def _load(self, file_parser, section_name):
        """The current element is loaded from the configuration file,
        all constraints and requirements are checked.
        """
        # pylint: disable-msg=W0621
        log = logging.getLogger('argtoolbox')
        try:
            log.debug("looking for field (section=" + section_name
                      + ") : " + self._name)
            data = None
            try:
                if self.e_type == int:
                    data = file_parser.getint(section_name, self._name)
                elif self.e_type == float:
                    data = file_parser.getfloat(section_name, self._name)
                elif self.e_type == bool:
                    data = file_parser.getboolean(section_name, self._name)
                elif self.e_type == list:
                    data = file_parser.get(section_name, self._name)
                    data = data.strip()
                    data = data.decode(locale.getpreferredencoding())
                    data = data.split()
                    if not data:
                        msg = "The optional field '%(name)s' was present, \
type is list, but the current value is an empty \
list." % {"name": self._name}
                        log.error(msg)
                        raise ValueError(msg)
                elif self.e_type == str:
                    data = file_parser.get(section_name, self._name)
                    # happens only when the current field is present,
                    # type is string, but value is ''
                    if not data:
                        msg = "The optional field '%(name)s' was present, \
                        type is string, but the current value is an empty \
                        string." % {"name": self._name}
                        log.error(msg)
                        raise ValueError(msg)
                    data = data.decode(locale.getpreferredencoding())
                else:
                    msg = "Data type not supported : %(type)s " % {
                        "type": self.e_type}
                    log.error(msg)
                    raise TypeError(msg)

            except ValueError as ex:
                msg = "The current field '%(name)s' was present, but the \
required type is : %(e_type)s." %  {
                "name": self._name,
                "e_type": self.e_type
                }
                log.error(msg)
                log.error(str(ex))
                raise ValueError(str(ex))

            log_data = {"name": self._name, "data": data,
                        "e_type": self.e_type}
            if self.hidden:
                log_data['data'] = "xxxxxxxx"
            log.debug("field found : '%(name)s', value : '%(data)s', \
type : '%(e_type)s'", log_data)
            self.value = data

        except ConfigParser.NoOptionError:
            if self.conf_required:
                msg = "The required field '%(name)s' was missing from the \
config file." % {"name": self._name}
                log.error(msg)
                raise ValueError(msg)

            if self.default is not None:
                self.value = self.default
                log_data = {"name": self._name, "data": self.default,
                            "e_type": self.e_type}
                if self.hidden:
                    log_data['data'] = "xxxxxxxx"
                log.debug("Field not found : '%(name)s', default value : \
'%(data)s', type : '%(e_type)s'", log_data)
            else:
                log.debug("Field not found : '" + self._name + "'")

    def reset(self):
        self.value = None

    def get_arg_parse_arguments(self):
        """
        During the element declaration, all configuration file requirements
        and all cli requirements have been described once.
        This method will build a dict containing all argparse options.
        It can be used to feed argparse.ArgumentParser.
        You does not need to have multiple declarations.
        """

        ret = dict()
        if self._required:
            if self.value is not None:
                ret["default"] = self.value
            else:
                ret["required"] = True
        ret["dest"] = self._name
        if not self.e_type_exclude:
            if self.e_type == int or self.e_type == float:
                # Just override argparse.add_argument 'type' parameter for int or float.
                ret["type"] = self.e_type
        if self.value is not None:
            ret["default"] = self.value
        if self._desc:
            ret["help"] = self._desc
        return ret

    def write_config_file(self, f, comments):
        """This method write a sample file, with attributes, descriptions,
        sample values, required flags, using the configuration object
        properties.
        """
        if self.conf_hidden:
            return False

        if comments:
            f.write("\n")
            f.write("# Attribute (")
            f.write(str(self.e_type.__name__))
            f.write(") : ")
            f.write(self._name.upper())
            f.write("\n")
            if self._desc and self._desc != argparse.SUPPRESS:
                f.write("# Description : ")
                for i in self._desc.split('\n'):
                    f.write("# ")
                    f.write(i)
                    f.write("\n")
                f.write("\n")

        if not self.conf_required:
            f.write(";")
        f.write(self._name)
        f.write("=")
        if self.default is not None and not self.hidden:
            f.write(str(self.default))
        f.write("\n")


# -----------------------------------------------------------------------------
class ElementWithSubSections(Element):
    """ This class extends the default class Element. It offers you the power
    to add sections (SubSection) inside a element.
    The simple case is one section containing some elements.
    But in some situation you may represent your data like a tree.
    Section :
        Element1 : name = port, value = 389
        Element2 : name = address, value = 127.0.0.1
        ElementWithSubSections
            SubSection
                Element1
                Element2
    """

    def __init__(self, *args, **kwargs):
        super(ElementWithSubSections, self).__init__(*args, **kwargs)
        self.e_type = str
        self.sections = OrderedDict()

    def get_representation(self, prefix="", suffix="\n"):
        res = ['\n']
        temp_line = prefix + " - " + str(self._name) + " : "
        if self.hidden:
            temp_line += "xxxxxxxx" + suffix
        else:
            temp_line += str(self.value) + suffix
        res.append(temp_line)

        if len(self.sections) > 0:
            for elt in self.sections.values():
                res.append("".join(elt.get_representation(prefix + "\t")))
        return res

    def add_section(self, section):
        """You can add section inside a Element, the section must be a
        subclass of SubSection. You can use this class to represent a tree.
        """

        if not issubclass(section.__class__, SubSection):
            raise TypeError("Argument should be a subclass of SubSection, \
                             not :" + str(section.__class__))
        self.sections[section.name] = section
        return section

    def load(self, file_parser, section_name):
        self._load(file_parser, section_name)
        if len(self.sections) > 0:
            for sec in self.sections.values():
                sec.name = self.value
                sec.load(file_parser)
        self.post_load()


# -----------------------------------------------------------------------------
class ElementWithRelativeSubSection(ElementWithSubSections):

    """ This class extends the default class Element. It offers you the power
    to add sections (SubSection) inside a element.
    The simple case is one section containing some elements.
    But in some situation you may represent your data like a tree and, you want
    to search a section dynamically.

    Section :
        Element1 : name = port, value = 389
        Element2 : name = address, value = 127.0.0.1
        ElementWithRelativeSubSection :
            name = list_of_section_name, value = sec_test1 sec_test2 sec_test3

    This class will look for sections named sec_test1, sec_test2 and sec_test3.
    The structure used to load the previous sections is second constructor
    argument name "rss". It is a SubSection that will be used as a template.
        ex :
            SubSection :
                - Element4
                - Element5
                - Element5

    This class could be used to store, inside a element, a list of complex
    structures.

    At the end, when ElementWithRelativeSubSection will be loaded,
    you should have the following struture :
    Section :
        Element1 : name = port, value = 389
        Element2 : name = address, value = 127.0.0.1
        ElementWithRelativeSubSection :
            SubSection : sec_test1
                - Element4
                - Element5
                - Element5
            SubSection : sec_test2
                - Element4
                - Element5
                - Element5
            SubSection : sec_test3
                - Element4
                - Element5
                - Element5

    """

    def __init__(self, name, rss, **kwargs):
        super(ElementWithRelativeSubSection, self).__init__(name, **kwargs)
        self.e_type = list
        if not issubclass(rss.__class__, SubSection):
            raise TypeError("Argument should be a subclass of SubSection, \
                            not :" + str(_Section.__class__))
        self.rss = rss

    def load(self, file_parser, section_name):
        self._load(file_parser, section_name)
        if isinstance(self.value, list):
            for sec_name in self.value:
                try:
                    sec = copy.deepcopy(self.rss, None)
                    setattr(sec, '_name', sec_name)
                    self.sections[sec_name] = sec
                    sec.load(file_parser)
                except ValueError as e:
                    # pylint: disable-msg=W0621
                    log = logging.getLogger('argtoolbox')
                    error = []
                    error.append("Missing relative section, attribute : ")
                    error.append("'[" + section_name + "]." + self._name)
                    error.append("', value : " + str(self.value))
                    log.error("".join(error))
                    raise ValueError(e)
        self.post_load()

    def get_representation(self, prefix="", suffix="\n"):
        res = ['\n']
        res.append('#')
        temp_line = prefix + " - " + str(self._name) + " : "
        if self.hidden:
            temp_line += "xxxxxxxx" + suffix
        else:
            temp_line += str(self.value) + suffix
        res.append(temp_line)

        res.append("".join(self.rss.get_representation(prefix + "#\t")))
        res.append('\n')
        if len(self.sections) > 0:
            for elt in self.sections.values():
                res.append('\n')
                res.append("".join(elt.get_representation(prefix + "\t")))
            res.append('\n')
        return res


# -----------------------------------------------------------------------------
class DefaultCommand(object):
    """This class do nothing, this is just the default structure to implement
    your own class. Use this class as the base for every the command line
    action you want to create."""

    def __init__(self, config=None):
        self.log = logging.getLogger(
            'argtoolbox.' + str(self.__class__.__name__.lower()))
        self.config = config
        self.protected_args = ['password']

    def __call__(self, args):
        dict_tmp = copy.copy(args)
        #delattr(dict_tmp, "__func__")
        for field in getattr(self, 'protected_args', []):
            if hasattr(dict_tmp, field):
                setattr(dict_tmp, field, "xxxxxxxx")
        self.log.debug("Namespace : begin :")
        for i in dict_tmp.__dict__:
            attribute = getattr(dict_tmp, i)
            if isinstance(attribute, types.UnicodeType):
                self.log.debug(i + " : " + attribute + " : <type 'unicode'>")
            else:
                self.log.debug(i + " : " + str(attribute) + " : " + str(type(attribute)))
        self.log.debug("Namespace : end.")

    # pylint: disable-msg=W0613
    # pylint: disable-msg=R0201
    def complete(self, args, prefix):
        """Auto complete method, args is comming from argparse and prefix is
        the input data from command line.
        You must return a list."""
        return []


# -----------------------------------------------------------------------------
class TestCommand(DefaultCommand):
    """Just a simple command, using the default command class."""

    def __call__(self, args):
        super(TestCommand, self).__call__(args)
        print ""
        print "This is the beginning of the TestCommand class."
        print ""

        print "The loaded configuration : "
        print "---------------------------"
        print unicode(self.config)
        print ""

        print "The command line arguments (argv) : "
        print "------------------------------------"
        print args

        print ""
        print "This is the end of the TestCommand class."
        print ""


# -----------------------------------------------------------------------------
class DefaultCompleter(object):
    """ TODO
    """
    def __init__(self, func_name="complete"):
        self.func_name = func_name

    def __call__(self, prefix, **kwargs):
        from argcomplete import debug
        try:
            debug("\n------------ DefaultCompleter -----------------")
            debug("Kwargs content :")
            for i, j in kwargs.items():
                debug("key : " + str(i))
                debug("\t - " + str(j))
            debug("\n------------ DefaultCompleter -----------------\n")

            args = kwargs.get('parsed_args')
            # pylint: disable-msg=W0612
            parser = kwargs.get('parser')
            #a = parser.parse_known_args()

            # getting form args the current Command and looking for a method
            # called by default 'complete'. See __init__ method. The method
            # name is store in the class member called self.func_name
            fn = getattr(args.__func__, self.func_name, None)
            if fn:
                return fn(args, prefix)

        # pylint: disable-msg=W0703
        except Exception as e:
            from argcomplete import warn
            warn("\nERROR::COMPLETE:An exception was caught :" + str(e) + "\n")
            import traceback
            traceback.print_exc()
            debug("\n------\n")
            return ["comlete-error"]


# -----------------------------------------------------------------------------
class DefaultProgram(object):
    """ TODO """

    def __init__(self, parser, config=None, force_debug=False):
        self.parser = parser
        self.config = config
        self.force_debug = force_debug

    def __call__(self):

        def patch(self, parser, namespace, values, option_string=None):
            """patch original __call__ method for argparse 1.1 (fix)"""
            from argparse import _UNRECOGNIZED_ARGS_ATTR
            from argparse import SUPPRESS
            from argparse import _

            parser_name = values[0]
            arg_strings = values[1:]

            # set the parser name if requested
            if self.dest is not SUPPRESS:
                setattr(namespace, self.dest, parser_name)

            # select the parser
            try:
                parser = self._name_parser_map[parser_name]
            except KeyError:
                tup = parser_name, ', '.join(self._name_parser_map)
                msg = _('unknown parser %r (choices: %s)') % tup
                raise ArgumentError(self, msg)

            # parse all the remaining options into the namespace
            # store any unrecognized options on the object, so that the top
            # level parser can decide what to do with them

            namespace, arg_strings = parser.parse_known_args(arg_strings,
                                                             namespace)
            if arg_strings:
                vars(namespace).setdefault(_UNRECOGNIZED_ARGS_ATTR, [])
                getattr(namespace, _UNRECOGNIZED_ARGS_ATTR).extend(arg_strings)

        # integration with argcomplete python module (bash completion)
        try:
            # Very ugly dirty hook/fix
            if argparse.__version__ == "1.1":
                # pylint: disable=protected-access
                argparse._SubParsersAction.__call__ = patch
            import argcomplete
            argcomplete.autocomplete(self.parser)
        except ImportError:
            pass

        # parse cli arguments
        args = self.parse_args()

        if getattr(args, 'debug', False) or self.force_debug:
            if hasattr(args, 'debugger_names') and getattr(args, 'debugger_names'):
                for name in args.debugger_names:
                    llog = logging.getLogger(name)
                    llog.setLevel(logging.DEBUG)
            else:
                llog = logging.getLogger()
                llog.setLevel(logging.DEBUG)
            streamHandler.setFormatter(DEBUG_LOGGING_FORMAT)
            if self.config:
                print "debug>>>----------- config -------------------"
                print unicode(self.config)
                print "debug----------- processing --------------<<<<"

            # run command
            return args.__func__(args)
        else:
            # pylint: disable-msg=W0621
            log = logging.getLogger('argtoolbox')
            from argparse import ArgumentError
            try:
                # run command
                return args.__func__(args)
            except ValueError as a:
                log.error("ValueError : " + str(a))
            except KeyboardInterrupt as a:
                log.warn("Keyboard interruption detected.")
            except ArgumentError as a:
                self.parser.error(a.message)
            except Exception as a:
                log.error("unexcepted error : " + str(a))
            return False


    def parse_args(self):
        args = self.parser.parse_args()
        for attr in args.__dict__:
            data = getattr(args, attr)
            if isinstance(data, str):
                data = data.decode(locale.getpreferredencoding())
                setattr(args, attr, data)

            if isinstance(data, list):
                res = []
                for val in data:
                    if isinstance(val, str):
                        res.append(val.decode(locale.getpreferredencoding()))
                    else:
                        res.append(val)
                setattr(args, attr, res)
        return args


# -----------------------------------------------------------------------------
class BasicProgram(object):
    """ TODO """

    def __init__(self, name, config_file=None, desc=None,
                 mandatory=False, use_config_file=True, version="0.1-alpha",
                 force_debug=False, force_debug_to_file=False):

        # create configuration
        self.config = Config(name, config_file=config_file, desc=desc,
                             mandatory=mandatory,
                             use_config_file=use_config_file)
        self.prog_name = name
        self.parser = None
        self.version = version
        self.formatter_class = None
        self.force_debug = force_debug
        self.force_debug_to_file = force_debug_to_file
        self.log = self.init_logger()

    def init_logger(self):
        # logger
        log = logging.getLogger()
        log.setLevel(logging.INFO)
        # logger handlers
        log.addHandler(streamHandler)

        # debug mode
        # if you want to enable debug during class construction, file
        # configuration loading, ..., you need to modify the logger level here.
        if self.force_debug:
            log.setLevel(logging.DEBUG)
            streamHandler.setFormatter(DEBUG_LOGGING_FORMAT)

        if self.force_debug_to_file:
            dest = self.prog_name + ".log"
            FILEHA = logging.FileHandler(dest, 'w', 'utf-8')
            FILEHA.setFormatter(DEBUG_LOGGING_FORMAT)
            log.setLevel(logging.DEBUG)
            log.addHandler(FILEHA)
            streamHandler.setFormatter(DEBUG_LOGGING_FORMAT)
            log.warning("output log file : " + dest)
        return log

    def add_config_options(self):
        """ You can override this method in order to add your options to the
        config object."""
        # default section
        default = self.config.get_default_section()
        default.add_element(
            Element('debug',
                    e_type=int,
                    e_type_exclude=True,
                    default=0,
                    desc="""debug level : default : 0."""))

    def load(self):
        # loading default configuration from the file
        self.config.load()

    def init_parser(self):
        # arguments parser
        self.parser = self.config.get_parser()
        if self.formatter_class:
            self.parser.formatter_class = self.formatter_class
        self.parser.add_argument('-v', '--verbose',
                                 action="store_true",
                                 default=False)
        self.parser.add_argument('--version',
                                 action="version",
                                 version="%(prog)s " + self.version)

    def add_pre_commands(self):
        """ You can override this method in order to add your command line
        arguments to the argparse parser. The configuration file is already
        loaded at this time."""
        pass

    def reload(self):
        # reloading configuration with previous optional arguments
        # (example : config file name from argv, ...)
        self.config.reload()

    def add_commands(self):
        """ You can override this method in order to add your command line
        arguments to the argparse parser. The configuration file  was
        reloaded at this time."""
        self.parser.add_argument(
            '-d',
            action="count",
            **self.config.default.debug.get_arg_parse_arguments())

    def __call__(self):

        # adding some user options to the config object
        self.add_config_options()

        # loading default configuration from the file
        self.load()

        # initialisation of the cli parser,
        # some default arguments are also added.
        self.init_parser()

        # adding some user arguments
        self.add_pre_commands()

        # reloading configuration with previous optional arguments
        # (example : config file name from argv, ...)
        self.reload()

        # adding all commands
        self.add_commands()

        # run
        run = DefaultProgram(self.parser, self.config,
                             force_debug=self.force_debug)
        if run():
            sys.exit(0)
        else:
            sys.exit(1)


# -----------------------------------------------------------------------------
def query_yes_no(question, default="yes"):
    """Just prompt the user for a yes/no question"""
    res = _query_yes_no(question, default)
    if res == "yes":
        return True
    else:
        return False


# -----------------------------------------------------------------------------
def _query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": "yes", "y": "yes", "ye": "yes",
             "no": "no", "n": "no"}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        try:
            choice = raw_input().lower()
        except KeyboardInterrupt:
            print
            return "no"
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
