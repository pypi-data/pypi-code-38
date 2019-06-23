#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Salut à Toi: an XMPP client
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

""" regex tools common to backend and frontends """

import re

path_escape = {"%": "%25", "/": "%2F", "\\": "%5c"}
path_escape_rev = {re.escape(v): k for k, v in path_escape.iteritems()}
path_escape = {re.escape(k): v for k, v in path_escape.iteritems()}
#  thanks to Martijn Pieters (https://stackoverflow.com/a/14693789)
RE_ANSI_REMOVE = re.compile(r"\x1b[^m]*m")


def reJoin(exps):
    """Join (OR) various regexes"""
    return re.compile("|".join(exps))


def reSubDict(pattern, repl_dict, string):
    """Replace key, value found in dict according to pattern

    @param pattern(basestr): pattern using keys found in repl_dict
    @repl_dict(dict): keys found in this dict will be replaced by
        corresponding values
    @param string(basestr): string to use for the replacement
    """
    return pattern.sub(lambda m: repl_dict[re.escape(m.group(0))], string)


path_escape_re = reJoin(path_escape.keys())
path_escape_rev_re = reJoin(path_escape_rev.keys())


def pathEscape(string):
    """Escape string so it can be use in a file path

    @param string(basestr): string to escape
    @return (str, unicode): escaped string, usable in a file path
    """
    return reSubDict(path_escape_re, path_escape, string)


def pathUnescape(string):
    """Unescape string from value found in file path

    @param string(basestr): string found in file path
    @return (str, unicode): unescaped string
    """
    return reSubDict(path_escape_rev_re, path_escape_rev, string)


def ansiRemove(string):
    """Remove ANSI escape codes from string

    @param string(basestr): string to filter
    @return (str, unicode): string without ANSI escape codes
    """
    return RE_ANSI_REMOVE.sub("", string)
