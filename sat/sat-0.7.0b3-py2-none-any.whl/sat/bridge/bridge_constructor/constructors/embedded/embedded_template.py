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

from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core import exceptions


class _Bridge(object):
    def __init__(self):
        log.debug(u"Init embedded bridge...")
        self._methods_cbs = {}
        self._signals_cbs = {"core": {}, "plugin": {}}

    def bridgeConnect(self, callback, errback):
        callback()

    def register_method(self, name, callback):
        log.debug(u"registering embedded bridge method [{}]".format(name))
        if name in self._methods_cbs:
            raise exceptions.ConflictError(u"method {} is already regitered".format(name))
        self._methods_cbs[name] = callback

    def register_signal(self, functionName, handler, iface="core"):
        iface_dict = self._signals_cbs[iface]
        if functionName in iface_dict:
            raise exceptions.ConflictError(
                u"signal {name} is already regitered for interface {iface}".format(
                    name=functionName, iface=iface
                )
            )
        iface_dict[functionName] = handler

    def call_method(self, name, out_sign, async_, args, kwargs):
        callback = kwargs.pop("callback", None)
        errback = kwargs.pop("errback", None)
        if async_:
            d = self._methods_cbs[name](*args, **kwargs)
            if callback is not None:
                d.addCallback(callback if out_sign else lambda __: callback())
            if errback is None:
                d.addErrback(lambda failure_: log.error(failure_))
            else:
                d.addErrback(errback)
            return d
        else:
            try:
                ret = self._methods_cbs[name](*args, **kwargs)
            except Exception as e:
                if errback is not None:
                    errback(e)
                else:
                    raise e
            else:
                if callback is None:
                    return ret
                else:
                    if out_sign:
                        callback(ret)
                    else:
                        callback()

    def send_signal(self, name, args, kwargs):
        try:
            cb = self._signals_cbs["plugin"][name]
        except KeyError:
            log.debug(u"ignoring signal {}: no callback registered".format(name))
        else:
            cb(*args, **kwargs)

    def addMethod(self, name, int_suffix, in_sign, out_sign, method, async=False, doc={}):
        # FIXME: doc parameter is kept only temporary, the time to remove it from calls
        log.debug("Adding method [{}] to embedded bridge".format(name))
        self.register_method(name, method)
        setattr(
            self.__class__,
            name,
            lambda self_, *args, **kwargs: self.call_method(
                name, out_sign, async, args, kwargs
            ),
        )

    def addSignal(self, name, int_suffix, signature, doc={}):
        setattr(
            self.__class__,
            name,
            lambda self_, *args, **kwargs: self.send_signal(name, args, kwargs),
        )

    ## signals ##


##SIGNALS_PART##
## methods ##

##METHODS_PART##

# we want the same instance for both core and frontend
bridge = None


def Bridge():
    global bridge
    if bridge is None:
        bridge = _Bridge()
    return bridge
