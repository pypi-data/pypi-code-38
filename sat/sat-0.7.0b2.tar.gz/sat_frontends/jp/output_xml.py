#! /usr/bin/python
# -*- coding: utf-8 -*-

# jp: a SàT command line tool
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
"""Standard outputs"""


from sat_frontends.jp.constants import Const as C
from sat.core.i18n import _
from lxml import etree
from sat.core.log import getLogger

log = getLogger(__name__)
import sys

try:
    import pygments
    from pygments.lexers.html import XmlLexer
    from pygments.formatters import TerminalFormatter
except ImportError:
    pygments = None


__outputs__ = ["XML"]
RAW = u"xml_raw"
PRETTY = u"xml_pretty"


class XML(object):
    """Outputs for XML"""

    def __init__(self, host):
        self.host = host
        host.register_output(C.OUTPUT_XML, PRETTY, self.pretty, default=True)
        host.register_output(C.OUTPUT_LIST_XML, PRETTY, self.pretty_list, default=True)
        host.register_output(C.OUTPUT_XML, RAW, self.raw)
        host.register_output(C.OUTPUT_LIST_XML, RAW, self.list_raw)

    def colorize(self, xml):
        if pygments is None:
            self.host.disp(
                _(
                    u"Pygments is not available, syntax highlighting is not possible. Please install if from http://pygments.org or with pip install pygments"
                ),
                error=True,
            )
            return xml
        if not sys.stdout.isatty():
            return xml
        lexer = XmlLexer(encoding="utf-8")
        formatter = TerminalFormatter(bg=u"dark")
        return pygments.highlight(xml, lexer, formatter)

    def format(self, data, pretty=True):
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(data, parser)
        xml = etree.tostring(tree, encoding="unicode", pretty_print=pretty)
        return self.colorize(xml)

    def format_no_pretty(self, data):
        return self.format(data, pretty=False)

    def pretty(self, data):
        self.host.disp(self.format(data))

    def pretty_list(self, data, separator=u"\n"):
        list_pretty = map(self.format, data)
        self.host.disp(separator.join(list_pretty))

    def raw(self, data):
        self.host.disp(self.format_no_pretty(data))

    def list_raw(self, data, separator=u"\n"):
        list_no_pretty = map(self.format_no_pretty, data)
        self.host.disp(separator.join(list_no_pretty))
