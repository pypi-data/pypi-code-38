#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# helper class for making a SAT frontend
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

from sat.core.i18n import _
from sat.core import exceptions
from sat.tools import trigger
from sat.tools.common import data_format

from sat_frontends.tools import jid
from sat_frontends.quick_frontend import quick_widgets
from sat_frontends.quick_frontend import quick_menus
from sat_frontends.quick_frontend import quick_blog
from sat_frontends.quick_frontend import quick_chat, quick_games
from sat_frontends.quick_frontend import quick_contact_list
from sat_frontends.quick_frontend.constants import Const as C

import sys
from collections import OrderedDict
import time

try:
    # FIXME: to be removed when an acceptable solution is here
    unicode("")  # XXX: unicode doesn't exist in pyjamas
except (
    TypeError,
    AttributeError,
):  # Error raised is not the same depending on pyjsbuild options
    unicode = str


class ProfileManager(object):
    """Class managing all data relative to one profile, and plugging in mechanism"""

    # TODO: handle waiting XMLUI requests: getWaitingConf doesn't exist anymore
    #       and a way to keep some XMLUI request between sessions is expected in backend
    host = None
    bridge = None
    # cache_keys_to_get = ['avatar']

    def __init__(self, profile):
        self.profile = profile
        self.connected = False
        self.whoami = None
        self.notifications = {}  # key: bare jid or '' for general, value: notif data

    @property
    def autodisconnect(self):
        try:
            autodisconnect = self._autodisconnect
        except AttributeError:
            autodisconnect = False
        return autodisconnect

    def plug(self):
        """Plug the profile to the host"""
        # first of all we create the contact lists
        self.host.contact_lists.addProfile(self.profile)

        # we get the essential params
        self.bridge.asyncGetParamA(
            "JabberID",
            "Connection",
            profile_key=self.profile,
            callback=self._plug_profile_jid,
            errback=self._getParamError,
        )

    def _plug_profile_jid(self, jid_s):
        self.whoami = jid.JID(jid_s)  # resource might change after the connection
        self.bridge.isConnected(self.profile, callback=self._plug_profile_isconnected)

    def _autodisconnectEb(self, failure_):
        # XXX: we ignore error on this parameter, as Libervia can't access it
        log.warning(
            _("Error while trying to get autodisconnect param, ignoring: {}").format(
                failure_
            )
        )
        self._plug_profile_autodisconnect("false")

    def _plug_profile_isconnected(self, connected):
        self.connected = connected
        self.bridge.asyncGetParamA(
            "autodisconnect",
            "Connection",
            profile_key=self.profile,
            callback=self._plug_profile_autodisconnect,
            errback=self._autodisconnectEb,
        )

    def _plug_profile_autodisconnect(self, autodisconnect):
        if C.bool(autodisconnect):
            self._autodisconnect = True
        self.bridge.asyncGetParamA(
            "autoconnect",
            "Connection",
            profile_key=self.profile,
            callback=self._plug_profile_autoconnect,
            errback=self._getParamError,
        )

    def _plug_profile_autoconnect(self, value_str):
        autoconnect = C.bool(value_str)
        if autoconnect and not self.connected:
            self.host.connect(
                self.profile, callback=lambda __: self._plug_profile_afterconnect()
            )
        else:
            self._plug_profile_afterconnect()

    def _plug_profile_afterconnect(self):
        # Profile can be connected or not
        # we get cached data
        self.connected = True
        self.host.bridge.getFeatures(
            profile_key=self.profile,
            callback=self._plug_profile_getFeaturesCb,
            errback=self._plug_profile_getFeaturesEb,
        )

    def _plug_profile_getFeaturesEb(self, failure):
        log.error(u"Couldn't get features: {}".format(failure))
        self._plug_profile_getFeaturesCb({})

    def _plug_profile_getFeaturesCb(self, features):
        self.host.features = features
        # FIXME: we don't use cached value at the moment, but keep the code for later use
        #        it was previously used for avatars, but as we don't get full path here,
        #        it's better to request later
        # self.host.bridge.getEntitiesData([], ProfileManager.cache_keys_to_get,
        #                                  profile=self.profile,
        #                                  callback=self._plug_profile_gotCachedValues,
        #                                  errback=self._plug_profile_failedCachedValues)
        self._plug_profile_gotCachedValues({})

    def _plug_profile_failedCachedValues(self, failure):
        log.error(u"Couldn't get cached values: {}".format(failure))
        self._plug_profile_gotCachedValues({})

    def _plug_profile_gotCachedValues(self, cached_values):
        contact_list = self.host.contact_lists[self.profile]
        # add the contact list and its listener
        for entity_s, data in cached_values.iteritems():
            for key, value in data.iteritems():
                self.host.entityDataUpdatedHandler(entity_s, key, value, self.profile)

        if not self.connected:
            self.host.setPresenceStatus(C.PRESENCE_UNAVAILABLE, "", profile=self.profile)
        else:

            contact_list.fill()
            self.host.setPresenceStatus(profile=self.profile)

            # The waiting subscription requests
            self.bridge.getWaitingSub(
                self.profile, callback=self._plug_profile_gotWaitingSub
            )

    def _plug_profile_gotWaitingSub(self, waiting_sub):
        for sub in waiting_sub:
            self.host.subscribeHandler(waiting_sub[sub], sub, self.profile)

        self.bridge.mucGetRoomsJoined(
            self.profile, callback=self._plug_profile_gotRoomsJoined
        )

    def _plug_profile_gotRoomsJoined(self, rooms_args):
        # Now we open the MUC window where we already are:
        for room_args in rooms_args:
            self.host.mucRoomJoinedHandler(*room_args, profile=self.profile)
        # Presence must be requested after rooms are filled
        self.host.bridge.getPresenceStatuses(
            self.profile, callback=self._plug_profile_gotPresences
        )

    def _plug_profile_gotPresences(self, presences):
        def gotEntityData(data, contact):
            for key in ("avatar", "nick"):
                if key in data:
                    self.host.entityDataUpdatedHandler(
                        contact, key, data[key], self.profile
                    )

        for contact in presences:
            for res in presences[contact]:
                jabber_id = (u"%s/%s" % (jid.JID(contact).bare, res)) if res else contact
                show = presences[contact][res][0]
                priority = presences[contact][res][1]
                statuses = presences[contact][res][2]
                self.host.presenceUpdateHandler(
                    jabber_id, show, priority, statuses, self.profile
                )
            self.host.bridge.getEntityData(
                contact,
                ["avatar", "nick"],
                self.profile,
                callback=lambda data, contact=contact: gotEntityData(data, contact),
                errback=lambda failure, contact=contact: log.debug(
                    u"No cache data for {}".format(contact)
                ),
            )

        # At this point, profile should be fully plugged
        # and we launch frontend specific method
        self.host.profilePlugged(self.profile)

    def _getParamError(self, failure):
        log.error(_("Can't get profile parameter: {msg}").format(msg=failure))


class ProfilesManager(object):
    """Class managing collection of profiles"""

    def __init__(self):
        self._profiles = {}

    def __contains__(self, profile):
        return profile in self._profiles

    def __iter__(self):
        return self._profiles.iterkeys()

    def __getitem__(self, profile):
        return self._profiles[profile]

    def __len__(self):
        return len(self._profiles)

    def iteritems(self):
        return self._profiles.iteritems()

    def itervalues(self):
        return self._profiles.itervalues()

    def plug(self, profile):
        if profile in self._profiles:
            raise exceptions.ConflictError(
                "A profile of the name [{}] is already plugged".format(profile)
            )
        self._profiles[profile] = ProfileManager(profile)
        self._profiles[profile].plug()

    def unplug(self, profile):
        if profile not in self._profiles:
            raise ValueError("The profile [{}] is not plugged".format(profile))

        # remove the contact list and its listener
        host = self._profiles[profile].host
        host.contact_lists[profile].unplug()

        del self._profiles[profile]

    def chooseOneProfile(self):
        return self._profiles.keys()[0]


class QuickApp(object):
    """This class contain the main methods needed for the frontend"""

    MB_HANDLER = True  #: Set to False if the frontend doesn't manage microblog
    AVATARS_HANDLER = True  #: set to False if avatars are not used
    ENCRYPTION_HANDLERS = True  #: set to False if encryption is handled separatly
    #: if True, QuickApp will call resync itself, on all widgets at the same time
    #: if False, frontend must call resync itself when suitable (e.g. widget is being
    #: visible)
    AUTO_RESYNC = True

    def __init__(self, bridge_factory, xmlui, check_options=None, connect_bridge=True):
        """Create a frontend application

        @param bridge_factory: method to use to create the Bridge
        @param xmlui: xmlui module
        @param check_options: method to call to check options (usually command line
            arguments)
        """
        self.xmlui = xmlui
        self.menus = quick_menus.QuickMenusManager(self)
        ProfileManager.host = self
        self.profiles = ProfilesManager()
        self._plugs_in_progress = (
            set()
        )  # profiles currently being plugged, used to (un)lock contact list updates
        self.ready_profiles = set()  # profiles which are connected and ready
        self.signals_cache = {}  # used to keep signal received between start of
                                 # plug_profile and when the profile is actualy ready
        self.contact_lists = quick_contact_list.QuickContactListHandler(self)
        self.widgets = quick_widgets.QuickWidgetsManager(self)
        if check_options is not None:
            self.options = check_options()
        else:
            self.options = None

        # widget currently selected (must be filled by frontend)
        self.selected_widget = None

        # listeners are callable watching events
        self._listeners = {}  # key: listener type ("avatar", "selected", etc),
                              # value: list of callbacks

        # triggers
        self.trigger = (
            trigger.TriggerManager()
        )  # trigger are used to change the default behaviour

        ## bridge ##
        self.bridge = bridge_factory()
        ProfileManager.bridge = self.bridge
        if connect_bridge:
            self.connectBridge()

        # frontend notifications
        self._notif_id = 0
        self._notifications = OrderedDict()
        # watched progresses and associated callbacks
        self._progress_ids = {}
        # available features
        # FIXME: features are profile specific, to be checked
        self.features = None
        #: map of short name to namespaces
        self.ns_map = {}
        #: available encryptions
        self.encryption_plugins = []
        # state of synchronisation with backend
        self._sync = True

    def connectBridge(self):
        self.bridge.bridgeConnect(callback=self._bridgeCb, errback=self._bridgeEb)

    def _namespacesGetCb(self, ns_map):
        self.ns_map = ns_map

    def _namespacesGetEb(self, failure_):
        log.error(_(u"Can't get namespaces map: {msg}").format(msg=failure_))

    def _encryptionPluginsGetCb(self, plugins):
        self.encryption_plugins = plugins

    def _encryptionPluginsGetEb(self, failure_):
        log.warning(_(u"Can't retrieve encryption plugins: {msg}").format(msg=failure_))

    def onBridgeConnected(self):
        self.bridge.namespacesGet(
            callback=self._namespacesGetCb, errback=self._namespacesGetEb)
        # we cache available encryption plugins, as we'll use them on earch
        # new chat widget
        self.bridge.encryptionPluginsGet(
            callback=self._encryptionPluginsGetCb,
            errback=self._encryptionPluginsGetEb)

    def _bridgeCb(self):
        self.registerSignal("connected")
        self.registerSignal("disconnected")
        self.registerSignal("actionNew")
        self.registerSignal("newContact")
        self.registerSignal("messageNew")
        if self.ENCRYPTION_HANDLERS:
            self.registerSignal("messageEncryptionStarted")
            self.registerSignal("messageEncryptionStopped")
        self.registerSignal("presenceUpdate")
        self.registerSignal("subscribe")
        self.registerSignal("paramUpdate")
        self.registerSignal("contactDeleted")
        self.registerSignal("entityDataUpdated")
        self.registerSignal("progressStarted")
        self.registerSignal("progressFinished")
        self.registerSignal("progressError")
        self.registerSignal("mucRoomJoined", iface="plugin")
        self.registerSignal("mucRoomLeft", iface="plugin")
        self.registerSignal("mucRoomUserChangedNick", iface="plugin")
        self.registerSignal("mucRoomNewSubject", iface="plugin")
        self.registerSignal("chatStateReceived", iface="plugin")
        self.registerSignal("messageState", iface="plugin")
        self.registerSignal("psEvent", iface="plugin")
        # useful for debugging
        self.registerSignal("_debug", iface="core")

        # FIXME: do it dynamically
        quick_games.Tarot.registerSignals(self)
        quick_games.Quiz.registerSignals(self)
        quick_games.Radiocol.registerSignals(self)
        self.onBridgeConnected()

    def _bridgeEb(self, failure):
        if isinstance(failure, exceptions.BridgeExceptionNoService):
            print(_(u"Can't connect to SàT backend, are you sure it's launched ?"))
            sys.exit(1)
        elif isinstance(failure, exceptions.BridgeInitError):
            print(_(u"Can't init bridge"))
            sys.exit(1)
        else:
            print(_(u"Error while initialising bridge: {}".format(failure)))

    @property
    def current_profile(self):
        """Profile that a user would expect to use"""
        try:
            return self.selected_widget.profile
        except (TypeError, AttributeError):
            return self.profiles.chooseOneProfile()

    @property
    def visible_widgets(self):
        """Widgets currently visible

        This must be implemented by frontend
        @return (iter[object]): iterable on visible widgets
            widgets can be QuickWidgets or not
        """
        raise NotImplementedError

    @property
    def visible_quick_widgets(self):
        """QuickWidgets currently visible

        This generator iterate only on QuickWidgets, discarding other kinds of
        widget the frontend may have.
        @return (iter[object]): iterable on visible widgets
        """
        for w in self.visisble_widgets:
            if isinstance(w, quick_widgets.QuickWidget):
                return w

    # backend state management

    @property
    def sync(self):
        """Synchronization flag

        True if this frontend is synchronised with backend
        """
        return self._sync

    @sync.setter
    def sync(self, state):
        """Called when backend is desynchronised or resynchronising

        @param state(bool): True: if the backend is resynchronising
            False when we lose synchronisation, for instance if frontend is going to sleep
            or if connection has been lost and a reconnection is needed
        """
        if state:
            log.debug(u"we are synchronised with server")
            if self.AUTO_RESYNC:
                # we are resynchronising all widgets
                log.debug(u"doing a full widgets resynchronisation")
                for w in self.widgets:
                    try:
                        resync = w.resync
                    except AttributeError:
                        pass
                    else:
                        resync()
                self.contact_lists.fill()

            self._sync = state
        else:
            log.debug(u"we have lost synchronisation with server")
            self._sync = state
            # we've lost synchronisation, all widgets must be notified
            # note: this is always called independently of AUTO_RESYNC
            for w in self.widgets:
                try:
                    w.sync = False
                except AttributeError:
                    pass

    def registerSignal(
        self, function_name, handler=None, iface="core", with_profile=True
    ):
        """Register a handler for a signal

        @param function_name (str): name of the signal to handle
        @param handler (instancemethod): method to call when the signal arrive,
            None for calling an automatically named handler (function_name + 'Handler')
        @param iface (str): interface of the bridge to use ('core' or 'plugin')
        @param with_profile (boolean): True if the signal concerns a specific profile,
            in that case the profile name has to be passed by the caller
        """
        log.debug(u"registering signal {name}".format(name=function_name))
        if handler is None:
            handler = getattr(self, "{}{}".format(function_name, "Handler"))
        if not with_profile:
            self.bridge.register_signal(function_name, handler, iface)
            return

        def signalReceived(*args, **kwargs):
            profile = kwargs.get("profile")
            if profile is None:
                if not args:
                    raise exceptions.ProfileNotSetError
                profile = args[-1]
            if profile is not None:
                if not self.check_profile(profile):
                    if profile in self.profiles:
                        # profile is not ready but is in self.profiles, that's mean that
                        # it's being connecting and we need to cache the signal
                        self.signals_cache.setdefault(profile, []).append(
                            (function_name, handler, args, kwargs)
                        )
                    return  # we ignore signal for profiles we don't manage
            handler(*args, **kwargs)

        self.bridge.register_signal(function_name, signalReceived, iface)

    def addListener(self, type_, callback, profiles_filter=None):
        """Add a listener for an event

        /!\ don't forget to remove listener when not used anymore (e.g. if you delete a
            widget)
        @param type_: type of event, can be:
            - avatar: called when avatar data is updated
                args: (entity, avatar file, profile)
            - nick: called when nick data is updated
                args: (entity, new_nick, profile)
            - presence: called when a presence is received
                args: (entity, show, priority, statuses, profile)
            - notification: called when a new notification is emited
                args: (entity, notification_data, profile)
            - notification_clear: called when notifications are cleared
                args: (entity, type_, profile)
            - menu: called when a menu item is added or removed
                args: (type_, path, path_i18n, item) were values are:
                    type_: same as in [sat.core.sat_main.SAT.importMenu]
                    path: same as in [sat.core.sat_main.SAT.importMenu]
                    path_i18n: translated path (or None if the item is removed)
                    item: instance of quick_menus.MenuItemBase or None if the item is
                          removed
            - gotMenus: called only once when menu are available (no arg)
            - progressFinished: called when a progressing action has just finished
                args:  (progress_id, metadata, profile)
            - progressError: called when a progressing action failed
                args: (progress_id, error_msg, profile):
        @param callback: method to call on event
        @param profiles_filter (set[unicode]): if set and not empty, the
            listener will be callable only by one of the given profiles.
        """
        assert type_ in C.LISTENERS
        self._listeners.setdefault(type_, OrderedDict())[callback] = profiles_filter

    def removeListener(self, type_, callback):
        """Remove a callback from listeners

        @param type_: same as for [addListener]
        @param callback: callback to remove
        """
        assert type_ in C.LISTENERS
        self._listeners[type_].pop(callback)

    def callListeners(self, type_, *args, **kwargs):
        """Call the methods which listen type_ event. If a profiles filter has
        been register with a listener and profile argument is not None, the
        listener will be called only if profile is in the profiles filter list.

        @param type_: same as for [addListener]
        @param *args: arguments sent to callback
        @param **kwargs: keywords argument, mainly used to pass "profile" when needed
        """
        assert type_ in C.LISTENERS
        try:
            listeners = self._listeners[type_]
        except KeyError:
            pass
        else:
            profile = kwargs.get("profile")
            for listener, profiles_filter in listeners.iteritems():
                if profile is None or not profiles_filter or profile in profiles_filter:
                    listener(*args, **kwargs)

    def check_profile(self, profile):
        """Tell if the profile is currently followed by the application, and ready"""
        return profile in self.ready_profiles

    def postInit(self, profile_manager):
        """Must be called after initialization is done, do all automatic task

        (auto plug profile)
        @param profile_manager: instance of a subclass of
            Quick_frontend.QuickProfileManager
        """
        if self.options and self.options.profile:
            profile_manager.autoconnect([self.options.profile])

    def profilePlugged(self, profile):
        """Method called when the profile is fully plugged

        This will launch frontend specific workflow

        /!\ if you override the method and don't call the parent, be sure to add the
            profile to ready_profiles ! if you don't, all signals will stay in cache

        @param profile(unicode): %(doc_profile)s
        """
        self._plugs_in_progress.remove(profile)
        self.ready_profiles.add(profile)

        # profile is ready, we can call send signals that where is cache
        cached_signals = self.signals_cache.pop(profile, [])
        for function_name, handler, args, kwargs in cached_signals:
            log.debug(
                u"Calling cached signal [%s] with args %s and kwargs %s"
                % (function_name, args, kwargs)
            )
            handler(*args, **kwargs)

        self.callListeners("profilePlugged", profile=profile)
        if not self._plugs_in_progress:
            self.contact_lists.lockUpdate(False)

    def connect(self, profile, callback=None, errback=None):
        if not callback:
            callback = lambda __: None
        if not errback:

            def errback(failure):
                log.error(_(u"Can't connect profile [%s]") % failure)
                try:
                    module = failure.module
                except AttributeError:
                    module = ""
                try:
                    message = failure.message
                except AttributeError:
                    message = "error"
                try:
                    fullname = failure.fullname
                except AttributeError:
                    fullname = "error"
                if (
                    module.startswith("twisted.words.protocols.jabber")
                    and failure.condition == "not-authorized"
                ):
                    self.launchAction(C.CHANGE_XMPP_PASSWD_ID, {}, profile=profile)
                else:
                    self.showDialog(message, fullname, "error")

        self.bridge.connect(profile, callback=callback, errback=errback)

    def plug_profiles(self, profiles):
        """Tell application which profiles must be used

        @param profiles: list of valid profile names
        """
        self.contact_lists.lockUpdate()
        self._plugs_in_progress.update(profiles)
        self.plugging_profiles()
        for profile in profiles:
            self.profiles.plug(profile)

    def plugging_profiles(self):
        """Method to subclass to manage frontend specific things to do

        will be called when profiles are choosen and are to be plugged soon
        """
        pass

    def unplug_profile(self, profile):
        """Tell the application to not follow anymore the profile"""
        if not profile in self.profiles:
            raise ValueError("The profile [{}] is not plugged".format(profile))
        self.profiles.unplug(profile)

    def clear_profile(self):
        self.profiles.clear()

    def newWidget(self, widget):
        raise NotImplementedError

    # bridge signals hanlers

    def connectedHandler(self, jid_s, profile):
        """Called when the connection is made.

        @param jid_s (unicode): the JID that we were assigned by the server,
            as the resource might differ from the JID we asked for.
        """
        log.debug(_("Connected"))
        self.profiles[profile].whoami = jid.JID(jid_s)
        self.setPresenceStatus(profile=profile)
        # FIXME: fill() is already called for all profiles when doing self.sync = True
        #        a per-profile fill() should be done once, see below note
        self.contact_lists[profile].fill()
        # if we were already displaying widgets, they must be resynchronized
        # FIXME: self.sync is for all profiles
        #        while (dis)connection is per-profile.
        #        A mechanism similar to sync should be available
        #        on a per-profile basis
        self.sync = True

    def disconnectedHandler(self, profile):
        """called when the connection is closed"""
        log.debug(_("Disconnected"))
        self.contact_lists[profile].disconnect()
        # FIXME: see note on connectedHandler
        self.sync = False
        self.setPresenceStatus(C.PRESENCE_UNAVAILABLE, "", profile=profile)

    def actionNewHandler(self, action_data, id_, security_limit, profile):
        self.actionManager(action_data, user_action=False, profile=profile)

    def newContactHandler(self, jid_s, attributes, groups, profile):
        entity = jid.JID(jid_s)
        groups = list(groups)
        self.contact_lists[profile].setContact(entity, groups, attributes, in_roster=True)

    def messageNewHandler(self, uid, timestamp, from_jid_s, to_jid_s, msg, subject, type_,
                          extra, profile):
        from_jid = jid.JID(from_jid_s)
        to_jid = jid.JID(to_jid_s)
        if not self.trigger.point(
            "messageNewTrigger", uid, timestamp, from_jid, to_jid, msg, subject, type_,
            extra, profile=profile,):
            return

        from_me = from_jid.bare == self.profiles[profile].whoami.bare
        mess_to_jid = to_jid if from_me else from_jid
        target = mess_to_jid.bare
        contact_list = self.contact_lists[profile]

        try:
            is_room = contact_list.isRoom(target)
        except exceptions.NotFound:
            is_room = False

        if target.resource and not is_room:
            # we avoid resource locking, but we must keep resource for private MUC
            # messages
            target = target
        # we want to be sure to have at least one QuickChat instance
        self.widgets.getOrCreateWidget(
            quick_chat.QuickChat,
            target,
            type_ = C.CHAT_GROUP if is_room else C.CHAT_ONE2ONE,
            on_new_widget = None,
            profile = profile,
        )

        if (
            not from_jid in contact_list
            and from_jid.bare != self.profiles[profile].whoami.bare
        ):
            # XXX: needed to show entities which haven't sent any
            #     presence information and which are not in roster
            contact_list.setContact(from_jid)

        # we dispatch the message in the widgets
        for widget in self.widgets.getWidgets(
            quick_chat.QuickChat, target=target, profiles=(profile,)
        ):
            widget.messageNew(
                uid, timestamp, from_jid, mess_to_jid, msg, subject, type_, extra, profile
            )

    def messageEncryptionStartedHandler(self, destinee_jid_s, plugin_data, profile):
        destinee_jid = jid.JID(destinee_jid_s)
        plugin_data = data_format.deserialise(plugin_data)
        for widget in self.widgets.getWidgets(quick_chat.QuickChat,
                                              target=destinee_jid.bare,
                                              profiles=(profile,)):
            widget.messageEncryptionStarted(plugin_data)

    def messageEncryptionStoppedHandler(self, destinee_jid_s, plugin_data, profile):
        destinee_jid = jid.JID(destinee_jid_s)
        for widget in self.widgets.getWidgets(quick_chat.QuickChat,
                                              target=destinee_jid.bare,
                                              profiles=(profile,)):
            widget.messageEncryptionStopped(plugin_data)

    def messageStateHandler(self, uid, status, profile):
        for widget in self.widgets.getWidgets(quick_chat.QuickChat, profiles=(profile,)):
            widget.onMessageState(uid, status, profile)

    def messageSend(self, to_jid, message, subject=None, mess_type="auto", extra=None, callback=None, errback=None, profile_key=C.PROF_KEY_NONE):
        if not subject and not extra and (not message or message == {u'': u''}):
            log.debug(u"Not sending empty message")
            return

        if subject is None:
            subject = {}
        if extra is None:
            extra = {}
        if callback is None:
            callback = (
                lambda __=None: None
            )  # FIXME: optional argument is here because pyjamas doesn't support callback
               #        without arg with json proxy
        if errback is None:
            errback = lambda failure: self.showDialog(
                failure.fullname, failure.message, "error"
            )

        if not self.trigger.point("messageSendTrigger", to_jid, message, subject, mess_type, extra, callback, errback, profile_key=profile_key):
            return

        self.bridge.messageSend(
            unicode(to_jid),
            message,
            subject,
            mess_type,
            extra,
            profile_key,
            callback=callback,
            errback=errback,
        )

    def setPresenceStatus(self, show="", status=None, profile=C.PROF_KEY_NONE):
        raise NotImplementedError

    def presenceUpdateHandler(self, entity_s, show, priority, statuses, profile):
        log.debug(
            _(
                u"presence update for %(entity)s (show=%(show)s, priority=%(priority)s, "
                u"statuses=%(statuses)s) [profile:%(profile)s]"
            )
            % {
                "entity": entity_s,
                C.PRESENCE_SHOW: show,
                C.PRESENCE_PRIORITY: priority,
                C.PRESENCE_STATUSES: statuses,
                "profile": profile,
            }
        )
        entity = jid.JID(entity_s)

        if entity == self.profiles[profile].whoami:
            if show == C.PRESENCE_UNAVAILABLE:
                self.setPresenceStatus(C.PRESENCE_UNAVAILABLE, "", profile=profile)
            else:
                # FIXME: try to retrieve user language status before fallback to default
                status = statuses.get(C.PRESENCE_STATUSES_DEFAULT, None)
                self.setPresenceStatus(show, status, profile=profile)
            return

        self.callListeners("presence", entity, show, priority, statuses, profile=profile)

    def mucRoomJoinedHandler(self, room_jid_s, occupants, user_nick, subject, profile):
        """Called when a MUC room is joined"""
        log.debug(
            u"Room [{room_jid}] joined by {profile}, users presents:{users}".format(
                room_jid=room_jid_s, profile=profile, users=occupants.keys()
            )
        )
        room_jid = jid.JID(room_jid_s)
        self.widgets.getOrCreateWidget(
            quick_chat.QuickChat,
            room_jid,
            type_=C.CHAT_GROUP,
            nick=user_nick,
            occupants=occupants,
            subject=subject,
            profile=profile,
        )
        self.contact_lists[profile].setSpecial(room_jid, C.CONTACT_SPECIAL_GROUP)
        # chat_widget.update()

    def mucRoomLeftHandler(self, room_jid_s, profile):
        """Called when a MUC room is left"""
        log.debug(
            u"Room [%(room_jid)s] left by %(profile)s"
            % {"room_jid": room_jid_s, "profile": profile}
        )
        room_jid = jid.JID(room_jid_s)
        chat_widget = self.widgets.getWidget(quick_chat.QuickChat, room_jid, profile)
        if chat_widget:
            self.widgets.deleteWidget(chat_widget)
        self.contact_lists[profile].removeContact(room_jid)

    def mucRoomUserChangedNickHandler(self, room_jid_s, old_nick, new_nick, profile):
        """Called when an user joined a MUC room"""
        room_jid = jid.JID(room_jid_s)
        chat_widget = self.widgets.getOrCreateWidget(
            quick_chat.QuickChat, room_jid, type_=C.CHAT_GROUP, profile=profile
        )
        chat_widget.changeUserNick(old_nick, new_nick)
        log.debug(
            u"user [%(old_nick)s] is now known as [%(new_nick)s] in room [%(room_jid)s]"
            % {"old_nick": old_nick, "new_nick": new_nick, "room_jid": room_jid}
        )

    def mucRoomNewSubjectHandler(self, room_jid_s, subject, profile):
        """Called when subject of MUC room change"""
        room_jid = jid.JID(room_jid_s)
        chat_widget = self.widgets.getOrCreateWidget(
            quick_chat.QuickChat, room_jid, type_=C.CHAT_GROUP, profile=profile
        )
        chat_widget.setSubject(subject)
        log.debug(
            u"new subject for room [%(room_jid)s]: %(subject)s"
            % {"room_jid": room_jid, "subject": subject}
        )

    def chatStateReceivedHandler(self, from_jid_s, state, profile):
        """Called when a new chat state (XEP-0085) is received.

        @param from_jid_s (unicode): JID of a contact or C.ENTITY_ALL
        @param state (unicode): new state
        @param profile (unicode): current profile
        """
        from_jid = jid.JID(from_jid_s)
        for widget in self.widgets.getWidgets(quick_chat.QuickChat, target=from_jid.bare,
                                              profiles=(profile,)):
            widget.onChatState(from_jid, state, profile)

    def notify(self, type_, entity=None, message=None, subject=None, callback=None,
               cb_args=None, widget=None, profile=C.PROF_KEY_NONE):
        """Trigger an event notification

        @param type_(unicode): notifation kind,
            one of C.NOTIFY_* constant or any custom type specific to frontend
        @param entity(jid.JID, None): entity involved in the notification
            if entity is in contact list, a indicator may be added in front of it
        @param message(unicode, None): message of the notification
        @param subject(unicode, None): subject of the notification
        @param callback(callable, None): method to call when notification is selected
        @param cb_args(list, None): list of args for callback
        @param widget(object, None): widget where the notification happened
        """
        assert type_ in C.NOTIFY_ALL
        notif_dict = self.profiles[profile].notifications
        key = "" if entity is None else entity.bare
        type_notifs = notif_dict.setdefault(key, {}).setdefault(type_, [])
        notif_data = {
            "id": self._notif_id,
            "time": time.time(),
            "entity": entity,
            "callback": callback,
            "cb_args": cb_args,
            "message": message,
            "subject": subject,
        }
        if widget is not None:
            notif_data[widget] = widget
        type_notifs.append(notif_data)
        self._notifications[self._notif_id] = notif_data
        self._notif_id += 1
        self.callListeners("notification", entity, notif_data, profile=profile)

    def getNotifs(self, entity=None, type_=None, exact_jid=None, profile=C.PROF_KEY_NONE):
        """return notifications for given entity

        @param entity(jid.JID, None, C.ENTITY_ALL): jid of the entity to check
            bare jid to get all notifications, full jid to filter on resource
            None to get general notifications
            C.ENTITY_ALL to get all notifications
        @param type_(unicode, None): notification type to filter
            None to get all notifications
        @param exact_jid(bool, None): if True, only return notifications from
            exact entity jid (i.e. not including other resources)
            None for automatic selection (True for full jid, False else)
            False to get resources notifications
            False doesn't do anything if entity is not a bare jid
        @return (iter[dict]): notifications
        """
        main_notif_dict = self.profiles[profile].notifications

        if entity is C.ENTITY_ALL:
            selected_notifs = main_notif_dict.itervalues()
            exact_jid = False
        else:
            if entity is None:
                key = ""
                exact_jid = False
            else:
                key = entity.bare
                if exact_jid is None:
                    exact_jid = bool(entity.resource)
            selected_notifs = (main_notif_dict.setdefault(key, {}),)

        for notifs_from_select in selected_notifs:

            if type_ is None:
                type_notifs = notifs_from_select.itervalues()
            else:
                type_notifs = (notifs_from_select.get(type_, []),)

            for notifs in type_notifs:
                for notif in notifs:
                    if exact_jid and notif["entity"] != entity:
                        continue
                    yield notif

    def clearNotifs(self, entity, type_=None, profile=C.PROF_KEY_NONE):
        """return notifications for given entity

        @param entity(jid.JID, None): bare jid of the entity to check
            None to clear general notifications (but keep entities ones)
        @param type_(unicode, None): notification type to filter
            None to clear all notifications
        @return (list[dict]): list of notifications
        """
        notif_dict = self.profiles[profile].notifications
        key = "" if entity is None else entity.bare
        try:
            if type_ is None:
                del notif_dict[key]
            else:
                del notif_dict[key][type_]
        except KeyError:
            return
        self.callListeners("notificationsClear", entity, type_, profile=profile)

    def psEventHandler(self, category, service_s, node, event_type, data, profile):
        """Called when a PubSub event is received.

        @param category(unicode): event category (e.g. "PEP", "MICROBLOG")
        @param service_s (unicode): pubsub service
        @param node (unicode): pubsub node
        @param event_type (unicode): event type (one of C.PUBLISH, C.RETRACT, C.DELETE)
        @param data (serialised_dict): event data
        """
        data = data_format.deserialise(data)
        service_s = jid.JID(service_s)

        if category == C.PS_MICROBLOG and self.MB_HANDLER:
            if event_type == C.PS_PUBLISH:
                if not "content" in data:
                    log.warning("No content found in microblog data")
                    return

                # FIXME: check if [] make sense (instead of None)
                _groups = data.get("group")

                for wid in self.widgets.getWidgets(quick_blog.QuickBlog):
                    wid.addEntryIfAccepted(service_s, node, data, _groups, profile)

                try:
                    comments_node, comments_service = (
                        data["comments_node"],
                        data["comments_service"],
                    )
                except KeyError:
                    pass
                else:
                    self.bridge.mbGet(
                        comments_service,
                        comments_node,
                        C.NO_LIMIT,
                        [],
                        {"subscribe": C.BOOL_TRUE},
                        profile=profile,
                    )
            elif event_type == C.PS_RETRACT:
                for wid in self.widgets.getWidgets(quick_blog.QuickBlog):
                    wid.deleteEntryIfPresent(service_s, node, data["id"], profile)
                pass
            else:
                log.warning("Unmanaged PubSub event type {}".format(event_type))

    def registerProgressCbs(self, progress_id, callback, errback):
        """Register progression callbacks

        @param progress_id(unicode): id of the progression to check
        @param callback(callable, None): method to call when progressing action
            successfuly finished.
            None to ignore
        @param errback(callable, None): method to call when progressions action failed
            None to ignore
        """
        callbacks = self._progress_ids.setdefault(progress_id, [])
        callbacks.append((callback, errback))

    def progressStartedHandler(self, pid, metadata, profile):
        log.info(u"Progress {} started".format(pid))

    def progressFinishedHandler(self, pid, metadata, profile):
        log.info(u"Progress {} finished".format(pid))
        try:
            callbacks = self._progress_ids.pop(pid)
        except KeyError:
            pass
        else:
            for callback, __ in callbacks:
                if callback is not None:
                    callback(metadata, profile=profile)
        self.callListeners("progressFinished", pid, metadata, profile=profile)

    def progressErrorHandler(self, pid, err_msg, profile):
        log.warning(u"Progress {pid} error: {err_msg}".format(pid=pid, err_msg=err_msg))
        try:
            callbacks = self._progress_ids.pop(pid)
        except KeyError:
            pass
        else:
            for __, errback in callbacks:
                if errback is not None:
                    errback(err_msg, profile=profile)
        self.callListeners("progressError", pid, err_msg, profile=profile)

    def _subscribe_cb(self, answer, data):
        entity, profile = data
        type_ = "subscribed" if answer else "unsubscribed"
        self.bridge.subscription(type_, unicode(entity.bare), profile_key=profile)

    def subscribeHandler(self, type, raw_jid, profile):
        """Called when a subsciption management signal is received"""
        entity = jid.JID(raw_jid)
        if type == "subscribed":
            # this is a subscription confirmation, we just have to inform user
            # TODO: call self.getEntityMBlog to add the new contact blogs
            self.showDialog(
                _(u"The contact {contact} has accepted your subscription").format(
                    contact=entity.bare
                ),
                _(u"Subscription confirmation"),
            )
        elif type == "unsubscribed":
            # this is a subscription refusal, we just have to inform user
            self.showDialog(
                _(u"The contact {contact} has refused your subscription").format(
                    contact=entity.bare
                ),
                _(u"Subscription refusal"),
                "error",
            )
        elif type == "subscribe":
            # this is a subscriptionn request, we have to ask for user confirmation
            # TODO: use sat.stdui.ui_contact_list to display the groups selector
            self.showDialog(
                _(
                    u"The contact {contact} wants to subscribe to your presence"
                    u".\nDo you accept ?"
                ).format(contact=entity.bare),
                _("Subscription confirmation"),
                "yes/no",
                answer_cb=self._subscribe_cb,
                answer_data=(entity, profile),
            )

    def _debugHandler(self, action, parameters, profile):
        if action == u"widgets_dump":
            from pprint import pformat
            log.info(u"Widgets dump:\n{data}".format(data=pformat(self.widgets._widgets)))
        else:
            log.warning(u"Unknown debug action: {action}".format(action=action))


    def showDialog(self, message, title, type="info", answer_cb=None, answer_data=None):
        """Show a dialog to user

        Frontends must override this method
        @param message(unicode): body of the dialog
        @param title(unicode): title of the dialog
        @param type(unicode): one of:
            - "info": information dialog (callbacks not used)
            - "warning": important information to notice (callbacks not used)
            - "error": something went wrong (callbacks not used)
            - "yes/no": a dialog with 2 choices (yes and no)
        @param answer_cb(callable): method to call on answer.
            Arguments depend on dialog type:
            - "yes/no": argument is a boolean (True for yes)
        @param answer_data(object): data to link on callback
        """
        # FIXME: misnamed method + types are not well chosen. Need to be rethought
        raise NotImplementedError

    def showAlert(self, message):
        # FIXME: doesn't seems used anymore, to remove?
        pass  # FIXME

    def dialogFailure(self, failure):
        log.warning(u"Failure: {}".format(failure))

    def progressIdHandler(self, progress_id, profile):
        """Callback used when an action result in a progress id"""
        log.info(u"Progress ID received: {}".format(progress_id))

    def isHidden(self):
        """Tells if the frontend window is hidden.

        @return bool
        """
        raise NotImplementedError

    def paramUpdateHandler(self, name, value, namespace, profile):
        log.debug(
            _(u"param update: [%(namespace)s] %(name)s = %(value)s")
            % {"namespace": namespace, "name": name, "value": value}
        )
        if (namespace, name) == ("Connection", "JabberID"):
            log.debug(_(u"Changing JID to %s") % value)
            self.profiles[profile].whoami = jid.JID(value)
        elif (namespace, name) == ("General", C.SHOW_OFFLINE_CONTACTS):
            self.contact_lists[profile].showOfflineContacts(C.bool(value))
        elif (namespace, name) == ("General", C.SHOW_EMPTY_GROUPS):
            self.contact_lists[profile].showEmptyGroups(C.bool(value))

    def contactDeletedHandler(self, jid_s, profile):
        target = jid.JID(jid_s)
        self.contact_lists[profile].removeContact(target)

    def entityDataUpdatedHandler(self, entity_s, key, value, profile):
        entity = jid.JID(entity_s)
        if key == "nick":  # this is the roster nick, not the MUC nick
            if entity in self.contact_lists[profile]:
                self.contact_lists[profile].setCache(entity, "nick", value)
                self.callListeners("nick", entity, value, profile=profile)
        elif key == "avatar" and self.AVATARS_HANDLER:
            if value and entity in self.contact_lists[profile]:
                self.getAvatar(entity, ignore_cache=True, profile=profile)

    def actionManager(self, action_data, callback=None, ui_show_cb=None, user_action=True,
                      progress_cb=None, progress_eb=None, profile=C.PROF_KEY_NONE):
        """Handle backend action

        @param action_data(dict): action dict as sent by launchAction or returned by an
            UI action
        @param callback(None, callback): if not None, callback to use on XMLUI answer
        @param ui_show_cb(None, callback): if not None, method to call to show the XMLUI
        @param user_action(bool): if True, the action is a result of a user interaction
            else the action come from backend direclty (i.e. actionNew).
            This is useful to know if the frontend can display a popup immediately (if
            True) or if it should add it to a queue that the user can activate later.
        @param progress_cb(None, callable): method to call when progression is finished.
            Only make sense if a progress is expected in this action
        @param progress_eb(None, callable): method to call when something went wrong
            during progression.
            Only make sense if a progress is expected in this action
        """
        try:
            xmlui = action_data.pop("xmlui")
        except KeyError:
            pass
        else:
            ui = self.xmlui.create(
                self,
                xml_data=xmlui,
                flags=("FROM_BACKEND",) if not user_action else None,
                callback=callback,
                profile=profile,
            )
            if ui_show_cb is None:
                ui.show()
            else:
                ui_show_cb(ui)

        try:
            progress_id = action_data.pop("progress")
        except KeyError:
            pass
        else:
            if progress_cb or progress_eb:
                self.registerProgressCbs(progress_id, progress_cb, progress_eb)
            self.progressIdHandler(progress_id, profile)

        # we ignore metadata
        action_data = {
            k: v for k, v in action_data.iteritems() if not k.startswith("meta_")
        }

        if action_data:
            raise exceptions.DataError(
                u"Not all keys in action_data are managed ({keys})".format(
                    keys=", ".join(action_data.keys())
                )
            )

    def _actionCb(self, data, callback, callback_id, profile):
        if callback is None:
            self.actionManager(data, profile=profile)
        else:
            callback(data=data, cb_id=callback_id, profile=profile)

    def launchAction(
        self, callback_id, data=None, callback=None, profile=C.PROF_KEY_NONE
    ):
        """Launch a dynamic action

        @param callback_id: id of the action to launch
        @param data: data needed only for certain actions
        @param callback(callable, None): will be called with the resut
            if None, self.actionManager will be called
            else the callable will be called with the following kw parameters:
                - data: action_data
                - cb_id: callback id
                - profile: %(doc_profile)s
        @param profile: %(doc_profile)s

        """
        if data is None:
            data = dict()
        action_cb = lambda data: self._actionCb(data, callback, callback_id, profile)
        self.bridge.launchAction(
            callback_id, data, profile, callback=action_cb, errback=self.dialogFailure
        )

    def launchMenu(
        self,
        menu_type,
        path,
        data=None,
        callback=None,
        security_limit=C.SECURITY_LIMIT_MAX,
        profile=C.PROF_KEY_NONE,
    ):
        """Launch a menu manually

        @param menu_type(unicode): type of the menu to launch
        @param path(iterable[unicode]): path to the menu
        @param data: data needed only for certain actions
        @param callback(callable, None): will be called with the resut
            if None, self.actionManager will be called
            else the callable will be called with the following kw parameters:
                - data: action_data
                - cb_id: (menu_type, path) tuple
                - profile: %(doc_profile)s
        @param profile: %(doc_profile)s

        """
        if data is None:
            data = dict()
        action_cb = lambda data: self._actionCb(
            data, callback, (menu_type, path), profile
        )
        self.bridge.menuLaunch(
            menu_type,
            path,
            data,
            security_limit,
            profile,
            callback=action_cb,
            errback=self.dialogFailure,
        )

    def _avatarGetCb(self, avatar_path, entity, contact_list, profile):
        path = avatar_path or self.getDefaultAvatar(entity)
        contact_list.setCache(entity, "avatar", path)
        self.callListeners("avatar", entity, path, profile=profile)

    def _avatarGetEb(self, failure, entity, contact_list):
        log.warning(u"Can't get avatar: {}".format(failure))
        contact_list.setCache(entity, "avatar", self.getDefaultAvatar(entity))

    def getAvatar(
        self,
        entity,
        cache_only=True,
        hash_only=False,
        ignore_cache=False,
        profile=C.PROF_KEY_NONE,
    ):
        """return avatar path for an entity

        @param entity(jid.JID): entity to get avatar from
        @param cache_only(bool): if False avatar will be requested if not in cache
            with current vCard based implementation, it's better to keep True
            except if we request avatars for roster items
        @param hash_only(bool): if True avatar hash is returned, else full path
        @param ignore_cache(bool): if False, won't check local cache and will request
            backend in every case
        @return (unicode, None): avatar full path (None if no avatar found)
        """
        contact_list = self.contact_lists[profile]
        if ignore_cache:
            avatar = None
        else:
            try:
                avatar = contact_list.getCache(entity, "avatar", bare_default=None)
            except exceptions.NotFound:
                avatar = None
        if avatar is None:
            self.bridge.avatarGet(
                unicode(entity),
                cache_only,
                hash_only,
                profile=profile,
                callback=lambda path: self._avatarGetCb(
                    path, entity, contact_list, profile
                ),
                errback=lambda failure: self._avatarGetEb(failure, entity, contact_list),
            )
            # we set avatar to empty string to avoid requesting several time the same
            # avatar while we are waiting for avatarGet result
            contact_list.setCache(entity, "avatar", "")
        return avatar

    def getDefaultAvatar(self, entity=None):
        """return default avatar to use with given entity

        must be implemented by frontend
        @param entity(jid.JID): entity for which a default avatar is needed
        """
        raise NotImplementedError

    def disconnect(self, profile):
        log.info("disconnecting")
        self.callListeners("disconnect", profile=profile)
        self.bridge.disconnect(profile)

    def onExit(self):
        """Must be called when the frontend is terminating"""
        to_unplug = []
        for profile, profile_manager in self.profiles.iteritems():
            if profile_manager.connected and profile_manager.autodisconnect:
                # The user wants autodisconnection
                self.disconnect(profile)
            to_unplug.append(profile)
        for profile in to_unplug:
            self.unplug_profile(profile)
