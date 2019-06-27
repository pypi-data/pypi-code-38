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

from sat.core.i18n import _
import dbus
import dbus.service
import dbus.mainloop.glib
import inspect
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.internet.defer import Deferred
from sat.core.exceptions import BridgeInitError

const_INT_PREFIX = "org.salutatoi.SAT"  # Interface prefix
const_ERROR_PREFIX = const_INT_PREFIX + ".error"
const_OBJ_PATH = "/org/salutatoi/SAT/bridge"
const_CORE_SUFFIX = ".core"
const_PLUGIN_SUFFIX = ".plugin"


class ParseError(Exception):
    pass


class MethodNotRegistered(dbus.DBusException):
    _dbus_error_name = const_ERROR_PREFIX + ".MethodNotRegistered"


class InternalError(dbus.DBusException):
    _dbus_error_name = const_ERROR_PREFIX + ".InternalError"


class AsyncNotDeferred(dbus.DBusException):
    _dbus_error_name = const_ERROR_PREFIX + ".AsyncNotDeferred"


class DeferredNotAsync(dbus.DBusException):
    _dbus_error_name = const_ERROR_PREFIX + ".DeferredNotAsync"


class GenericException(dbus.DBusException):
    def __init__(self, twisted_error):
        """

        @param twisted_error (Failure): instance of twisted Failure
        @return: DBusException
        """
        super(GenericException, self).__init__()
        try:
            # twisted_error.value is a class
            class_ = twisted_error.value().__class__
        except TypeError:
            # twisted_error.value is an instance
            class_ = twisted_error.value.__class__
            message = twisted_error.getErrorMessage()
            try:
                self.args = (message, twisted_error.value.condition)
            except AttributeError:
                self.args = (message,)
        self._dbus_error_name = ".".join(
            [const_ERROR_PREFIX, class_.__module__, class_.__name__]
        )


class DbusObject(dbus.service.Object):
    def __init__(self, bus, path):
        dbus.service.Object.__init__(self, bus, path)
        log.debug("Init DbusObject...")
        self.cb = {}

    def register_method(self, name, cb):
        self.cb[name] = cb

    def _callback(self, name, *args, **kwargs):
        """call the callback if it exists, raise an exception else
        if the callback return a deferred, use async methods"""
        if not name in self.cb:
            raise MethodNotRegistered

        if "callback" in kwargs:
            # we must have errback too
            if not "errback" in kwargs:
                log.error("errback is missing in method call [%s]" % name)
                raise InternalError
            callback = kwargs.pop("callback")
            errback = kwargs.pop("errback")
            async = True
        else:
            async = False
        result = self.cb[name](*args, **kwargs)
        if async:
            if not isinstance(result, Deferred):
                log.error("Asynchronous method [%s] does not return a Deferred." % name)
                raise AsyncNotDeferred
            result.addCallback(
                lambda result: callback() if result is None else callback(result)
            )
            result.addErrback(lambda err: errback(GenericException(err)))
        else:
            if isinstance(result, Deferred):
                log.error("Synchronous method [%s] return a Deferred." % name)
                raise DeferredNotAsync
            return result

    ### signals ###

    @dbus.service.signal(const_INT_PREFIX + const_PLUGIN_SUFFIX, signature="")
    def dummySignal(self):
        # FIXME: workaround for addSignal (doesn't work if one method doensn't
        #       already exist for plugins), probably missing some initialisation, need
        #       further investigations
        pass

##SIGNALS_PART##
    ### methods ###

##METHODS_PART##
    def __attributes(self, in_sign):
        """Return arguments to user given a in_sign
        @param in_sign: in_sign in the short form (using s,a,i,b etc)
        @return: list of arguments that correspond to a in_sign (e.g.: "sss" return "arg1, arg2, arg3")"""
        i = 0
        idx = 0
        attr = []
        while i < len(in_sign):
            if in_sign[i] not in ["b", "y", "n", "i", "x", "q", "u", "t", "d", "s", "a"]:
                raise ParseError("Unmanaged attribute type [%c]" % in_sign[i])

            attr.append("arg_%i" % idx)
            idx += 1

            if in_sign[i] == "a":
                i += 1
                if (
                    in_sign[i] != "{" and in_sign[i] != "("
                ):  # FIXME: must manage tuples out of arrays
                    i += 1
                    continue  # we have a simple type for the array
                opening_car = in_sign[i]
                assert opening_car in ["{", "("]
                closing_car = "}" if opening_car == "{" else ")"
                opening_count = 1
                while True:  # we have a dict or a list of tuples
                    i += 1
                    if i >= len(in_sign):
                        raise ParseError("missing }")
                    if in_sign[i] == opening_car:
                        opening_count += 1
                    if in_sign[i] == closing_car:
                        opening_count -= 1
                        if opening_count == 0:
                            break
            i += 1
        return attr

    def addMethod(self, name, int_suffix, in_sign, out_sign, method, async=False):
        """Dynamically add a method to Dbus Bridge"""
        inspect_args = inspect.getargspec(method)

        _arguments = inspect_args.args
        _defaults = list(inspect_args.defaults or [])

        if inspect.ismethod(method):
            # if we have a method, we don't want the first argument (usually 'self')
            del (_arguments[0])

        # first arguments are for the _callback method
        arguments_callback = ", ".join(
            [repr(name)]
            + (
                (_arguments + ["callback=callback", "errback=errback"])
                if async
                else _arguments
            )
        )

        if async:
            _arguments.extend(["callback", "errback"])
            _defaults.extend([None, None])

        # now we create a second list with default values
        for i in range(1, len(_defaults) + 1):
            _arguments[-i] = "%s = %s" % (_arguments[-i], repr(_defaults[-i]))

        arguments_defaults = ", ".join(_arguments)

        code = compile(
            "def %(name)s (self,%(arguments_defaults)s): return self._callback(%(arguments_callback)s)"
            % {
                "name": name,
                "arguments_defaults": arguments_defaults,
                "arguments_callback": arguments_callback,
            },
            "<DBus bridge>",
            "exec",
        )
        exec(code)  # FIXME: to the same thing in a cleaner way, without compile/exec
        method = locals()[name]
        async_callbacks = ("callback", "errback") if async else None
        setattr(
            DbusObject,
            name,
            dbus.service.method(
                const_INT_PREFIX + int_suffix,
                in_signature=in_sign,
                out_signature=out_sign,
                async_callbacks=async_callbacks,
            )(method),
        )
        function = getattr(self, name)
        func_table = self._dbus_class_table[
            self.__class__.__module__ + "." + self.__class__.__name__
        ][function._dbus_interface]
        func_table[function.__name__] = function  # Needed for introspection

    def addSignal(self, name, int_suffix, signature, doc={}):
        """Dynamically add a signal to Dbus Bridge"""
        attributes = ", ".join(self.__attributes(signature))
        # TODO: use doc parameter to name attributes

        # code = compile ('def '+name+' (self,'+attributes+'): log.debug ("'+name+' signal")', '<DBus bridge>','exec') #XXX: the log.debug is too annoying with xmllog
        code = compile(
            "def " + name + " (self," + attributes + "): pass", "<DBus bridge>", "exec"
        )
        exec(code)
        signal = locals()[name]
        setattr(
            DbusObject,
            name,
            dbus.service.signal(const_INT_PREFIX + int_suffix, signature=signature)(
                signal
            ),
        )
        function = getattr(self, name)
        func_table = self._dbus_class_table[
            self.__class__.__module__ + "." + self.__class__.__name__
        ][function._dbus_interface]
        func_table[function.__name__] = function  # Needed for introspection


class Bridge(object):
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        log.info("Init DBus...")
        try:
            self.session_bus = dbus.SessionBus()
        except dbus.DBusException as e:
            if e._dbus_error_name == "org.freedesktop.DBus.Error.NotSupported":
                log.error(
                    _(
                        u"D-Bus is not launched, please see README to see instructions on how to launch it"
                    )
                )
            raise BridgeInitError
        self.dbus_name = dbus.service.BusName(const_INT_PREFIX, self.session_bus)
        self.dbus_bridge = DbusObject(self.session_bus, const_OBJ_PATH)

##SIGNAL_DIRECT_CALLS_PART##
    def register_method(self, name, callback):
        log.debug("registering DBus bridge method [%s]" % name)
        self.dbus_bridge.register_method(name, callback)

    def addMethod(self, name, int_suffix, in_sign, out_sign, method, async=False, doc={}):
        """Dynamically add a method to Dbus Bridge"""
        # FIXME: doc parameter is kept only temporary, the time to remove it from calls
        log.debug("Adding method [%s] to DBus bridge" % name)
        self.dbus_bridge.addMethod(name, int_suffix, in_sign, out_sign, method, async)
        self.register_method(name, method)

    def addSignal(self, name, int_suffix, signature, doc={}):
        self.dbus_bridge.addSignal(name, int_suffix, signature, doc)
        setattr(Bridge, name, getattr(self.dbus_bridge, name))
