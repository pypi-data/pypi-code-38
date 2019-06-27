#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT communication bridge
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

from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core import exceptions
from twisted.spread import pb
from twisted.internet import reactor


class SignalsHandler(pb.Referenceable):
    def __getattr__(self, name):
        if name.startswith("remote_"):
            log.debug(u"calling an unregistered signal: {name}".format(name=name[7:]))
            return lambda *args, **kwargs: None

        else:
            raise AttributeError(name)

    def register_signal(self, name, handler, iface="core"):
        log.debug("registering signal {name}".format(name=name))
        method_name = "remote_" + name
        try:
            self.__getattribute__(self, method_name)
        except AttributeError:
            pass
        else:
            raise exceptions.InternalError(
                u"{name} signal handler has been registered twice".format(
                    name=method_name
                )
            )
        setattr(self, method_name, handler)


class Bridge(object):
    def __init__(self):
        self.signals_handler = SignalsHandler()

    def __getattr__(self, name):
        return lambda *args, **kwargs: self.call(name, args, kwargs)

    def remoteCallback(self, result, callback):
        """call callback with argument or None

        if result is not None not argument is used,
        else result is used as argument
        @param result: remote call result
        @param callback(callable): method to call on result
        """
        if result is None:
            callback()
        else:
            callback(result)

    def call(self, name, args, kwargs):
        """call a remote method

        @param name(str): name of the bridge method
        @param args(list): arguments
            may contain callback and errback as last 2 items
        @param kwargs(dict): keyword arguments
            may contain callback and errback
        """
        callback = errback = None
        if kwargs:
            try:
                callback = kwargs.pop("callback")
            except KeyError:
                pass
            try:
                errback = kwargs.pop("errback")
            except KeyError:
                pass
        elif len(args) >= 2 and callable(args[-1]) and callable(args[-2]):
            errback = args.pop()
            callback = args.pop()
        d = self.root.callRemote(name, *args, **kwargs)
        if callback is not None:
            d.addCallback(self.remoteCallback, callback)
        if errback is not None:
            d.addErrback(errback)

    def _initBridgeEb(self, failure):
        log.error(u"Can't init bridge: {msg}".format(msg=failure))

    def _set_root(self, root):
        """set remote root object

        bridge will then be initialised
        """
        self.root = root
        d = root.callRemote("initBridge", self.signals_handler)
        d.addErrback(self._initBridgeEb)
        return d

    def _generic_errback(self, failure):
        log.error(u"bridge failure: {}".format(failure))

    def bridgeConnect(self, callback, errback):
        factory = pb.PBClientFactory()
        reactor.connectTCP("localhost", 8789, factory)
        d = factory.getRootObject()
        d.addCallback(self._set_root)
        d.addCallback(lambda __: callback())
        d.addErrback(errback)

    def register_signal(self, functionName, handler, iface="core"):
        self.signals_handler.register_signal(functionName, handler, iface)


##METHODS_PART##
