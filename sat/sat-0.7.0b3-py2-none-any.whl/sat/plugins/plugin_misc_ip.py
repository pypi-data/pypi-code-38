#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for IP address discovery
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

from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.tools import xml_tools
from twisted.web import client as webclient
from twisted.web import error as web_error
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet import protocol
from twisted.internet import endpoints
from twisted.internet import error as internet_error
from zope.interface import implements
from wokkel import disco, iwokkel
from twisted.words.protocols.jabber.xmlstream import XMPPHandler
from twisted.words.protocols.jabber.error import StanzaError
import urlparse

try:
    import netifaces
except ImportError:
    log.warning(
        u"netifaces is not available, it help discovering IPs, you can install it on https://pypi.python.org/pypi/netifaces"
    )
    netifaces = None


PLUGIN_INFO = {
    C.PI_NAME: "IP discovery",
    C.PI_IMPORT_NAME: "IP",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_PROTOCOLS: ["XEP-0279"],
    C.PI_RECOMMENDATIONS: ["NAT-PORT"],
    C.PI_MAIN: "IPPlugin",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""This plugin help to discover our external IP address."""),
}

# TODO: GET_IP_PAGE should be configurable in sat.conf
GET_IP_PAGE = (
    "http://salut-a-toi.org/whereami/"
)  # This page must only return external IP of the requester
GET_IP_LABEL = D_(u"Allow external get IP")
GET_IP_CATEGORY = "General"
GET_IP_NAME = "allow_get_ip"
GET_IP_CONFIRM_TITLE = D_(u"Confirm external site request")
GET_IP_CONFIRM = D_(
    u"""To facilitate data transfer, we need to contact a website.
A request will be done on {page}
That means that administrators of {domain} can know that you use "{app_name}" and your IP Address.

IP address is an identifier to locate you on Internet (similar to a phone number).

Do you agree to do this request ?
"""
).format(
    page=GET_IP_PAGE, domain=urlparse.urlparse(GET_IP_PAGE).netloc, app_name=C.APP_NAME
)
NS_IP_CHECK = "urn:xmpp:sic:1"

PARAMS = """
    <params>
    <general>
    <category name="{category}">
        <param name="{name}" label="{label}" type="bool" />
    </category>
    </general>
    </params>
    """.format(
    category=GET_IP_CATEGORY, name=GET_IP_NAME, label=GET_IP_LABEL
)


class IPPlugin(object):
    # TODO: refresh IP if a new connection is detected
    # TODO: manage IPv6 when implemented in SàT

    def __init__(self, host):
        log.info(_("plugin IP discovery initialization"))
        self.host = host
        host.memory.updateParams(PARAMS)

        # NAT-Port
        try:
            self._nat = host.plugins["NAT-PORT"]
        except KeyError:
            log.debug(u"NAT port plugin not available")
            self._nat = None

        # XXX: cache is kept until SàT is restarted
        #      if IP may have changed, use self.refreshIP
        self._external_ip_cache = None
        self._local_ip_cache = None

    def getHandler(self, client):
        return IPPlugin_handler()

    def refreshIP(self):
        # FIXME: use a trigger instead ?
        self._external_ip_cache = None
        self._local_ip_cache = None

    def _externalAllowed(self, client):
        """Return value of parameter with autorisation of user to do external requests

        if parameter is not set, a dialog is shown to use to get its confirmation, and parameted is set according to answer
        @return (defer.Deferred[bool]): True if external request is autorised
        """
        allow_get_ip = self.host.memory.params.getParamA(
            GET_IP_NAME, GET_IP_CATEGORY, use_default=False
        )

        if allow_get_ip is None:
            # we don't have autorisation from user yet to use get_ip, we ask him
            def setParam(allowed):
                # FIXME: we need to use boolConst as setParam only manage str/unicode
                #        need to be fixed when params will be refactored
                self.host.memory.setParam(
                    GET_IP_NAME, C.boolConst(allowed), GET_IP_CATEGORY
                )
                return allowed

            d = xml_tools.deferConfirm(
                self.host,
                _(GET_IP_CONFIRM),
                _(GET_IP_CONFIRM_TITLE),
                profile=client.profile,
            )
            d.addCallback(setParam)
            return d

        return defer.succeed(allow_get_ip)

    def _filterAddresse(self, ip_addr):
        """Filter acceptable addresses

        For now, just remove IPv4 local addresses
        @param ip_addr(str): IP addresse
        @return (bool): True if addresse is acceptable
        """
        return not ip_addr.startswith("127.")

    def _insertFirst(self, addresses, ip_addr):
        """Insert ip_addr as first item in addresses

        @param ip_addr(str): IP addresse
        @param addresses(list): list of IP addresses
        """
        if ip_addr in addresses:
            if addresses[0] != ip_addr:
                addresses.remove(ip_addr)
                addresses.insert(0, ip_addr)
        else:
            addresses.insert(0, ip_addr)

    def _getIPFromExternal(self, ext_url):
        """Get local IP by doing a connection on an external url

        @param ext_utl(str): url to connect to
        @return (D(str)): return local IP
        """
        url = urlparse.urlparse(ext_url)
        port = url.port
        if port is None:
            if url.scheme == "http":
                port = 80
            elif url.scheme == "https":
                port = 443
            else:
                log.error(u"Unknown url scheme: {}".format(url.scheme))
                defer.returnValue(None)
        if url.hostname is None:
            log.error(u"Can't find url hostname for {}".format(GET_IP_PAGE))

        point = endpoints.TCP4ClientEndpoint(reactor, url.hostname, port)

        def gotConnection(p):
            local_ip = p.transport.getHost().host
            p.transport.loseConnection()
            return local_ip

        d = endpoints.connectProtocol(point, protocol.Protocol())
        d.addCallback(gotConnection)
        return d

    @defer.inlineCallbacks
    def getLocalIPs(self, client):
        """Try do discover local area network IPs

        @return (deferred): list of lan IP addresses
            if there are several addresses, the one used with the server is put first
            if no address is found, localhost IP will be in the list
        """
        # TODO: manage permission requesting (e.g. for UMTS link)
        if self._local_ip_cache is not None:
            defer.returnValue(self._local_ip_cache)
        addresses = []
        localhost = ["127.0.0.1"]

        # we first try our luck with netifaces
        if netifaces is not None:
            addresses = []
            for interface in netifaces.interfaces():
                if_addresses = netifaces.ifaddresses(interface)
                try:
                    inet_list = if_addresses[netifaces.AF_INET]
                except KeyError:
                    continue
                for data in inet_list:
                    addresse = data["addr"]
                    if self._filterAddresse(addresse):
                        addresses.append(addresse)

        # then we use our connection to server
        ip = client.xmlstream.transport.getHost().host
        if self._filterAddresse(ip):
            self._insertFirst(addresses, ip)
            defer.returnValue(addresses)

        # if server is local, we try with NAT-Port
        if self._nat is not None:
            nat_ip = yield self._nat.getIP(local=True)
            if nat_ip is not None:
                self._insertFirst(addresses, nat_ip)
                defer.returnValue(addresses)

            if addresses:
                defer.returnValue(addresses)

        # still not luck, we need to contact external website
        allow_get_ip = yield self._externalAllowed(client)

        if not allow_get_ip:
            defer.returnValue(addresses or localhost)

        try:
            ip_tuple = yield self._getIPFromExternal(GET_IP_PAGE)
        except (internet_error.DNSLookupError, internet_error.TimeoutError):
            log.warning(u"Can't access Domain Name System")
            defer.returnValue(addresses or localhost)
        self._insertFirst(addresses, ip_tuple.local)
        defer.returnValue(addresses)

    @defer.inlineCallbacks
    def getExternalIP(self, client):
        """Try to discover external IP

        @return (deferred): external IP address or None if it can't be discovered
        """
        if self._external_ip_cache is not None:
            defer.returnValue(self._external_ip_cache)

        # we first try with XEP-0279
        ip_check = yield self.host.hasFeature(client, NS_IP_CHECK)
        if ip_check:
            log.debug(u"Server IP Check available, we use it to retrieve our IP")
            iq_elt = client.IQ("get")
            iq_elt.addElement((NS_IP_CHECK, "address"))
            try:
                result_elt = yield iq_elt.send()
                address_elt = result_elt.elements(NS_IP_CHECK, "address").next()
                ip_elt = address_elt.elements(NS_IP_CHECK, "ip").next()
            except StopIteration:
                log.warning(
                    u"Server returned invalid result on XEP-0279 request, we ignore it"
                )
            except StanzaError as e:
                log.warning(u"error while requesting ip to server: {}".format(e))
            else:
                # FIXME: server IP may not be the same as external IP (server can be on local machine or network)
                #        IP should be checked to see if we have a local one, and rejected in this case
                external_ip = str(ip_elt)
                log.debug(u"External IP found: {}".format(external_ip))
                self._external_ip_cache = external_ip
                defer.returnValue(self._external_ip_cache)

        # then with NAT-Port
        if self._nat is not None:
            nat_ip = yield self._nat.getIP()
            if nat_ip is not None:
                self._external_ip_cache = nat_ip
                defer.returnValue(nat_ip)

        # and finally by requesting external website
        allow_get_ip = yield self._externalAllowed(client)
        try:
            ip = (yield webclient.getPage(GET_IP_PAGE)) if allow_get_ip else None
        except (internet_error.DNSLookupError, internet_error.TimeoutError):
            log.warning(u"Can't access Domain Name System")
            ip = None
        except web_error.Error as e:
            log.warning(
                u"Error while retrieving IP on {url}: {message}".format(
                    url=GET_IP_PAGE, message=e
                )
            )
            ip = None
        else:
            self._external_ip_cache = ip
        defer.returnValue(ip)


class IPPlugin_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_IP_CHECK)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
