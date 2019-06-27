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
from sat.core import exceptions


def escape(arg, smart=True):
    """format arg with quotes

    @param smart(bool): if True, only escape if needed
    """
    if smart and not " " in arg and not '"' in arg:
        return arg
    return u'"' + arg.replace(u'"', u'\\"') + u'"'


def get_cmd_choices(cmd=None, parser=None):
    try:
        choices = parser._subparsers._group_actions[0].choices
        return choices[cmd] if cmd is not None else choices
    except (KeyError, AttributeError):
        raise exceptions.NotFound


def get_use_args(host, args, use, verbose=False, parser=None):
    """format args for argparse parser with values prefilled

    @param host(JP): jp instance
    @param args(list(str)): arguments to use
    @param use(dict[str, str]): arguments to fill if found in parser
    @param verbose(bool): if True a message will be displayed when argument is used or not
    @param parser(argparse.ArgumentParser): parser to use
    @return (tuple[list[str],list[str]]): 2 args lists:
        - parser args, i.e. given args corresponding to parsers
        - use args, i.e. generated args from use
    """
    # FIXME: positional args are not handled correclty
    #        if there is more that one, the position is not corrected
    if parser is None:
        parser = host.parser

    # we check not optional args to see if there
    # is a corresonding parser
    # else USE args would not work correctly (only for current parser)
    parser_args = []
    for arg in args:
        if arg.startswith("-"):
            break
        try:
            parser = get_cmd_choices(arg, parser)
        except exceptions.NotFound:
            break
        parser_args.append(arg)

    # post_args are remaning given args,
    # without the ones corresponding to parsers
    post_args = args[len(parser_args) :]

    opt_args = []
    pos_args = []
    actions = {a.dest: a for a in parser._actions}
    for arg, value in use.iteritems():
        try:
            if arg == u"item" and not u"item" in actions:
                # small hack when --item is appended to a --items list
                arg = u"items"
            action = actions[arg]
        except KeyError:
            if verbose:
                host.disp(
                    _(
                        u"ignoring {name}={value}, not corresponding to any argument (in USE)"
                    ).format(name=arg, value=escape(value))
                )
        else:
            if verbose:
                host.disp(
                    _(u"arg {name}={value} (in USE)").format(
                        name=arg, value=escape(value)
                    )
                )
            if not action.option_strings:
                pos_args.append(value)
            else:
                opt_args.append(action.option_strings[0])
                opt_args.append(value)
    return parser_args, opt_args + pos_args + post_args
