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


    def actionsGet(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("actionsGet", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def addContact(self, entity_jid, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("addContact", entity_jid, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def asyncDeleteProfile(self, profile, callback=None, errback=None):
        d = self.root.callRemote("asyncDeleteProfile", profile)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def asyncGetParamA(self, name, category, attribute="value", security_limit=-1, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("asyncGetParamA", name, category, attribute, security_limit, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def asyncGetParamsValuesFromCategory(self, category, security_limit=-1, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("asyncGetParamsValuesFromCategory", category, security_limit, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def connect(self, profile_key="@DEFAULT@", password='', options={}, callback=None, errback=None):
        d = self.root.callRemote("connect", profile_key, password, options)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def delContact(self, entity_jid, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("delContact", entity_jid, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def discoFindByFeatures(self, namespaces, identities, bare_jid=False, service=True, roster=True, own_jid=True, local_device=False, profile_key=u"@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("discoFindByFeatures", namespaces, identities, bare_jid, service, roster, own_jid, local_device, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def discoInfos(self, entity_jid, node=u'', use_cache=True, profile_key=u"@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("discoInfos", entity_jid, node, use_cache, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def discoItems(self, entity_jid, node=u'', use_cache=True, profile_key=u"@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("discoItems", entity_jid, node, use_cache, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def disconnect(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("disconnect", profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def encryptionNamespaceGet(self, arg_0, callback=None, errback=None):
        d = self.root.callRemote("encryptionNamespaceGet", arg_0)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def encryptionPluginsGet(self, callback=None, errback=None):
        d = self.root.callRemote("encryptionPluginsGet")
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def encryptionTrustUIGet(self, namespace, arg_1, profile_key, callback=None, errback=None):
        d = self.root.callRemote("encryptionTrustUIGet", namespace, arg_1, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def getConfig(self, section, name, callback=None, errback=None):
        d = self.root.callRemote("getConfig", section, name)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def getContacts(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("getContacts", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def getContactsFromGroup(self, group, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("getContactsFromGroup", group, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def getEntitiesData(self, jids, keys, profile, callback=None, errback=None):
        d = self.root.callRemote("getEntitiesData", jids, keys, profile)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def getEntityData(self, jid, keys, profile, callback=None, errback=None):
        d = self.root.callRemote("getEntityData", jid, keys, profile)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def getFeatures(self, profile_key, callback=None, errback=None):
        d = self.root.callRemote("getFeatures", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def getMainResource(self, contact_jid, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("getMainResource", contact_jid, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def getParamA(self, name, category, attribute="value", profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("getParamA", name, category, attribute, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def getParamsCategories(self, callback=None, errback=None):
        d = self.root.callRemote("getParamsCategories")
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def getParamsUI(self, security_limit=-1, app='', profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("getParamsUI", security_limit, app, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def getPresenceStatuses(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("getPresenceStatuses", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def getReady(self, callback=None, errback=None):
        d = self.root.callRemote("getReady")
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def getVersion(self, callback=None, errback=None):
        d = self.root.callRemote("getVersion")
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def getWaitingSub(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("getWaitingSub", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def historyGet(self, from_jid, to_jid, limit, between=True, filters='', profile="@NONE@", callback=None, errback=None):
        d = self.root.callRemote("historyGet", from_jid, to_jid, limit, between, filters, profile)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def isConnected(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("isConnected", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def launchAction(self, callback_id, data, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("launchAction", callback_id, data, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def loadParamsTemplate(self, filename, callback=None, errback=None):
        d = self.root.callRemote("loadParamsTemplate", filename)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def menuHelpGet(self, menu_id, language, callback=None, errback=None):
        d = self.root.callRemote("menuHelpGet", menu_id, language)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def menuLaunch(self, menu_type, path, data, security_limit, profile_key, callback=None, errback=None):
        d = self.root.callRemote("menuLaunch", menu_type, path, data, security_limit, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def menusGet(self, language, security_limit, callback=None, errback=None):
        d = self.root.callRemote("menusGet", language, security_limit)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def messageEncryptionGet(self, to_jid, profile_key, callback=None, errback=None):
        d = self.root.callRemote("messageEncryptionGet", to_jid, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def messageEncryptionStart(self, to_jid, namespace='', replace=False, profile_key="@NONE@", callback=None, errback=None):
        d = self.root.callRemote("messageEncryptionStart", to_jid, namespace, replace, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def messageEncryptionStop(self, to_jid, profile_key, callback=None, errback=None):
        d = self.root.callRemote("messageEncryptionStop", to_jid, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def messageSend(self, to_jid, message, subject={}, mess_type="auto", extra={}, profile_key="@NONE@", callback=None, errback=None):
        d = self.root.callRemote("messageSend", to_jid, message, subject, mess_type, extra, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def namespacesGet(self, callback=None, errback=None):
        d = self.root.callRemote("namespacesGet")
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def paramsRegisterApp(self, xml, security_limit=-1, app='', callback=None, errback=None):
        d = self.root.callRemote("paramsRegisterApp", xml, security_limit, app)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def profileCreate(self, profile, password='', component='', callback=None, errback=None):
        d = self.root.callRemote("profileCreate", profile, password, component)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def profileIsSessionStarted(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("profileIsSessionStarted", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def profileNameGet(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("profileNameGet", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def profileSetDefault(self, profile, callback=None, errback=None):
        d = self.root.callRemote("profileSetDefault", profile)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def profileStartSession(self, password='', profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("profileStartSession", password, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def profilesListGet(self, clients=True, components=False, callback=None, errback=None):
        d = self.root.callRemote("profilesListGet", clients, components)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def progressGet(self, id, profile, callback=None, errback=None):
        d = self.root.callRemote("progressGet", id, profile)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def progressGetAll(self, profile, callback=None, errback=None):
        d = self.root.callRemote("progressGetAll", profile)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def progressGetAllMetadata(self, profile, callback=None, errback=None):
        d = self.root.callRemote("progressGetAllMetadata", profile)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def rosterResync(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("rosterResync", profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def saveParamsTemplate(self, filename, callback=None, errback=None):
        d = self.root.callRemote("saveParamsTemplate", filename)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def sessionInfosGet(self, profile_key, callback=None, errback=None):
        d = self.root.callRemote("sessionInfosGet", profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def setParam(self, name, value, category, security_limit=-1, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("setParam", name, value, category, security_limit, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def setPresence(self, to_jid='', show='', statuses={}, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("setPresence", to_jid, show, statuses, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def subscription(self, sub_type, entity, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("subscription", sub_type, entity, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)

    def updateContact(self, entity_jid, name, groups, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self.root.callRemote("updateContact", entity_jid, name, groups, profile_key)
        if callback is not None:
            d.addCallback(lambda __: callback())
        if errback is None:
            errback = self._generic_errback
        d.addErrback(errback)
