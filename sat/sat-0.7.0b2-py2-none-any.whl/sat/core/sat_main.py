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

from glob import glob
import sys
import os.path
import uuid
import sat
from sat.core.i18n import _, languageSwitch
from sat.core import patches
patches.apply()
from twisted.application import service
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from twisted.internet import reactor
from wokkel.xmppim import RosterItem
from sat.core import xmpp
from sat.core import exceptions
from sat.core.log import getLogger

from sat.core.constants import Const as C
from sat.memory import memory
from sat.memory import cache
from sat.memory import encryption
from sat.tools import async_trigger as trigger
from sat.tools import utils
from sat.tools.common import dynamic_import
from sat.tools.common import regex
from sat.stdui import ui_contact_list, ui_profile_manager
import sat.plugins


try:
    from collections import OrderedDict  # only available from python 2.7
except ImportError:
    from ordereddict import OrderedDict

log = getLogger(__name__)

class SAT(service.Service):
    def __init__(self):
        self._cb_map = {}  # map from callback_id to callbacks
        self._menus = (
            OrderedDict()
        )  # dynamic menus. key: callback_id, value: menu data (dictionnary)
        self._menus_paths = {}  # path to id. key: (menu_type, lower case tuple of path),
                                # value: menu id
        self.initialised = defer.Deferred()
        self.profiles = {}
        self.plugins = {}
        # map for short name to whole namespace,
        self.ns_map = {
            u"x-data": xmpp.NS_X_DATA,
            u"disco#info": xmpp.NS_DISCO_INFO,
        }
        # extended by plugins with registerNamespace
        self.memory = memory.Memory(self)
        self.trigger = (
            trigger.TriggerManager()
        )  # trigger are used to change SàT behaviour

        bridge_name = self.memory.getConfig("", "bridge", "dbus")

        bridge_module = dynamic_import.bridge(bridge_name)
        if bridge_module is None:
            log.error(u"Can't find bridge module of name {}".format(bridge_name))
            sys.exit(1)
        log.info(u"using {} bridge".format(bridge_name))
        try:
            self.bridge = bridge_module.Bridge()
        except exceptions.BridgeInitError:
            log.error(u"Bridge can't be initialised, can't start SàT core")
            sys.exit(1)
        self.bridge.register_method("getReady", lambda: self.initialised)
        self.bridge.register_method("getVersion", lambda: self.full_version)
        self.bridge.register_method("getFeatures", self.getFeatures)
        self.bridge.register_method("profileNameGet", self.memory.getProfileName)
        self.bridge.register_method("profilesListGet", self.memory.getProfilesList)
        self.bridge.register_method(
            "getEntityData",
            lambda jid_, keys, profile: self.memory.getEntityData(
                jid.JID(jid_), keys, profile
            ),
        )
        self.bridge.register_method("getEntitiesData", self.memory._getEntitiesData)
        self.bridge.register_method("profileCreate", self.memory.createProfile)
        self.bridge.register_method("asyncDeleteProfile", self.memory.asyncDeleteProfile)
        self.bridge.register_method("profileStartSession", self.memory.startSession)
        self.bridge.register_method(
            "profileIsSessionStarted", self.memory._isSessionStarted
        )
        self.bridge.register_method("profileSetDefault", self.memory.profileSetDefault)
        self.bridge.register_method("connect", self._connect)
        self.bridge.register_method("disconnect", self.disconnect)
        self.bridge.register_method("getContacts", self.getContacts)
        self.bridge.register_method("getContactsFromGroup", self.getContactsFromGroup)
        self.bridge.register_method("getMainResource", self.memory._getMainResource)
        self.bridge.register_method(
            "getPresenceStatuses", self.memory._getPresenceStatuses
        )
        self.bridge.register_method("getWaitingSub", self.memory.getWaitingSub)
        self.bridge.register_method("messageSend", self._messageSend)
        self.bridge.register_method("messageEncryptionStart",
                                    self._messageEncryptionStart)
        self.bridge.register_method("messageEncryptionStop",
                                    self._messageEncryptionStop)
        self.bridge.register_method("messageEncryptionGet",
                                    self._messageEncryptionGet)
        self.bridge.register_method("encryptionNamespaceGet",
                                    self._encryptionNamespaceGet)
        self.bridge.register_method("encryptionPluginsGet", self._encryptionPluginsGet)
        self.bridge.register_method("encryptionTrustUIGet", self._encryptionTrustUIGet)
        self.bridge.register_method("getConfig", self._getConfig)
        self.bridge.register_method("setParam", self.setParam)
        self.bridge.register_method("getParamA", self.memory.getStringParamA)
        self.bridge.register_method("asyncGetParamA", self.memory.asyncGetStringParamA)
        self.bridge.register_method(
            "asyncGetParamsValuesFromCategory",
            self.memory.asyncGetParamsValuesFromCategory,
        )
        self.bridge.register_method("getParamsUI", self.memory.getParamsUI)
        self.bridge.register_method(
            "getParamsCategories", self.memory.getParamsCategories
        )
        self.bridge.register_method("paramsRegisterApp", self.memory.paramsRegisterApp)
        self.bridge.register_method("historyGet", self.memory._historyGet)
        self.bridge.register_method("setPresence", self._setPresence)
        self.bridge.register_method("subscription", self.subscription)
        self.bridge.register_method("addContact", self._addContact)
        self.bridge.register_method("updateContact", self._updateContact)
        self.bridge.register_method("delContact", self._delContact)
        self.bridge.register_method("rosterResync", self._rosterResync)
        self.bridge.register_method("isConnected", self.isConnected)
        self.bridge.register_method("launchAction", self.launchCallback)
        self.bridge.register_method("actionsGet", self.actionsGet)
        self.bridge.register_method("progressGet", self._progressGet)
        self.bridge.register_method("progressGetAll", self._progressGetAll)
        self.bridge.register_method("menusGet", self.getMenus)
        self.bridge.register_method("menuHelpGet", self.getMenuHelp)
        self.bridge.register_method("menuLaunch", self._launchMenu)
        self.bridge.register_method("discoInfos", self.memory.disco._discoInfos)
        self.bridge.register_method("discoItems", self.memory.disco._discoItems)
        self.bridge.register_method("discoFindByFeatures", self._findByFeatures)
        self.bridge.register_method("saveParamsTemplate", self.memory.save_xml)
        self.bridge.register_method("loadParamsTemplate", self.memory.load_xml)
        self.bridge.register_method("sessionInfosGet", self.getSessionInfos)
        self.bridge.register_method("namespacesGet", self.getNamespaces)

        self.memory.initialized.addCallback(self._postMemoryInit)

    @property
    def version(self):
        """Return the short version of SàT"""
        return C.APP_VERSION

    @property
    def full_version(self):
        """Return the full version of SàT

        In developement mode, release name and extra data are returned too
        """
        version = self.version
        if version[-1] == "D":
            # we are in debug version, we add extra data
            try:
                return self._version_cache
            except AttributeError:
                self._version_cache = u"{} « {} » ({})".format(
                    version, C.APP_RELEASE_NAME, utils.getRepositoryData(sat)
                )
                return self._version_cache
        else:
            return version

    @property
    def bridge_name(self):
        return os.path.splitext(os.path.basename(self.bridge.__file__))[0]

    def _postMemoryInit(self, ignore):
        """Method called after memory initialization is done"""
        self.common_cache = cache.Cache(self, None)
        log.info(_("Memory initialised"))
        try:
            self._import_plugins()
            ui_contact_list.ContactList(self)
            ui_profile_manager.ProfileManager(self)
        except Exception as e:
            log.error(
                _(u"Could not initialize backend: {reason}").format(
                    reason=str(e).decode("utf-8", "ignore")
                )
            )
            sys.exit(1)
        self._addBaseMenus()
        self.initialised.callback(None)
        log.info(_(u"Backend is ready"))

    def _addBaseMenus(self):
        """Add base menus"""
        encryption.EncryptionHandler._importMenus(self)

    def _unimport_plugin(self, plugin_path):
        """remove a plugin from sys.modules if it is there"""
        try:
            del sys.modules[plugin_path]
        except KeyError:
            pass

    def _import_plugins(self):
        """Import all plugins found in plugins directory"""
        # FIXME: module imported but cancelled should be deleted
        # TODO: make this more generic and reusable in tools.common
        # FIXME: should use imp
        # TODO: do not import all plugins if no needed: component plugins are not needed
        #       if we just use a client, and plugin blacklisting should be possible in
        #       sat.conf
        plugins_path = os.path.dirname(sat.plugins.__file__)
        plugin_glob = "plugin*." + C.PLUGIN_EXT
        plug_lst = [
            os.path.splitext(plugin)[0]
            for plugin in map(
                os.path.basename, glob(os.path.join(plugins_path, plugin_glob))
            )
        ]
        plugins_to_import = {}  # plugins we still have to import
        for plug in plug_lst:
            plugin_path = "sat.plugins." + plug
            try:
                __import__(plugin_path)
            except exceptions.MissingModule as e:
                self._unimport_plugin(plugin_path)
                log.warning(
                    u"Can't import plugin [{path}] because of an unavailale third party "
                    u"module:\n{msg}".format(
                        path=plugin_path, msg=e
                    )
                )
                continue
            except exceptions.CancelError as e:
                log.info(
                    u"Plugin [{path}] cancelled its own import: {msg}".format(
                        path=plugin_path, msg=e
                    )
                )
                self._unimport_plugin(plugin_path)
                continue
            except Exception as e:
                import traceback

                log.error(
                    _(u"Can't import plugin [{path}]:\n{error}").format(
                        path=plugin_path, error=traceback.format_exc()
                    )
                )
                self._unimport_plugin(plugin_path)
                continue
            mod = sys.modules[plugin_path]
            plugin_info = mod.PLUGIN_INFO
            import_name = plugin_info["import_name"]

            plugin_modes = plugin_info[u"modes"] = set(
                plugin_info.setdefault(u"modes", C.PLUG_MODE_DEFAULT)
            )

            # if the plugin is an entry point, it must work in component mode
            if plugin_info[u"type"] == C.PLUG_TYPE_ENTRY_POINT:
                # if plugin is an entrypoint, we cache it
                if C.PLUG_MODE_COMPONENT not in plugin_modes:
                    log.error(
                        _(
                            u"{type} type must be used with {mode} mode, ignoring plugin"
                        ).format(type=C.PLUG_TYPE_ENTRY_POINT, mode=C.PLUG_MODE_COMPONENT)
                    )
                    self._unimport_plugin(plugin_path)
                    continue

            if import_name in plugins_to_import:
                log.error(
                    _(
                        u"Name conflict for import name [{import_name}], can't import "
                        u"plugin [{name}]"
                    ).format(**plugin_info)
                )
                continue
            plugins_to_import[import_name] = (plugin_path, mod, plugin_info)
        while True:
            try:
                self._import_plugins_from_dict(plugins_to_import)
            except ImportError:
                pass
            if not plugins_to_import:
                break

    def _import_plugins_from_dict(
        self, plugins_to_import, import_name=None, optional=False
    ):
        """Recursively import and their dependencies in the right order

        @param plugins_to_import(dict): key=import_name and values=(plugin_path, module,
                                        plugin_info)
        @param import_name(unicode, None): name of the plugin to import as found in
                                           PLUGIN_INFO['import_name']
        @param optional(bool): if False and plugin is not found, an ImportError exception
                               is raised
        """
        if import_name in self.plugins:
            log.debug(u"Plugin {} already imported, passing".format(import_name))
            return
        if not import_name:
            import_name, (plugin_path, mod, plugin_info) = plugins_to_import.popitem()
        else:
            if not import_name in plugins_to_import:
                if optional:
                    log.warning(
                        _(u"Recommended plugin not found: {}").format(import_name)
                    )
                    return
                msg = u"Dependency not found: {}".format(import_name)
                log.error(msg)
                raise ImportError(msg)
            plugin_path, mod, plugin_info = plugins_to_import.pop(import_name)
        dependencies = plugin_info.setdefault("dependencies", [])
        recommendations = plugin_info.setdefault("recommendations", [])
        for to_import in dependencies + recommendations:
            if to_import not in self.plugins:
                log.debug(
                    u"Recursively import dependency of [%s]: [%s]"
                    % (import_name, to_import)
                )
                try:
                    self._import_plugins_from_dict(
                        plugins_to_import, to_import, to_import not in dependencies
                    )
                except ImportError as e:
                    log.warning(
                        _(u"Can't import plugin {name}: {error}").format(
                            name=plugin_info["name"], error=e
                        )
                    )
                    if optional:
                        return
                    raise e
        log.info("importing plugin: {}".format(plugin_info["name"]))
        # we instanciate the plugin here
        try:
            self.plugins[import_name] = getattr(mod, plugin_info["main"])(self)
        except Exception as e:
            log.warning(
                u'Error while loading plugin "{name}", ignoring it: {error}'.format(
                    name=plugin_info["name"], error=e
                )
            )
            if optional:
                return
            raise ImportError(u"Error during initiation")
        if C.bool(plugin_info.get(C.PI_HANDLER, C.BOOL_FALSE)):
            self.plugins[import_name].is_handler = True
        else:
            self.plugins[import_name].is_handler = False
        # we keep metadata as a Class attribute
        self.plugins[import_name]._info = plugin_info
        # TODO: test xmppclient presence and register handler parent

    def pluginsUnload(self):
        """Call unload method on every loaded plugin, if exists

        @return (D): A deferred which return None when all method have been called
        """
        # TODO: in the futur, it should be possible to hot unload a plugin
        #       pluging depending on the unloaded one should be unloaded too
        #       for now, just a basic call on plugin.unload is done
        defers_list = []
        for plugin in self.plugins.itervalues():
            try:
                unload = plugin.unload
            except AttributeError:
                continue
            else:
                defers_list.append(defer.maybeDeferred(unload))
        return defers_list

    def _connect(self, profile_key, password="", options=None):
        profile = self.memory.getProfileName(profile_key)
        return self.connect(profile, password, options)

    def connect(self, profile, password="", options=None, max_retries=C.XMPP_MAX_RETRIES):
        """Connect a profile (i.e. connect client.component to XMPP server)

        Retrieve the individual parameters, authenticate the profile
        and initiate the connection to the associated XMPP server.
        @param profile: %(doc_profile)s
        @param password (string): the SàT profile password
        @param options (dict): connection options. Key can be:
            -
        @param max_retries (int): max number of connection retries
        @return (D(bool)):
            - True if the XMPP connection was already established
            - False if the XMPP connection has been initiated (it may still fail)
        @raise exceptions.PasswordError: Profile password is wrong
        """
        if options is None:
            options = {}

        def connectProfile(__=None):
            if self.isConnected(profile):
                log.info(_(u"already connected !"))
                return True

            if self.memory.isComponent(profile):
                d = xmpp.SatXMPPComponent.startConnection(self, profile, max_retries)
            else:
                d = xmpp.SatXMPPClient.startConnection(self, profile, max_retries)
            return d.addCallback(lambda __: False)

        d = self.memory.startSession(password, profile)
        d.addCallback(connectProfile)
        return d

    def disconnect(self, profile_key):
        """disconnect from jabber server"""
        # FIXME: client should not be deleted if only disconnected
        #        it shoud be deleted only when session is finished
        if not self.isConnected(profile_key):
            # isConnected is checked here and not on client
            # because client is deleted when session is ended
            log.info(_(u"not connected !"))
            return defer.succeed(None)
        client = self.getClient(profile_key)
        return client.entityDisconnect()

    def getFeatures(self, profile_key=C.PROF_KEY_NONE):
        """Get available features

        Return list of activated plugins and plugin specific data
        @param profile_key: %(doc_profile_key)s
            C.PROF_KEY_NONE can be used to have general plugins data (i.e. not profile
            dependent)
        @return (dict)[Deferred]: features data where:
            - key is plugin import name, present only for activated plugins
            - value is a an other dict, when meaning is specific to each plugin.
                this dict is return by plugin's getFeature method.
                If this method doesn't exists, an empty dict is returned.
        """
        try:
            # FIXME: there is no method yet to check profile session
            #        as soon as one is implemented, it should be used here
            self.getClient(profile_key)
        except KeyError:
            log.warning("Requesting features for a profile outside a session")
            profile_key = C.PROF_KEY_NONE
        except exceptions.ProfileNotSetError:
            pass

        features = []
        for import_name, plugin in self.plugins.iteritems():
            try:
                features_d = defer.maybeDeferred(plugin.getFeatures, profile_key)
            except AttributeError:
                features_d = defer.succeed({})
            features.append(features_d)

        d_list = defer.DeferredList(features)

        def buildFeatures(result, import_names):
            assert len(result) == len(import_names)
            ret = {}
            for name, (success, data) in zip(import_names, result):
                if success:
                    ret[name] = data
                else:
                    log.warning(
                        u"Error while getting features for {name}: {failure}".format(
                            name=name, failure=data
                        )
                    )
                    ret[name] = {}
            return ret

        d_list.addCallback(buildFeatures, self.plugins.keys())
        return d_list

    def getContacts(self, profile_key):
        client = self.getClient(profile_key)

        def got_roster(__):
            ret = []
            for item in client.roster.getItems():  # we get all items for client's roster
                # and convert them to expected format
                attr = client.roster.getAttributes(item)
                ret.append([item.jid.userhost(), attr, item.groups])
            return ret

        return client.roster.got_roster.addCallback(got_roster)

    def getContactsFromGroup(self, group, profile_key):
        client = self.getClient(profile_key)
        return [jid_.full() for jid_ in client.roster.getJidsFromGroup(group)]

    def purgeEntity(self, profile):
        """Remove reference to a profile client/component and purge cache

        the garbage collector can then free the memory
        """
        try:
            del self.profiles[profile]
        except KeyError:
            log.error(_("Trying to remove reference to a client not referenced"))
        else:
            self.memory.purgeProfileSession(profile)

    def startService(self):
        log.info(u"Salut à toi ô mon frère !")

    def stopService(self):
        log.info(u"Salut aussi à Rantanplan")
        return self.pluginsUnload()

    def run(self):
        log.debug(_("running app"))
        reactor.run()

    def stop(self):
        log.debug(_("stopping app"))
        reactor.stop()

    ## Misc methods ##

    def getJidNStream(self, profile_key):
        """Convenient method to get jid and stream from profile key
        @return: tuple (jid, xmlstream) from profile, can be None"""
        # TODO: deprecate this method (getClient is enough)
        profile = self.memory.getProfileName(profile_key)
        if not profile or not self.profiles[profile].isConnected():
            return (None, None)
        return (self.profiles[profile].jid, self.profiles[profile].xmlstream)

    def getClient(self, profile_key):
        """Convenient method to get client from profile key

        @return: client or None if it doesn't exist
        @raise exceptions.ProfileKeyUnknown: the profile or profile key doesn't exist
        @raise exceptions.NotFound: client is not available
            This happen if profile has not been used yet
        """
        profile = self.memory.getProfileName(profile_key)
        if not profile:
            raise exceptions.ProfileKeyUnknown
        try:
            return self.profiles[profile]
        except KeyError:
            raise exceptions.NotFound(profile_key)

    def getClients(self, profile_key):
        """Convenient method to get list of clients from profile key

        Manage list through profile_key like C.PROF_KEY_ALL
        @param profile_key: %(doc_profile_key)s
        @return: list of clients
        """
        if not profile_key:
            raise exceptions.DataError(_(u"profile_key must not be empty"))
        try:
            profile = self.memory.getProfileName(profile_key, True)
        except exceptions.ProfileUnknownError:
            return []
        if profile == C.PROF_KEY_ALL:
            return self.profiles.values()
        elif profile[0] == "@":  #  only profile keys can start with "@"
            raise exceptions.ProfileKeyUnknown
        return [self.profiles[profile]]

    def _getConfig(self, section, name):
        """Get the main configuration option

        @param section: section of the config file (None or '' for DEFAULT)
        @param name: name of the option
        @return: unicode representation of the option
        """
        return unicode(self.memory.getConfig(section, name, ""))

    def logErrback(self, failure_):
        """generic errback logging

        can be used as last errback to show unexpected error
        """
        log.error(_(u"Unexpected error: {}".format(failure_)))
        return failure_

    #  namespaces

    def registerNamespace(self, short_name, namespace):
        """associate a namespace to a short name"""
        if short_name in self.ns_map:
            raise exceptions.ConflictError(u"this short name is already used")
        self.ns_map[short_name] = namespace

    def getNamespaces(self):
        return self.ns_map

    def getNamespace(self, short_name):
        try:
            return self.ns_map[short_name]
        except KeyError:
            raise exceptions.NotFound(u"namespace {short_name} is not registered"
                                      .format(short_name=short_name))

    def getSessionInfos(self, profile_key):
        """compile interesting data on current profile session"""
        client = self.getClient(profile_key)
        data = {
            "jid": client.jid.full(),
            "started": unicode(int(client.started))
            }
        return defer.succeed(data)

    # local dirs

    def getLocalPath(self, client, dir_name, *extra_path, **kwargs):
        """retrieve path for local data

        if path doesn't exist, it will be created
        @param client(SatXMPPClient, None): client instance
            used when profile is set, can be None if profile is False
        @param dir_name(unicode): name of the main path directory
        @param component(bool): if True, path will be prefixed with C.COMPONENTS_DIR
        @param profile(bool): if True, path will be suffixed by profile name
        @param *extra_path: extra path element(s) to use
        @return (unicode): path
        """
        # FIXME: component and profile are parsed with **kwargs because of python 2
        #   limitations. Once moved to python 3, this can be fixed
        component = kwargs.pop("component", False)
        profile = kwargs.pop("profile", True)
        assert not kwargs

        path_elts = [self.memory.getConfig("", "local_dir")]
        if component:
            path_elts.append(C.COMPONENTS_DIR)
        path_elts.append(regex.pathEscape(dir_name))
        if extra_path:
            path_elts.extend([regex.pathEscape(p) for p in extra_path])
        if profile:
            regex.pathEscape(client.profile)
        path = os.path.join(*path_elts)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    ## Client management ##

    def setParam(self, name, value, category, security_limit, profile_key):
        """set wanted paramater and notice observers"""
        self.memory.setParam(name, value, category, security_limit, profile_key)

    def isConnected(self, profile_key):
        """Return connection status of profile
        @param profile_key: key_word or profile name to determine profile name
        @return: True if connected
        """
        profile = self.memory.getProfileName(profile_key)
        if not profile:
            log.error(_("asking connection status for a non-existant profile"))
            raise exceptions.ProfileUnknownError(profile_key)
        if profile not in self.profiles:
            return False
        return self.profiles[profile].isConnected()

    ## Encryption ##

    def registerEncryptionPlugin(self, *args, **kwargs):
        return encryption.EncryptionHandler.registerPlugin(*args, **kwargs)

    def _messageEncryptionStart(self, to_jid_s, namespace, replace=False,
                                profile_key=C.PROF_KEY_NONE):
        client = self.getClient(profile_key)
        to_jid = jid.JID(to_jid_s)
        return client.encryption.start(to_jid, namespace or None, replace)

    def _messageEncryptionStop(self, to_jid_s, profile_key=C.PROF_KEY_NONE):
        client = self.getClient(profile_key)
        to_jid = jid.JID(to_jid_s)
        return client.encryption.stop(to_jid)

    def _messageEncryptionGet(self, to_jid_s, profile_key=C.PROF_KEY_NONE):
        client = self.getClient(profile_key)
        to_jid = jid.JID(to_jid_s)
        session_data = client.encryption.getSession(to_jid)
        return client.encryption.getBridgeData(session_data)

    def _encryptionNamespaceGet(self, name):
        return encryption.EncryptionHandler.getNSFromName(name)

    def _encryptionPluginsGet(self):
        plugins = encryption.EncryptionHandler.getPlugins()
        ret = []
        for p in plugins:
            ret.append({
                u"name": p.name,
                u"namespace": p.namespace,
                u"priority": unicode(p.priority),
                })
        return ret

    def _encryptionTrustUIGet(self, to_jid_s, namespace, profile_key):
        client = self.getClient(profile_key)
        to_jid = jid.JID(to_jid_s)
        d = client.encryption.getTrustUI(to_jid, namespace=namespace or None)
        d.addCallback(lambda xmlui: xmlui.toXml())
        return d

    ## XMPP methods ##

    def _messageSend(self, to_jid_s, message, subject=None, mess_type="auto", extra=None,
                     profile_key=C.PROF_KEY_NONE,):
        client = self.getClient(profile_key)
        to_jid = jid.JID(to_jid_s)
        # XXX: we need to use the dictionary comprehension because D-Bus return its own
        #      types, and pickle can't manage them. TODO: Need to find a better way
        return client.sendMessage(
            to_jid,
            message,
            subject,
            mess_type,
            {unicode(key): unicode(value) for key, value in extra.items()},
        )

    def _setPresence(self, to="", show="", statuses=None, profile_key=C.PROF_KEY_NONE):
        return self.setPresence(jid.JID(to) if to else None, show, statuses, profile_key)

    def setPresence(self, to_jid=None, show="", statuses=None,
                    profile_key=C.PROF_KEY_NONE):
        """Send our presence information"""
        if statuses is None:
            statuses = {}
        profile = self.memory.getProfileName(profile_key)
        assert profile
        priority = int(
            self.memory.getParamA("Priority", "Connection", profile_key=profile)
        )
        self.profiles[profile].presence.available(to_jid, show, statuses, priority)
        # XXX: FIXME: temporary fix to work around openfire 3.7.0 bug (presence is not
        #             broadcasted to generating resource)
        if "" in statuses:
            statuses[C.PRESENCE_STATUSES_DEFAULT] = statuses.pop("")
        self.bridge.presenceUpdate(
            self.profiles[profile].jid.full(), show, int(priority), statuses, profile
        )

    def subscription(self, subs_type, raw_jid, profile_key):
        """Called to manage subscription
        @param subs_type: subsciption type (cf RFC 3921)
        @param raw_jid: unicode entity's jid
        @param profile_key: profile"""
        profile = self.memory.getProfileName(profile_key)
        assert profile
        to_jid = jid.JID(raw_jid)
        log.debug(
            _(u"subsciption request [%(subs_type)s] for %(jid)s")
            % {"subs_type": subs_type, "jid": to_jid.full()}
        )
        if subs_type == "subscribe":
            self.profiles[profile].presence.subscribe(to_jid)
        elif subs_type == "subscribed":
            self.profiles[profile].presence.subscribed(to_jid)
        elif subs_type == "unsubscribe":
            self.profiles[profile].presence.unsubscribe(to_jid)
        elif subs_type == "unsubscribed":
            self.profiles[profile].presence.unsubscribed(to_jid)

    def _addContact(self, to_jid_s, profile_key):
        return self.addContact(jid.JID(to_jid_s), profile_key)

    def addContact(self, to_jid, profile_key):
        """Add a contact in roster list"""
        profile = self.memory.getProfileName(profile_key)
        assert profile
        # presence is sufficient, as a roster push will be sent according to
        # RFC 6121 §3.1.2
        self.profiles[profile].presence.subscribe(to_jid)

    def _updateContact(self, to_jid_s, name, groups, profile_key):
        return self.updateContact(jid.JID(to_jid_s), name, groups, profile_key)

    def updateContact(self, to_jid, name, groups, profile_key):
        """update a contact in roster list"""
        profile = self.memory.getProfileName(profile_key)
        assert profile
        groups = set(groups)
        roster_item = RosterItem(to_jid)
        roster_item.name = name or None
        roster_item.groups = set(groups)
        return self.profiles[profile].roster.setItem(roster_item)

    def _delContact(self, to_jid_s, profile_key):
        return self.delContact(jid.JID(to_jid_s), profile_key)

    def delContact(self, to_jid, profile_key):
        """Remove contact from roster list"""
        profile = self.memory.getProfileName(profile_key)
        assert profile
        self.profiles[profile].presence.unsubscribe(to_jid)  # is not asynchronous
        return self.profiles[profile].roster.removeItem(to_jid)

    def _rosterResync(self, profile_key):
        client = self.getClient(profile_key)
        return client.roster.resync()

    ## Discovery ##
    # discovery methods are shortcuts to self.memory.disco
    # the main difference with client.disco is that self.memory.disco manage cache

    def hasFeature(self, *args, **kwargs):
        return self.memory.disco.hasFeature(*args, **kwargs)

    def checkFeature(self, *args, **kwargs):
        return self.memory.disco.checkFeature(*args, **kwargs)

    def checkFeatures(self, *args, **kwargs):
        return self.memory.disco.checkFeatures(*args, **kwargs)

    def getDiscoInfos(self, *args, **kwargs):
        return self.memory.disco.getInfos(*args, **kwargs)

    def getDiscoItems(self, *args, **kwargs):
        return self.memory.disco.getItems(*args, **kwargs)

    def findServiceEntity(self, *args, **kwargs):
        return self.memory.disco.findServiceEntity(*args, **kwargs)

    def findServiceEntities(self, *args, **kwargs):
        return self.memory.disco.findServiceEntities(*args, **kwargs)

    def findFeaturesSet(self, *args, **kwargs):
        return self.memory.disco.findFeaturesSet(*args, **kwargs)

    def _findByFeatures(self, namespaces, identities, bare_jids, service, roster, own_jid,
                        local_device, profile_key):
        client = self.getClient(profile_key)
        return self.findByFeatures(client, namespaces, identities, bare_jids, service,
                                   roster, own_jid, local_device,)

    @defer.inlineCallbacks
    def findByFeatures(self, client, namespaces, identities=None, bare_jids=False,
                       service=True, roster=True, own_jid=True, local_device=False):
        """retrieve all services or contacts managing a set a features

        @param namespaces(list[unicode]): features which must be handled
        @param identities(list[tuple[unicode,unicode]], None): if not None or empty,
            only keep those identities tuple must by (category, type)
        @param bare_jids(bool): retrieve only bare_jids if True
            if False, retrieve full jid of connected devices
        @param service(bool): if True return service from our roster
        @param roster(bool): if True, return entities in roster
            full jid of all matching resources available will be returned
        @param own_jid(bool): if True, return profile's jid resources
        @param local_device(bool): if True, return profile's jid local resource
            (i.e. client.jid)
        @return (tuple(dict[jid.JID(), tuple[unicode, unicode, unicode]]*3)): found
            entities in a tuple with:
            - service entities
            - own entities
            - roster entities
        """
        assert isinstance(namespaces, list)
        if not identities:
            identities = None
        if not namespaces and not identities:
            raise exceptions.DataError(
                "at least one namespace or one identity must be set"
            )
        found_service = {}
        found_own = {}
        found_roster = {}
        if service:
            services_jids = yield self.findFeaturesSet(client, namespaces)
            services_jids = list(services_jids)  # we need a list to map results below
            services_infos  = yield defer.DeferredList(
                [self.getDiscoInfos(client, service_jid) for service_jid in services_jids]
            )

            for idx, (success, infos) in enumerate(services_infos):
                service_jid = services_jids[idx]
                if not success:
                    log.warning(
                        _(u"Can't find features for service {service_jid}, ignoring")
                        .format(service_jid=service_jid.full()))
                    continue
                if (identities is not None
                    and not set(infos.identities.keys()).issuperset(identities)):
                    continue
                found_identities = [
                    (cat, type_, name or u"")
                    for (cat, type_), name in infos.identities.iteritems()
                ]
                found_service[service_jid.full()] = found_identities

        to_find = []
        if own_jid:
            to_find.append((found_own, [client.jid.userhostJID()]))
        if roster:
            to_find.append((found_roster, client.roster.getJids()))

        full_jids = []
        d_list = []

        for found, jids in to_find:
            for jid_ in jids:
                if jid_.resource:
                    if bare_jids:
                        continue
                    resources = [jid_.resource]
                else:
                    if bare_jids:
                        resources = [None]
                    else:
                        try:
                            resources = self.memory.getAvailableResources(client, jid_)
                        except exceptions.UnknownEntityError:
                            continue
                        if not resources and jid_ == client.jid.userhostJID() and own_jid:
                            # small hack to avoid missing our own resource when this
                            # method is called at the very beginning of the session
                            # and our presence has not been received yet
                            resources = [client.jid.resource]
                for resource in resources:
                    full_jid = jid.JID(tuple=(jid_.user, jid_.host, resource))
                    if full_jid == client.jid and not local_device:
                        continue
                    full_jids.append(full_jid)

                    d_list.append(self.getDiscoInfos(client, full_jid))

        d_list = defer.DeferredList(d_list)
        # XXX: 10 seconds may be too low for slow connections (e.g. mobiles)
        #      but for discovery, that's also the time the user will wait the first time
        #      before seing the page, if something goes wrong.
        d_list.addTimeout(10, reactor)
        infos_data = yield d_list

        for idx, (success, infos) in enumerate(infos_data):
            full_jid = full_jids[idx]
            if not success:
                log.warning(
                    _(u"Can't retrieve {full_jid} infos, ignoring")
                    .format(full_jid=full_jid.full()))
                continue
            if infos.features.issuperset(namespaces):
                if identities is not None and not set(
                    infos.identities.keys()
                ).issuperset(identities):
                    continue
                found_identities = [
                    (cat, type_, name or u"")
                    for (cat, type_), name in infos.identities.iteritems()
                ]
                found[full_jid.full()] = found_identities

        defer.returnValue((found_service, found_own, found_roster))

    ## Generic HMI ##

    def _killAction(self, keep_id, client):
        log.debug(u"Killing action {} for timeout".format(keep_id))
        client.actions[keep_id]

    def actionNew(
        self,
        action_data,
        security_limit=C.NO_SECURITY_LIMIT,
        keep_id=None,
        profile=C.PROF_KEY_NONE,
    ):
        """Shortcut to bridge.actionNew which generate and id and keep for retrieval

        @param action_data(dict): action data (see bridge documentation)
        @param security_limit: %(doc_security_limit)s
        @param keep_id(None, unicode): if not None, used to keep action for differed
            retrieval. Must be set to the callback_id.
            Action will be deleted after 30 min.
        @param profile: %(doc_profile)s
        """
        id_ = unicode(uuid.uuid4())
        if keep_id is not None:
            client = self.getClient(profile)
            action_timer = reactor.callLater(60 * 30, self._killAction, keep_id, client)
            client.actions[keep_id] = (action_data, id_, security_limit, action_timer)

        self.bridge.actionNew(action_data, id_, security_limit, profile)

    def actionsGet(self, profile):
        """Return current non answered actions

        @param profile: %(doc_profile)s
        """
        client = self.getClient(profile)
        return [action_tuple[:-1] for action_tuple in client.actions.itervalues()]

    def registerProgressCb(
        self, progress_id, callback, metadata=None, profile=C.PROF_KEY_NONE
    ):
        """Register a callback called when progress is requested for id"""
        if metadata is None:
            metadata = {}
        client = self.getClient(profile)
        if progress_id in client._progress_cb:
            raise exceptions.ConflictError(u"Progress ID is not unique !")
        client._progress_cb[progress_id] = (callback, metadata)

    def removeProgressCb(self, progress_id, profile):
        """Remove a progress callback"""
        client = self.getClient(profile)
        try:
            del client._progress_cb[progress_id]
        except KeyError:
            log.error(_(u"Trying to remove an unknow progress callback"))

    def _progressGet(self, progress_id, profile):
        data = self.progressGet(progress_id, profile)
        return {k: unicode(v) for k, v in data.iteritems()}

    def progressGet(self, progress_id, profile):
        """Return a dict with progress information

        @param progress_id(unicode): unique id of the progressing element
        @param profile: %(doc_profile)s
        @return (dict): data with the following keys:
            'position' (int): current possition
            'size' (int): end_position
            if id doesn't exists (may be a finished progression), and empty dict is
            returned
        """
        client = self.getClient(profile)
        try:
            data = client._progress_cb[progress_id][0](progress_id, profile)
        except KeyError:
            data = {}
        return data

    def _progressGetAll(self, profile_key):
        progress_all = self.progressGetAll(profile_key)
        for profile, progress_dict in progress_all.iteritems():
            for progress_id, data in progress_dict.iteritems():
                for key, value in data.iteritems():
                    data[key] = unicode(value)
        return progress_all

    def progressGetAllMetadata(self, profile_key):
        """Return all progress metadata at once

        @param profile_key: %(doc_profile)s
            if C.PROF_KEY_ALL is used, all progress metadata from all profiles are
            returned
        @return (dict[dict[dict]]): a dict which map profile to progress_dict
            progress_dict map progress_id to progress_data
            progress_metadata is the same dict as sent by [progressStarted]
        """
        clients = self.getClients(profile_key)
        progress_all = {}
        for client in clients:
            profile = client.profile
            progress_dict = {}
            progress_all[profile] = progress_dict
            for (
                progress_id,
                (__, progress_metadata),
            ) in client._progress_cb.iteritems():
                progress_dict[progress_id] = progress_metadata
        return progress_all

    def progressGetAll(self, profile_key):
        """Return all progress status at once

        @param profile_key: %(doc_profile)s
            if C.PROF_KEY_ALL is used, all progress status from all profiles are returned
        @return (dict[dict[dict]]): a dict which map profile to progress_dict
            progress_dict map progress_id to progress_data
            progress_data is the same dict as returned by [progressGet]
        """
        clients = self.getClients(profile_key)
        progress_all = {}
        for client in clients:
            profile = client.profile
            progress_dict = {}
            progress_all[profile] = progress_dict
            for progress_id, (progress_cb, __) in client._progress_cb.iteritems():
                progress_dict[progress_id] = progress_cb(progress_id, profile)
        return progress_all

    def registerCallback(self, callback, *args, **kwargs):
        """Register a callback.

        @param callback(callable): method to call
        @param kwargs: can contain:
            with_data(bool): True if the callback use the optional data dict
            force_id(unicode): id to avoid generated id. Can lead to name conflict, avoid
                               if possible
            one_shot(bool): True to delete callback once it has been called
        @return: id of the registered callback
        """
        callback_id = kwargs.pop("force_id", None)
        if callback_id is None:
            callback_id = str(uuid.uuid4())
        else:
            if callback_id in self._cb_map:
                raise exceptions.ConflictError(_(u"id already registered"))
        self._cb_map[callback_id] = (callback, args, kwargs)

        if "one_shot" in kwargs:  # One Shot callback are removed after 30 min

            def purgeCallback():
                try:
                    self.removeCallback(callback_id)
                except KeyError:
                    pass

            reactor.callLater(1800, purgeCallback)

        return callback_id

    def removeCallback(self, callback_id):
        """ Remove a previously registered callback
        @param callback_id: id returned by [registerCallback] """
        log.debug("Removing callback [%s]" % callback_id)
        del self._cb_map[callback_id]

    def launchCallback(self, callback_id, data=None, profile_key=C.PROF_KEY_NONE):
        """Launch a specific callback

        @param callback_id: id of the action (callback) to launch
        @param data: optional data
        @profile_key: %(doc_profile_key)s
        @return: a deferred which fire a dict where key can be:
            - xmlui: a XMLUI need to be displayed
            - validated: if present, can be used to launch a callback, it can have the
                values
                - C.BOOL_TRUE
                - C.BOOL_FALSE
        """
        #  FIXME: security limit need to be checked here
        try:
            client = self.getClient(profile_key)
        except exceptions.NotFound:
            # client is not available yet
            profile = self.memory.getProfileName(profile_key)
            if not profile:
                raise exceptions.ProfileUnknownError(
                    _(u"trying to launch action with a non-existant profile")
                )
        else:
            profile = client.profile
            # we check if the action is kept, and remove it
            try:
                action_tuple = client.actions[callback_id]
            except KeyError:
                pass
            else:
                action_tuple[-1].cancel()  # the last item is the action timer
                del client.actions[callback_id]

        try:
            callback, args, kwargs = self._cb_map[callback_id]
        except KeyError:
            raise exceptions.DataError(u"Unknown callback id {}".format(callback_id))

        if kwargs.get("with_data", False):
            if data is None:
                raise exceptions.DataError("Required data for this callback is missing")
            args, kwargs = (
                list(args)[:],
                kwargs.copy(),
            )  # we don't want to modify the original (kw)args
            args.insert(0, data)
            kwargs["profile"] = profile
            del kwargs["with_data"]

        if kwargs.pop("one_shot", False):
            self.removeCallback(callback_id)

        return defer.maybeDeferred(callback, *args, **kwargs)

    # Menus management

    def _getMenuCanonicalPath(self, path):
        """give canonical form of path

        canonical form is a tuple of the path were every element is stripped and lowercase
        @param path(iterable[unicode]): untranslated path to menu
        @return (tuple[unicode]): canonical form of path
        """
        return tuple((p.lower().strip() for p in path))

    def importMenu(self, path, callback, security_limit=C.NO_SECURITY_LIMIT,
                   help_string="", type_=C.MENU_GLOBAL):
        """register a new menu for frontends

        @param path(iterable[unicode]): path to go to the menu
            (category/subcategory/.../item) (e.g.: ("File", "Open"))
            /!\ use D_() instead of _() for translations (e.g. (D_("File"), D_("Open")))
            untranslated/lower case path can be used to identity a menu, for this reason
            it must be unique independently of case.
        @param callback(callable): method to be called when menuitem is selected, callable
            or a callback id (string) as returned by [registerCallback]
        @param security_limit(int): %(doc_security_limit)s
            /!\ security_limit MUST be added to data in launchCallback if used #TODO
        @param help_string(unicode): string used to indicate what the menu do (can be
            show as a tooltip).
            /!\ use D_() instead of _() for translations
        @param type(unicode): one of:
            - C.MENU_GLOBAL: classical menu, can be shown in a menubar on top (e.g.
                something like File/Open)
            - C.MENU_ROOM: like a global menu, but only shown in multi-user chat
                menu_data must contain a "room_jid" data
            - C.MENU_SINGLE: like a global menu, but only shown in one2one chat
                menu_data must contain a "jid" data
            - C.MENU_JID_CONTEXT: contextual menu, used with any jid (e.g.: ad hoc
                commands, jid is already filled)
                menu_data must contain a "jid" data
            - C.MENU_ROSTER_JID_CONTEXT: like JID_CONTEXT, but restricted to jids in
                roster.
                menu_data must contain a "room_jid" data
            - C.MENU_ROSTER_GROUP_CONTEXT: contextual menu, used with group (e.g.: publish
                microblog, group is already filled)
                menu_data must contain a "group" data
        @return (unicode): menu_id (same as callback_id)
        """

        if callable(callback):
            callback_id = self.registerCallback(callback, with_data=True)
        elif isinstance(callback, basestring):
            # The callback is already registered
            callback_id = callback
            try:
                callback, args, kwargs = self._cb_map[callback_id]
            except KeyError:
                raise exceptions.DataError("Unknown callback id")
            kwargs["with_data"] = True  # we have to be sure that we use extra data
        else:
            raise exceptions.DataError("Unknown callback type")

        for menu_data in self._menus.itervalues():
            if menu_data["path"] == path and menu_data["type"] == type_:
                raise exceptions.ConflictError(
                    _("A menu with the same path and type already exists")
                )

        path_canonical = self._getMenuCanonicalPath(path)
        menu_key = (type_, path_canonical)

        if menu_key in self._menus_paths:
            raise exceptions.ConflictError(
                u"this menu path is already used: {path} ({menu_key})".format(
                    path=path_canonical, menu_key=menu_key
                )
            )

        menu_data = {
            "path": tuple(path),
            "path_canonical": path_canonical,
            "security_limit": security_limit,
            "help_string": help_string,
            "type": type_,
        }

        self._menus[callback_id] = menu_data
        self._menus_paths[menu_key] = callback_id

        return callback_id

    def getMenus(self, language="", security_limit=C.NO_SECURITY_LIMIT):
        """Return all menus registered

        @param language: language used for translation, or empty string for default
        @param security_limit: %(doc_security_limit)s
        @return: array of tuple with:
            - menu id (same as callback_id)
            - menu type
            - raw menu path (array of strings)
            - translated menu path
            - extra (dict(unicode, unicode)): extra data where key can be:
                - icon: name of the icon to use (TODO)
                - help_url: link to a page with more complete documentation (TODO)
        """
        ret = []
        for menu_id, menu_data in self._menus.iteritems():
            type_ = menu_data["type"]
            path = menu_data["path"]
            menu_security_limit = menu_data["security_limit"]
            if security_limit != C.NO_SECURITY_LIMIT and (
                menu_security_limit == C.NO_SECURITY_LIMIT
                or menu_security_limit > security_limit
            ):
                continue
            languageSwitch(language)
            path_i18n = [_(elt) for elt in path]
            languageSwitch()
            extra = {}  # TODO: manage extra data like icon
            ret.append((menu_id, type_, path, path_i18n, extra))

        return ret

    def _launchMenu(self, menu_type, path, data=None, security_limit=C.NO_SECURITY_LIMIT,
                    profile_key=C.PROF_KEY_NONE):
        client = self.getClient(profile_key)
        return self.launchMenu(client, menu_type, path, data, security_limit)

    def launchMenu(self, client, menu_type, path, data=None,
        security_limit=C.NO_SECURITY_LIMIT):
        """launch action a menu action

        @param menu_type(unicode): type of menu to launch
        @param path(iterable[unicode]): canonical path of the menu
        @params data(dict): menu data
        @raise NotFound: this path is not known
        """
        # FIXME: manage security_limit here
        #        defaut security limit should be high instead of C.NO_SECURITY_LIMIT
        canonical_path = self._getMenuCanonicalPath(path)
        menu_key = (menu_type, canonical_path)
        try:
            callback_id = self._menus_paths[menu_key]
        except KeyError:
            raise exceptions.NotFound(
                u"Can't find menu {path} ({menu_type})".format(
                    path=canonical_path, menu_type=menu_type
                )
            )
        return self.launchCallback(callback_id, data, client.profile)

    def getMenuHelp(self, menu_id, language=""):
        """return the help string of the menu

        @param menu_id: id of the menu (same as callback_id)
        @param language: language used for translation, or empty string for default
        @param return: translated help

        """
        try:
            menu_data = self._menus[menu_id]
        except KeyError:
            raise exceptions.DataError("Trying to access an unknown menu")
        languageSwitch(language)
        help_string = _(menu_data["help_string"])
        languageSwitch()
        return help_string
