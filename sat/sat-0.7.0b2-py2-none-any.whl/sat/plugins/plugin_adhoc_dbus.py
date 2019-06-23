#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for adding D-Bus to Ad-Hoc Commands
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

from sat.core.i18n import D_, _
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from wokkel import data_form

try:
    from lxml import etree
except ImportError:
    etree = None
    log.warning(u"Missing module lxml, please download/install it from http://lxml.de/"
                u"auto D-Bus discovery will be disabled")
from collections import OrderedDict
import os.path
import uuid
try:
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
except ImportError:
    dbus = None
    log.warning(u"Missing module dbus, please download/install it"
                u"auto D-Bus discovery will be disabled")

else:
    DBusGMainLoop(set_as_default=True)

NS_MEDIA_PLAYER = "org.salutatoi.mediaplayer"
FD_NAME = "org.freedesktop.DBus"
FD_PATH = "/org/freedekstop/DBus"
INTROSPECT_IFACE = "org.freedesktop.DBus.Introspectable"
MPRIS_PREFIX = u"org.mpris.MediaPlayer2"
CMD_GO_BACK = u"GoBack"
CMD_GO_FWD = u"GoFW"
SEEK_OFFSET = 5 * 1000 * 1000
MPRIS_COMMANDS = [u"org.mpris.MediaPlayer2.Player." + cmd for cmd in (
    u"Previous", CMD_GO_BACK, u"PlayPause", CMD_GO_FWD, u"Next")]
MPRIS_PATH = u"/org/mpris/MediaPlayer2"
MPRIS_PROPERTIES = OrderedDict((
    (u"org.mpris.MediaPlayer2", (
        "Identity",
        )),
    (u"org.mpris.MediaPlayer2.Player", (
        "Metadata",
        "PlaybackStatus",
        "Volume",
        )),
    ))
MPRIS_METADATA_KEY = "Metadata"
MPRIS_METADATA_MAP = OrderedDict((
    ("xesam:title", u"Title"),
    ))

INTROSPECT_METHOD = "Introspect"
IGNORED_IFACES_START = (
    "org.freedesktop",
    "org.qtproject",
    "org.kde.KMainWindow",
)  # commands in interface starting with these values will be ignored
FLAG_LOOP = "LOOP"

PLUGIN_INFO = {
    C.PI_NAME: "Ad-Hoc Commands - D-Bus",
    C.PI_IMPORT_NAME: "AD_HOC_DBUS",
    C.PI_TYPE: "Misc",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0050"],
    C.PI_MAIN: "AdHocDBus",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(u"""Add D-Bus management to Ad-Hoc commands"""),
}


class AdHocDBus(object):

    def __init__(self, host):
        log.info(_("plugin Ad-Hoc D-Bus initialization"))
        self.host = host
        if etree is not None:
            host.bridge.addMethod(
                "adHocDBusAddAuto",
                ".plugin",
                in_sign="sasasasasasass",
                out_sign="(sa(sss))",
                method=self._adHocDBusAddAuto,
                async=True,
            )
        host.bridge.addMethod(
            "adHocRemotesGet",
            ".plugin",
            in_sign="s",
            out_sign="a(sss)",
            method=self._adHocRemotesGet,
            async=True,
        )
        self._c = host.plugins["XEP-0050"]
        host.registerNamespace(u"mediaplayer", NS_MEDIA_PLAYER)
        if dbus is not None:
            self.session_bus = dbus.SessionBus()
            self.fd_object = self.session_bus.get_object(
                FD_NAME, FD_PATH, introspect=False)

    def profileConnected(self, client):
        if dbus is not None:
            self._c.addAdHocCommand(
                client, self.localMediaCb, D_(u"Media Players"),
                node=NS_MEDIA_PLAYER,
                timeout=60*60*6  # 6 hours timeout, to avoid breaking remote
                                 # in the middle of a movie
            )

    def _DBusAsyncCall(self, proxy, method, *args, **kwargs):
        """ Call a DBus method asynchronously and return a deferred

        @param proxy: DBus object proxy, as returner by get_object
        @param method: name of the method to call
        @param args: will be transmitted to the method
        @param kwargs: will be transmetted to the method, except for the following poped
                       values:
                       - interface: name of the interface to use
        @return: a deferred

        """
        d = defer.Deferred()
        interface = kwargs.pop("interface", None)
        kwargs["reply_handler"] = lambda ret=None: d.callback(ret)
        kwargs["error_handler"] = d.errback
        proxy.get_dbus_method(method, dbus_interface=interface)(*args, **kwargs)
        return d

    def _DBusGetProperty(self, proxy, interface, name):
        return self._DBusAsyncCall(
            proxy, u"Get", interface, name, interface=u"org.freedesktop.DBus.Properties")


    def _DBusListNames(self):
        return self._DBusAsyncCall(self.fd_object, "ListNames")

    def _DBusIntrospect(self, proxy):
        return self._DBusAsyncCall(proxy, INTROSPECT_METHOD, interface=INTROSPECT_IFACE)

    def _acceptMethod(self, method):
        """ Return True if we accept the method for a command
        @param method: etree.Element
        @return: True if the method is acceptable

        """
        if method.xpath(
            "arg[@direction='in']"
        ):  # we don't accept method with argument for the moment
            return False
        return True

    @defer.inlineCallbacks
    def _introspect(self, methods, bus_name, proxy):
        log.debug("introspecting path [%s]" % proxy.object_path)
        introspect_xml = yield self._DBusIntrospect(proxy)
        el = etree.fromstring(introspect_xml)
        for node in el.iterchildren("node", "interface"):
            if node.tag == "node":
                new_path = os.path.join(proxy.object_path, node.get("name"))
                new_proxy = self.session_bus.get_object(
                    bus_name, new_path, introspect=False
                )
                yield self._introspect(methods, bus_name, new_proxy)
            elif node.tag == "interface":
                name = node.get("name")
                if any(name.startswith(ignored) for ignored in IGNORED_IFACES_START):
                    log.debug("interface [%s] is ignored" % name)
                    continue
                log.debug("introspecting interface [%s]" % name)
                for method in node.iterchildren("method"):
                    if self._acceptMethod(method):
                        method_name = method.get("name")
                        log.debug("method accepted: [%s]" % method_name)
                        methods.add((proxy.object_path, name, method_name))

    def _adHocDBusAddAuto(self, prog_name, allowed_jids, allowed_groups, allowed_magics,
                          forbidden_jids, forbidden_groups, flags, profile_key):
        client = self.host.getClient(profile_key)
        return self.adHocDBusAddAuto(
            client, prog_name, allowed_jids, allowed_groups, allowed_magics,
            forbidden_jids, forbidden_groups, flags)

    @defer.inlineCallbacks
    def adHocDBusAddAuto(self, client, prog_name, allowed_jids=None, allowed_groups=None,
                         allowed_magics=None, forbidden_jids=None, forbidden_groups=None,
                         flags=None):
        bus_names = yield self._DBusListNames()
        bus_names = [bus_name for bus_name in bus_names if "." + prog_name in bus_name]
        if not bus_names:
            log.info("Can't find any bus for [%s]" % prog_name)
            defer.returnValue(("", []))
        bus_names.sort()
        for bus_name in bus_names:
            if bus_name.endswith(prog_name):
                break
        log.info("bus name found: [%s]" % bus_name)
        proxy = self.session_bus.get_object(bus_name, "/", introspect=False)
        methods = set()

        yield self._introspect(methods, bus_name, proxy)

        if methods:
            self._addCommand(
                client,
                prog_name,
                bus_name,
                methods,
                allowed_jids=allowed_jids,
                allowed_groups=allowed_groups,
                allowed_magics=allowed_magics,
                forbidden_jids=forbidden_jids,
                forbidden_groups=forbidden_groups,
                flags=flags,
            )

        defer.returnValue((bus_name, methods))

    def _addCommand(self, client, adhoc_name, bus_name, methods, allowed_jids=None,
                    allowed_groups=None, allowed_magics=None, forbidden_jids=None,
                    forbidden_groups=None, flags=None):
        if flags is None:
            flags = set()

        def DBusCallback(client, command_elt, session_data, action, node):
            actions = session_data.setdefault("actions", [])
            names_map = session_data.setdefault("names_map", {})
            actions.append(action)

            if len(actions) == 1:
                # it's our first request, we ask the desired new status
                status = self._c.STATUS.EXECUTING
                form = data_form.Form("form", title=_("Command selection"))
                options = []
                for path, iface, command in methods:
                    label = command.rsplit(".", 1)[-1]
                    name = str(uuid.uuid4())
                    names_map[name] = (path, iface, command)
                    options.append(data_form.Option(name, label))

                field = data_form.Field(
                    "list-single", "command", options=options, required=True
                )
                form.addField(field)

                payload = form.toElement()
                note = None

            elif len(actions) == 2:
                # we should have the answer here
                try:
                    x_elt = command_elt.elements(data_form.NS_X_DATA, "x").next()
                    answer_form = data_form.Form.fromElement(x_elt)
                    command = answer_form["command"]
                except (KeyError, StopIteration):
                    raise self._c.AdHocError(self._c.ERROR.BAD_PAYLOAD)

                if command not in names_map:
                    raise self._c.AdHocError(self._c.ERROR.BAD_PAYLOAD)

                path, iface, command = names_map[command]
                proxy = self.session_bus.get_object(bus_name, path)

                self._DBusAsyncCall(proxy, command, interface=iface)

                # job done, we can end the session, except if we have FLAG_LOOP
                if FLAG_LOOP in flags:
                    # We have a loop, so we clear everything and we execute again the
                    # command as we had a first call (command_elt is not used, so None
                    # is OK)
                    del actions[:]
                    names_map.clear()
                    return DBusCallback(
                        client, None, session_data, self._c.ACTION.EXECUTE, node
                    )
                form = data_form.Form("form", title=_(u"Updated"))
                form.addField(data_form.Field("fixed", u"Command sent"))
                status = self._c.STATUS.COMPLETED
                payload = None
                note = (self._c.NOTE.INFO, _(u"Command sent"))
            else:
                raise self._c.AdHocError(self._c.ERROR.INTERNAL)

            return (payload, status, None, note)

        self._c.addAdHocCommand(
            client,
            DBusCallback,
            adhoc_name,
            allowed_jids=allowed_jids,
            allowed_groups=allowed_groups,
            allowed_magics=allowed_magics,
            forbidden_jids=forbidden_jids,
            forbidden_groups=forbidden_groups,
        )

    ## Local media ##

    def _adHocRemotesGet(self, profile):
        return self.adHocRemotesGet(self.host.getClient(profile))

    @defer.inlineCallbacks
    def adHocRemotesGet(self, client):
        """Retrieve available remote media controlers in our devices
        @return (list[tuple[unicode, unicode, unicode]]): list of devices with:
            - entity full jid
            - device name
            - device label
        """
        found_data = yield self.host.findByFeatures(
            client, [self.host.ns_map['commands']], service=False, roster=False,
            own_jid=True, local_device=True)

        remotes = []

        for found in found_data:
            for device_jid_s in found:
                device_jid = jid.JID(device_jid_s)
                cmd_list = yield self._c.list(client, device_jid)
                for cmd in cmd_list:
                    if cmd.nodeIdentifier == NS_MEDIA_PLAYER:
                        try:
                            result_elt = yield self._c.do(client, device_jid,
                                                          NS_MEDIA_PLAYER, timeout=5)
                            command_elt = self._c.getCommandElt(result_elt)
                            form = data_form.findForm(command_elt, NS_MEDIA_PLAYER)
                            mp_options = form.fields['media_player'].options
                            session_id = command_elt.getAttribute('sessionid')
                            if mp_options and session_id:
                                # we just want to discover player, so we cancel the
                                # session
                                self._c.do(client, device_jid, NS_MEDIA_PLAYER,
                                           action=self._c.ACTION.CANCEL,
                                           session_id=session_id)

                            for opt in mp_options:
                                remotes.append((device_jid_s,
                                                opt.value,
                                                opt.label or opt.value))
                        except Exception as e:
                            log.warning(_(
                                u"Can't retrieve remote controllers on {device_jid}: "
                                u"{reason}".format(device_jid=device_jid, reason=e)))
                        break
        defer.returnValue(remotes)

    def doMPRISCommand(self, proxy, command):
        iface, command = command.rsplit(u".", 1)
        if command == CMD_GO_BACK:
            command = u'Seek'
            args = [-SEEK_OFFSET]
        elif command == CMD_GO_FWD:
            command = u'Seek'
            args = [SEEK_OFFSET]
        else:
            args = []
        return self._DBusAsyncCall(proxy, command, *args, interface=iface)

    def addMPRISMetadata(self, form, metadata):
        """Serialise MRPIS Metadata according to MPRIS_METADATA_MAP"""
        for mpris_key, name in MPRIS_METADATA_MAP.iteritems():
            if mpris_key in metadata:
                value = unicode(metadata[mpris_key])
                form.addField(data_form.Field(fieldType=u"fixed",
                                              var=name,
                                              value=value))

    @defer.inlineCallbacks
    def localMediaCb(self, client, command_elt, session_data, action, node):
        try:
            x_elt = command_elt.elements(data_form.NS_X_DATA, "x").next()
            command_form = data_form.Form.fromElement(x_elt)
        except StopIteration:
            command_form = None

        if command_form is None or len(command_form.fields) == 0:
            # root request, we looks for media players
            bus_names = yield self._DBusListNames()
            bus_names = [b for b in bus_names if b.startswith(MPRIS_PREFIX)]
            if len(bus_names) == 0:
                note = (self._c.NOTE.INFO, D_(u"No media player found."))
                defer.returnValue((None, self._c.STATUS.COMPLETED, None, note))
            options = []
            status = self._c.STATUS.EXECUTING
            form = data_form.Form("form", title=D_(u"Media Player Selection"),
                                  formNamespace=NS_MEDIA_PLAYER)
            for bus in bus_names:
                player_name = bus[len(MPRIS_PREFIX)+1:]
                if not player_name:
                    log.warning(_(u"Ignoring MPRIS bus without suffix"))
                    continue
                options.append(data_form.Option(bus, player_name))
            field = data_form.Field(
                "list-single", "media_player", options=options, required=True
            )
            form.addField(field)
            payload = form.toElement()
            defer.returnValue((payload, status, None, None))
        else:
            # player request
            try:
                bus_name = command_form[u"media_player"]
            except KeyError:
                raise ValueError(_(u"missing media_player value"))

            if not bus_name.startswith(MPRIS_PREFIX):
                log.warning(_(u"Media player ad-hoc command trying to use non MPRIS bus. "
                              u"Hack attempt? Refused bus: {bus_name}").format(
                              bus_name=bus_name))
                note = (self._c.NOTE.ERROR, D_(u"Invalid player name."))
                defer.returnValue((None, self._c.STATUS.COMPLETED, None, note))

            try:
                proxy = self.session_bus.get_object(bus_name, MPRIS_PATH)
            except dbus.exceptions.DBusException as e:
                log.warning(_(u"Can't get D-Bus proxy: {reason}").format(reason=e))
                note = (self._c.NOTE.ERROR, D_(u"Media player is not available anymore"))
                defer.returnValue((None, self._c.STATUS.COMPLETED, None, note))
            try:
                command = command_form[u"command"]
            except KeyError:
                pass
            else:
                yield self.doMPRISCommand(proxy, command)

            # we construct the remote control form
            form = data_form.Form("form", title=D_(u"Media Player Selection"))
            form.addField(data_form.Field(fieldType=u"hidden",
                                          var=u"media_player",
                                          value=bus_name))
            for iface, properties_names in MPRIS_PROPERTIES.iteritems():
                for name in properties_names:
                    try:
                        value = yield self._DBusGetProperty(proxy, iface, name)
                    except Exception as e:
                        log.warning(_(u"Can't retrieve attribute {name}: {reason}")
                                    .format(name=name, reason=e))
                        continue
                    if name == MPRIS_METADATA_KEY:
                        self.addMPRISMetadata(form, value)
                    else:
                        form.addField(data_form.Field(fieldType=u"fixed",
                                                      var=name,
                                                      value=unicode(value)))

            commands = [data_form.Option(c, c.rsplit(u".", 1)[1]) for c in MPRIS_COMMANDS]
            form.addField(data_form.Field(fieldType=u"list-single",
                                          var=u"command",
                                          options=commands,
                                          required=True))

            payload = form.toElement()
            status = self._c.STATUS.EXECUTING
            defer.returnValue((payload, status, None, None))
