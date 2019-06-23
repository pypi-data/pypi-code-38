#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for OTR encryption
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

# XXX: thanks to Darrik L Mazey for his documentation
#      (https://blog.darmasoft.net/2013/06/30/using-pure-python-otr.html)
#      this implentation is based on it

from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger
from sat.core import exceptions

log = getLogger(__name__)
from sat.tools import xml_tools
from twisted.words.protocols.jabber import jid
from twisted.python import failure
from twisted.internet import defer
from sat.memory import persistent
import potr
import copy
import time
import uuid


PLUGIN_INFO = {
    C.PI_NAME: u"OTR",
    C.PI_IMPORT_NAME: u"OTR",
    C.PI_TYPE: u"SEC",
    C.PI_PROTOCOLS: [u"XEP-0364"],
    C.PI_DEPENDENCIES: [u"XEP-0280", u"XEP-0334"],
    C.PI_MAIN: u"OTR",
    C.PI_HANDLER: u"no",
    C.PI_DESCRIPTION: _(u"""Implementation of OTR"""),
}

NS_OTR = "urn:xmpp:otr:0"
PRIVATE_KEY = "PRIVATE KEY"
OTR_MENU = D_(u"OTR")
AUTH_TXT = D_(
    u"To authenticate your correspondent, you need to give your below fingerprint "
    u"*BY AN EXTERNAL CANAL* (i.e. not in this chat), and check that the one he gives "
    u"you is the same as below. If there is a mismatch, there can be a spy between you!"
)
DROP_TXT = D_(
    u"You private key is used to encrypt messages for your correspondent, nobody except "
    u"you must know it, if you are in doubt, you should drop it!\n\nAre you sure you "
    u"want to drop your private key?"
)
# NO_LOG_AND = D_(u"/!\\Your history is not logged anymore, and")   # FIXME: not used at the moment
NO_ADV_FEATURES = D_(u"Some of advanced features are disabled !")

DEFAULT_POLICY_FLAGS = {"ALLOW_V1": False, "ALLOW_V2": True, "REQUIRE_ENCRYPTION": True}

OTR_STATE_TRUSTED = "trusted"
OTR_STATE_UNTRUSTED = "untrusted"
OTR_STATE_UNENCRYPTED = "unencrypted"
OTR_STATE_ENCRYPTED = "encrypted"


class Context(potr.context.Context):
    def __init__(self, context_manager, other_jid):
        self.context_manager = context_manager
        super(Context, self).__init__(context_manager.account, other_jid)

    @property
    def host(self):
        return self.context_manager.host

    @property
    def _p_hints(self):
        return self.context_manager.parent._p_hints

    @property
    def _p_carbons(self):
        return self.context_manager.parent._p_carbons

    def getPolicy(self, key):
        if key in DEFAULT_POLICY_FLAGS:
            return DEFAULT_POLICY_FLAGS[key]
        else:
            return False

    def inject(self, msg_str, appdata=None):
        """Inject encrypted data in the stream

        if appdata is not None, we are sending a message in sendMessageDataTrigger
        stanza will be injected directly if appdata is None,
        else we just update the element and follow normal workflow
        @param msg_str(str): encrypted message body
        @param appdata(None, dict): None for signal message,
            message data when an encrypted message is going to be sent
        """
        assert isinstance(self.peer, jid.JID)
        msg = msg_str.decode("utf-8")
        client = self.user.client
        log.debug(u"injecting encrypted message to {to}".format(to=self.peer))
        if appdata is None:
            mess_data = {
                "from": client.jid,
                "to": self.peer,
                "uid": unicode(uuid.uuid4()),
                "message": {"": msg},
                "subject": {},
                "type": "chat",
                "extra": {},
                "timestamp": time.time(),
            }
            client.generateMessageXML(mess_data)
            xml = mess_data[u'xml']
            self._p_carbons.setPrivate(xml)
            self._p_hints.addHintElements(xml, [
                self._p_hints.HINT_NO_COPY,
                self._p_hints.HINT_NO_PERMANENT_STORE])
            client.send(mess_data["xml"])
        else:
            message_elt = appdata[u"xml"]
            assert message_elt.name == u"message"
            message_elt.addElement("body", content=msg)

    def stopCb(self, __, feedback):
        client = self.user.client
        self.host.bridge.otrState(
            OTR_STATE_UNENCRYPTED, self.peer.full(), client.profile
        )
        client.feedback(self.peer, feedback)

    def stopEb(self, failure_):
        # encryption may be already stopped in case of manual stop
        if not failure_.check(exceptions.NotFound):
            log.error(u"Error while stopping OTR encryption: {msg}".format(msg=failure_))

    def isTrusted(self):
        # we have to check value because potr code says that a 2-tuples should be
        # returned while in practice it's either None or u"trusted"
        trusted = self.getCurrentTrust()
        if trusted is None:
            return False
        elif trusted == u'trusted':
            return True
        else:
            log.error(u"Unexpected getCurrentTrust() value: {value}".format(
                value=trusted))
            return False

    def setState(self, state):
        client = self.user.client
        old_state = self.state
        super(Context, self).setState(state)
        log.debug(u"setState: %s (old_state=%s)" % (state, old_state))

        if state == potr.context.STATE_PLAINTEXT:
            feedback = _(u"/!\\ conversation with %(other_jid)s is now UNENCRYPTED") % {
                "other_jid": self.peer.full()
            }
            d = client.encryption.stop(self.peer, NS_OTR)
            d.addCallback(self.stopCb, feedback=feedback)
            d.addErrback(self.stopEb)
            return
        elif state == potr.context.STATE_ENCRYPTED:
            client.encryption.start(self.peer, NS_OTR)
            try:
                trusted = self.isTrusted()
            except TypeError:
                trusted = False
            trusted_str = _(u"trusted") if trusted else _(u"untrusted")

            if old_state == potr.context.STATE_ENCRYPTED:
                feedback = D_(
                    u"{trusted} OTR conversation with {other_jid} REFRESHED"
                ).format(trusted=trusted_str, other_jid=self.peer.full())
            else:
                feedback = D_(
                    u"{trusted} encrypted OTR conversation started with {other_jid}\n"
                    u"{extra_info}"
                ).format(
                    trusted=trusted_str,
                    other_jid=self.peer.full(),
                    extra_info=NO_ADV_FEATURES,
                )
            self.host.bridge.otrState(
                OTR_STATE_ENCRYPTED, self.peer.full(), client.profile
            )
        elif state == potr.context.STATE_FINISHED:
            feedback = D_(u"OTR conversation with {other_jid} is FINISHED").format(
                other_jid=self.peer.full()
            )
            d = client.encryption.stop(self.peer, NS_OTR)
            d.addCallback(self.stopCb, feedback=feedback)
            d.addErrback(self.stopEb)
            return
        else:
            log.error(D_(u"Unknown OTR state"))
            return

        client.feedback(self.peer, feedback)

    def disconnect(self):
        """Disconnect the session."""
        if self.state != potr.context.STATE_PLAINTEXT:
            super(Context, self).disconnect()

    def finish(self):
        """Finish the session

        avoid to send any message but the user still has to end the session himself.
        """
        if self.state == potr.context.STATE_ENCRYPTED:
            self.processTLVs([potr.proto.DisconnectTLV()])


class Account(potr.context.Account):
    # TODO: manage trusted keys: if a fingerprint is not used anymore,
    #       we have no way to remove it from database yet (same thing for a
    #       correspondent jid)
    # TODO: manage explicit message encryption

    def __init__(self, host, client):
        log.debug(u"new account: %s" % client.jid)
        if not client.jid.resource:
            log.warning("Account created without resource")
        super(Account, self).__init__(unicode(client.jid), "xmpp", 1024)
        self.host = host
        self.client = client

    def loadPrivkey(self):
        log.debug(u"loadPrivkey")
        return self.privkey

    def savePrivkey(self):
        log.debug(u"savePrivkey")
        if self.privkey is None:
            raise exceptions.InternalError(_(u"Save is called but privkey is None !"))
        priv_key = self.privkey.serializePrivateKey().encode("hex")
        d = self.host.memory.encryptValue(priv_key, self.client.profile)

        def save_encrypted_key(encrypted_priv_key):
            self.client._otr_data[PRIVATE_KEY] = encrypted_priv_key

        d.addCallback(save_encrypted_key)

    def loadTrusts(self):
        trust_data = self.client._otr_data.get("trust", {})
        for jid_, jid_data in trust_data.iteritems():
            for fingerprint, trust_level in jid_data.iteritems():
                log.debug(
                    u'setting trust for {jid}: [{fingerprint}] = "{trust_level}"'.format(
                        jid=jid_, fingerprint=fingerprint, trust_level=trust_level
                    )
                )
                self.trusts.setdefault(jid.JID(jid_), {})[fingerprint] = trust_level

    def saveTrusts(self):
        log.debug(u"saving trusts for {profile}".format(profile=self.client.profile))
        log.debug(u"trusts = {}".format(self.client._otr_data["trust"]))
        self.client._otr_data.force("trust")

    def setTrust(self, other_jid, fingerprint, trustLevel):
        try:
            trust_data = self.client._otr_data["trust"]
        except KeyError:
            trust_data = {}
            self.client._otr_data["trust"] = trust_data
        jid_data = trust_data.setdefault(other_jid.full(), {})
        jid_data[fingerprint] = trustLevel
        super(Account, self).setTrust(other_jid, fingerprint, trustLevel)


class ContextManager(object):
    def __init__(self, parent, client):
        self.parent = parent
        self.account = Account(parent.host, client)
        self.contexts = {}

    @property
    def host(self):
        return self.parent.host

    def startContext(self, other_jid):
        assert isinstance(other_jid, jid.JID)
        context = self.contexts.setdefault(
            other_jid, Context(self, other_jid)
        )
        return context

    def getContextForUser(self, other):
        log.debug(u"getContextForUser [%s]" % other)
        if not other.resource:
            log.warning(u"getContextForUser called with a bare jid: %s" % other.full())
        return self.startContext(other)


class OTR(object):

    def __init__(self, host):
        log.info(_(u"OTR plugin initialization"))
        self.host = host
        self.context_managers = {}
        self.skipped_profiles = (
            set()
        )  #  FIXME: OTR should not be skipped per profile, this need to be refactored
        self._p_hints = host.plugins[u"XEP-0334"]
        self._p_carbons = host.plugins[u"XEP-0280"]
        host.trigger.add("MessageReceived", self.MessageReceivedTrigger, priority=100000)
        host.trigger.add("sendMessage", self.sendMessageTrigger, priority=100000)
        host.trigger.add("sendMessageData", self._sendMessageDataTrigger)
        host.bridge.addMethod(
            "skipOTR", ".plugin", in_sign="s", out_sign="", method=self._skipOTR
        )  # FIXME: must be removed, must be done on per-message basis
        host.bridge.addSignal(
            "otrState", ".plugin", signature="sss"
        )  # args: state, destinee_jid, profile
        # XXX: menus are disabled in favor to the new more generic encryption menu
        #      there are let here commented for a little while as a reference
        # host.importMenu(
        #     (OTR_MENU, D_(u"Start/Refresh")),
        #     self._otrStartRefresh,
        #     security_limit=0,
        #     help_string=D_(u"Start or refresh an OTR session"),
        #     type_=C.MENU_SINGLE,
        # )
        # host.importMenu(
        #     (OTR_MENU, D_(u"End session")),
        #     self._otrSessionEnd,
        #     security_limit=0,
        #     help_string=D_(u"Finish an OTR session"),
        #     type_=C.MENU_SINGLE,
        # )
        # host.importMenu(
        #     (OTR_MENU, D_(u"Authenticate")),
        #     self._otrAuthenticate,
        #     security_limit=0,
        #     help_string=D_(u"Authenticate user/see your fingerprint"),
        #     type_=C.MENU_SINGLE,
        # )
        # host.importMenu(
        #     (OTR_MENU, D_(u"Drop private key")),
        #     self._dropPrivKey,
        #     security_limit=0,
        #     type_=C.MENU_SINGLE,
        # )
        host.trigger.add("presence_received", self._presenceReceivedTrigger)
        self.host.registerEncryptionPlugin(self, u"OTR", NS_OTR, directed=True)

    def _skipOTR(self, profile):
        """Tell the backend to not handle OTR for this profile.

        @param profile (str): %(doc_profile)s
        """
        # FIXME: should not be done per profile but per message, using extra data
        #        for message received, profile wide hook may be need, but client
        #        should be used anyway instead of a class attribute
        self.skipped_profiles.add(profile)

    @defer.inlineCallbacks
    def profileConnecting(self, client):
        if client.profile in self.skipped_profiles:
            return
        ctxMng = client._otr_context_manager = ContextManager(self, client)
        client._otr_data = persistent.PersistentBinaryDict(NS_OTR, client.profile)
        yield client._otr_data.load()
        encrypted_priv_key = client._otr_data.get(PRIVATE_KEY, None)
        if encrypted_priv_key is not None:
            priv_key = yield self.host.memory.decryptValue(
                encrypted_priv_key, client.profile
            )
            ctxMng.account.privkey = potr.crypt.PK.parsePrivateKey(
                priv_key.decode("hex")
            )[0]
        else:
            ctxMng.account.privkey = None
        ctxMng.account.loadTrusts()

    def profileDisconnected(self, client):
        if client.profile in self.skipped_profiles:
            self.skipped_profiles.remove(client.profile)
            return
        for context in client._otr_context_manager.contexts.values():
            context.disconnect()
        del client._otr_context_manager

    # encryption plugin methods

    def startEncryption(self, client, entity_jid):
        self.startRefresh(client, entity_jid)

    def stopEncryption(self, client, entity_jid):
        self.endSession(client, entity_jid)

    def getTrustUI(self, client, entity_jid):
        if not entity_jid.resource:
            entity_jid.resource = self.host.memory.getMainResource(
                client, entity_jid
            )  # FIXME: temporary and unsecure, must be changed when frontends
               #        are refactored
        ctxMng = client._otr_context_manager
        otrctx = ctxMng.getContextForUser(entity_jid)
        priv_key = ctxMng.account.privkey

        if priv_key is None:
            # we have no private key yet
            dialog = xml_tools.XMLUI(
                C.XMLUI_DIALOG,
                dialog_opt={
                    C.XMLUI_DATA_TYPE: C.XMLUI_DIALOG_MESSAGE,
                    C.XMLUI_DATA_MESS: _(
                        u"You have no private key yet, start an OTR conversation to "
                        u"have one"
                    ),
                    C.XMLUI_DATA_LVL: C.XMLUI_DATA_LVL_WARNING,
                },
                title=_(u"No private key"),
            )
            return dialog

        other_fingerprint = otrctx.getCurrentKey()

        if other_fingerprint is None:
            # we have a private key, but not the fingerprint of our correspondent
            dialog = xml_tools.XMLUI(
                C.XMLUI_DIALOG,
                dialog_opt={
                    C.XMLUI_DATA_TYPE: C.XMLUI_DIALOG_MESSAGE,
                    C.XMLUI_DATA_MESS: _(
                        u"Your fingerprint is:\n{fingerprint}\n\n"
                        u"Start an OTR conversation to have your correspondent one."
                    ).format(fingerprint=priv_key),
                    C.XMLUI_DATA_LVL: C.XMLUI_DATA_LVL_INFO,
                },
                title=_(u"Fingerprint"),
            )
            return dialog

        def setTrust(raw_data, profile):
            if xml_tools.isXMLUICancelled(raw_data):
                return {}
            # This method is called when authentication form is submited
            data = xml_tools.XMLUIResult2DataFormResult(raw_data)
            if data["match"] == "yes":
                otrctx.setCurrentTrust(OTR_STATE_TRUSTED)
                note_msg = _(u"Your correspondent {correspondent} is now TRUSTED")
                self.host.bridge.otrState(
                    OTR_STATE_TRUSTED, entity_jid.full(), client.profile
                )
            else:
                otrctx.setCurrentTrust("")
                note_msg = _(u"Your correspondent {correspondent} is now UNTRUSTED")
                self.host.bridge.otrState(
                    OTR_STATE_UNTRUSTED, entity_jid.full(), client.profile
                )
            note = xml_tools.XMLUI(
                C.XMLUI_DIALOG,
                dialog_opt={
                    C.XMLUI_DATA_TYPE: C.XMLUI_DIALOG_NOTE,
                    C.XMLUI_DATA_MESS: note_msg.format(correspondent=otrctx.peer),
                },
            )
            return {"xmlui": note.toXml()}

        submit_id = self.host.registerCallback(setTrust, with_data=True, one_shot=True)
        trusted = otrctx.isTrusted()

        xmlui = xml_tools.XMLUI(
            C.XMLUI_FORM,
            title=_(u"Authentication ({entity_jid})").format(entity_jid=entity_jid.full()),
            submit_id=submit_id,
        )
        xmlui.addText(_(AUTH_TXT))
        xmlui.addDivider()
        xmlui.addText(
            D_(u"Your own fingerprint is:\n{fingerprint}").format(fingerprint=priv_key)
        )
        xmlui.addText(
            D_(u"Your correspondent fingerprint should be:\n{fingerprint}").format(
                fingerprint=other_fingerprint
            )
        )
        xmlui.addDivider("blank")
        xmlui.changeContainer("pairs")
        xmlui.addLabel(D_(u"Is your correspondent fingerprint the same as here ?"))
        xmlui.addList(
            "match", [("yes", _("yes")), ("no", _("no"))], ["yes" if trusted else "no"]
        )
        return xmlui

    def _otrStartRefresh(self, menu_data, profile):
        """Start or refresh an OTR session

        @param menu_data: %(menu_data)s
        @param profile: %(doc_profile)s
        """
        client = self.host.getClient(profile)
        try:
            to_jid = jid.JID(menu_data["jid"])
        except KeyError:
            log.error(_(u"jid key is not present !"))
            return defer.fail(exceptions.DataError)
        self.startRefresh(client, to_jid)
        return {}

    def startRefresh(self, client, to_jid):
        """Start or refresh an OTR session

        @param to_jid(jid.JID): jid to start encrypted session with
        """
        encrypted_session = client.encryption.getSession(to_jid.userhostJID())
        if encrypted_session and encrypted_session[u'plugin'].namespace != NS_OTR:
            raise exceptions.ConflictError(_(
                u"Can't start an OTR session, there is already an encrypted session "
                u"with {name}").format(name=encrypted_session[u'plugin'].name))
        if not to_jid.resource:
            to_jid.resource = self.host.memory.getMainResource(
                client, to_jid
            )  # FIXME: temporary and unsecure, must be changed when frontends
               #        are refactored
        otrctx = client._otr_context_manager.getContextForUser(to_jid)
        query = otrctx.sendMessage(0, "?OTRv?")
        otrctx.inject(query)

    def _otrSessionEnd(self, menu_data, profile):
        """End an OTR session

        @param menu_data: %(menu_data)s
        @param profile: %(doc_profile)s
        """
        client = self.host.getClient(profile)
        try:
            to_jid = jid.JID(menu_data["jid"])
        except KeyError:
            log.error(_(u"jid key is not present !"))
            return defer.fail(exceptions.DataError)
        self.endSession(client, to_jid)
        return {}

    def endSession(self, client, to_jid):
        """End an OTR session"""
        if not to_jid.resource:
            to_jid.resource = self.host.memory.getMainResource(
                client, to_jid
            )  # FIXME: temporary and unsecure, must be changed when frontends
               #        are refactored
        otrctx = client._otr_context_manager.getContextForUser(to_jid)
        otrctx.disconnect()
        return {}

    def _otrAuthenticate(self, menu_data, profile):
        """End an OTR session

        @param menu_data: %(menu_data)s
        @param profile: %(doc_profile)s
        """
        client = self.host.getClient(profile)
        try:
            to_jid = jid.JID(menu_data["jid"])
        except KeyError:
            log.error(_(u"jid key is not present !"))
            return defer.fail(exceptions.DataError)
        return self.authenticate(client, to_jid)

    def authenticate(self, client, to_jid):
        """Authenticate other user and see our own fingerprint"""
        xmlui = self.getTrustUI(client, to_jid)
        return {"xmlui": xmlui.toXml()}

    def _dropPrivKey(self, menu_data, profile):
        """Drop our private Key

        @param menu_data: %(menu_data)s
        @param profile: %(doc_profile)s
        """
        client = self.host.getClient(profile)
        try:
            to_jid = jid.JID(menu_data["jid"])
            if not to_jid.resource:
                to_jid.resource = self.host.memory.getMainResource(
                    client, to_jid
                )  # FIXME: temporary and unsecure, must be changed when frontends
                   #        are refactored
        except KeyError:
            log.error(_(u"jid key is not present !"))
            return defer.fail(exceptions.DataError)

        ctxMng = client._otr_context_manager
        if ctxMng.account.privkey is None:
            return {
                "xmlui": xml_tools.note(_(u"You don't have a private key yet !")).toXml()
            }

        def dropKey(data, profile):
            if C.bool(data["answer"]):
                # we end all sessions
                for context in ctxMng.contexts.values():
                    context.disconnect()
                ctxMng.account.privkey = None
                ctxMng.account.getPrivkey()  # as account.privkey is None, getPrivkey
                                             # will generate a new key, and save it
                return {
                    "xmlui": xml_tools.note(
                        D_(u"Your private key has been dropped")
                    ).toXml()
                }
            return {}

        submit_id = self.host.registerCallback(dropKey, with_data=True, one_shot=True)

        confirm = xml_tools.XMLUI(
            C.XMLUI_DIALOG,
            title=_(u"Confirm private key drop"),
            dialog_opt={"type": C.XMLUI_DIALOG_CONFIRM, "message": _(DROP_TXT)},
            submit_id=submit_id,
        )
        return {"xmlui": confirm.toXml()}

    def _receivedTreatment(self, data, client):
        from_jid = data["from"]
        log.debug(u"_receivedTreatment [from_jid = %s]" % from_jid)
        otrctx = client._otr_context_manager.getContextForUser(from_jid)

        try:
            message = (
                data["message"].itervalues().next()
            )  # FIXME: Q&D fix for message refactoring, message is now a dict
            res = otrctx.receiveMessage(message.encode("utf-8"))
        except potr.context.UnencryptedMessage:
            encrypted = False
            if otrctx.state == potr.context.STATE_ENCRYPTED:
                log.warning(
                    u"Received unencrypted message in an encrypted context (from {jid})"
                    .format(jid=from_jid.full())
                )

                feedback = (
                    D_(
                        u"WARNING: received unencrypted data in a supposedly encrypted "
                        u"context"
                    ),
                )
                client.feedback(from_jid, feedback)
        except potr.context.NotEncryptedError:
            msg = D_(u"WARNING: received OTR encrypted data in an unencrypted context")
            log.warning(msg)
            feedback = msg
            client.feedback(from_jid, msg)
            raise failure.Failure(exceptions.CancelError(msg))
        except potr.context.ErrorReceived as e:
            msg = D_(u"WARNING: received OTR error message: {msg}".format(msg=e))
            log.warning(msg)
            feedback = msg
            client.feedback(from_jid, msg)
            raise failure.Failure(exceptions.CancelError(msg))
        except potr.crypt.InvalidParameterError as e:
            msg = D_(u"Error while trying de decrypt OTR message: {msg}".format(msg=e))
            log.warning(msg)
            feedback = msg
            client.feedback(from_jid, msg)
            raise failure.Failure(exceptions.CancelError(msg))
        except StopIteration:
            return data
        else:
            encrypted = True

        if encrypted:
            if res[0] != None:
                # decrypted messages handling.
                # receiveMessage() will return a tuple,
                # the first part of which will be the decrypted message
                data["message"] = {
                    "": res[0].decode("utf-8")
                }  # FIXME: Q&D fix for message refactoring, message is now a dict
                try:
                    # we want to keep message in history, even if no store is
                    # requested in message hints
                    del data[u"history"]
                except KeyError:
                    pass
                # TODO: add skip history as an option, but by default we don't skip it
                # data[u'history'] = C.HISTORY_SKIP # we send the decrypted message to
                                                    # frontends, but we don't want it in
                                                    # history
            else:
                raise failure.Failure(
                    exceptions.CancelError("Cancelled by OTR")
                )  # no message at all (no history, no signal)

            client.encryption.markAsEncrypted(data)
            trusted = otrctx.isTrusted()

            if trusted:
                client.encryption.markAsTrusted(data)
            else:
                client.encryption.markAsUntrusted(data)

        return data

    def _receivedTreatmentForSkippedProfiles(self, data):
        """This profile must be skipped because the frontend manages OTR itself,

        but we still need to check if the message must be stored in history or not
        """
        #  XXX: FIXME: this should not be done on a per-profile basis, but  per-message
        try:
            message = (
                data["message"].itervalues().next().encode("utf-8")
            )  # FIXME: Q&D fix for message refactoring, message is now a dict
        except StopIteration:
            return data
        if message.startswith(potr.proto.OTRTAG):
            #  FIXME: it may be better to cancel the message and send it direclty to
            #         bridge
            #        this is used by Libervia, but this may send garbage message to
            #        other frontends
            #        if they are used at the same time as Libervia.
            #        Hard to avoid with decryption on Libervia though.
            data[u"history"] = C.HISTORY_SKIP
        return data

    def MessageReceivedTrigger(self, client, message_elt, post_treat):
        if message_elt.getAttribute("type") == C.MESS_TYPE_GROUPCHAT:
            # OTR is not possible in group chats
            return True
        from_jid = jid.JID(message_elt['from'])
        if not from_jid.resource or from_jid.userhostJID() == client.jid.userhostJID():
            # OTR is only usable when resources are present
            return True
        if client.profile in self.skipped_profiles:
            post_treat.addCallback(self._receivedTreatmentForSkippedProfiles)
        else:
            post_treat.addCallback(self._receivedTreatment, client)
        return True

    def _sendMessageDataTrigger(self, client, mess_data):
        encryption = mess_data.get(C.MESS_KEY_ENCRYPTION)
        if encryption is None or encryption['plugin'].namespace != NS_OTR:
            return
        to_jid = mess_data['to']
        if not to_jid.resource:
            to_jid.resource = self.host.memory.getMainResource(
                client, to_jid
            )  # FIXME: temporary and unsecure, must be changed when frontends
        otrctx = client._otr_context_manager.getContextForUser(to_jid)
        message_elt = mess_data["xml"]
        if otrctx.state == potr.context.STATE_ENCRYPTED:
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
            else:
                self._p_carbons.setPrivate(message_elt)
                self._p_hints.addHintElements(message_elt, [
                    self._p_hints.HINT_NO_COPY,
                    self._p_hints.HINT_NO_PERMANENT_STORE])
                otrctx.sendMessage(0, unicode(body).encode("utf-8"), appdata=mess_data)
        else:
            feedback = D_(
                u"Your message was not sent because your correspondent closed the "
                u"encrypted conversation on his/her side. "
                u"Either close your own side, or refresh the session."
            )
            log.warning(_(u"Message discarded because closed encryption channel"))
            client.feedback(to_jid, feedback)
            raise failure.Failure(exceptions.CancelError(u"Cancelled by OTR plugin"))

    def sendMessageTrigger(self, client, mess_data, pre_xml_treatments,
                           post_xml_treatments):
        if mess_data["type"] == "groupchat":
            return True

        if client.profile in self.skipped_profiles:
            #  FIXME: should not be done on a per-profile basis
            return True

        to_jid = copy.copy(mess_data["to"])
        if client.encryption.getSession(to_jid.userhostJID()):
            # there is already an encrypted session with this entity
            return True

        if not to_jid.resource:
            to_jid.resource = self.host.memory.getMainResource(
                client, to_jid
            )  # FIXME: full jid may not be known

        otrctx = client._otr_context_manager.getContextForUser(to_jid)

        if otrctx.state != potr.context.STATE_PLAINTEXT:
            client.encryption.start(to_jid, NS_OTR)
            client.encryption.setEncryptionFlag(mess_data)
            if not mess_data["to"].resource:
                # if not resource was given, we force it here
                mess_data["to"] = to_jid
        return True

    def _presenceReceivedTrigger(self, client, entity, show, priority, statuses):
        if show != C.PRESENCE_UNAVAILABLE:
            return True
        if not entity.resource:
            try:
                entity.resource = self.host.memory.getMainResource(
                    client, entity
                )  # FIXME: temporary and unsecure, must be changed when frontends
                   #        are refactored
            except exceptions.UnknownEntityError:
                return True  #  entity was not connected
        if entity in client._otr_context_manager.contexts:
            otrctx = client._otr_context_manager.getContextForUser(entity)
            otrctx.disconnect()
        return True
