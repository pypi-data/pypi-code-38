#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Hash functions (XEP-0300)
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
from twisted.words.xish import domish
from twisted.words.protocols.jabber.xmlstream import XMPPHandler
from twisted.internet import threads
from twisted.internet import defer
from zope.interface import implements
from wokkel import disco, iwokkel
from collections import OrderedDict
import hashlib
import base64


PLUGIN_INFO = {
    C.PI_NAME: "Cryptographic Hash Functions",
    C.PI_IMPORT_NAME: "XEP-0300",
    C.PI_TYPE: "XEP",
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_PROTOCOLS: ["XEP-0300"],
    C.PI_MAIN: "XEP_0300",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Management of cryptographic hashes"""),
}

NS_HASHES = "urn:xmpp:hashes:2"
NS_HASHES_FUNCTIONS = u"urn:xmpp:hash-function-text-names:{}"
BUFFER_SIZE = 2 ** 12
ALGO_DEFAULT = "sha-256"


class XEP_0300(object):
    # TODO: add blake after moving to Python 3
    ALGOS = OrderedDict(
        (
            (u"md5", hashlib.md5),
            (u"sha-1", hashlib.sha1),
            (u"sha-256", hashlib.sha256),
            (u"sha-512", hashlib.sha512),
        )
    )

    def __init__(self, host):
        log.info(_("plugin Hashes initialization"))
        host.registerNamespace("hashes", NS_HASHES)

    def getHandler(self, client):
        return XEP_0300_handler()

    def getHasher(self, algo=ALGO_DEFAULT):
        """Return hasher instance

        @param algo(unicode): one of the XEP_300.ALGOS keys
        @return (hash object): same object s in hashlib.
           update method need to be called for each chunh
           diget or hexdigest can be used at the end
        """
        return self.ALGOS[algo]()

    def getDefaultAlgo(self):
        return ALGO_DEFAULT

    @defer.inlineCallbacks
    def getBestPeerAlgo(self, to_jid, profile):
        """Return the best available hashing algorith of other peer

         @param to_jid(jid.JID): peer jid
         @parm profile: %(doc_profile)s
         @return (D(unicode, None)): best available algorithm,
            or None if hashing is not possible
        """
        client = self.host.getClient(profile)
        for algo in reversed(XEP_0300.ALGOS):
            has_feature = yield self.host.hasFeature(
                client, NS_HASHES_FUNCTIONS.format(algo), to_jid
            )
            if has_feature:
                log.debug(
                    u"Best hashing algorithm found for {jid}: {algo}".format(
                        jid=to_jid.full(), algo=algo
                    )
                )
                defer.returnValue(algo)

    def _calculateHashBlocking(self, file_obj, hasher):
        """Calculate hash in a blocking way

        /!\\ blocking method, please use calculateHash instead
        @param file_obj(file): a file-like object
        @param hasher(callable): the method to call to initialise hash object
        @return (str): the hex digest of the hash
        """
        hash_ = hasher()
        while True:
            buf = file_obj.read(BUFFER_SIZE)
            if not buf:
                break
            hash_.update(buf)
        return hash_.hexdigest()

    def calculateHash(self, file_obj, hasher):
        return threads.deferToThread(self._calculateHashBlocking, file_obj, hasher)

    def calculateHashElt(self, file_obj=None, algo=ALGO_DEFAULT):
        """Compute hash and build hash element

        @param file_obj(file, None): file-like object to use to calculate the hash
        @param algo(unicode): algorithme to use, must be a key of XEP_0300.ALGOS
        @return (D(domish.Element)): hash element
        """

        def hashCalculated(hash_):
            return self.buildHashElt(hash_, algo)

        hasher = self.ALGOS[algo]
        hash_d = self.calculateHash(file_obj, hasher)
        hash_d.addCallback(hashCalculated)
        return hash_d

    def buildHashUsedElt(self, algo=ALGO_DEFAULT):
        hash_used_elt = domish.Element((NS_HASHES, "hash-used"))
        hash_used_elt["algo"] = algo
        return hash_used_elt

    def parseHashUsedElt(self, parent):
        """Find and parse a hash-used element

        @param (domish.Element): parent of <hash/> element
        @return (unicode): hash algorithm used
        @raise exceptions.NotFound: the element is not present
        @raise exceptions.DataError: the element is invalid
        """
        try:
            hash_used_elt = next(parent.elements(NS_HASHES, "hash-used"))
        except StopIteration:
            raise exceptions.NotFound
        algo = hash_used_elt[u"algo"]
        if not algo:
            raise exceptions.DataError
        return algo

    def buildHashElt(self, hash_, algo=ALGO_DEFAULT):
        """Compute hash and build hash element

        @param hash_(str): hash to use
        @param algo(unicode): algorithme to use, must be a key of XEP_0300.ALGOS
        @return (domish.Element): computed hash
        """
        assert hash_
        assert algo
        hash_elt = domish.Element((NS_HASHES, "hash"))
        if hash_ is not None:
            hash_elt.addContent(base64.b64encode(hash_))
        hash_elt["algo"] = algo
        return hash_elt

    def parseHashElt(self, parent):
        """Find and parse a hash element

        if multiple elements are found, the strongest managed one is returned
        @param (domish.Element): parent of <hash/> element
        @return (tuple[unicode, str]): (algo, hash) tuple
            both values can be None if <hash/> is empty
        @raise exceptions.NotFound: the element is not present
        @raise exceptions.DataError: the element is invalid
        """
        algos = XEP_0300.ALGOS.keys()
        hash_elt = None
        best_algo = None
        best_value = None
        for hash_elt in parent.elements(NS_HASHES, "hash"):
            algo = hash_elt.getAttribute("algo")
            try:
                idx = algos.index(algo)
            except ValueError:
                log.warning(u"Proposed {} algorithm is not managed".format(algo))
                algo = None
                continue

            if best_algo is None or algos.index(best_algo) < idx:
                best_algo = algo
                best_value = base64.b64decode(unicode(hash_elt))

        if not hash_elt:
            raise exceptions.NotFound
        if not best_algo or not best_value:
            raise exceptions.DataError
        return best_algo, best_value


class XEP_0300_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        hash_functions_names = [
            disco.DiscoFeature(NS_HASHES_FUNCTIONS.format(algo))
            for algo in XEP_0300.ALGOS
        ]
        return [disco.DiscoFeature(NS_HASHES)] + hash_functions_names

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
