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


class pbConstructor(base_constructor.Constructor):
    NAME = "pb"
    CORE_TEMPLATE = "pb_core_template.py"
    CORE_DEST = "pb.py"
    CORE_FORMATS = {
        "signals": """\
    def {name}(self, {args}):
        {debug}self.sendSignal("{name}", {args_no_def})\n"""
    }

    FRONTEND_TEMPLATE = "pb_frontend_template.py"
    FRONTEND_DEST = CORE_DEST
    FRONTEND_FORMATS = {
        "methods": """\
    def {name}(self{args_comma}{args}, callback=None, errback=None):
        {debug}d = self.root.callRemote("{name}"{args_comma}{args_no_def})
        if callback is not None:
            d.addCallback({callback})
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)\n"""
    }

    def core_completion_signal(self, completion, function, default, arg_doc, async_):
        completion["args_no_def"] = self.getArguments(function["sig_in"], name=arg_doc)
        completion["debug"] = (
            ""
            if not self.args.debug
            else 'log.debug ("%s")\n%s' % (completion["name"], 8 * " ")
        )

    def frontend_completion_method(self, completion, function, default, arg_doc, async_):
        completion.update(
            {
                "args_comma": ", " if function["sig_in"] else "",
                "args_no_def": self.getArguments(function["sig_in"], name=arg_doc),
                "callback": "callback"
                if function["sig_out"]
                else "lambda __: callback()",
                "debug": ""
                if not self.args.debug
                else 'log.debug ("%s")\n%s' % (completion["name"], 8 * " "),
            }
        )
