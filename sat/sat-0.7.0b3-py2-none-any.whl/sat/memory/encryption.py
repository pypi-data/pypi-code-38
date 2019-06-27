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

from functools import partial
from sat.core.i18n import D_, _
from sat.core.constants import Const as C
from sat.core import exceptions
from collections import namedtuple
from sat.core.log import getLogger
from sat.tools.common import data_format
from twisted.words.protocols.jabber import jid
from twisted.internet import defer
from twisted.python import failure
import copy
log = getLogger(__name__)

log = getLogger(__name__)

EncryptionPlugin = namedtuple("EncryptionPlugin", ("instance",
                                                   "name",
                                                   "namespace",
                                                   "priority",
                                                   "directed"))


class EncryptionHandler(object):
    """Class to handle encryption sessions for a client"""
    plugins = []  # plugin able to encrypt messages

    def __init__(self, client):
        self.client = client
        self._sessions = {}  # bare_jid ==> encryption_data

    @property
    def host(self):
        return self.client.host_app

    @classmethod
    def registerPlugin(cls, plg_instance, name, namespace, priority=0, directed=False):
        """Register a plugin handling an encryption algorithm

        @param plg_instance(object): instance of the plugin
            it must have the following methods:
                - getTrustUI(entity): return a XMLUI for trust management
                    entity(jid.JID): entity to manage
                    The returned XMLUI must be a form
            if may have the following methods:
                - startEncryption(entity): start encrypted session
                    entity(jid.JID): entity to start encrypted session with
                - stopEncryption(entity): start encrypted session
                    entity(jid.JID): entity to stop encrypted session with
            if they don't exists, those 2 methods will be ignored.

        @param name(unicode): human readable name of the encryption algorithm
        @param namespace(unicode): namespace of the encryption algorithm
        @param priority(int): priority of this plugin to encrypt an message when not
            selected manually
        @param directed(bool): True if this plugin is directed (if it works with one
                               device only at a time)
        """
        existing_ns = set()
        existing_names = set()
        for p in cls.plugins:
            existing_ns.add(p.namespace.lower())
            existing_names.add(p.name.lower())
        if namespace.lower() in existing_ns:
            raise exceptions.ConflictError("A plugin with this namespace already exists!")
        if name.lower() in existing_names:
            raise exceptions.ConflictError("A plugin with this name already exists!")
        plugin = EncryptionPlugin(
            instance=plg_instance,
            name=name,
            namespace=namespace,
            priority=priority,
            directed=directed)
        cls.plugins.append(plugin)
        cls.plugins.sort(key=lambda p: p.priority)
        log.info(_(u"Encryption plugin registered: {name}").format(name=name))

    @classmethod
    def getPlugins(cls):
        return cls.plugins

    @classmethod
    def getPlugin(cls, namespace):
        try:
            return next(p for p in cls.plugins if p.namespace == namespace)
        except StopIteration:
            raise exceptions.NotFound(_(
                u"Can't find requested encryption plugin: {namespace}").format(
                    namespace=namespace))

    @classmethod
    def getNamespaces(cls):
        """Get available plugin namespaces"""
        return {p.namespace for p in cls.getPlugins()}

    @classmethod
    def getNSFromName(cls, name):
        """Retrieve plugin namespace from its name

        @param name(unicode): name of the plugin (case insensitive)
        @return (unicode): namespace of the plugin
        @raise exceptions.NotFound: there is not encryption plugin of this name
        """
        for p in cls.plugins:
            if p.name.lower() == name.lower():
                return p.namespace
        raise exceptions.NotFound(_(
            u"Can't find a plugin with the name \"{name}\".".format(
                name=name)))

    def getBridgeData(self, session):
        """Retrieve session data serialized for bridge.

        @param session(dict): encryption session
        @return (unicode): serialized data for bridge
        """
        if session is None:
            return u''
        plugin = session[u'plugin']
        bridge_data = {'name': plugin.name,
                       'namespace': plugin.namespace}
        if u'directed_devices' in session:
            bridge_data[u'directed_devices'] = session[u'directed_devices']

        return data_format.serialise(bridge_data)

    def _startEncryption(self, plugin, entity):
        """Start encryption with a plugin

        This method must be called just before adding a plugin session.
        StartEncryptionn method of plugin will be called if it exists.
        """
        try:
            start_encryption = plugin.instance.startEncryption
        except AttributeError:
            log.debug(u"No startEncryption method found for {plugin}".format(
                plugin = plugin.namespace))
            return defer.succeed(None)
        else:
            # we copy entity to avoid having the resource changed by stop_encryption
            return defer.maybeDeferred(start_encryption, self.client, copy.copy(entity))

    def _stopEncryption(self, plugin, entity):
        """Stop encryption with a plugin

        This method must be called just before removing a plugin session.
        StopEncryptionn method of plugin will be called if it exists.
        """
        try:
            stop_encryption = plugin.instance.stopEncryption
        except AttributeError:
            log.debug(u"No stopEncryption method found for {plugin}".format(
                plugin = plugin.namespace))
            return defer.succeed(None)
        else:
            # we copy entity to avoid having the resource changed by stop_encryption
            return defer.maybeDeferred(stop_encryption, self.client, copy.copy(entity))

    @defer.inlineCallbacks
    def start(self, entity, namespace=None, replace=False):
        """Start an encryption session with an entity

        @param entity(jid.JID): entity to start an encryption session with
            must be bare jid is the algorithm encrypt for all devices
        @param namespace(unicode, None): namespace of the encryption algorithm
            to use.
            None to select automatically an algorithm
        @param replace(bool): if True and an encrypted session already exists,
            it will be replaced by the new one
        """
        if not self.plugins:
            raise exceptions.NotFound(_(u"No encryption plugin is registered, "
                                        u"an encryption session can't be started"))

        if namespace is None:
            plugin = self.plugins[0]
        else:
            plugin = self.getPlugin(namespace)

        bare_jid = entity.userhostJID()
        if bare_jid in self._sessions:
            # we have already an encryption session with this contact
            former_plugin = self._sessions[bare_jid][u"plugin"]
            if former_plugin.namespace == namespace:
                log.info(_(u"Session with {bare_jid} is already encrypted with {name}. "
                           u"Nothing to do.").format(
                               bare_jid=bare_jid, name=former_plugin.name))
                return

            if replace:
                # there is a conflict, but replacement is requested
                # so we stop previous encryption to use new one
                del self._sessions[bare_jid]
                yield self._stopEncryption(former_plugin, entity)
            else:
                msg = (_(u"Session with {bare_jid} is already encrypted with {name}. "
                         u"Please stop encryption session before changing algorithm.")
                       .format(bare_jid=bare_jid, name=plugin.name))
                log.warning(msg)
                raise exceptions.ConflictError(msg)

        data = {"plugin": plugin}
        if plugin.directed:
            if not entity.resource:
                entity.resource = self.host.memory.getMainResource(self.client, entity)
                if not entity.resource:
                    raise exceptions.NotFound(
                        _(u"No resource found for {destinee}, can't encrypt with {name}")
                        .format(destinee=entity.full(), name=plugin.name))
                log.info(_(u"No resource specified to encrypt with {name}, using "
                           u"{destinee}.").format(destinee=entity.full(),
                                                  name=plugin.name))
            # indicate that we encrypt only for some devices
            directed_devices = data[u'directed_devices'] = [entity.resource]
        elif entity.resource:
            raise ValueError(_(u"{name} encryption must be used with bare jids."))

        yield self._startEncryption(plugin, entity)
        self._sessions[entity.userhostJID()] = data
        log.info(_(u"Encryption session has been set for {entity_jid} with "
                   u"{encryption_name}").format(
                   entity_jid=entity.full(), encryption_name=plugin.name))
        self.host.bridge.messageEncryptionStarted(
            entity.full(),
            self.getBridgeData(data),
            self.client.profile)
        msg = D_(u"Encryption session started: your messages with {destinee} are "
                 u"now end to end encrypted using {name} algorithm.").format(
                 destinee=entity.full(), name=plugin.name)
        directed_devices = data.get(u'directed_devices')
        if directed_devices:
            msg += u"\n" + D_(u"Message are encrypted only for {nb_devices} device(s): "
                              u"{devices_list}.").format(
                              nb_devices=len(directed_devices),
                              devices_list = u', '.join(directed_devices))

        self.client.feedback(bare_jid, msg)

    @defer.inlineCallbacks
    def stop(self, entity, namespace=None):
        """Stop an encryption session with an entity

        @param entity(jid.JID): entity with who the encryption session must be stopped
            must be bare jid if the algorithm encrypt for all devices
        @param namespace(unicode): namespace of the session to stop
            when specified, used to check we stop the right encryption session
        """
        session = self.getSession(entity.userhostJID())
        if not session:
            raise failure.Failure(
                exceptions.NotFound(_(u"There is no encryption session with this "
                                      u"entity.")))
        plugin = session['plugin']
        if namespace is not None and plugin.namespace != namespace:
            raise exceptions.InternalError(_(
                u"The encryption session is not run with the expected plugin: encrypted "
                u"with {current_name} and was expecting {expected_name}").format(
                current_name=session[u'plugin'].namespace,
                expected_name=namespace))
        if entity.resource:
            try:
                directed_devices = session[u'directed_devices']
            except KeyError:
                raise exceptions.NotFound(_(
                    u"There is a session for the whole entity (i.e. all devices of the "
                    u"entity), not a directed one. Please use bare jid if you want to "
                    u"stop the whole encryption with this entity."))

            try:
                directed_devices.remove(entity.resource)
            except ValueError:
                raise exceptions.NotFound(_(u"There is no directed session with this "
                                            u"entity."))
            else:
                if not directed_devices:
                    # if we have no more directed device sessions,
                    # we stop the whole session
                    # see comment below for deleting session before stopping encryption
                    del self._sessions[entity.userhostJID()]
                    yield self._stopEncryption(plugin, entity)
        else:
            # plugin's stopEncryption may call stop again (that's the case with OTR)
            # so we need to remove plugin from session before calling self._stopEncryption
            del self._sessions[entity.userhostJID()]
            yield self._stopEncryption(plugin, entity)

        log.info(_(u"encryption session stopped with entity {entity}").format(
            entity=entity.full()))
        self.host.bridge.messageEncryptionStopped(
            entity.full(),
            {'name': plugin.name,
             'namespace': plugin.namespace,
            },
            self.client.profile)
        msg = D_(u"Encryption session finished: your messages with {destinee} are "
                 u"NOT end to end encrypted anymore.\nYour server administrators or "
                 u"{destinee} server administrators will be able to read them.").format(
                 destinee=entity.full())

        self.client.feedback(entity, msg)

    def getSession(self, entity):
        """Get encryption session for this contact

        @param entity(jid.JID): get the session for this entity
            must be a bare jid
        @return (dict, None): encryption session data
            None if there is not encryption for this session with this jid
        """
        if entity.resource:
            raise ValueError(u"Full jid given when expecting bare jid")
        return self._sessions.get(entity)

    def getTrustUI(self, entity_jid, namespace=None):
        """Retrieve encryption UI

        @param entity_jid(jid.JID): get the UI for this entity
            must be a bare jid
        @param namespace(unicode): namespace of the algorithm to manage
            if None use current algorithm
        @return D(xmlui): XMLUI for trust management
            the xmlui is a form
            None if there is not encryption for this session with this jid
        @raise exceptions.NotFound: no algorithm/plugin found
        @raise NotImplementedError: plugin doesn't handle UI management
        """
        if namespace is None:
            session = self.getSession(entity_jid)
            if not session:
                raise exceptions.NotFound(
                    u"No encryption session currently active for {entity_jid}"
                    .format(entity_jid=entity_jid.full()))
            plugin = session['plugin']
        else:
            plugin = self.getPlugin(namespace)
        try:
            get_trust_ui = plugin.instance.getTrustUI
        except AttributeError:
            raise NotImplementedError(
                u"Encryption plugin doesn't handle trust management UI")
        else:
            return defer.maybeDeferred(get_trust_ui, self.client, entity_jid)

    ## Menus ##

    @classmethod
    def _importMenus(cls, host):
        host.importMenu(
             (D_(u"Encryption"), D_(u"unencrypted (plain text)")),
             partial(cls._onMenuUnencrypted, host=host),
             security_limit=0,
             help_string=D_(u"End encrypted session"),
             type_=C.MENU_SINGLE,
        )
        for plg in cls.getPlugins():
            host.importMenu(
                 (D_(u"Encryption"), plg.name),
                 partial(cls._onMenuName, host=host, plg=plg),
                 security_limit=0,
                 help_string=D_(u"Start {name} session").format(name=plg.name),
                 type_=C.MENU_SINGLE,
            )
            host.importMenu(
                 (D_(u"Encryption"), D_(u"⛨ {name} trust").format(name=plg.name)),
                 partial(cls._onMenuTrust, host=host, plg=plg),
                 security_limit=0,
                 help_string=D_(u"Manage {name} trust").format(name=plg.name),
                 type_=C.MENU_SINGLE,
            )

    @classmethod
    def _onMenuUnencrypted(cls, data, host, profile):
        client = host.getClient(profile)
        peer_jid = jid.JID(data[u'jid']).userhostJID()
        d = client.encryption.stop(peer_jid)
        d.addCallback(lambda __: {})
        return d

    @classmethod
    def _onMenuName(cls, data, host, plg, profile):
        client = host.getClient(profile)
        peer_jid = jid.JID(data[u'jid'])
        if not plg.directed:
            peer_jid = peer_jid.userhostJID()
        d = client.encryption.start(peer_jid, plg.namespace, replace=True)
        d.addCallback(lambda __: {})
        return d

    @classmethod
    @defer.inlineCallbacks
    def _onMenuTrust(cls, data, host, plg, profile):
        client = host.getClient(profile)
        peer_jid = jid.JID(data[u'jid']).userhostJID()
        ui = yield client.encryption.getTrustUI(peer_jid, plg.namespace)
        defer.returnValue({u'xmlui': ui.toXml()})

    ## Triggers ##

    def setEncryptionFlag(self, mess_data):
        """Set "encryption" key in mess_data if session with destinee is encrypted"""

        if mess_data["type"] == "groupchat":
            # FIXME: to change when group chat encryption will be handled
            return

        to_jid = mess_data['to']
        encryption = self._sessions.get(to_jid.userhostJID())
        if encryption is not None:
            mess_data[C.MESS_KEY_ENCRYPTION] = encryption

    ## Misc ##

    def markAsEncrypted(self, mess_data):
        """Helper method to mark a message as having been e2e encrypted.

        This should be used in the post_treat workflow of MessageReceived trigger of
        the plugin
        @param mess_data(dict): message data as used in post treat workflow
        """
        mess_data[C.MESS_KEY_ENCRYPTED] = True
        return mess_data

    def markAsTrusted(self, mess_data):
        """Helper methor to mark a message as sent from a trusted entity.

        This should be used in the post_treat workflow of MessageReceived trigger of
        the plugin
        @param mess_data(dict): message data as used in post treat workflow
        """
        mess_data[C.MESS_KEY_TRUSTED] = True
        return mess_data

    def markAsUntrusted(self, mess_data):
        """Helper methor to mark a message as sent from an untrusted entity.

        This should be used in the post_treat workflow of MessageReceived trigger of
        the plugin
        @param mess_data(dict): message data as used in post treat workflow
        """
        mess_data['trusted'] = False
        return mess_data
