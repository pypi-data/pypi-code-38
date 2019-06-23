#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for file tansfer
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

import sys
import os
import os.path
import tempfile
from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger
from sat.core import exceptions
from twisted.internet import reactor
from twisted.internet import protocol
from twisted.internet import error as int_error
from twisted.web import client as web_client

log = getLogger(__name__)

PLUGIN_INFO = {
    C.PI_NAME: "Android ",
    C.PI_IMPORT_NAME: "android",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_RECOMMENDATIONS: [u"XEP-0352"],
    C.PI_MAIN: "AndroidPlugin",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: D_(
        """Manage Android platform specificities, like pause or notifications"""
    ),
}

if sys.platform != "android":
    raise exceptions.CancelError(u"this module is not needed on this platform")


from plyer import notification, vibrator
from plyer.platforms.android import activity
from jnius import autoclass
from android.broadcast import BroadcastReceiver

#: delay between a pause event and sending the inactive indication to server, in seconds
#: we don't send the indication immediately because user can be just checking something
#: quickly on an other app.
CSI_DELAY = 30

PARAM_VIBRATE_CATEGORY = "Notifications"
PARAM_VIBRATE_NAME = "vibrate"
PARAM_VIBRATE_LABEL = D_(u"Vibrate on notifications")
SOCKET_DIR = "/data/data/org.salutatoi.cagou/"
SOCKET_FILE = ".socket"
STATE_RUNNING = "running"
STATE_PAUSED = "paused"
STATE_STOPPED = "stopped"
STATES = (STATE_RUNNING, STATE_PAUSED, STATE_STOPPED)
NET_TYPE_NONE = "no network"
NET_TYPE_WIFI = "wifi"
NET_TYPE_MOBILE = "mobile"
NET_TYPE_OTHER = "other"


Context = autoclass('android.content.Context')
ConnectivityManager = autoclass('android.net.ConnectivityManager')


def determineLength_workaround(self, fObj):
    """Method working around seek() bug on Android"""
    try:
        seek = fObj.seek
        tell = fObj.tell
    except AttributeError:
        return web_client.UNKNOWN_LENGTH
    originalPosition = tell()
    seek(os.SEEK_END)
    end = tell()
    seek(os.SEEK_SET, originalPosition)
    return end - originalPosition


def patch_seek_bug():
    """Check seek bug and apply a workaround if still here

    cf. https://github.com/kivy/python-for-android/issues/1768
    """
    with tempfile.TemporaryFile() as f:
        f.write(b'1234567890')
        f.seek(0, os.SEEK_END)
        size = f.tell()
    if size == 10:
        log.info(u"seek() bug not present anymore, workaround code can be removed")
    else:
        log.warning(u"seek() bug detected, applying a workaround")
        web_client.FileBodyProducer._determineLength = determineLength_workaround

patch_seek_bug()


class FrontendStateProtocol(protocol.Protocol):

    def __init__(self, android_plugin):
        self.android_plugin = android_plugin

    def dataReceived(self, data):
        if data in STATES:
            self.android_plugin.state = data
        else:
            log.warning(u"Unexpected data: {data}".format(data=data))


class FrontendStateFactory(protocol.Factory):

    def __init__(self, android_plugin):
        self.android_plugin = android_plugin

    def buildProtocol(self, addr):
        return FrontendStateProtocol(self.android_plugin)



class AndroidPlugin(object):

    params = """
    <params>
    <individual>
    <category name="{category_name}" label="{category_label}">
        <param name="{param_name}" label="{param_label}" value="true" type="bool" security="0" />
     </category>
    </individual>
    </params>
    """.format(
        category_name=PARAM_VIBRATE_CATEGORY,
        category_label=D_(PARAM_VIBRATE_CATEGORY),
        param_name=PARAM_VIBRATE_NAME,
        param_label=PARAM_VIBRATE_LABEL,
    )

    def __init__(self, host):
        log.info(_(u"plugin Android initialization"))
        self.host = host
        self._csi = host.plugins.get(u'XEP-0352')
        self._csi_timer = None
        host.memory.updateParams(self.params)
        try:
            os.mkdir(SOCKET_DIR, 0700)
        except OSError as e:
            if e.errno == 17:
                # dir already exists
                pass
            else:
                raise e
        self._state = None
        factory = FrontendStateFactory(self)
        socket_path = os.path.join(SOCKET_DIR, SOCKET_FILE)
        try:
            reactor.listenUNIX(socket_path, factory)
        except int_error.CannotListenError as e:
            if e.socketError.errno == 98:
                # the address is already in use, we need to remove it
                os.unlink(socket_path)
                reactor.listenUNIX(socket_path, factory)
            else:
                raise e
        # we set a low priority because we want the notification to be sent after all
        # plugins have done their job
        host.trigger.add("MessageReceived", self.messageReceivedTrigger, priority=-1000)

        # Connectivity handling
        self.cm = activity.getSystemService(Context.CONNECTIVITY_SERVICE)
        self._net_type = None
        self._checkConnectivity()
        # XXX: we need to keep a reference to BroadcastReceiver to avoid
        #     "XXX has no attribute 'invoke'" error (looks like the same issue as
        #     https://github.com/kivy/pyjnius/issues/59)
        self.br = BroadcastReceiver(
            callback=lambda *args, **kwargs: reactor.callLater(0,
                                                              self.onConnectivityChange),
            actions=[u"android.net.conn.CONNECTIVITY_CHANGE"])
        self.br.start()


    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        log.debug(u"frontend state has changed: {state}".format(state=new_state))
        previous_state = self._state
        self._state = new_state
        if new_state == STATE_RUNNING:
            self._onRunning(previous_state)
        elif new_state == STATE_PAUSED:
            self._onPaused(previous_state)
        elif new_state == STATE_STOPPED:
            self._onStopped(previous_state)

    @property
    def cagou_active(self):
        return self._state == STATE_RUNNING

    def _onRunning(self, previous_state):
        if previous_state is not None:
            self.host.bridge.bridgeReactivateSignals()
        self.setActive()

    def _onPaused(self, previous_state):
        self.host.bridge.bridgeDeactivateSignals()
        self.setInactive()

    def _onStopped(self, previous_state):
        self.setInactive()

    def _notifyMessage(self, mess_data, client):
        """Send notification when suitable

        notification is sent if:
            - there is a message and it is not a groupchat
            - message is not coming from ourself
        """
        if (mess_data["message"] and mess_data["type"] != C.MESS_TYPE_GROUPCHAT
            and not mess_data["from"].userhostJID() == client.jid.userhostJID()):
            message = mess_data["message"].itervalues().next()
            try:
                subject = mess_data["subject"].itervalues().next()
            except StopIteration:
                subject = u"Cagou new message"

            notification.notify(title=subject, message=message)
            if self.host.memory.getParamA(
                PARAM_VIBRATE_NAME, PARAM_VIBRATE_CATEGORY, profile_key=client.profile
            ):
                vibrator.vibrate()
        return mess_data

    def messageReceivedTrigger(self, client, message_elt, post_treat):
        if not self.cagou_active:
            # we only send notification is the frontend is not displayed
            post_treat.addCallback(self._notifyMessage, client)

        return True

    # CSI

    def _setInactive(self):
        self._csi_timer = None
        for client in self.host.getClients(C.PROF_KEY_ALL):
            self._csi.setInactive(client)

    def setInactive(self):
        if self._csi is None or self._csi_timer is not None:
            return
        self._csi_timer = reactor.callLater(CSI_DELAY, self._setInactive)

    def setActive(self):
        if self._csi is None:
            return
        if self._csi_timer is not None:
            self._csi_timer.cancel()
            self._csi_timer = None
        for client in self.host.getClients(C.PROF_KEY_ALL):
            self._csi.setActive(client)

    # Connectivity

    def _handleNetworkChange(self, previous, new):
        """Notify the clients about network changes.

        This way the client can disconnect/reconnect transport, or change delays
        """
        if new == NET_TYPE_NONE:
            for client in self.host.getClients(C.PROF_KEY_ALL):
                client.networkDisabled()
        elif previous == NET_TYPE_NONE:
            for client in self.host.getClients(C.PROF_KEY_ALL):
                client.networkEnabled()

    def _checkConnectivity(self):
        active_network = self.cm.getActiveNetworkInfo()
        if active_network is None:
            net_type = NET_TYPE_NONE
        else:
            net_type_android = active_network.getType()
            if net_type_android == ConnectivityManager.TYPE_WIFI:
                net_type = NET_TYPE_WIFI
            elif net_type_android == ConnectivityManager.TYPE_MOBILE:
                net_type = NET_TYPE_MOBILE
            else:
                net_type = NET_TYPE_OTHER
        if net_type != self._net_type:
            log.info(u"connectivity has changed")
            previous = self._net_type
            self._net_type = net_type
            if net_type == NET_TYPE_NONE:
                log.info(u"no network active")
            elif net_type == NET_TYPE_WIFI:
                log.info(u"WIFI activated")
            elif net_type == NET_TYPE_MOBILE:
                log.info(u"mobile data activated")
            else:
                log.info(u"network activated (type={net_type_android})"
                    .format(net_type_android=net_type_android))
            self._handleNetworkChange(previous, net_type)
        else:
            log.debug(u"_checkConnectivity called without network change ({net_type})"
                .format(net_type = net_type))


    def onConnectivityChange(self):
        log.debug(u"onConnectivityChange called")
        self._checkConnectivity()
