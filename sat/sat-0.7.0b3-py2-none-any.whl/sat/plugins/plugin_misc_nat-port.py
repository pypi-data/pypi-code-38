#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for NAT port mapping
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
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core import exceptions
from twisted.internet import threads
from twisted.internet import defer
from twisted.python import failure
import threading

try:
    import miniupnpc
except ImportError:
    raise exceptions.MissingModule(
        u"Missing module MiniUPnPc, please download/install it (and its Python binding) at http://miniupnp.free.fr/ (or use pip install miniupnpc)"
    )


PLUGIN_INFO = {
    C.PI_NAME: "NAT port mapping",
    C.PI_IMPORT_NAME: "NAT-PORT",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_MAIN: "NatPort",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Automatic NAT port mapping using UPnP"""),
}

STARTING_PORT = 6000  # starting point to automatically find a port
DEFAULT_DESC = (
    u"SaT port mapping"
)  # we don't use "à" here as some bugged NAT don't manage charset correctly


class MappingError(Exception):
    pass


class NatPort(object):
    # TODO: refresh data if a new connection is detected (see plugin_misc_ip)

    def __init__(self, host):
        log.info(_("plugin NAT Port initialization"))
        self.host = host
        self._external_ip = None
        self._initialised = defer.Deferred()
        self._upnp = miniupnpc.UPnP()  # will be None if no device is available
        self._upnp.discoverdelay = 200
        self._mutex = threading.Lock()  # used to protect access to self._upnp
        self._starting_port_cache = None  # used to cache the first available port
        self._to_unmap = []  # list of tuples (ext_port, protocol) of ports to unmap on unload
        discover_d = threads.deferToThread(self._discover)
        discover_d.chainDeferred(self._initialised)
        self._initialised.addErrback(self._init_failed)

    def unload(self):
        if self._to_unmap:
            log.info(u"Cleaning mapped ports")
            return threads.deferToThread(self._unmapPortsBlocking)

    def _init_failed(self, failure_):
        e = failure_.trap(exceptions.NotFound, exceptions.FeatureNotFound)
        if e == exceptions.FeatureNotFound:
            log.info(u"UPnP-IGD seems to be not activated on the device")
        else:
            log.info(u"UPnP-IGD not available")
        self._upnp = None

    def _discover(self):
        devices = self._upnp.discover()
        if devices:
            log.info(u"{nb} UPnP-IGD device(s) found".format(nb=devices))
        else:
            log.info(u"Can't find UPnP-IGD device on the local network")
            raise failure.Failure(exceptions.NotFound())
        self._upnp.selectigd()
        try:
            self._external_ip = self._upnp.externalipaddress()
        except Exception:
            raise failure.Failure(exceptions.FeatureNotFound())

    def getIP(self, local=False):
        """Return IP address found with UPnP-IGD

        @param local(bool): True to get external IP address, False to get local network one
        @return (None, str): found IP address, or None of something got wrong
        """

        def getIP(__):
            if self._upnp is None:
                return None
            # lanaddr can be the empty string if not found,
            # we need to return None in this case
            return (self._upnp.lanaddr or None) if local else self._external_ip

        return self._initialised.addCallback(getIP)

    def _unmapPortsBlocking(self):
        """Unmap ports mapped in this session"""
        self._mutex.acquire()
        try:
            for port, protocol in self._to_unmap:
                log.info(u"Unmapping port {}".format(port))
                unmapping = self._upnp.deleteportmapping(
                    # the last parameter is remoteHost, we don't use it
                    port,
                    protocol,
                    "",
                )

                if not unmapping:
                    log.error(
                        u"Can't unmap port {port} ({protocol})".format(
                            port=port, protocol=protocol
                        )
                    )
            del self._to_unmap[:]
        finally:
            self._mutex.release()

    def _mapPortBlocking(self, int_port, ext_port, protocol, desc):
        """Internal blocking method to map port

        @param int_port(int): internal port to use
        @param ext_port(int): external port to use, or None to find one automatically
        @param protocol(str): 'TCP' or 'UDP'
        @param desc(str): description of the mapping
        @param return(int, None): external port used in case of success, otherwise None
        """
        # we use mutex to avoid race condition if 2 threads
        # try to acquire a port at the same time
        self._mutex.acquire()
        try:
            if ext_port is None:
                # find a free port
                starting_port = self._starting_port_cache
                ext_port = STARTING_PORT if starting_port is None else starting_port
                ret = self._upnp.getspecificportmapping(ext_port, protocol)
                while ret != None and ext_port < 65536:
                    ext_port += 1
                    ret = self._upnp.getspecificportmapping(ext_port, protocol)
                if starting_port is None:
                    # XXX: we cache the first successfuly found external port
                    #      to avoid testing again the first series the next time
                    self._starting_port_cache = ext_port

            try:
                mapping = self._upnp.addportmapping(
                    # the last parameter is remoteHost, we don't use it
                    ext_port,
                    protocol,
                    self._upnp.lanaddr,
                    int_port,
                    desc,
                    "",
                )
            except Exception as e:
                log.error(_(u"addportmapping error: {msg}").format(msg=e))
                raise failure.Failure(MappingError())

            if not mapping:
                raise failure.Failure(MappingError())
            else:
                self._to_unmap.append((ext_port, protocol))
        finally:
            self._mutex.release()

        return ext_port

    def mapPort(self, int_port, ext_port=None, protocol="TCP", desc=DEFAULT_DESC):
        """Add a port mapping

        @param int_port(int): internal port to use
        @param ext_port(int,None): external port to use, or None to find one automatically
        @param protocol(str): 'TCP' or 'UDP'
        @param desc(unicode): description of the mapping
            Some UPnP IGD devices have broken encoding. It's probably a good idea to avoid non-ascii chars here
        @return (D(int, None)): external port used in case of success, otherwise None
        """
        if self._upnp is None:
            return defer.succeed(None)

        def mappingCb(ext_port):
            log.info(
                u"{protocol} mapping from {int_port} to {ext_port} successful".format(
                    protocol=protocol, int_port=int_port, ext_port=ext_port
                )
            )
            return ext_port

        def mappingEb(failure_):
            failure_.trap(MappingError)
            log.warning(u"Can't map internal {int_port}".format(int_port=int_port))

        def mappingUnknownEb(failure_):
            log.error(_(u"error while trying to map ports: {msg}").format(msg=failure_))

        d = threads.deferToThread(
            self._mapPortBlocking, int_port, ext_port, protocol, desc
        )
        d.addCallbacks(mappingCb, mappingEb)
        d.addErrback(mappingUnknownEb)
        return d
