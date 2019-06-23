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
import cmd
import sys
from sat.core.i18n import _
from sat.core import exceptions
from sat_frontends.jp.constants import Const as C
from sat_frontends.jp import arg_tools
from sat.tools.common.ansi import ANSI as A
import shlex
import subprocess

__commands__ = ["Shell"]
INTRO = _(
    u"""Welcome to {app_name} shell, the Salut à Toi shell !

This enrironment helps you using several {app_name} commands with similar parameters.

To quit, just enter "quit" or press C-d.
Enter "help" or "?" to know what to do
"""
).format(app_name=C.APP_NAME)


class Shell(base.CommandBase, cmd.Cmd):
    def __init__(self, host):
        base.CommandBase.__init__(
            self, host, "shell", help=_(u"launch jp in shell (REPL) mode")
        )
        cmd.Cmd.__init__(self)

    def parse_args(self, args):
        """parse line arguments"""
        return shlex.split(args, posix=True)

    def update_path(self):
        self._cur_parser = self.host.parser
        self.help = u""
        for idx, path_elt in enumerate(self.path):
            try:
                self._cur_parser = arg_tools.get_cmd_choices(path_elt, self._cur_parser)
            except exceptions.NotFound:
                self.disp(_(u"bad command path"), error=True)
                self.path = self.path[:idx]
                break
            else:
                self.help = self._cur_parser

        self.prompt = A.color(C.A_PROMPT_PATH, u"/".join(self.path)) + A.color(
            C.A_PROMPT_SUF, u"> "
        )
        try:
            self.actions = arg_tools.get_cmd_choices(parser=self._cur_parser).keys()
        except exceptions.NotFound:
            self.actions = []

    def add_parser_options(self):
        pass

    def format_args(self, args):
        """format argument to be printed with quotes if needed"""
        for arg in args:
            if " " in arg:
                yield arg_tools.escape(arg)
            else:
                yield arg

    def run_cmd(self, args, external=False):
        """run command and retur exit code

        @param args[list[string]]: arguments of the command
            must not include program name
        @param external(bool): True if it's an external command (i.e. not jp)
        @return (int): exit code (0 success, any other int failure)
        """
        # FIXME: we have to use subprocess
        # and relaunch whole python for now
        # because if host.quit() is called in D-Bus callback
        # GLib quit the whole app without possibility to stop it
        # didn't found a nice way to work around it so far
        # Situation should be better when we'll move away from python-dbus
        if self.verbose:
            self.disp(
                _(u"COMMAND {external}=> {args}").format(
                    external=_(u"(external) ") if external else u"",
                    args=u" ".join(self.format_args(args)),
                )
            )
        if not external:
            args = sys.argv[0:1] + args
        ret_code = subprocess.call(args)
        # XXX: below is a way to launch the command without creating a new process
        #      may be used when a solution to the aforementioned issue is there
        # try:
        #     self.host.run(args)
        # except SystemExit as e:
        #     ret_code = e.code
        # except Exception as e:
        #     self.disp(A.color(C.A_FAILURE, u'command failed with an exception: {msg}'.format(msg=e)), error=True)
        #     ret_code = 1
        # else:
        #     ret_code = 0

        if ret_code != 0:
            self.disp(
                A.color(
                    C.A_FAILURE,
                    u"command failed with an error code of {err_no}".format(
                        err_no=ret_code
                    ),
                ),
                error=True,
            )
        return ret_code

    def default(self, args):
        """called when no shell command is recognized

        will launch the command with args on the line
        (i.e. will launch do [args])
        """
        if args == "EOF":
            self.do_quit("")
        self.do_do(args)

    def do_help(self, args):
        """show help message"""
        if not args:
            self.disp(A.color(C.A_HEADER, _(u"Shell commands:")), no_lf=True)
        super(Shell, self).do_help(args)
        if not args:
            self.disp(A.color(C.A_HEADER, _(u"Action commands:")))
            help_list = self._cur_parser.format_help().split("\n\n")
            print("\n\n".join(help_list[1 if self.path else 2 :]))

    def do_debug(self, args):
        """launch internal debugger"""
        try:
            import ipdb as pdb
        except ImportError:
            import pdb
        pdb.set_trace()

    def do_verbose(self, args):
        """show verbose mode, or (de)activate it"""
        args = self.parse_args(args)
        if args:
            self.verbose = C.bool(args[0])
        self.disp(
            _(u"verbose mode is {status}").format(
                status=_(u"ENABLED") if self.verbose else _(u"DISABLED")
            )
        )

    def do_cmd(self, args):
        """change command path"""
        if args == "..":
            self.path = self.path[:-1]
        else:
            if not args or args[0] == "/":
                self.path = []
            args = "/".join(args.split())
            for path_elt in args.split("/"):
                path_elt = path_elt.strip()
                if not path_elt:
                    continue
                self.path.append(path_elt)
        self.update_path()

    def do_version(self, args):
        """show current SàT/jp version"""
        try:
            self.host.run(["--version"])
        except SystemExit:
            pass

    def do_shell(self, args):
        """launch an external command (you can use ![command] too)"""
        args = self.parse_args(args)
        self.run_cmd(args, external=True)

    def do_do(self, args):
        """lauch a command"""
        args = self.parse_args(args)
        if (
            self._not_default_profile
            and not "-p" in args
            and not "--profile" in args
            and not "profile" in self.use
        ):
            # profile is not specified and we are not using the default profile
            # so we need to add it in arguments to use current user profile
            if self.verbose:
                self.disp(
                    _(u"arg profile={profile} (logged profile)").format(
                        profile=self.profile
                    )
                )
            use = self.use.copy()
            use["profile"] = self.profile
        else:
            use = self.use

        # args may be modified by use_args
        # to remove subparsers from it
        parser_args, use_args = arg_tools.get_use_args(
            self.host, args, use, verbose=self.verbose, parser=self._cur_parser
        )
        cmd_args = self.path + parser_args + use_args
        self.run_cmd(cmd_args)

    def do_use(self, args):
        """fix an argument"""
        args = self.parse_args(args)
        if not args:
            if not self.use:
                self.disp(_(u"no argument in USE"))
            else:
                self.disp(_(u"arguments in USE:"))
                for arg, value in self.use.iteritems():
                    self.disp(
                        _(
                            A.color(
                                C.A_SUBHEADER,
                                arg,
                                A.RESET,
                                u" = ",
                                arg_tools.escape(value),
                            )
                        )
                    )
        elif len(args) != 2:
            self.disp(u"bad syntax, please use:\nuse [arg] [value]", error=True)
        else:
            self.use[args[0]] = u" ".join(args[1:])
            if self.verbose:
                self.disp(
                    "set {name} = {value}".format(
                        name=args[0], value=arg_tools.escape(args[1])
                    )
                )

    def do_use_clear(self, args):
        """unset one or many argument(s) in USE, or all of them if no arg is specified"""
        args = self.parse_args(args)
        if not args:
            self.use.clear()
        else:
            for arg in args:
                try:
                    del self.use[arg]
                except KeyError:
                    self.disp(
                        A.color(
                            C.A_FAILURE, _(u"argument {name} not found").format(name=arg)
                        ),
                        error=True,
                    )
                else:
                    if self.verbose:
                        self.disp(_(u"argument {name} removed").format(name=arg))

    def do_whoami(self, args):
        u"""print profile currently used"""
        self.disp(self.profile)

    def do_quit(self, args):
        u"""quit the shell"""
        self.disp(_(u"good bye!"))
        self.host.quit()

    def do_exit(self, args):
        u"""alias for quit"""
        self.do_quit(args)

    def start(self):
        default_profile = self.host.bridge.profileNameGet(C.PROF_KEY_DEFAULT)
        self._not_default_profile = self.profile != default_profile
        self.path = []
        self._cur_parser = self.host.parser
        self.use = {}
        self.verbose = False
        self.update_path()
        self.cmdloop(INTRO.encode("utf-8"))
