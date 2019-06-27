#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT: a XMPP client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""base constructor class"""

from sat.bridge.bridge_constructor.constants import Const as C
from ConfigParser import NoOptionError
import sys
import os
import os.path
import re
from importlib import import_module


class ParseError(Exception):
    # Used when the signature parsing is going wrong (invalid signature ?)
    pass


class Constructor(object):
    NAME = None  # used in arguments parsing, filename will be used if not set
    # following attribute are used by default generation method
    # they can be set to dict of strings using python formatting syntax
    # dict keys will be used to select part to replace (e.g. "signals" key will
    # replace ##SIGNALS_PART## in template), while the value is the format
    # keys starting with "signal" will be used for signals, while ones starting with
    # "method" will be used for methods
    #  check D-Bus constructor for an example
    CORE_FORMATS = None
    CORE_TEMPLATE = None
    CORE_DEST = None
    FRONTEND_FORMATS = None
    FRONTEND_TEMPLATE = None
    FRONTEND_DEST = None

    # set to False if your bridge need only core
    FRONTEND_ACTIVATE = True

    def __init__(self, bridge_template, options):
        self.bridge_template = bridge_template
        self.args = options

    @property
    def constructor_dir(self):
        constructor_mod = import_module(self.__module__)
        return os.path.dirname(constructor_mod.__file__)

    def getValues(self, name):
        """Return values of a function in a dict
        @param name: Name of the function to get
        @return: dict, each key has the config value or None if the value is not set"""
        function = {}
        for option in ["type", "category", "sig_in", "sig_out", "doc"]:
            try:
                value = self.bridge_template.get(name, option)
            except NoOptionError:
                value = None
            function[option] = value
        return function

    def getDefault(self, name):
        """Return default values of a function in a dict
        @param name: Name of the function to get
        @return: dict, each key is the integer param number (no key if no default value)"""
        default_dict = {}
        def_re = re.compile(r"param_(\d+)_default")

        for option in self.bridge_template.options(name):
            match = def_re.match(option)
            if match:
                try:
                    idx = int(match.group(1))
                except ValueError:
                    raise ParseError(
                        "Invalid value [%s] for parameter number" % match.group(1)
                    )
                default_dict[idx] = self.bridge_template.get(name, option)

        return default_dict

    def getFlags(self, name):
        """Return list of flags set for this function

        @param name: Name of the function to get
        @return: List of flags (string)
        """
        flags = []
        for option in self.bridge_template.options(name):
            if option in C.DECLARATION_FLAGS:
                flags.append(option)
        return flags

    def getArgumentsDoc(self, name):
        """Return documentation of arguments
        @param name: Name of the function to get
        @return: dict, each key is the integer param number (no key if no argument doc), value is a tuple (name, doc)"""
        doc_dict = {}
        option_re = re.compile(r"doc_param_(\d+)")
        value_re = re.compile(r"^(\w+): (.*)$", re.MULTILINE | re.DOTALL)
        for option in self.bridge_template.options(name):
            if option == "doc_return":
                doc_dict["return"] = self.bridge_template.get(name, option)
                continue
            match = option_re.match(option)
            if match:
                try:
                    idx = int(match.group(1))
                except ValueError:
                    raise ParseError(
                        "Invalid value [%s] for parameter number" % match.group(1)
                    )
                value_match = value_re.match(self.bridge_template.get(name, option))
                if not value_match:
                    raise ParseError("Invalid value for parameter doc [%i]" % idx)
                doc_dict[idx] = (value_match.group(1), value_match.group(2))
        return doc_dict

    def getDoc(self, name):
        """Return documentation of the method
        @param name: Name of the function to get
        @return: string documentation, or None"""
        if self.bridge_template.has_option(name, "doc"):
            return self.bridge_template.get(name, "doc")
        return None

    def argumentsParser(self, signature):
        """Generator which return individual arguments signatures from a global signature"""
        start = 0
        i = 0

        while i < len(signature):
            if signature[i] not in ["b", "y", "n", "i", "x", "q", "u", "t", "d", "s",
                                    "a"]:
                raise ParseError("Unmanaged attribute type [%c]" % signature[i])

            if signature[i] == "a":
                i += 1
                if (
                    signature[i] != "{" and signature[i] != "("
                ):  # FIXME: must manage tuples out of arrays
                    i += 1
                    yield signature[start:i]
                    start = i
                    continue  # we have a simple type for the array
                opening_car = signature[i]
                assert opening_car in ["{", "("]
                closing_car = "}" if opening_car == "{" else ")"
                opening_count = 1
                while True:  # we have a dict or a list of tuples
                    i += 1
                    if i >= len(signature):
                        raise ParseError("missing }")
                    if signature[i] == opening_car:
                        opening_count += 1
                    if signature[i] == closing_car:
                        opening_count -= 1
                        if opening_count == 0:
                            break
            i += 1
            yield signature[start:i]
            start = i

    def getArguments(self, signature, name=None, default=None, unicode_protect=False):
        """Return arguments to user given a signature

        @param signature: signature in the short form (using s,a,i,b etc)
        @param name: dictionary of arguments name like given by getArgumentsDoc
        @param default: dictionary of default values, like given by getDefault
        @param unicode_protect: activate unicode protection on strings (return strings as unicode(str))
        @return (str): arguments that correspond to a signature (e.g.: "sss" return "arg1, arg2, arg3")
        """
        idx = 0
        attr_string = []

        for arg in self.argumentsParser(signature):
            attr_string.append(
                (
                    "unicode(%(name)s)%(default)s"
                    if (unicode_protect and arg == "s")
                    else "%(name)s%(default)s"
                )
                % {
                    "name": name[idx][0] if (name and idx in name) else "arg_%i" % idx,
                    "default": "=" + default[idx] if (default and idx in default) else "",
                }
            )
            # give arg_1, arg2, etc or name1, name2=default, etc.
            # give unicode(arg_1), unicode(arg_2), etc. if unicode_protect is set and arg is a string
            idx += 1

        return ", ".join(attr_string)

    def getTemplatePath(self, template_file):
        """return template path corresponding to file name

        @param template_file(str): name of template file
        """
        return os.path.join(self.constructor_dir, template_file)

    def core_completion_method(self, completion, function, default, arg_doc, async_):
        """override this method to extend completion"""
        pass

    def core_completion_signal(self, completion, function, default, arg_doc, async_):
        """override this method to extend completion"""
        pass

    def frontend_completion_method(self, completion, function, default, arg_doc, async_):
        """override this method to extend completion"""
        pass

    def frontend_completion_signal(self, completion, function, default, arg_doc, async_):
        """override this method to extend completion"""
        pass

    def generate(self, side):
        """generate bridge

        call generateCoreSide or generateFrontendSide if they exists
        else call generic self._generate method
        """
        try:
            if side == "core":
                method = self.generateCoreSide
            elif side == "frontend":
                if not self.FRONTEND_ACTIVATE:
                    print(u"This constructor only handle core, please use core side")
                    sys.exit(1)
                method = self.generateFrontendSide
        except AttributeError:
            self._generate(side)
        else:
            method()

    def _generate(self, side):
        """generate the backend

        this is a generic method which will use formats found in self.CORE_SIGNAL_FORMAT
        and self.CORE_METHOD_FORMAT (standard format method will be used)
        @param side(str): core or frontend
        """
        side_vars = []
        for var in ("FORMATS", "TEMPLATE", "DEST"):
            attr = "{}_{}".format(side.upper(), var)
            value = getattr(self, attr)
            if value is None:
                raise NotImplementedError
            side_vars.append(value)

        FORMATS, TEMPLATE, DEST = side_vars
        del side_vars

        parts = {part.upper(): [] for part in FORMATS}
        sections = self.bridge_template.sections()
        sections.sort()
        for section in sections:
            function = self.getValues(section)
            print("Adding %s %s" % (section, function["type"]))
            default = self.getDefault(section)
            arg_doc = self.getArgumentsDoc(section)
            async_ = "async" in self.getFlags(section)
            completion = {
                "sig_in": function["sig_in"] or "",
                "sig_out": function["sig_out"] or "",
                "category": "plugin" if function["category"] == "plugin" else "core",
                "name": section,
                # arguments with default values
                "args": self.getArguments(
                    function["sig_in"], name=arg_doc, default=default
                ),
            }

            extend_method = getattr(
                self, "{}_completion_{}".format(side, function["type"])
            )
            extend_method(completion, function, default, arg_doc, async_)

            for part, fmt in FORMATS.iteritems():
                if part.startswith(function["type"]):
                    parts[part.upper()].append(fmt.format(**completion))

        # at this point, signals_part, methods_part and direct_calls should be filled,
        # we just have to place them in the right part of the template
        bridge = []
        const_override = {
            env[len(C.ENV_OVERRIDE) :]: v
            for env, v in os.environ.iteritems()
            if env.startswith(C.ENV_OVERRIDE)
        }
        template_path = self.getTemplatePath(TEMPLATE)
        try:
            with open(template_path) as template:
                for line in template:

                    for part, extend_list in parts.iteritems():
                        if line.startswith("##{}_PART##".format(part)):
                            bridge.extend(extend_list)
                            break
                    else:
                        # the line is not a magic part replacement
                        if line.startswith("const_"):
                            const_name = line[len("const_") : line.find(" = ")].strip()
                            if const_name in const_override:
                                print("const {} overriden".format(const_name))
                                bridge.append(
                                    "const_{} = {}".format(
                                        const_name, const_override[const_name]
                                    )
                                )
                                continue
                        bridge.append(line.replace("\n", ""))
        except IOError:
            print("can't open template file [{}]".format(template_path))
            sys.exit(1)

        # now we write to final file
        self.finalWrite(DEST, bridge)

    def finalWrite(self, filename, file_buf):
        """Write the final generated file in [dest dir]/filename

        @param filename: name of the file to generate
        @param file_buf: list of lines (stings) of the file
        """
        if os.path.exists(self.args.dest_dir) and not os.path.isdir(self.args.dest_dir):
            print(
                "The destination dir [%s] can't be created: a file with this name already exists !"
            )
            sys.exit(1)
        try:
            if not os.path.exists(self.args.dest_dir):
                os.mkdir(self.args.dest_dir)
            full_path = os.path.join(self.args.dest_dir, filename)
            if os.path.exists(full_path) and not self.args.force:
                print(
                    "The destination file [%s] already exists ! Use --force to overwrite it"
                    % full_path
                )
            try:
                with open(full_path, "w") as dest_file:
                    dest_file.write("\n".join(file_buf))
            except IOError:
                print("Can't open destination file [%s]" % full_path)
        except OSError:
            print("It's not possible to generate the file, check your permissions")
            exit(1)
