#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
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

"""This library help manage XML used in SàT frontends """

# we don't import minidom as a different class can be used in frontends
# (e.g. NativeDOM in Libervia)


def inlineRoot(doc):
    """ make the root attribute inline
    @param root_node: minidom's Document compatible class
    @return: plain XML
    """
    root_elt = doc.documentElement
    if root_elt.hasAttribute("style"):
        styles_raw = root_elt.getAttribute("style")
        styles = styles_raw.split(";")
        new_styles = []
        for style in styles:
            try:
                key, value = style.split(":")
            except ValueError:
                continue
            if key.strip().lower() == "display":
                value = "inline"
            new_styles.append("%s: %s" % (key.strip(), value.strip()))
        root_elt.setAttribute("style", "; ".join(new_styles))
    else:
        root_elt.setAttribute("style", "display: inline")
    return root_elt.toxml()
