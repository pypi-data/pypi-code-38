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

from sat.core.i18n import _
import dbus
import dbus.service
import dbus.mainloop.glib
import inspect
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.internet.defer import Deferred
from sat.core.exceptions import BridgeInitError

const_INT_PREFIX = "org.salutatoi.SAT"  # Interface prefix
const_ERROR_PREFIX = const_INT_PREFIX + ".error"
const_OBJ_PATH = "/org/salutatoi/SAT/bridge"
const_CORE_SUFFIX = ".core"
const_PLUGIN_SUFFIX = ".plugin"


class ParseError(Exception):
    pass


class MethodNotRegistered(dbus.DBusException):
    _dbus_error_name = const_ERROR_PREFIX + ".MethodNotRegistered"


class InternalError(dbus.DBusException):
    _dbus_error_name = const_ERROR_PREFIX + ".InternalError"


class AsyncNotDeferred(dbus.DBusException):
    _dbus_error_name = const_ERROR_PREFIX + ".AsyncNotDeferred"


class DeferredNotAsync(dbus.DBusException):
    _dbus_error_name = const_ERROR_PREFIX + ".DeferredNotAsync"


class GenericException(dbus.DBusException):
    def __init__(self, twisted_error):
        """

        @param twisted_error (Failure): instance of twisted Failure
        @return: DBusException
        """
        super(GenericException, self).__init__()
        try:
            # twisted_error.value is a class
            class_ = twisted_error.value().__class__
        except TypeError:
            # twisted_error.value is an instance
            class_ = twisted_error.value.__class__
            message = twisted_error.getErrorMessage()
            try:
                self.args = (message, twisted_error.value.condition)
            except AttributeError:
                self.args = (message,)
        self._dbus_error_name = ".".join(
            [const_ERROR_PREFIX, class_.__module__, class_.__name__]
        )


class DbusObject(dbus.service.Object):
    def __init__(self, bus, path):
        dbus.service.Object.__init__(self, bus, path)
        log.debug("Init DbusObject...")
        self.cb = {}

    def register_method(self, name, cb):
        self.cb[name] = cb

    def _callback(self, name, *args, **kwargs):
        """call the callback if it exists, raise an exception else
        if the callback return a deferred, use async methods"""
        if not name in self.cb:
            raise MethodNotRegistered

        if "callback" in kwargs:
            # we must have errback too
            if not "errback" in kwargs:
                log.error("errback is missing in method call [%s]" % name)
                raise InternalError
            callback = kwargs.pop("callback")
            errback = kwargs.pop("errback")
            async = True
        else:
            async = False
        result = self.cb[name](*args, **kwargs)
        if async:
            if not isinstance(result, Deferred):
                log.error("Asynchronous method [%s] does not return a Deferred." % name)
                raise AsyncNotDeferred
            result.addCallback(
                lambda result: callback() if result is None else callback(result)
            )
            result.addErrback(lambda err: errback(GenericException(err)))
        else:
            if isinstance(result, Deferred):
                log.error("Synchronous method [%s] return a Deferred." % name)
                raise DeferredNotAsync
            return result

    ### signals ###

    @dbus.service.signal(const_INT_PREFIX + const_PLUGIN_SUFFIX, signature="")
    def dummySignal(self):
        # FIXME: workaround for addSignal (doesn't work if one method doensn't
        #       already exist for plugins), probably missing some initialisation, need
        #       further investigations
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='sa{ss}s')
    def _debug(self, action, params, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='a{ss}sis')
    def actionNew(self, action_data, id, security_limit, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='ss')
    def connected(self, jid_s, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='ss')
    def contactDeleted(self, entity_jid, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='s')
    def disconnected(self, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='ssss')
    def entityDataUpdated(self, jid, name, value, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='sss')
    def messageEncryptionStarted(self, to_jid, encryption_data, profile_key):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='sa{ss}s')
    def messageEncryptionStopped(self, to_jid, encryption_data, profile_key):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='sdssa{ss}a{ss}sa{ss}s')
    def messageNew(self, uid, timestamp, from_jid, to_jid, message, subject, mess_type, extra, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='sa{ss}ass')
    def newContact(self, contact_jid, attributes, groups, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='ssss')
    def paramUpdate(self, name, value, category, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='ssia{ss}s')
    def presenceUpdate(self, entity_jid, show, priority, statuses, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='sss')
    def progressError(self, id, error, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='sa{ss}s')
    def progressFinished(self, id, metadata, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='sa{ss}s')
    def progressStarted(self, id, metadata, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='sss')
    def subscribe(self, sub_type, entity_jid, profile):
        pass

    ### methods ###

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='a(a{ss}si)',
                         async_callbacks=None)
    def actionsGet(self, profile_key="@DEFAULT@"):
        return self._callback("actionsGet", unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='',
                         async_callbacks=None)
    def addContact(self, entity_jid, profile_key="@DEFAULT@"):
        return self._callback("addContact", unicode(entity_jid), unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='',
                         async_callbacks=('callback', 'errback'))
    def asyncDeleteProfile(self, profile, callback=None, errback=None):
        return self._callback("asyncDeleteProfile", unicode(profile), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sssis', out_signature='s',
                         async_callbacks=('callback', 'errback'))
    def asyncGetParamA(self, name, category, attribute="value", security_limit=-1, profile_key="@DEFAULT@", callback=None, errback=None):
        return self._callback("asyncGetParamA", unicode(name), unicode(category), unicode(attribute), security_limit, unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sis', out_signature='a{ss}',
                         async_callbacks=('callback', 'errback'))
    def asyncGetParamsValuesFromCategory(self, category, security_limit=-1, profile_key="@DEFAULT@", callback=None, errback=None):
        return self._callback("asyncGetParamsValuesFromCategory", unicode(category), security_limit, unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ssa{ss}', out_signature='b',
                         async_callbacks=('callback', 'errback'))
    def connect(self, profile_key="@DEFAULT@", password='', options={}, callback=None, errback=None):
        return self._callback("connect", unicode(profile_key), unicode(password), options, callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='',
                         async_callbacks=('callback', 'errback'))
    def delContact(self, entity_jid, profile_key="@DEFAULT@", callback=None, errback=None):
        return self._callback("delContact", unicode(entity_jid), unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='asa(ss)bbbbbs', out_signature='(a{sa(sss)}a{sa(sss)}a{sa(sss)})',
                         async_callbacks=('callback', 'errback'))
    def discoFindByFeatures(self, namespaces, identities, bare_jid=False, service=True, roster=True, own_jid=True, local_device=False, profile_key=u"@DEFAULT@", callback=None, errback=None):
        return self._callback("discoFindByFeatures", namespaces, identities, bare_jid, service, roster, own_jid, local_device, unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ssbs', out_signature='(asa(sss)a{sa(a{ss}as)})',
                         async_callbacks=('callback', 'errback'))
    def discoInfos(self, entity_jid, node=u'', use_cache=True, profile_key=u"@DEFAULT@", callback=None, errback=None):
        return self._callback("discoInfos", unicode(entity_jid), unicode(node), use_cache, unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ssbs', out_signature='a(sss)',
                         async_callbacks=('callback', 'errback'))
    def discoItems(self, entity_jid, node=u'', use_cache=True, profile_key=u"@DEFAULT@", callback=None, errback=None):
        return self._callback("discoItems", unicode(entity_jid), unicode(node), use_cache, unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='',
                         async_callbacks=('callback', 'errback'))
    def disconnect(self, profile_key="@DEFAULT@", callback=None, errback=None):
        return self._callback("disconnect", unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='s',
                         async_callbacks=None)
    def encryptionNamespaceGet(self, arg_0):
        return self._callback("encryptionNamespaceGet", unicode(arg_0))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='', out_signature='aa{ss}',
                         async_callbacks=None)
    def encryptionPluginsGet(self, ):
        return self._callback("encryptionPluginsGet", )

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sss', out_signature='s',
                         async_callbacks=('callback', 'errback'))
    def encryptionTrustUIGet(self, namespace, arg_1, profile_key, callback=None, errback=None):
        return self._callback("encryptionTrustUIGet", unicode(namespace), unicode(arg_1), unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='s',
                         async_callbacks=None)
    def getConfig(self, section, name):
        return self._callback("getConfig", unicode(section), unicode(name))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='a(sa{ss}as)',
                         async_callbacks=('callback', 'errback'))
    def getContacts(self, profile_key="@DEFAULT@", callback=None, errback=None):
        return self._callback("getContacts", unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='as',
                         async_callbacks=None)
    def getContactsFromGroup(self, group, profile_key="@DEFAULT@"):
        return self._callback("getContactsFromGroup", unicode(group), unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='asass', out_signature='a{sa{ss}}',
                         async_callbacks=None)
    def getEntitiesData(self, jids, keys, profile):
        return self._callback("getEntitiesData", jids, keys, unicode(profile))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sass', out_signature='a{ss}',
                         async_callbacks=None)
    def getEntityData(self, jid, keys, profile):
        return self._callback("getEntityData", unicode(jid), keys, unicode(profile))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='a{sa{ss}}',
                         async_callbacks=('callback', 'errback'))
    def getFeatures(self, profile_key, callback=None, errback=None):
        return self._callback("getFeatures", unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='s',
                         async_callbacks=None)
    def getMainResource(self, contact_jid, profile_key="@DEFAULT@"):
        return self._callback("getMainResource", unicode(contact_jid), unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ssss', out_signature='s',
                         async_callbacks=None)
    def getParamA(self, name, category, attribute="value", profile_key="@DEFAULT@"):
        return self._callback("getParamA", unicode(name), unicode(category), unicode(attribute), unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='', out_signature='as',
                         async_callbacks=None)
    def getParamsCategories(self, ):
        return self._callback("getParamsCategories", )

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='iss', out_signature='s',
                         async_callbacks=('callback', 'errback'))
    def getParamsUI(self, security_limit=-1, app='', profile_key="@DEFAULT@", callback=None, errback=None):
        return self._callback("getParamsUI", security_limit, unicode(app), unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='a{sa{s(sia{ss})}}',
                         async_callbacks=None)
    def getPresenceStatuses(self, profile_key="@DEFAULT@"):
        return self._callback("getPresenceStatuses", unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='', out_signature='',
                         async_callbacks=('callback', 'errback'))
    def getReady(self, callback=None, errback=None):
        return self._callback("getReady", callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='', out_signature='s',
                         async_callbacks=None)
    def getVersion(self, ):
        return self._callback("getVersion", )

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='a{ss}',
                         async_callbacks=None)
    def getWaitingSub(self, profile_key="@DEFAULT@"):
        return self._callback("getWaitingSub", unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ssiba{ss}s', out_signature='a(sdssa{ss}a{ss}sa{ss})',
                         async_callbacks=('callback', 'errback'))
    def historyGet(self, from_jid, to_jid, limit, between=True, filters='', profile="@NONE@", callback=None, errback=None):
        return self._callback("historyGet", unicode(from_jid), unicode(to_jid), limit, between, filters, unicode(profile), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='b',
                         async_callbacks=None)
    def isConnected(self, profile_key="@DEFAULT@"):
        return self._callback("isConnected", unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sa{ss}s', out_signature='a{ss}',
                         async_callbacks=('callback', 'errback'))
    def launchAction(self, callback_id, data, profile_key="@DEFAULT@", callback=None, errback=None):
        return self._callback("launchAction", unicode(callback_id), data, unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='b',
                         async_callbacks=None)
    def loadParamsTemplate(self, filename):
        return self._callback("loadParamsTemplate", unicode(filename))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='s',
                         async_callbacks=None)
    def menuHelpGet(self, menu_id, language):
        return self._callback("menuHelpGet", unicode(menu_id), unicode(language))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sasa{ss}is', out_signature='a{ss}',
                         async_callbacks=('callback', 'errback'))
    def menuLaunch(self, menu_type, path, data, security_limit, profile_key, callback=None, errback=None):
        return self._callback("menuLaunch", unicode(menu_type), path, data, security_limit, unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='si', out_signature='a(ssasasa{ss})',
                         async_callbacks=None)
    def menusGet(self, language, security_limit):
        return self._callback("menusGet", unicode(language), security_limit)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='s',
                         async_callbacks=None)
    def messageEncryptionGet(self, to_jid, profile_key):
        return self._callback("messageEncryptionGet", unicode(to_jid), unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ssbs', out_signature='',
                         async_callbacks=('callback', 'errback'))
    def messageEncryptionStart(self, to_jid, namespace='', replace=False, profile_key="@NONE@", callback=None, errback=None):
        return self._callback("messageEncryptionStart", unicode(to_jid), unicode(namespace), replace, unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='',
                         async_callbacks=('callback', 'errback'))
    def messageEncryptionStop(self, to_jid, profile_key, callback=None, errback=None):
        return self._callback("messageEncryptionStop", unicode(to_jid), unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sa{ss}a{ss}sa{ss}s', out_signature='',
                         async_callbacks=('callback', 'errback'))
    def messageSend(self, to_jid, message, subject={}, mess_type="auto", extra={}, profile_key="@NONE@", callback=None, errback=None):
        return self._callback("messageSend", unicode(to_jid), message, subject, unicode(mess_type), extra, unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='', out_signature='a{ss}',
                         async_callbacks=None)
    def namespacesGet(self, ):
        return self._callback("namespacesGet", )

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sis', out_signature='',
                         async_callbacks=None)
    def paramsRegisterApp(self, xml, security_limit=-1, app=''):
        return self._callback("paramsRegisterApp", unicode(xml), security_limit, unicode(app))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sss', out_signature='',
                         async_callbacks=('callback', 'errback'))
    def profileCreate(self, profile, password='', component='', callback=None, errback=None):
        return self._callback("profileCreate", unicode(profile), unicode(password), unicode(component), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='b',
                         async_callbacks=None)
    def profileIsSessionStarted(self, profile_key="@DEFAULT@"):
        return self._callback("profileIsSessionStarted", unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='s',
                         async_callbacks=None)
    def profileNameGet(self, profile_key="@DEFAULT@"):
        return self._callback("profileNameGet", unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='',
                         async_callbacks=None)
    def profileSetDefault(self, profile):
        return self._callback("profileSetDefault", unicode(profile))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='b',
                         async_callbacks=('callback', 'errback'))
    def profileStartSession(self, password='', profile_key="@DEFAULT@", callback=None, errback=None):
        return self._callback("profileStartSession", unicode(password), unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='bb', out_signature='as',
                         async_callbacks=None)
    def profilesListGet(self, clients=True, components=False):
        return self._callback("profilesListGet", clients, components)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='a{ss}',
                         async_callbacks=None)
    def progressGet(self, id, profile):
        return self._callback("progressGet", unicode(id), unicode(profile))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='a{sa{sa{ss}}}',
                         async_callbacks=None)
    def progressGetAll(self, profile):
        return self._callback("progressGetAll", unicode(profile))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='a{sa{sa{ss}}}',
                         async_callbacks=None)
    def progressGetAllMetadata(self, profile):
        return self._callback("progressGetAllMetadata", unicode(profile))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='',
                         async_callbacks=('callback', 'errback'))
    def rosterResync(self, profile_key="@DEFAULT@", callback=None, errback=None):
        return self._callback("rosterResync", unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='b',
                         async_callbacks=None)
    def saveParamsTemplate(self, filename):
        return self._callback("saveParamsTemplate", unicode(filename))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='a{ss}',
                         async_callbacks=('callback', 'errback'))
    def sessionInfosGet(self, profile_key, callback=None, errback=None):
        return self._callback("sessionInfosGet", unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sssis', out_signature='',
                         async_callbacks=None)
    def setParam(self, name, value, category, security_limit=-1, profile_key="@DEFAULT@"):
        return self._callback("setParam", unicode(name), unicode(value), unicode(category), security_limit, unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ssa{ss}s', out_signature='',
                         async_callbacks=None)
    def setPresence(self, to_jid='', show='', statuses={}, profile_key="@DEFAULT@"):
        return self._callback("setPresence", unicode(to_jid), unicode(show), statuses, unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sss', out_signature='',
                         async_callbacks=None)
    def subscription(self, sub_type, entity, profile_key="@DEFAULT@"):
        return self._callback("subscription", unicode(sub_type), unicode(entity), unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ssass', out_signature='',
                         async_callbacks=('callback', 'errback'))
    def updateContact(self, entity_jid, name, groups, profile_key="@DEFAULT@", callback=None, errback=None):
        return self._callback("updateContact", unicode(entity_jid), unicode(name), groups, unicode(profile_key), callback=callback, errback=errback)

    def __attributes(self, in_sign):
        """Return arguments to user given a in_sign
        @param in_sign: in_sign in the short form (using s,a,i,b etc)
        @return: list of arguments that correspond to a in_sign (e.g.: "sss" return "arg1, arg2, arg3")"""
        i = 0
        idx = 0
        attr = []
        while i < len(in_sign):
            if in_sign[i] not in ["b", "y", "n", "i", "x", "q", "u", "t", "d", "s", "a"]:
                raise ParseError("Unmanaged attribute type [%c]" % in_sign[i])

            attr.append("arg_%i" % idx)
            idx += 1

            if in_sign[i] == "a":
                i += 1
                if (
                    in_sign[i] != "{" and in_sign[i] != "("
                ):  # FIXME: must manage tuples out of arrays
                    i += 1
                    continue  # we have a simple type for the array
                opening_car = in_sign[i]
                assert opening_car in ["{", "("]
                closing_car = "}" if opening_car == "{" else ")"
                opening_count = 1
                while True:  # we have a dict or a list of tuples
                    i += 1
                    if i >= len(in_sign):
                        raise ParseError("missing }")
                    if in_sign[i] == opening_car:
                        opening_count += 1
                    if in_sign[i] == closing_car:
                        opening_count -= 1
                        if opening_count == 0:
                            break
            i += 1
        return attr

    def addMethod(self, name, int_suffix, in_sign, out_sign, method, async=False):
        """Dynamically add a method to Dbus Bridge"""
        inspect_args = inspect.getargspec(method)

        _arguments = inspect_args.args
        _defaults = list(inspect_args.defaults or [])

        if inspect.ismethod(method):
            # if we have a method, we don't want the first argument (usually 'self')
            del (_arguments[0])

        # first arguments are for the _callback method
        arguments_callback = ", ".join(
            [repr(name)]
            + (
                (_arguments + ["callback=callback", "errback=errback"])
                if async
                else _arguments
            )
        )

        if async:
            _arguments.extend(["callback", "errback"])
            _defaults.extend([None, None])

        # now we create a second list with default values
        for i in range(1, len(_defaults) + 1):
            _arguments[-i] = "%s = %s" % (_arguments[-i], repr(_defaults[-i]))

        arguments_defaults = ", ".join(_arguments)

        code = compile(
            "def %(name)s (self,%(arguments_defaults)s): return self._callback(%(arguments_callback)s)"
            % {
                "name": name,
                "arguments_defaults": arguments_defaults,
                "arguments_callback": arguments_callback,
            },
            "<DBus bridge>",
            "exec",
        )
        exec(code)  # FIXME: to the same thing in a cleaner way, without compile/exec
        method = locals()[name]
        async_callbacks = ("callback", "errback") if async else None
        setattr(
            DbusObject,
            name,
            dbus.service.method(
                const_INT_PREFIX + int_suffix,
                in_signature=in_sign,
                out_signature=out_sign,
                async_callbacks=async_callbacks,
            )(method),
        )
        function = getattr(self, name)
        func_table = self._dbus_class_table[
            self.__class__.__module__ + "." + self.__class__.__name__
        ][function._dbus_interface]
        func_table[function.__name__] = function  # Needed for introspection

    def addSignal(self, name, int_suffix, signature, doc={}):
        """Dynamically add a signal to Dbus Bridge"""
        attributes = ", ".join(self.__attributes(signature))
        # TODO: use doc parameter to name attributes

        # code = compile ('def '+name+' (self,'+attributes+'): log.debug ("'+name+' signal")', '<DBus bridge>','exec') #XXX: the log.debug is too annoying with xmllog
        code = compile(
            "def " + name + " (self," + attributes + "): pass", "<DBus bridge>", "exec"
        )
        exec(code)
        signal = locals()[name]
        setattr(
            DbusObject,
            name,
            dbus.service.signal(const_INT_PREFIX + int_suffix, signature=signature)(
                signal
            ),
        )
        function = getattr(self, name)
        func_table = self._dbus_class_table[
            self.__class__.__module__ + "." + self.__class__.__name__
        ][function._dbus_interface]
        func_table[function.__name__] = function  # Needed for introspection


class Bridge(object):
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        log.info("Init DBus...")
        try:
            self.session_bus = dbus.SessionBus()
        except dbus.DBusException as e:
            if e._dbus_error_name == "org.freedesktop.DBus.Error.NotSupported":
                log.error(
                    _(
                        u"D-Bus is not launched, please see README to see instructions on how to launch it"
                    )
                )
            raise BridgeInitError
        self.dbus_name = dbus.service.BusName(const_INT_PREFIX, self.session_bus)
        self.dbus_bridge = DbusObject(self.session_bus, const_OBJ_PATH)

    def _debug(self, action, params, profile):
        self.dbus_bridge._debug(action, params, profile)

    def actionNew(self, action_data, id, security_limit, profile):
        self.dbus_bridge.actionNew(action_data, id, security_limit, profile)

    def connected(self, jid_s, profile):
        self.dbus_bridge.connected(jid_s, profile)

    def contactDeleted(self, entity_jid, profile):
        self.dbus_bridge.contactDeleted(entity_jid, profile)

    def disconnected(self, profile):
        self.dbus_bridge.disconnected(profile)

    def entityDataUpdated(self, jid, name, value, profile):
        self.dbus_bridge.entityDataUpdated(jid, name, value, profile)

    def messageEncryptionStarted(self, to_jid, encryption_data, profile_key):
        self.dbus_bridge.messageEncryptionStarted(to_jid, encryption_data, profile_key)

    def messageEncryptionStopped(self, to_jid, encryption_data, profile_key):
        self.dbus_bridge.messageEncryptionStopped(to_jid, encryption_data, profile_key)

    def messageNew(self, uid, timestamp, from_jid, to_jid, message, subject, mess_type, extra, profile):
        self.dbus_bridge.messageNew(uid, timestamp, from_jid, to_jid, message, subject, mess_type, extra, profile)

    def newContact(self, contact_jid, attributes, groups, profile):
        self.dbus_bridge.newContact(contact_jid, attributes, groups, profile)

    def paramUpdate(self, name, value, category, profile):
        self.dbus_bridge.paramUpdate(name, value, category, profile)

    def presenceUpdate(self, entity_jid, show, priority, statuses, profile):
        self.dbus_bridge.presenceUpdate(entity_jid, show, priority, statuses, profile)

    def progressError(self, id, error, profile):
        self.dbus_bridge.progressError(id, error, profile)

    def progressFinished(self, id, metadata, profile):
        self.dbus_bridge.progressFinished(id, metadata, profile)

    def progressStarted(self, id, metadata, profile):
        self.dbus_bridge.progressStarted(id, metadata, profile)

    def subscribe(self, sub_type, entity_jid, profile):
        self.dbus_bridge.subscribe(sub_type, entity_jid, profile)

    def register_method(self, name, callback):
        log.debug("registering DBus bridge method [%s]" % name)
        self.dbus_bridge.register_method(name, callback)

    def addMethod(self, name, int_suffix, in_sign, out_sign, method, async=False, doc={}):
        """Dynamically add a method to Dbus Bridge"""
        # FIXME: doc parameter is kept only temporary, the time to remove it from calls
        log.debug("Adding method [%s] to DBus bridge" % name)
        self.dbus_bridge.addMethod(name, int_suffix, in_sign, out_sign, method, async)
        self.register_method(name, method)

    def addSignal(self, name, int_suffix, signature, doc={}):
        self.dbus_bridge.addSignal(name, int_suffix, signature, doc)
        setattr(Bridge, name, getattr(self.dbus_bridge, name))