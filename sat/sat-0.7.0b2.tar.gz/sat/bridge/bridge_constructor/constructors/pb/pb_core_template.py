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


from sat.core.log import getLogger

from twisted.spread import jelly, pb
from twisted.internet import reactor
log = getLogger(__name__)


## jelly hack
# we monkey patch jelly to handle namedtuple
ori_jelly = jelly._Jellier.jelly


def fixed_jelly(self, obj):
    """this method fix handling of namedtuple"""
    if isinstance(obj, tuple) and not obj is tuple:
        obj = tuple(obj)
    return ori_jelly(self, obj)


jelly._Jellier.jelly = fixed_jelly


class PBRoot(pb.Root):
    def __init__(self):
        self.signals_handlers = []

    def remote_initBridge(self, signals_handler):
        self.signals_handlers.append(signals_handler)
        log.info(u"registered signal handler")

    def sendSignalEb(self, failure, signal_name):
        log.error(
            u"Error while sending signal {name}: {msg}".format(
                name=signal_name, msg=failure
            )
        )

    def sendSignal(self, name, args, kwargs):
        to_remove = []
        for handler in self.signals_handlers:
            try:
                d = handler.callRemote(name, *args, **kwargs)
            except pb.DeadReferenceError:
                to_remove.append(handler)
            else:
                d.addErrback(self.sendSignalEb, name)
        if to_remove:
            for handler in to_remove:
                log.debug(u"Removing signal handler for dead frontend")
                self.signals_handlers.remove(handler)

    def _bridgeDeactivateSignals(self):
        if hasattr(self, "signals_paused"):
            log.warning(u"bridge signals already deactivated")
            if self.signals_handler:
                self.signals_paused.extend(self.signals_handler)
        else:
            self.signals_paused = self.signals_handlers
        self.signals_handlers = []
        log.debug(u"bridge signals have been deactivated")

    def _bridgeReactivateSignals(self):
        try:
            self.signals_handlers = self.signals_paused
        except AttributeError:
            log.debug(u"signals were already activated")
        else:
            del self.signals_paused
            log.debug(u"bridge signals have been reactivated")

##METHODS_PART##


class Bridge(object):
    def __init__(self):
        log.info("Init Perspective Broker...")
        self.root = PBRoot()
        reactor.listenTCP(8789, pb.PBServerFactory(self.root))

    def sendSignal(self, name, *args, **kwargs):
        self.root.sendSignal(name, args, kwargs)

    def remote_initBridge(self, signals_handler):
        self.signals_handlers.append(signals_handler)
        log.info(u"registered signal handler")

    def register_method(self, name, callback):
        log.debug("registering PB bridge method [%s]" % name)
        setattr(self.root, "remote_" + name, callback)
        #  self.root.register_method(name, callback)

    def addMethod(self, name, int_suffix, in_sign, out_sign, method, async=False, doc={}):
        """Dynamically add a method to PB Bridge"""
        # FIXME: doc parameter is kept only temporary, the time to remove it from calls
        log.debug("Adding method {name} to PB bridge".format(name=name))
        self.register_method(name, method)

    def addSignal(self, name, int_suffix, signature, doc={}):
        log.debug("Adding signal {name} to PB bridge".format(name=name))
        setattr(
            self, name, lambda *args, **kwargs: self.sendSignal(name, *args, **kwargs)
        )

    def bridgeDeactivateSignals(self):
        """Stop sending signals to bridge

        Mainly used for mobile frontends, when the frontend is paused
        """
        self.root._bridgeDeactivateSignals()

    def bridgeReactivateSignals(self):
        """Send again signals to bridge

        Should only be used after bridgeDeactivateSignals has been called
        """
        self.root._bridgeReactivateSignals()

##SIGNALS_PART##
