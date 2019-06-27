#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Primitivus: a SAT frontend
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

from sat_frontends.quick_frontend import constants
from sat.tools.common.ansi import ANSI as A


class Const(constants.Const):

    APP_NAME = u"jp"
    PLUGIN_CMD = u"commands"
    PLUGIN_OUTPUT = u"outputs"
    OUTPUT_TEXT = u"text"  # blob of unicode text
    OUTPUT_DICT = u"dict"  # simple key/value dictionary
    OUTPUT_LIST = u"list"
    OUTPUT_LIST_DICT = u"list_dict"  # list of dictionaries
    OUTPUT_DICT_DICT = u"dict_dict"  # dict  of nested dictionaries
    OUTPUT_MESS = u"mess"  # messages (chat)
    OUTPUT_COMPLEX = u"complex"  # complex data (e.g. multi-level dictionary)
    OUTPUT_XML = u"xml"  # XML node (as unicode string)
    OUTPUT_LIST_XML = u"list_xml"  # list of XML nodes (as unicode strings)
    OUTPUT_XMLUI = u"xmlui"  # XMLUI as unicode string
    OUTPUT_LIST_XMLUI = u"list_xmlui"  # list of XMLUI (as unicode strings)
    OUTPUT_TYPES = (
        OUTPUT_TEXT,
        OUTPUT_DICT,
        OUTPUT_LIST,
        OUTPUT_LIST_DICT,
        OUTPUT_DICT_DICT,
        OUTPUT_MESS,
        OUTPUT_COMPLEX,
        OUTPUT_XML,
        OUTPUT_LIST_XML,
        OUTPUT_XMLUI,
        OUTPUT_LIST_XMLUI,
    )

    # Pubsub options flags
    SERVICE = u"service"  # service required
    NODE = u"node"  # node required
    ITEM = u"item"  # item required
    SINGLE_ITEM = u"single_item"  # only one item is allowed
    MULTI_ITEMS = u"multi_items"  # multiple items are allowed
    NO_MAX = u"no_max"  # don't add --max option for multi items

    # ANSI
    A_HEADER = A.BOLD + A.FG_YELLOW
    A_SUBHEADER = A.BOLD + A.FG_RED
    # A_LEVEL_COLORS may be used to cycle on colors according to depth of data
    A_LEVEL_COLORS = (A_HEADER, A.BOLD + A.FG_BLUE, A.FG_MAGENTA, A.FG_CYAN)
    A_SUCCESS = A.BOLD + A.FG_GREEN
    A_FAILURE = A.BOLD + A.FG_RED
    #  A_PROMPT_* is for shell
    A_PROMPT_PATH = A.BOLD + A.FG_CYAN
    A_PROMPT_SUF = A.BOLD
    # Files
    A_DIRECTORY = A.BOLD + A.FG_CYAN
    A_FILE = A.FG_WHITE

    # exit codes
    EXIT_OK = 0
    EXIT_ERROR = 1  # generic error, when nothing else match
    EXIT_BAD_ARG = 2  # arguments given by user are bad
    EXIT_BRIDGE_ERROR = 3  # can't connect to bridge
    EXIT_BRIDGE_ERRBACK = 4  # something went wrong when calling a bridge method
    EXIT_NOT_FOUND = 16  # an item required by a command was not found
    EXIT_DATA_ERROR = 17  # data needed for a command is invalid
    EXIT_MISSING_FEATURE = 18  # a needed plugin or feature is not available
    EXIT_USER_CANCELLED = 20  # user cancelled action
    EXIT_FILE_NOT_EXE = (
        126
    )  # a file to be executed was found, but it was not an executable utility (cf. man 1 exit)
    EXIT_CMD_NOT_FOUND = 127  # a utility to be executed was not found (cf. man 1 exit)
    EXIT_CMD_ERROR = 127  # a utility to be executed returned an error exit code
    EXIT_SIGNAL_INT = 128  # a command was interrupted by a signal (cf. man 1 exit)
