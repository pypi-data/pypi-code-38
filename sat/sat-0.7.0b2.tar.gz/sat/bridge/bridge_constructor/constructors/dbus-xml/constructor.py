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

from sat.bridge.bridge_constructor import base_constructor
from xml.dom import minidom
import sys


class DbusXmlConstructor(base_constructor.Constructor):
    """Constructor for DBus XML syntaxt (used by Qt frontend)"""

    def __init__(self, bridge_template, options):
        base_constructor.Constructor.__init__(self, bridge_template, options)

        self.template = "dbus_xml_template.xml"
        self.core_dest = "org.salutatoi.sat.xml"
        self.default_annotation = {
            "a{ss}": "StringDict",
            "a(sa{ss}as)": "QList<Contact>",
            "a{i(ss)}": "HistoryT",
            "a(sss)": "QList<MenuT>",
            "a{sa{s(sia{ss})}}": "PresenceStatusT",
        }

    def generateCoreSide(self):
        try:
            doc = minidom.parse(self.getTemplatePath(self.template))
            interface_elt = doc.getElementsByTagName("interface")[0]
        except IOError:
            print("Can't access template")
            sys.exit(1)
        except IndexError:
            print("Template error")
            sys.exit(1)

        sections = self.bridge_template.sections()
        sections.sort()
        for section in sections:
            function = self.getValues(section)
            print("Adding %s %s" % (section, function["type"]))
            new_elt = doc.createElement(
                "method" if function["type"] == "method" else "signal"
            )
            new_elt.setAttribute("name", section)

            idx = 0
            args_doc = self.getArgumentsDoc(section)
            for arg in self.argumentsParser(function["sig_in"] or ""):
                arg_elt = doc.createElement("arg")
                arg_elt.setAttribute(
                    "name", args_doc[idx][0] if idx in args_doc else "arg_%i" % idx
                )
                arg_elt.setAttribute("type", arg)
                _direction = "in" if function["type"] == "method" else "out"
                arg_elt.setAttribute("direction", _direction)
                new_elt.appendChild(arg_elt)
                if "annotation" in self.args.flags:
                    if arg in self.default_annotation:
                        annot_elt = doc.createElement("annotation")
                        annot_elt.setAttribute(
                            "name", "com.trolltech.QtDBus.QtTypeName.In%d" % idx
                        )
                        annot_elt.setAttribute("value", self.default_annotation[arg])
                        new_elt.appendChild(annot_elt)
                idx += 1

            if function["sig_out"]:
                arg_elt = doc.createElement("arg")
                arg_elt.setAttribute("type", function["sig_out"])
                arg_elt.setAttribute("direction", "out")
                new_elt.appendChild(arg_elt)
                if "annotation" in self.args.flags:
                    if function["sig_out"] in self.default_annotation:
                        annot_elt = doc.createElement("annotation")
                        annot_elt.setAttribute(
                            "name", "com.trolltech.QtDBus.QtTypeName.Out0"
                        )
                        annot_elt.setAttribute(
                            "value", self.default_annotation[function["sig_out"]]
                        )
                        new_elt.appendChild(annot_elt)

            interface_elt.appendChild(new_elt)

        # now we write to final file
        self.finalWrite(self.core_dest, [doc.toprettyxml()])
