#!/usr/bin/env python2
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

from sat.core.i18n import _
from sat_frontends.jp.constants import Const as C

def etreeParse(cmd, raw_xml, reraise=False):
    """Import lxml and parse raw XML

    @param cmd(CommandBase): current command instance
    @param raw_xml(file, str): an XML bytestring, string or file-like object
    @param reraise(bool): if True, re raise exception on parse error instead of doing a
        parser.error (which terminate the execution)
    @return (tuple(etree.Element, module): parsed element, etree module
    """
    try:
        from lxml import etree
    except ImportError:
        cmd.disp(
            u'lxml module must be installed, please install it with "pip install lxml"',
            error=True,
        )
        cmd.host.quit(C.EXIT_ERROR)
    try:
        if isinstance(raw_xml, basestring):
            parser = etree.XMLParser(remove_blank_text=True)
            element = etree.fromstring(raw_xml, parser)
        else:
            element = etree.parse(raw_xml).getroot()
    except Exception as e:
        if reraise:
            raise e
        cmd.parser.error(
            _(u"Can't parse the payload XML in input: {msg}").format(msg=e)
        )
    return element, etree

def getPayload(cmd, element):
    """Retrieve payload element and exit with and error if not found

    @param element(etree.Element): root element
    @return element(etree.Element): payload element
    """
    if element.tag in ("item", "{http://jabber.org/protocol/pubsub}item"):
        if len(element) > 1:
            cmd.disp(_(u"<item> can only have one child element (the payload)"),
                     error=True)
            cmd.host.quit(C.EXIT_DATA_ERROR)
        element = element[0]
    return element
