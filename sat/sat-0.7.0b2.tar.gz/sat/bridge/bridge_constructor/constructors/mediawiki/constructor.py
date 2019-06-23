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
import sys
from datetime import datetime
import re


class MediawikiConstructor(base_constructor.Constructor):
    def __init__(self, bridge_template, options):
        base_constructor.Constructor.__init__(self, bridge_template, options)
        self.core_template = "mediawiki_template.tpl"
        self.core_dest = "mediawiki.wiki"

    def _addTextDecorations(self, text):
        """Add text decorations like coloration or shortcuts"""

        def anchor_link(match):
            link = match.group(1)
            # we add anchor_link for [method_name] syntax:
            if link in self.bridge_template.sections():
                return "[[#%s|%s]]" % (link, link)
            print("WARNING: found an anchor link to an unknown method")
            return link

        return re.sub(r"\[(\w+)\]", anchor_link, text)

    def _wikiParameter(self, name, sig_in):
        """Format parameters with the wiki syntax
        @param name: name of the function
        @param sig_in: signature in
        @return: string of the formated parameters"""
        arg_doc = self.getArgumentsDoc(name)
        arg_default = self.getDefault(name)
        args_str = self.getArguments(sig_in)
        args = args_str.split(", ") if args_str else []  # ugly but it works :)
        wiki = []
        for i in range(len(args)):
            if i in arg_doc:
                name, doc = arg_doc[i]
                doc = "\n:".join(doc.rstrip("\n").split("\n"))
                wiki.append("; %s: %s" % (name, self._addTextDecorations(doc)))
            else:
                wiki.append("; arg_%d: " % i)
            if i in arg_default:
                wiki.append(":''DEFAULT: %s''" % arg_default[i])
        return "\n".join(wiki)

    def _wikiReturn(self, name):
        """Format return doc with the wiki syntax
        @param name: name of the function
        """
        arg_doc = self.getArgumentsDoc(name)
        wiki = []
        if "return" in arg_doc:
            wiki.append("\n|-\n! scope=row | return value\n|")
            wiki.append(
                "<br />\n".join(
                    self._addTextDecorations(arg_doc["return"]).rstrip("\n").split("\n")
                )
            )
        return "\n".join(wiki)

    def generateCoreSide(self):
        signals_part = []
        methods_part = []
        sections = self.bridge_template.sections()
        sections.sort()
        for section in sections:
            function = self.getValues(section)
            print("Adding %s %s" % (section, function["type"]))
            async_msg = """<br />'''This method is asynchronous'''"""
            deprecated_msg = """<br />'''<font color="#FF0000">/!\ WARNING /!\ : This method is deprecated, please don't use it !</font>'''"""
            signature_signal = (
                """\
! scope=row | signature
| %s
|-\
"""
                % function["sig_in"]
            )
            signature_method = """\
! scope=row | signature in
| %s
|-
! scope=row | signature out
| %s
|-\
""" % (
                function["sig_in"],
                function["sig_out"],
            )
            completion = {
                "signature": signature_signal
                if function["type"] == "signal"
                else signature_method,
                "sig_out": function["sig_out"] or "",
                "category": function["category"],
                "name": section,
                "doc": self.getDoc(section) or "FIXME: No description available",
                "async": async_msg if "async" in self.getFlags(section) else "",
                "deprecated": deprecated_msg
                if "deprecated" in self.getFlags(section)
                else "",
                "parameters": self._wikiParameter(section, function["sig_in"]),
                "return": self._wikiReturn(section)
                if function["type"] == "method"
                else "",
            }

            dest = signals_part if function["type"] == "signal" else methods_part
            dest.append(
                """\
== %(name)s ==
''%(doc)s''
%(deprecated)s
%(async)s
{| class="wikitable" style="text-align:left; width:80%%;"
! scope=row | category
| %(category)s
|-
%(signature)s
! scope=row | parameters
|
%(parameters)s%(return)s
|}
"""
                % completion
            )

        # at this point, signals_part, and methods_part should be filled,
        # we just have to place them in the right part of the template
        core_bridge = []
        template_path = self.getTemplatePath(self.core_template)
        try:
            with open(template_path) as core_template:
                for line in core_template:
                    if line.startswith("##SIGNALS_PART##"):
                        core_bridge.extend(signals_part)
                    elif line.startswith("##METHODS_PART##"):
                        core_bridge.extend(methods_part)
                    elif line.startswith("##TIMESTAMP##"):
                        core_bridge.append("Generated on %s" % datetime.now())
                    else:
                        core_bridge.append(line.replace("\n", ""))
        except IOError:
            print("Can't open template file [%s]" % template_path)
            sys.exit(1)

        # now we write to final file
        self.finalWrite(self.core_dest, core_bridge)
