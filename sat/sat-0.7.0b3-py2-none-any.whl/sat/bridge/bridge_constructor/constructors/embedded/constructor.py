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

#  from textwraps import dedent


class EmbeddedConstructor(base_constructor.Constructor):
    NAME = "embedded"
    CORE_TEMPLATE = "embedded_template.py"
    CORE_DEST = "embedded.py"
    CORE_FORMATS = {
        "methods": """\
    def {name}(self, {args}{args_comma}callback=None, errback=None):
{ret_routine}
""",
        "signals": """\
    def {name}(self, {args}):
        try:
            cb = self._signals_cbs["{category}"]["{name}"]
        except KeyError:
            log.warning(u"ignoring signal {name}: no callback registered")
        else:
            cb({args_result})
""",
    }
    FRONTEND_TEMPLATE = "embedded_frontend_template.py"
    FRONTEND_DEST = CORE_DEST
    FRONTEND_FORMATS = {}

    def core_completion_method(self, completion, function, default, arg_doc, async_):
        completion.update(
            {
                "debug": ""
                if not self.args.debug
                else 'log.debug ("%s")\n%s' % (completion["name"], 8 * " "),
                "args_result": self.getArguments(function["sig_in"], name=arg_doc),
                "args_comma": ", " if function["sig_in"] else "",
            }
        )

        if async_:
            completion["cb_or_lambda"] = (
                "callback" if function["sig_out"] else "lambda __: callback()"
            )
            completion[
                "ret_routine"
            ] = """\
        d = self._methods_cbs["{name}"]({args_result})
        if callback is not None:
            d.addCallback({cb_or_lambda})
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        """.format(
                **completion
            )
        else:
            completion["ret_or_nothing"] = "ret" if function["sig_out"] else ""
            completion[
                "ret_routine"
            ] = """\
        try:
            ret = self._methods_cbs["{name}"]({args_result})
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback({ret_or_nothing})""".format(
                **completion
            )

    def core_completion_signal(self, completion, function, default, arg_doc, async_):
        completion.update(
            {"args_result": self.getArguments(function["sig_in"], name=arg_doc)}
        )
