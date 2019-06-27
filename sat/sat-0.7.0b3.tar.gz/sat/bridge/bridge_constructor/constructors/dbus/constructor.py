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


class DbusConstructor(base_constructor.Constructor):
    NAME = "dbus"
    CORE_TEMPLATE = "dbus_core_template.py"
    CORE_DEST = "dbus_bridge.py"
    CORE_FORMATS = {
        "signals": """\
    @dbus.service.signal(const_INT_PREFIX+const_{category}_SUFFIX,
                         signature='{sig_in}')
    def {name}(self, {args}):
        {body}\n""",
        "methods": """\
    @dbus.service.method(const_INT_PREFIX+const_{category}_SUFFIX,
                         in_signature='{sig_in}', out_signature='{sig_out}',
                         async_callbacks={async_callbacks})
    def {name}(self, {args}{async_comma}{async_args_def}):
        {debug}return self._callback("{name}", {args_result}{async_comma}{async_args_call})\n""",
        "signal_direct_calls": """\
    def {name}(self, {args}):
        self.dbus_bridge.{name}({args})\n""",
    }

    FRONTEND_TEMPLATE = "dbus_frontend_template.py"
    FRONTEND_DEST = CORE_DEST
    FRONTEND_FORMATS = {
        "methods": """\
    def {name}(self, {args}{async_comma}{async_args}):
        {error_handler}{blocking_call}{debug}return {result}\n"""
    }

    def core_completion_signal(self, completion, function, default, arg_doc, async_):
        completion["category"] = completion["category"].upper()
        completion["body"] = (
            "pass"
            if not self.args.debug
            else 'log.debug ("{}")'.format(completion["name"])
        )

    def core_completion_method(self, completion, function, default, arg_doc, async_):
        completion.update(
            {
                "debug": ""
                if not self.args.debug
                else 'log.debug ("%s")\n%s' % (completion["name"], 8 * " "),
                "args_result": self.getArguments(
                    function["sig_in"], name=arg_doc, unicode_protect=self.args.unicode
                ),
                "async_comma": ", " if async_ and function["sig_in"] else "",
                "async_args_def": "callback=None, errback=None" if async_ else "",
                "async_args_call": "callback=callback, errback=errback" if async_ else "",
                "async_callbacks": "('callback', 'errback')" if async_ else "None",
                "category": completion["category"].upper(),
            }
        )

    def frontend_completion_method(self, completion, function, default, arg_doc, async_):
        completion.update(
            {
                # XXX: we can manage blocking call in the same way as async one: if callback is None the call will be blocking
                "debug": ""
                if not self.args.debug
                else 'log.debug ("%s")\n%s' % (completion["name"], 8 * " "),
                "args_result": self.getArguments(function["sig_in"], name=arg_doc),
                "async_args": "callback=None, errback=None",
                "async_comma": ", " if function["sig_in"] else "",
                "error_handler": """if callback is None:
            error_handler = None
        else:
            if errback is None:
                errback = log.error
            error_handler = lambda err:errback(dbus_to_bridge_exception(err))
        """,
            }
        )
        if async_:
            completion["blocking_call"] = ""
            completion[
                "async_args_result"
            ] = "timeout=const_TIMEOUT, reply_handler=callback, error_handler=error_handler"
        else:
            # XXX: To have a blocking call, we must have not reply_handler, so we test if callback exists, and add reply_handler only in this case
            completion[
                "blocking_call"
            ] = """kwargs={}
        if callback is not None:
            kwargs['timeout'] = const_TIMEOUT
            kwargs['reply_handler'] = callback
            kwargs['error_handler'] = error_handler
        """
            completion["async_args_result"] = "**kwargs"
        result = (
            "self.db_%(category)s_iface.%(name)s(%(args_result)s%(async_comma)s%(async_args_result)s)"
            % completion
        )
        completion["result"] = (
            "unicode(%s)" if self.args.unicode and function["sig_out"] == "s" else "%s"
        ) % result
