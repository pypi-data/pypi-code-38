#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for OMEMO encryption
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
from sat.core import exceptions
from omemo import exceptions as omemo_excpt
from twisted.internet import defer
from twisted.words.xish import domish
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber import error
from sat.memory import persistent
from functools import partial
from sat.tools import xml_tools
import logging
import random
import base64
try:
    import omemo
    from omemo.extendedpublicbundle import ExtendedPublicBundle
    from omemo_backend_signal import BACKEND as omemo_backend
    # from omemo import wireformat
except ImportError as e:
    raise exceptions.MissingModule(
        u'Missing module omemo, please download/install it. You can use '
        u'"pip install omemo"'
    )

log = getLogger(__name__)

PLUGIN_INFO = {
    C.PI_NAME: u"OMEMO",
    C.PI_IMPORT_NAME: u"XEP-0384",
    C.PI_TYPE: u"SEC",
    C.PI_PROTOCOLS: [u"XEP-0384"],
    C.PI_DEPENDENCIES: [u"XEP-0163", u"XEP-0280", u"XEP-0334", u"XEP-0060"],
    C.PI_MAIN: u"OMEMO",
    C.PI_HANDLER: u"no",
    C.PI_DESCRIPTION: _(u"""Implementation of OMEMO"""),
}

OMEMO_MIN_VER = (0, 10, 4)
NS_OMEMO = "eu.siacs.conversations.axolotl"
NS_OMEMO_DEVICES = NS_OMEMO + ".devicelist"
NS_OMEMO_BUNDLE = NS_OMEMO + ".bundles:{device_id}"
KEY_STATE = "STATE"
KEY_DEVICE_ID = "DEVICE_ID"
KEY_SESSION = "SESSION"
KEY_TRUST = "TRUST"
KEY_ACTIVE_DEVICES = "DEVICES"
KEY_INACTIVE_DEVICES = "INACTIVE_DEVICES"
KEY_ALL_JIDS = "ALL_JIDS"


# we want to manage log emitted by omemo module ourselves

class SatHandler(logging.Handler):

    def emit(self, record):
        log.log(record.levelname, record.getMessage())

    @staticmethod
    def install():
        omemo_sm_logger = logging.getLogger("omemo.SessionManager")
        omemo_sm_logger.propagate = False
        omemo_sm_logger.addHandler(SatHandler())


SatHandler.install()


def b64enc(data):
    return base64.b64encode(bytes(bytearray(data))).decode("US-ASCII")


def promise2Deferred(promise_):
    """Create a Deferred and fire it when promise is resolved

    @param promise_(promise.Promise): promise to convert
    @return (defer.Deferred): deferred instance linked to the promise
    """
    d = defer.Deferred()
    promise_.then(d.callback, d.errback)
    return d


class OmemoStorage(omemo.Storage):

    def __init__(self, client, device_id, all_jids, persistent_dict):
        """
        @param persistent_dict(persistent.LazyPersistentBinaryDict): object which will
            store data in SàT database
        """
        self.own_bare_jid_s = client.jid.userhost()
        self.device_id = device_id
        self.all_jids = all_jids
        self.data = persistent_dict

    @property
    def is_async(self):
        return True

    def setCb(self, deferred, callback):
        """Associate Deferred and callback

        callback of omemo.Storage expect a boolean with success state then result
        Deferred on the other hand use 2 methods for callback and errback
        This method use partial to call callback with boolean then result when
        Deferred is called
        """
        deferred.addCallback(partial(callback, True))
        deferred.addErrback(partial(callback, False))

    def _checkJid(self, bare_jid):
        """Check if jid is know, and store it if not

        @param bare_jid(unicode): bare jid to check
        @return (D): Deferred fired when jid is stored
        """
        if bare_jid in self.all_jids:
            return defer.succeed(None)
        else:
            self.all_jids.add(bare_jid)
            d = self.data.force(KEY_ALL_JIDS, self.all_jids)
            return d

    def loadOwnData(self, callback):
        callback(True, {'own_bare_jid': self.own_bare_jid_s,
                        'own_device_id': self.device_id})

    def storeOwnData(self, callback, own_bare_jid, own_device_id):
        if own_bare_jid != self.own_bare_jid_s or own_device_id != self.device_id:
            raise exceptions.InternalError('bare jid or device id inconsistency!')
        callback(True, None)

    def loadState(self, callback):
        d = self.data.get(KEY_STATE)
        self.setCb(d, callback)

    def storeState(self, callback, state):
        d = self.data.force(KEY_STATE, state)
        self.setCb(d, callback)

    def loadSession(self, callback, bare_jid, device_id):
        key = u'\n'.join([KEY_SESSION, bare_jid, unicode(device_id)])
        d = self.data.get(key)
        self.setCb(d, callback)

    def storeSession(self, callback, bare_jid, device_id, session):
        key = u'\n'.join([KEY_SESSION, bare_jid, unicode(device_id)])
        d = self.data.force(key, session)
        self.setCb(d, callback)

    def deleteSession(self, callback, bare_jid, device_id):
        key = u'\n'.join([KEY_SESSION, bare_jid, unicode(device_id)])
        d = self.data.remove(key)
        self.setCb(d, callback)

    def loadActiveDevices(self, callback, bare_jid):
        key = u'\n'.join([KEY_ACTIVE_DEVICES, bare_jid])
        d = self.data.get(key, {})
        if callback is not None:
            self.setCb(d, callback)
        return d

    def loadInactiveDevices(self, callback, bare_jid):
        key = u'\n'.join([KEY_INACTIVE_DEVICES, bare_jid])
        d = self.data.get(key, {})
        if callback is not None:
            self.setCb(d, callback)
        return d

    def storeActiveDevices(self, callback, bare_jid, devices):
        key = u'\n'.join([KEY_ACTIVE_DEVICES, bare_jid])
        d = self._checkJid(bare_jid)
        d.addCallback(lambda _: self.data.force(key, devices))
        self.setCb(d, callback)

    def storeInactiveDevices(self, callback, bare_jid, devices):
        key = u'\n'.join([KEY_INACTIVE_DEVICES, bare_jid])
        d = self._checkJid(bare_jid)
        d.addCallback(lambda _: self.data.force(key, devices))
        self.setCb(d, callback)

    def storeTrust(self, callback, bare_jid, device_id, trust):
        key = u'\n'.join([KEY_TRUST, bare_jid, unicode(device_id)])
        d = self.data.force(key, trust)
        self.setCb(d, callback)

    def loadTrust(self, callback, bare_jid, device_id):
        key = u'\n'.join([KEY_TRUST, bare_jid, unicode(device_id)])
        d = self.data.get(key)
        if callback is not None:
            self.setCb(d, callback)
        return d

    def listJIDs(self, callback):
        d = defer.succeed(self.all_jids)
        if callback is not None:
            self.setCb(d, callback)
        return d

    def _deleteJID_logResults(self, results):
        failed = [success for success, __ in results if not success]
        if failed:
            log.warning(
                u"delete JID failed for {failed_count} on {total_count} operations"
                .format(failed_count=len(failed), total_count=len(results)))
        else:
            log.info(
                u"Delete JID operation succeed ({total_count} operations)."
                .format(total_count=len(results)))

    def _deleteJID_gotDevices(self, results, bare_jid):
        assert len(results) == 2
        active_success, active_devices = results[0]
        inactive_success, inactive_devices = results[0]
        d_list = []
        for success, devices in results:
            if not success:
                log.warning("Can't retrieve devices for {bare_jid}: {reason}"
                    .format(bare_jid=bare_jid, reason=active_devices))
            else:
                for device_id in devices:
                    for key in (KEY_SESSION, KEY_TRUST):
                        k = u'\n'.join([key, bare_jid, unicode(device_id)])
                        d_list.append(self.data.remove(k))

        d_list.append(self.data.remove(KEY_ACTIVE_DEVICES, bare_jid))
        d_list.append(self.data.remove(KEY_INACTIVE_DEVICES, bare_jid))
        d_list.append(lambda __: self.all_jids.discard(bare_jid))
        # FIXME: there is a risk of race condition here,
        #        if self.all_jids is modified between discard and force)
        d_list.append(lambda __: self.data.force(KEY_ALL_JIDS, self.all_jids))
        d = defer.DeferredList(d_list)
        d.addCallback(self._deleteJID_logResults)
        return d

    def deleteJID(self, callback, bare_jid):
        """Retrieve all (in)actives of bare_jid, and delete all related keys"""
        d_list = []

        key = u'\n'.join([KEY_ACTIVE_DEVICES, bare_jid])
        d_list.append(self.data.get(key, []))

        key = u'\n'.join([KEY_INACTIVE_DEVICES, bare_jid])
        d_inactive = self.data.get(key, {})
        # inactive devices are returned as a dict mapping from devices_id to timestamp
        # but we only need devices ids
        d_inactive.addCallback(lambda devices: [k for k, __ in devices])

        d_list.append(d_inactive)
        d = defer.DeferredList(d_list)
        d.addCallback(self._deleteJID_gotDevices, bare_jid)
        if callback is not None:
            self.setCb(d, callback)
        return d


class SatOTPKPolicy(omemo.DefaultOTPKPolicy):
    pass


class OmemoSession(object):
    """Wrapper to use omemo.OmemoSession with Deferred"""

    def __init__(self, session):
        self._session = session

    @property
    def republish_bundle(self):
        return self._session.republish_bundle

    @property
    def public_bundle(self):
        return self._session.public_bundle

    @classmethod
    def create(cls, client, storage, my_device_id = None):
        omemo_session_p = omemo.SessionManager.create(
            storage,
            SatOTPKPolicy,
            omemo_backend,
            client.jid.userhost(),
            my_device_id)
        d = promise2Deferred(omemo_session_p)
        d.addCallback(lambda session: cls(session))
        return d

    def newDeviceList(self, jid, devices):
        jid = jid.userhost()
        new_device_p = self._session.newDeviceList(jid, devices)
        return promise2Deferred(new_device_p)

    def getDevices(self, bare_jid=None):
        get_devices_p = self._session.getDevices(bare_jid=bare_jid)
        return promise2Deferred(get_devices_p)

    def buildSession(self, bare_jid, device, bundle):
        bare_jid = bare_jid.userhost()
        build_session_p = self._session.buildSession(bare_jid, device, bundle)
        return promise2Deferred(build_session_p)

    def encryptMessage(self, bare_jids, message, bundles=None, expect_problems=None):
        """Encrypt a message

        @param bare_jids(iterable[jid.JID]): destinees of the message
        @param message(unicode): message to encode
        @param bundles(dict[jid.JID, dict[int, ExtendedPublicBundle]):
            entities => devices => bundles map
        @return D(dict): encryption data
        """
        if isinstance(bare_jids, jid.JID):
            bare_jids = bare_jids.userhost()
        else:
            bare_jids = [e.userhost() for e in bare_jids]
        if bundles is not None:
            bundles = {e.userhost(): v for e, v in bundles.iteritems()}
        encrypt_mess_p = self._session.encryptMessage(
            bare_jids=bare_jids,
            plaintext=message.encode('utf-8'),
            bundles=bundles,
            expect_problems=expect_problems)
        return promise2Deferred(encrypt_mess_p)

    def decryptMessage(self, bare_jid, device, iv, message, is_pre_key_message,
                       ciphertext, additional_information=None, allow_untrusted=False):
        bare_jid = bare_jid.userhost()
        decrypt_mess_p = self._session.decryptMessage(
            bare_jid=bare_jid,
            device=device,
            iv=iv,
            message=message,
            is_pre_key_message=is_pre_key_message,
            ciphertext=ciphertext,
            additional_information=additional_information,
            allow_untrusted=allow_untrusted
            )
        return promise2Deferred(decrypt_mess_p)

    def trust(self, bare_jid, device, key):
        bare_jid = bare_jid.userhost()
        trust_p = self._session.trust(
            bare_jid=bare_jid,
            device=device,
            key=key)
        return promise2Deferred(trust_p)

    def distrust(self, bare_jid, device, key):
        bare_jid = bare_jid.userhost()
        distrust_p = self._session.distrust(
            bare_jid=bare_jid,
            device=device,
            key=key)
        return promise2Deferred(distrust_p)

    def getTrustForJID(self, bare_jid):
        bare_jid = bare_jid.userhost()
        get_trust_p = self._session.getTrustForJID(bare_jid=bare_jid)
        return promise2Deferred(get_trust_p)


class OMEMO(object):

    def __init__(self, host):
        log.info(_(u"OMEMO plugin initialization (omemo module v{version})").format(
            version=omemo.__version__))
        version = tuple(map(int, omemo.__version__.split(u'.')[:3]))
        if version < OMEMO_MIN_VER:
            log.warning(_(
                u"Your version of omemo module is too old: {v[0]}.{v[1]}.{v[2]} is "
                u"minimum required), please update.").format(v=OMEMO_MIN_VER))
            raise exceptions.CancelError("module is too old")
        self.host = host
        self._p_hints = host.plugins[u"XEP-0334"]
        self._p_carbons = host.plugins[u"XEP-0280"]
        self._p = host.plugins[u"XEP-0060"]
        host.trigger.add("MessageReceived", self._messageReceivedTrigger, priority=100050)
        host.trigger.add("sendMessageData", self._sendMessageDataTrigger)
        self.host.registerEncryptionPlugin(self, u"OMEMO", NS_OMEMO, 100)
        pep = host.plugins['XEP-0163']
        pep.addPEPEvent("OMEMO_DEVICES", NS_OMEMO_DEVICES, self.onNewDevices)

    @defer.inlineCallbacks
    def trustUICb(self, xmlui_data, trust_data, expect_problems=None,
                  profile=C.PROF_KEY_NONE):
        if C.bool(xmlui_data.get('cancelled', 'false')):
            defer.returnValue({})
        client = self.host.getClient(profile)
        session = client._xep_0384_session
        answer = xml_tools.XMLUIResult2DataFormResult(xmlui_data)
        for key, value in answer.iteritems():
            if key.startswith(u'trust_'):
                trust_id = key[6:]
            else:
                continue
            data = trust_data[trust_id]
            trust = C.bool(value)
            if trust:
                yield session.trust(data[u"jid"],
                                    data[u"device"],
                                    data[u"ik"])
            else:
                yield session.distrust(data[u"jid"],
                                       data[u"device"],
                                       data[u"ik"])
                if expect_problems is not None:
                    expect_problems.setdefault(data.bare_jid, set()).add(data.device)
        defer.returnValue({})



    @defer.inlineCallbacks
    def getTrustUI(self, client, entity_jid=None, trust_data=None, submit_id=None):
        """Generate a XMLUI to manage trust

        @param entity_jid(None, jid.JID): jid of entity to manage
            None to use trust_data
        @param trust_data(None, dict): devices data:
            None to use entity_jid
            else a dict mapping from trust ids (unicode) to devices data,
            where a device data must have the following keys:
                - jid(jid.JID): bare jid of the device owner
                - device(int): device id
                - ik(bytes): identity key
            and may have the following key:
                - trusted(bool): True if device is trusted
        @param submit_id(None, unicode): submit_id to use
            if None set UI callback to trustUICb
        @return D(xmlui): trust management form
        """
        # we need entity_jid xor trust_data
        assert entity_jid and not trust_data or not entity_jid and trust_data
        if entity_jid and entity_jid.resource:
            raise ValueError(u"A bare jid is expected")

        session = client._xep_0384_session

        if trust_data is None:
            cache = client._xep_0384_cache.setdefault(entity_jid, {})
            trust_data = {}
            trust_session_data = yield session.getTrustForJID(entity_jid)
            bare_jid_s = entity_jid.userhost()
            for device_id, trust_info in trust_session_data['active'].iteritems():
                if trust_info is None:
                    # device has never been (un)trusted, we have to retrieve its
                    # fingerprint (i.e. identity key or "ik") through public bundle
                    if device_id not in cache:
                        bundles, missing = yield self.getBundles(client,
                                                                 entity_jid,
                                                                 [device_id])
                        if device_id not in bundles:
                            log.warning(_(
                                u"Can't find bundle for device {device_id} of user "
                                u"{bare_jid}, ignoring").format(device_id=device_id,
                                                                bare_jid=bare_jid_s))
                            continue
                        cache[device_id] = bundles[device_id]
                    # TODO: replace False below by None when undecided
                    #       trusts are handled
                    trust_info = {
                        u"key": cache[device_id].ik,
                        u"trusted": False
                    }

                ik = trust_info["key"]
                trust_id = unicode(hash((bare_jid_s, device_id, ik)))
                trust_data[trust_id] = {
                    u"jid": entity_jid,
                    u"device": device_id,
                    u"ik": ik,
                    u"trusted": trust_info[u"trusted"],
                    }

        if submit_id is None:
            submit_id = self.host.registerCallback(partial(self.trustUICb,
                                                           trust_data=trust_data),
                                                   with_data=True,
                                                   one_shot=True)
        xmlui = xml_tools.XMLUI(
            panel_type = C.XMLUI_FORM,
            title = D_(u"OMEMO trust management"),
            submit_id = submit_id
        )
        xmlui.addText(D_(
            u"This is OMEMO trusting system. You'll see below the devices of your "
            u"contacts, and a checkbox to trust them or not. A trusted device "
            u"can read your messages in plain text, so be sure to only validate "
            u"devices that you are sure are belonging to your contact. It's better "
            u"to do this when you are next to your contact and her/his device, so "
            u"you can check the \"fingerprint\" (the number next to the device) "
            u"yourself. Do *not* validate a device if the fingerprint is wrong!"))

        xmlui.changeContainer("label")
        xmlui.addLabel(D_(u"This device ID"))
        xmlui.addText(unicode(client._xep_0384_device_id))
        xmlui.addLabel(D_(u"This device fingerprint"))
        ik_hex = session.public_bundle.ik.encode('hex').upper()
        fp_human = u' '.join([ik_hex[i:i+8] for i in range(0, len(ik_hex), 8)])
        xmlui.addText(fp_human)
        xmlui.addEmpty()
        xmlui.addEmpty()


        for trust_id, data in trust_data.iteritems():
            xmlui.addLabel(D_(u"Contact"))
            xmlui.addJid(data[u'jid'])
            xmlui.addLabel(D_(u"Device ID"))
            xmlui.addText(unicode(data[u'device']))
            xmlui.addLabel(D_(u"Fingerprint"))
            ik_hex = data[u'ik'].encode('hex').upper()
            fp_human = u' '.join([ik_hex[i:i+8] for i in range(0, len(ik_hex), 8)])
            xmlui.addText(fp_human)
            xmlui.addLabel(D_(u"Trust this device?"))
            xmlui.addBool(u"trust_{}".format(trust_id),
                          value=C.boolConst(data.get(u'trusted', False)))

            xmlui.addEmpty()
            xmlui.addEmpty()

        defer.returnValue(xmlui)

    @defer.inlineCallbacks
    def profileConnected(self, client):
        # FIXME: is _xep_0384_ready needed? can we use profileConnecting?
        #        Workflow should be checked
        client._xep_0384_ready = defer.Deferred()
        # we first need to get devices ids (including our own)
        persistent_dict = persistent.LazyPersistentBinaryDict("XEP-0384", client.profile)
        # all known devices of profile
        devices = yield self.getDevices(client)
        # and our own device id
        device_id = yield persistent_dict.get(KEY_DEVICE_ID)
        if device_id is None:
            log.info(_(u"We have no identity for this device yet, let's generate one"))
            # we have a new device, we create device_id
            device_id = random.randint(1, 2**31-1)
            # we check that it's really unique
            while device_id in devices:
                device_id = random.randint(1, 2**31-1)
            # and we save it
            persistent_dict[KEY_DEVICE_ID] = device_id

        if device_id not in devices:
            devices.add(device_id)
            yield self.setDevices(client, devices)

        all_jids = yield persistent_dict.get(KEY_ALL_JIDS, set())

        omemo_storage = OmemoStorage(client, device_id, all_jids, persistent_dict)
        omemo_session = yield OmemoSession.create(client, omemo_storage, device_id)
        client._xep_0384_cache = {}
        client._xep_0384_session = omemo_session
        client._xep_0384_device_id = device_id
        yield omemo_session.newDeviceList(client.jid, devices)
        if omemo_session.republish_bundle:
            log.info(_(u"Saving public bundle for this device ({device_id})").format(
                device_id=device_id))
            yield self.setBundle(client, omemo_session.public_bundle, device_id)
        client._xep_0384_ready.callback(None)
        del client._xep_0384_ready

    ## XMPP PEP nodes manipulation

    # devices

    def parseDevices(self, items):
        """Parse devices found in items

        @param items(iterable[domish.Element]): items as retrieved by getItems
        @return set[int]: parsed devices
        """
        devices = set()
        if len(items) > 1:
            log.warning(_(u"OMEMO devices list is stored in more that one items, "
                          u"this is not expected"))
        if items:
            try:
                list_elt = next(items[0].elements(NS_OMEMO, 'list'))
            except StopIteration:
                log.warning(_(u"no list element found in OMEMO devices list"))
                return
            for device_elt in list_elt.elements(NS_OMEMO, 'device'):
                try:
                    device_id = int(device_elt['id'])
                except KeyError:
                    log.warning(_(u'device element is missing "id" attribute: {elt}')
                                .format(elt=device_elt.toXml()))
                except ValueError:
                    log.warning(_(u'invalid device id: {device_id}').format(
                        device_id=device_elt['id']))
                else:
                    devices.add(device_id)
        return devices

    @defer.inlineCallbacks
    def getDevices(self, client, entity_jid=None):
        """Retrieve list of registered OMEMO devices

        @param entity_jid(jid.JID, None): get devices from this entity
            None to get our own devices
        @return (set(int)): list of devices
        """
        if entity_jid is not None:
            assert not entity_jid.resource
        try:
            items, metadata = yield self._p.getItems(client, entity_jid, NS_OMEMO_DEVICES)
        except error.StanzaError as e:
            if e.condition == 'item-not-found':
                log.info(_(u"there is no node to handle OMEMO devices"))
                defer.returnValue(set())
            raise e

        devices = self.parseDevices(items)
        defer.returnValue(devices)

    def setDevicesEb(self, failure_):
        log.warning(_(u"Can't set devices: {reason}").format(reason=failure_))

    def setDevices(self, client, devices):
        list_elt = domish.Element((NS_OMEMO, 'list'))
        for device in devices:
            device_elt = list_elt.addElement('device')
            device_elt['id'] = unicode(device)
        d = self._p.sendItem(
            client, None, NS_OMEMO_DEVICES, list_elt, item_id=self._p.ID_SINGLETON)
        d.addErrback(self.setDevicesEb)
        return d

    # bundles

    @defer.inlineCallbacks
    def getBundles(self, client, entity_jid, devices_ids):
        """Retrieve public bundles of an entity devices

        @param entity_jid(jid.JID): bare jid of entity
        @param devices_id(iterable[int]): ids of the devices bundles to retrieve
        @return (tuple(dict[int, ExtendedPublicBundle], list(int))):
            - bundles collection:
                * key is device_id
                * value is parsed bundle
            - set of bundles not found
        """
        assert not entity_jid.resource
        bundles = {}
        missing = set()
        for device_id in devices_ids:
            node = NS_OMEMO_BUNDLE.format(device_id=device_id)
            try:
                items, metadata = yield self._p.getItems(client, entity_jid, node)
            except error.StanzaError as e:
                if e.condition == u"item-not-found":
                    log.warning(_(u"Bundle missing for device {device_id}")
                        .format(device_id=device_id))
                    missing.add(device_id)
                    continue
                else:
                    log.warning(_(u"Can't get bundle for device {device_id}: {reason}")
                        .format(device_id=device_id, reason=e))
                    continue
            if not items:
                log.warning(_(u"no item found in node {node}, can't get public bundle "
                              u"for device {device_id}").format(node=node,
                                                                device_id=device_id))
                continue
            if len(items) > 1:
                log.warning(_(u"more than one item found in {node}, "
                              u"this is not expected").format(node=node))
            item = items[0]
            try:
                bundle_elt = next(item.elements(NS_OMEMO, 'bundle'))
                signedPreKeyPublic_elt = next(bundle_elt.elements(
                    NS_OMEMO, 'signedPreKeyPublic'))
                signedPreKeySignature_elt = next(bundle_elt.elements(
                    NS_OMEMO, 'signedPreKeySignature'))
                identityKey_elt = next(bundle_elt.elements(
                    NS_OMEMO, 'identityKey'))
                prekeys_elt =  next(bundle_elt.elements(
                    NS_OMEMO, 'prekeys'))
            except StopIteration:
                log.warning(_(u"invalid bundle for device {device_id}, ignoring").format(
                    device_id=device_id))
                continue

            try:
                spkPublic = base64.b64decode(unicode(signedPreKeyPublic_elt))
                spkSignature = base64.b64decode(
                    unicode(signedPreKeySignature_elt))

                ik = base64.b64decode(unicode(identityKey_elt))
                spk = {
                    "key": spkPublic,
                    "id": int(signedPreKeyPublic_elt['signedPreKeyId'])
                }
                otpks = []
                for preKeyPublic_elt in prekeys_elt.elements(NS_OMEMO, 'preKeyPublic'):
                    preKeyPublic = base64.b64decode(unicode(preKeyPublic_elt))
                    otpk = {
                        "key": preKeyPublic,
                        "id": int(preKeyPublic_elt['preKeyId'])
                    }
                    otpks.append(otpk)

            except Exception as e:
                log.warning(_(u"error while decoding key for device {device_id}: {msg}")
                            .format(device_id=device_id, msg=e))
                continue

            bundles[device_id] = ExtendedPublicBundle.parse(omemo_backend, ik, spk,
                                                            spkSignature, otpks)

        defer.returnValue((bundles, missing))

    def setBundleEb(self, failure_):
        log.warning(_(u"Can't set bundle: {reason}").format(reason=failure_))

    def setBundle(self, client, bundle, device_id):
        """Set public bundle for this device.

        @param bundle(ExtendedPublicBundle): bundle to publish
        """
        log.debug(_(u"updating bundle for {device_id}").format(device_id=device_id))
        bundle = bundle.serialize(omemo_backend)
        bundle_elt = domish.Element((NS_OMEMO, 'bundle'))
        signedPreKeyPublic_elt = bundle_elt.addElement(
            "signedPreKeyPublic",
            content=b64enc(bundle["spk"]['key']))
        signedPreKeyPublic_elt['signedPreKeyId'] = unicode(bundle["spk"]['id'])

        bundle_elt.addElement(
            "signedPreKeySignature",
            content=b64enc(bundle["spk_signature"]))

        bundle_elt.addElement(
            "identityKey",
            content=b64enc(bundle["ik"]))

        prekeys_elt = bundle_elt.addElement('prekeys')
        for otpk in bundle["otpks"]:
            preKeyPublic_elt = prekeys_elt.addElement(
                'preKeyPublic',
                content=b64enc(otpk["key"]))
            preKeyPublic_elt['preKeyId'] = unicode(otpk['id'])

        node = NS_OMEMO_BUNDLE.format(device_id=device_id)
        d = self._p.sendItem(client, None, node, bundle_elt, item_id=self._p.ID_SINGLETON)
        d.addErrback(self.setBundleEb)
        return d

    ## PEP node events callbacks

    @defer.inlineCallbacks
    def onNewDevices(self, itemsEvent, profile):
        client = self.host.getClient(profile)
        try:
            omemo_session = client._xep_0384_session
        except AttributeError:
            yield client._xep_0384_ready
            omemo_session = client._xep_0384_session
        entity = itemsEvent.sender

        devices = self.parseDevices(itemsEvent.items)
        omemo_session.newDeviceList(entity, devices)

        if entity == client.jid.userhostJID():
            own_device = client._xep_0384_device_id
            if own_device not in devices:
                log.warning(_(u"Our own device is missing from devices list, fixing it"))
                devices.add(own_device)
                yield self.setDevices(client, devices)

    ## triggers

    @defer.inlineCallbacks
    def handleProblems(self, client, entity, bundles, expect_problems, problems):
        """Try to solve problems found by EncryptMessage

        @param entity(jid.JID): bare jid of the destinee
        @param bundles(dict): bundles data as used in EncryptMessage
            already filled with known bundles, missing bundles
            need to be added to it
            This dict is updated
        @param problems(list): exceptions raised by EncryptMessage
        @param expect_problems(dict): known problems to expect, used in encryptMessage
            This dict will list devices where problems can be ignored
            (those devices won't receive the encrypted data)
            This dict is updated
        """
        # FIXME: not all problems are handled yet
        untrusted = {}
        missing_bundles = {}
        cache = client._xep_0384_cache
        for problem in problems:
            if isinstance(problem, omemo_excpt.TrustException):
                untrusted[unicode(hash(problem))] = problem
            elif isinstance(problem, omemo_excpt.MissingBundleException):
                pb_entity = jid.JID(problem.bare_jid)
                entity_cache = cache.setdefault(pb_entity, {})
                entity_bundles = bundles.setdefault(pb_entity, {})
                if problem.device in entity_cache:
                    entity_bundles[problem.device] = entity_cache[problem.device]
                else:
                    found_bundles, missing = yield self.getBundles(
                        client, pb_entity, [problem.device])
                    entity_cache.update(bundles)
                    entity_bundles.update(found_bundles)
                    if problem.device in missing:
                        missing_bundles.setdefault(pb_entity, set()).add(
                            problem.device)
                        expect_problems.setdefault(problem.bare_jid, set()).add(
                            problem.device)
            elif isinstance(problem, omemo_excpt.NoEligibleDevicesException):
                if untrusted or found_bundles:
                    # we may have new devices after this run, so let's continue for now
                    continue
                else:
                    raise problem
            else:
                raise problem

        for peer_jid, devices in missing_bundles.iteritems():
            devices_s = [unicode(d) for d in devices]
            log.warning(
                _(u"Can't retrieve bundle for device(s) {devices} of entity {peer}, "
                  u"the message will not be readable on this/those device(s)").format(
                    devices=u", ".join(devices_s), peer=peer_jid.full()))
            client.feedback(
                entity,
                D_(u"You're destinee {peer} has missing encryption data on some of "
                   u"his/her device(s) (bundle on device {devices}), the message won't  "
                   u"be readable on this/those device.").format(
                   peer=peer_jid.full(), devices=u", ".join(devices_s)))

        if untrusted:
            trust_data = {}
            for trust_id, data in untrusted.iteritems():
                trust_data[trust_id] = {
                    'jid': jid.JID(data.bare_jid),
                    'device':  data.device,
                    'ik': data.ik}

            user_msg =  D_(u"Not all destination devices are trusted, we can't encrypt "
                           u"message in such a situation. Please indicate if you trust "
                           u"those devices or not in the trust manager before we can "
                           "send this message")
            client.feedback(entity, user_msg)
            xmlui = yield self.getTrustUI(client, trust_data=trust_data, submit_id=u"")

            answer = yield xml_tools.deferXMLUI(
                self.host,
                xmlui,
                action_extra={
                    u"meta_encryption_trust": NS_OMEMO,
                },
                profile=client.profile)
            yield self.trustUICb(answer, trust_data, expect_problems, client.profile)

    @defer.inlineCallbacks
    def encryptMessage(self, client, entity_bare_jid, message):
        omemo_session = client._xep_0384_session
        expect_problems = {}
        bundles = {}
        loop_idx = 0
        try:
            while True:
                if loop_idx > 10:
                    msg = _(u"Too many iterations in encryption loop")
                    log.error(msg)
                    raise exceptions.InternalError(msg)
                # encryptMessage may fail, in case of e.g. trust issue or missing bundle
                try:
                    encrypted = yield omemo_session.encryptMessage(
                        entity_bare_jid,
                        message,
                        bundles,
                        expect_problems = expect_problems)
                except omemo_excpt.EncryptionProblemsException as e:
                    # we know the problem to solve, we can try to fix them
                    yield self.handleProblems(
                        client,
                        entity=entity_bare_jid,
                        bundles=bundles,
                        expect_problems=expect_problems,
                        problems=e.problems)
                    loop_idx += 1
                else:
                    break
        except Exception as e:
            msg = _(u"Can't encrypt message for {entity}: {reason}".format(
                entity=entity_bare_jid.full(), reason=str(e).decode('utf-8', 'replace')))
            log.warning(msg)
            extra = {C.MESS_EXTRA_INFO: C.EXTRA_INFO_ENCR_ERR}
            client.feedback(entity_bare_jid, msg, extra)
            raise e

        defer.returnValue(encrypted)

    @defer.inlineCallbacks
    def _messageReceivedTrigger(self, client, message_elt, post_treat):
        if message_elt.getAttribute("type") == C.MESS_TYPE_GROUPCHAT:
            defer.returnValue(True)
        try:
            encrypted_elt = next(message_elt.elements(NS_OMEMO, u"encrypted"))
        except StopIteration:
            # no OMEMO message here
            defer.returnValue(True)

        # we have an encrypted message let's decrypt it
        from_jid = jid.JID(message_elt['from'])
        if from_jid.userhostJID() == client.jid.userhostJID():
            feedback_jid = jid.JID(message_elt['to'])
        else:
            feedback_jid = from_jid
        try:
            omemo_session = client._xep_0384_session
        except AttributeError:
            # on startup, message can ve received before session actually exists
            # so we need to synchronise here
            yield client._xep_0384_ready
            omemo_session = client._xep_0384_session

        device_id = client._xep_0384_device_id
        try:
            header_elt = next(encrypted_elt.elements(NS_OMEMO, u'header'))
            iv_elt = next(header_elt.elements(NS_OMEMO, u'iv'))
        except StopIteration:
            log.warning(_(u"Invalid OMEMO encrypted stanza, ignoring: {xml}")
                .format(xml=message_elt.toXml()))
            defer.returnValue(False)
        try:
            s_device_id = header_elt['sid']
        except KeyError:
            log.warning(_(u"Invalid OMEMO encrypted stanza, missing sender device ID, "
                          u"ignoring: {xml}")
                .format(xml=message_elt.toXml()))
            defer.returnValue(False)
        try:
            key_elt = next((e for e in header_elt.elements(NS_OMEMO, u'key')
                            if int(e[u'rid']) == device_id))
        except StopIteration:
            log.warning(_(u"This OMEMO encrypted stanza has not been encrypted "
                          u"for our device (device_id: {device_id}, fingerprint: "
                          u"{fingerprint}): {xml}").format(
                          device_id=device_id,
                          fingerprint=omemo_session.public_bundle.ik.encode('hex'),
                          xml=encrypted_elt.toXml()))
            user_msg = (D_(u"An OMEMO message from {sender} has not been encrypted for "
                           u"our device, we can't decrypt it").format(
                           sender=from_jid.full()))
            extra = {C.MESS_EXTRA_INFO: C.EXTRA_INFO_DECR_ERR}
            client.feedback(feedback_jid, user_msg, extra)
            defer.returnValue(False)
        except ValueError as e:
            log.warning(_(u"Invalid recipient ID: {msg}".format(msg=e)))
            defer.returnValue(False)
        is_pre_key = C.bool(key_elt.getAttribute('prekey', 'false'))
        payload_elt = next(encrypted_elt.elements(NS_OMEMO, u'payload'), None)
        additional_information = {
            "from_storage": bool(message_elt.delay)
        }

        kwargs = {
            "bare_jid": from_jid.userhostJID(),
            "device": s_device_id,
            "iv": base64.b64decode(bytes(iv_elt)),
            "message": base64.b64decode(bytes(key_elt)),
            "is_pre_key_message": is_pre_key,
            "ciphertext": base64.b64decode(bytes(payload_elt))
                if payload_elt is not None else None,
            "additional_information":  additional_information,
        }
        try:
            try:
                plaintext = yield omemo_session.decryptMessage(**kwargs)
            except omemo_excpt.TrustException:
                post_treat.addCallback(client.encryption.markAsUntrusted)
                kwargs['allow_untrusted'] = True
                plaintext = yield omemo_session.decryptMessage(**kwargs)
            else:
                post_treat.addCallback(client.encryption.markAsTrusted)
        except Exception as e:
            log.warning(_(u"Can't decrypt message: {reason}\n{xml}").format(
                reason=e, xml=message_elt.toXml()))
            user_msg = (D_(u"An OMEMO message from {sender} can't be decrypted: {reason}")
                .format(sender=from_jid.full(), reason=e))
            extra = {C.MESS_EXTRA_INFO: C.EXTRA_INFO_DECR_ERR}
            client.feedback(feedback_jid, user_msg, extra)
            defer.returnValue(False)
        finally:
            if omemo_session.republish_bundle:
                # we don't wait for the Deferred (i.e. no yield) on purpose
                # there is no need to block the whole message workflow while
                # updating the bundle
                self.setBundle(client, omemo_session.public_bundle, device_id)

        message_elt.children.remove(encrypted_elt)
        if plaintext:
            message_elt.addElement("body", content=plaintext.decode('utf-8'))
        post_treat.addCallback(client.encryption.markAsEncrypted)
        defer.returnValue(True)

    @defer.inlineCallbacks
    def _sendMessageDataTrigger(self, client, mess_data):
        encryption = mess_data.get(C.MESS_KEY_ENCRYPTION)
        if encryption is None or encryption['plugin'].namespace != NS_OMEMO:
            return
        message_elt = mess_data["xml"]
        to_jid = mess_data["to"].userhostJID()
        log.debug(u"encrypting message")
        body = None
        for child in list(message_elt.children):
            if child.name == "body":
                # we remove all unencrypted body,
                # and will only encrypt the first one
                if body is None:
                    body = child
                message_elt.children.remove(child)
            elif child.name == "html":
                # we don't want any XHTML-IM element
                message_elt.children.remove(child)

        if body is None:
            log.warning(u"No message found")
            return

        encryption_data = yield self.encryptMessage(client, to_jid, unicode(body))

        encrypted_elt = message_elt.addElement((NS_OMEMO, 'encrypted'))
        header_elt = encrypted_elt.addElement('header')
        header_elt['sid'] = unicode(encryption_data['sid'])
        bare_jid_s = to_jid.userhost()

        for rid, data in encryption_data['keys'][bare_jid_s].iteritems():
            key_elt = header_elt.addElement(
                'key',
                content=b64enc(data['data']))
            key_elt['rid'] = unicode(rid)
            if data['pre_key']:
                key_elt['prekey'] = 'true'

        header_elt.addElement(
            'iv',
            content=b64enc(encryption_data['iv']))
        try:
            encrypted_elt.addElement(
                'payload',
                content=b64enc(encryption_data['payload']))
        except KeyError:
            pass
