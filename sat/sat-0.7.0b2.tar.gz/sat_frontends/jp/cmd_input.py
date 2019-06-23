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


import base
from sat.core.i18n import _
from sat.core import exceptions
from sat_frontends.jp.constants import Const as C
from sat.tools.common.ansi import ANSI as A
import subprocess
import argparse
import sys

__commands__ = ["Input"]
OPT_STDIN = "stdin"
OPT_SHORT = "short"
OPT_LONG = "long"
OPT_POS = "positional"
OPT_IGNORE = "ignore"
OPT_TYPES = (OPT_STDIN, OPT_SHORT, OPT_LONG, OPT_POS, OPT_IGNORE)
OPT_EMPTY_SKIP = "skip"
OPT_EMPTY_IGNORE = "ignore"
OPT_EMPTY_CHOICES = (OPT_EMPTY_SKIP, OPT_EMPTY_IGNORE)


class InputCommon(base.CommandBase):
    def __init__(self, host, name, help):
        base.CommandBase.__init__(
            self, host, name, use_verbose=True, use_profile=False, help=help
        )
        self.idx = 0
        self.reset()

    def reset(self):
        self.args_idx = 0
        self._stdin = []
        self._opts = []
        self._pos = []
        self._values_ori = []

    def add_parser_options(self):
        self.parser.add_argument(
            "--encoding", default="utf-8", help=_(u"encoding of the input data")
        )
        self.parser.add_argument(
            "-i",
            "--stdin",
            action="append_const",
            const=(OPT_STDIN, None),
            dest="arguments",
            help=_(u"standard input"),
        )
        self.parser.add_argument(
            "-s",
            "--short",
            type=self.opt(OPT_SHORT),
            action="append",
            dest="arguments",
            help=_(u"short option"),
        )
        self.parser.add_argument(
            "-l",
            "--long",
            type=self.opt(OPT_LONG),
            action="append",
            dest="arguments",
            help=_(u"long option"),
        )
        self.parser.add_argument(
            "-p",
            "--positional",
            type=self.opt(OPT_POS),
            action="append",
            dest="arguments",
            help=_(u"positional argument"),
        )
        self.parser.add_argument(
            "-x",
            "--ignore",
            action="append_const",
            const=(OPT_IGNORE, None),
            dest="arguments",
            help=_(u"ignore value"),
        )
        self.parser.add_argument(
            "-D",
            "--debug",
            action="store_true",
            help=_(u"don't actually run commands but echo what would be launched"),
        )
        self.parser.add_argument(
            "--log", type=argparse.FileType("wb"), help=_(u"log stdout to FILE")
        )
        self.parser.add_argument(
            "--log-err", type=argparse.FileType("wb"), help=_(u"log stderr to FILE")
        )
        self.parser.add_argument("command", nargs=argparse.REMAINDER)

    def opt(self, type_):
        return lambda s: (type_, s)

    def addValue(self, value):
        """add a parsed value according to arguments sequence"""
        self._values_ori.append(value)
        arguments = self.args.arguments
        try:
            arg_type, arg_name = arguments[self.args_idx]
        except IndexError:
            self.disp(
                _(u"arguments in input data and in arguments sequence don't match"),
                error=True,
            )
            self.host.quit(C.EXIT_DATA_ERROR)
        self.args_idx += 1
        while self.args_idx < len(arguments):
            next_arg = arguments[self.args_idx]
            if next_arg[0] not in OPT_TYPES:
                # value will not be used if False or None, so we skip filter
                if value not in (False, None):
                    # we have a filter
                    filter_type, filter_arg = arguments[self.args_idx]
                    value = self.filter(filter_type, filter_arg, value)
            else:
                break
            self.args_idx += 1

        if value is None:
            # we ignore this argument
            return

        if value is False:
            # we skip the whole row
            if self.args.debug:
                self.disp(
                    A.color(
                        C.A_SUBHEADER,
                        _(u"values: "),
                        A.RESET,
                        u", ".join(self._values_ori),
                    ),
                    2,
                )
                self.disp(A.color(A.BOLD, _(u"**SKIPPING**\n")))
            self.reset()
            self.idx += 1
            raise exceptions.CancelError

        if not isinstance(value, list):
            value = [value]

        for v in value:
            if arg_type == OPT_STDIN:
                self._stdin.append(v.encode("utf-8"))
            elif arg_type == OPT_SHORT:
                self._opts.append("-{}".format(arg_name))
                self._opts.append(v.encode("utf-8"))
            elif arg_type == OPT_LONG:
                self._opts.append("--{}".format(arg_name))
                self._opts.append(v.encode("utf-8"))
            elif arg_type == OPT_POS:
                self._pos.append(v.encode("utf-8"))
            elif arg_type == OPT_IGNORE:
                pass
            else:
                self.parser.error(
                    _(
                        u"Invalid argument, an option type is expected, got {type_}:{name}"
                    ).format(type_=arg_type, name=arg_name)
                )

    def runCommand(self):
        """run requested command with parsed arguments"""
        if self.args_idx != len(self.args.arguments):
            self.disp(
                _(u"arguments in input data and in arguments sequence don't match"),
                error=True,
            )
            self.host.quit(C.EXIT_DATA_ERROR)
        self.disp(
            A.color(C.A_HEADER, _(u"command {idx}").format(idx=self.idx)),
            no_lf=not self.args.debug,
        )
        stdin = "".join(self._stdin)
        if self.args.debug:
            self.disp(
                A.color(
                    C.A_SUBHEADER, _(u"values: "), A.RESET, u", ".join(self._values_ori)
                ),
                2,
            )

            if stdin:
                self.disp(A.color(C.A_SUBHEADER, u"--- STDIN ---"))
                self.disp(stdin.decode("utf-8"))
                self.disp(A.color(C.A_SUBHEADER, u"-------------"))
            self.disp(
                u"{indent}{prog} {static} {options} {positionals}".format(
                    indent=4 * u" ",
                    prog=sys.argv[0],
                    static=" ".join(self.args.command).decode("utf-8"),
                    options=u" ".join([o.decode("utf-8") for o in self._opts]),
                    positionals=u" ".join([p.decode("utf-8") for p in self._pos]),
                )
            )
            self.disp(u"\n")
        else:
            self.disp(u" (" + u", ".join(self._values_ori) + u")", 2, no_lf=True)
            args = [sys.argv[0]] + self.args.command + self._opts + self._pos
            p = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            (stdout, stderr) = p.communicate(stdin)
            log = self.args.log
            log_err = self.args.log_err
            log_tpl = "{command}\n{buff}\n\n"
            if log:
                log.write(log_tpl.format(command=" ".join(args), buff=stdout))
            if log_err:
                log_err.write(log_tpl.format(command=" ".join(args), buff=stderr))
            ret = p.wait()
            if ret == 0:
                self.disp(A.color(C.A_SUCCESS, _(u"OK")))
            else:
                self.disp(A.color(C.A_FAILURE, _(u"FAILED")))

        self.reset()
        self.idx += 1

    def filter(self, filter_type, filter_arg, value):
        """change input value

        @param filter_type(unicode): name of the filter
        @param filter_arg(unicode, None): argument of the filter
        @param value(unicode): value to filter
        @return (unicode, False, None): modified value
            False to skip the whole row
            None to ignore this argument (but continue row with other ones)
        """
        raise NotImplementedError


class Csv(InputCommon):
    def __init__(self, host):
        super(Csv, self).__init__(host, "csv", _(u"comma-separated values"))

    def add_parser_options(self):
        InputCommon.add_parser_options(self)
        self.parser.add_argument(
            "-r",
            "--row",
            type=int,
            default=0,
            help=_(u"starting row (previous ones will be ignored)"),
        )
        self.parser.add_argument(
            "-S",
            "--split",
            action="append_const",
            const=("split", None),
            dest="arguments",
            help=_(u"split value in several options"),
        )
        self.parser.add_argument(
            "-E",
            "--empty",
            action="append",
            type=self.opt("empty"),
            dest="arguments",
            help=_(u"action to do on empty value ({choices})").format(
                choices=u", ".join(OPT_EMPTY_CHOICES)
            ),
        )

    def filter(self, filter_type, filter_arg, value):
        if filter_type == "split":
            return value.split()
        elif filter_type == "empty":
            if filter_arg == OPT_EMPTY_IGNORE:
                return value if value else None
            elif filter_arg == OPT_EMPTY_SKIP:
                return value if value else False
            else:
                self.parser.error(
                    _(u"--empty value must be one of {choices}").format(
                        choices=u", ".join(OPT_EMPTY_CHOICES)
                    )
                )

        super(Csv, self).filter(filter_type, filter_arg, value)

    def start(self):
        import csv

        reader = csv.reader(sys.stdin)
        for idx, row in enumerate(reader):
            try:
                if idx < self.args.row:
                    continue
                for value in row:
                    self.addValue(value.decode(self.args.encoding))
                self.runCommand()
            except exceptions.CancelError:
                #  this row has been cancelled, we skip it
                continue


class Input(base.CommandBase):
    subcommands = (Csv,)

    def __init__(self, host):
        super(Input, self).__init__(
            host,
            "input",
            use_profile=False,
            help=_(u"launch command with external input"),
        )
