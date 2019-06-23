#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT helpers methods for plugins
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

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

import re

# Regexp from http://daringfireball.net/2010/07/improved_regex_for_matching_urls
RE_URL = re.compile(
    r"""(?i)\b((?:[a-z]{3,}://|(www|ftp)\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/|mailto:|xmpp:)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?]))"""
)


# TODO: merge this class with an other module or at least rename it (strings is not a good name)


def getURLParams(url):
    """This comes from pyjamas.Location.makeUrlDict with a small change
    to also parse full URLs, and parameters with no value specified
    (in that case the default value "" is used).
    @param url: any URL with or without parameters
    @return: a dictionary of the parameters, if any was given, or {}
    """
    dict_ = {}
    if "/" in url:
        # keep the part after the last "/"
        url = url[url.rindex("/") + 1 :]
    if url.startswith("?"):
        # remove the first "?"
        url = url[1:]
    pairs = url.split("&")
    for pair in pairs:
        if len(pair) < 3:
            continue
        kv = pair.split("=", 1)
        dict_[kv[0]] = kv[1] if len(kv) > 1 else ""
    return dict_


def addURLToText(string, new_target=True):
    """Check a text for what looks like an URL and make it clickable.

    @param string (unicode): text to process
    @param new_target (bool): if True, make the link open in a new window
    """
    # XXX: report any change to libervia.browser.strings.addURLToText
    def repl(match):
        url = match.group(0)
        if not re.match(r"""[a-z]{3,}://|mailto:|xmpp:""", url):
            url = "http://" + url
        target = ' target="_blank"' if new_target else ""
        return '<a href="%s"%s class="url">%s</a>' % (url, target, match.group(0))

    return RE_URL.sub(repl, string)


def addURLToImage(string):
    """Check a XHTML text for what looks like an imageURL and make it clickable.

    @param string (unicode): text to process
    """
    # XXX: report any change to libervia.browser.strings.addURLToImage
    def repl(match):
        url = match.group(1)
        return '<a href="%s" target="_blank">%s</a>' % (url, match.group(0))

    pattern = r"""<img[^>]* src="([^"]+)"[^>]*>"""
    return re.sub(pattern, repl, string)


def fixXHTMLLinks(xhtml):
    """Add http:// if the scheme is missing and force opening in a new window.

    @param string (unicode): XHTML Content
    """
    subs = []
    for match in re.finditer(r'<a( \w+="[^"]*")* ?/?>', xhtml):
        tag = match.group(0)
        url = re.search(r'href="([^"]*)"', tag)
        if url and not url.group(1).startswith("#"):  # skip internal anchor
            if not re.search(r'target="([^"]*)"', tag):  # no target
                subs.append((tag, '<a target="_blank"%s' % tag[2:]))
            if not re.match(r"^\w+://", url.group(1)):  # no scheme
                subs.append((url.group(0), 'href="http://%s"' % url.group(1)))

    for url, new_url in subs:
        xhtml = xhtml.replace(url, new_url)
    return xhtml
