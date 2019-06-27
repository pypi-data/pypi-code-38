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


from sat.bridge import bridge_constructor
from sat.bridge.bridge_constructor.constants import Const as C
from sat.bridge.bridge_constructor import constructors, base_constructor
import argparse
from ConfigParser import SafeConfigParser as Parser
from importlib import import_module
import os
import os.path

# consts
__version__ = C.APP_VERSION


class BridgeConstructor(object):
    def importConstructors(self):
        constructors_dir = os.path.dirname(constructors.__file__)
        self.protocoles = {}
        for dir_ in os.listdir(constructors_dir):
            init_path = os.path.join(constructors_dir, dir_, "__init__.py")
            constructor_path = os.path.join(constructors_dir, dir_, "constructor.py")
            module_path = "sat.bridge.bridge_constructor.constructors.{}.constructor".format(
                dir_
            )
            if os.path.isfile(init_path) and os.path.isfile(constructor_path):
                mod = import_module(module_path)
                for attr in dir(mod):
                    obj = getattr(mod, attr)
                    if not isinstance(obj, type):
                        continue
                    if issubclass(obj, base_constructor.Constructor):
                        name = obj.NAME or dir_
                        self.protocoles[name] = obj
                        break
        if not self.protocoles:
            raise ValueError("no protocole constructor found")

    def parse_args(self):
        """Check command line options"""
        parser = argparse.ArgumentParser(
            description=C.DESCRIPTION,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.add_argument("--version", action="version", version=__version__)
        default_protocole = (
            C.DEFAULT_PROTOCOLE
            if C.DEFAULT_PROTOCOLE in self.protocoles
            else self.protocoles[0]
        )
        parser.add_argument(
            "-p",
            "--protocole",
            choices=sorted(self.protocoles),
            default=default_protocole,
            help="generate bridge using PROTOCOLE (default: %(default)s)",
        )  # (default: %s, possible values: [%s])" % (DEFAULT_PROTOCOLE, ", ".join(MANAGED_PROTOCOLES)))
        parser.add_argument(
            "-s",
            "--side",
            choices=("core", "frontend"),
            default="core",
            help="which side of the bridge do you want to make ?",
        )  # (default: %default, possible values: [core, frontend])")
        default_template = os.path.join(
            os.path.dirname(bridge_constructor.__file__), "bridge_template.ini"
        )
        parser.add_argument(
            "-t",
            "--template",
            type=file,
            default=default_template,
            help="use TEMPLATE to generate bridge (default: %(default)s)",
        )
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help=("force overwritting of existing files"),
        )
        parser.add_argument(
            "-d", "--debug", action="store_true", help=("add debug information printing")
        )
        parser.add_argument(
            "--no-unicode",
            action="store_false",
            dest="unicode",
            help=("remove unicode type protection from string results"),
        )
        parser.add_argument(
            "--flags", nargs="+", default=[], help=("constructors' specific flags")
        )
        parser.add_argument(
            "--dest-dir",
            default=C.DEST_DIR_DEFAULT,
            help=(
                "directory when the generated files will be written (default: %(default)s)"
            ),
        )

        return parser.parse_args()

    def go(self):
        self.importConstructors()
        args = self.parse_args()
        template_parser = Parser()
        try:
            template_parser.readfp(args.template)
        except IOError:
            print("The template file doesn't exist or is not accessible")
            exit(1)
        constructor = self.protocoles[args.protocole](template_parser, args)
        constructor.generate(args.side)


if __name__ == "__main__":
    bc = BridgeConstructor()
    bc.go()
