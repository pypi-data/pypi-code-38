#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Ad-Hoc Commands (XEP-0050)
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

log = getLogger(__name__)
from twisted.words.protocols.jabber import jid
from twisted.words.protocols import jabber
from twisted.words.xish import domish
from twisted.internet import defer
from wokkel import disco, iwokkel, data_form
from sat.core import exceptions
from sat.memory.memory import Sessions
from uuid import uuid4
from sat.tools import xml_tools

from zope.interface import implements

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

from collections import namedtuple

try:
    from collections import OrderedDict  # only available from python 2.7
except ImportError:
    from ordereddict import OrderedDict

IQ_SET = '/iq[@type="set"]'
NS_COMMANDS = "http://jabber.org/protocol/commands"
ID_CMD_LIST = disco.DiscoIdentity("automation", "command-list")
ID_CMD_NODE = disco.DiscoIdentity("automation", "command-node")
CMD_REQUEST = IQ_SET + '/command[@xmlns="' + NS_COMMANDS + '"]'

SHOWS = OrderedDict(
    [
        ("default", _("Online")),
        ("away", _("Away")),
        ("chat", _("Free for chat")),
        ("dnd", _("Do not disturb")),
        ("xa", _("Left")),
        ("disconnect", _("Disconnect")),
    ]
)

PLUGIN_INFO = {
    C.PI_NAME: "Ad-Hoc Commands",
    C.PI_IMPORT_NAME: "XEP-0050",
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0050"],
    C.PI_MAIN: "XEP_0050",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _(u"""Implementation of Ad-Hoc Commands"""),
}


class AdHocError(Exception):
    def __init__(self, error_const):
        """ Error to be used from callback
        @param error_const: one of XEP_0050.ERROR
        """
        assert error_const in XEP_0050.ERROR
        self.callback_error = error_const


class AdHocCommand(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, callback, label, node, features, timeout,
                 allowed_jids, allowed_groups, allowed_magics, forbidden_jids,
                forbidden_groups):
        XMPPHandler.__init__(self)
        self.callback = callback
        self.label = label
        self.node = node
        self.features = [disco.DiscoFeature(feature) for feature in features]
        (
            self.allowed_jids,
            self.allowed_groups,
            self.allowed_magics,
            self.forbidden_jids,
            self.forbidden_groups,
        ) = (
            allowed_jids,
            allowed_groups,
            allowed_magics,
            forbidden_jids,
            forbidden_groups,
        )
        self.sessions = Sessions(timeout=timeout)

    @property
    def client(self):
        return self.parent

    def getName(self, xml_lang=None):
        return self.label

    def isAuthorised(self, requestor):
        if "@ALL@" in self.allowed_magics:
            return True
        forbidden = set(self.forbidden_jids)
        for group in self.forbidden_groups:
            forbidden.update(self.client.roster.getJidsFromGroup(group))
        if requestor.userhostJID() in forbidden:
            return False
        allowed = set(self.allowed_jids)
        for group in self.allowed_groups:
            try:
                allowed.update(self.client.roster.getJidsFromGroup(group))
            except exceptions.UnknownGroupError:
                log.warning(_(u"The groups [{group}] is unknown for profile [{profile}])")
                            .format(group=group, profile=self.client.profile))
        if requestor.userhostJID() in allowed:
            return True
        return False

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        if (
            nodeIdentifier != NS_COMMANDS
        ):  # FIXME: we should manage other disco nodes here
            return []
        # identities = [ID_CMD_LIST if self.node == NS_COMMANDS else ID_CMD_NODE] # FIXME
        return [disco.DiscoFeature(NS_COMMANDS)] + self.features

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

    def _sendAnswer(self, callback_data, session_id, request):
        """ Send result of the command

        @param callback_data: tuple (payload, status, actions, note) with:
            - payload (domish.Element, None) usualy containing data form
            - status: current status, see XEP_0050.STATUS
            - actions(list[str], None): list of allowed actions (see XEP_0050.ACTION).
                       First action is the default one. Default to EXECUTE
            - note(tuple[str, unicode]): optional additional note: either None or a
                tuple with (note type, human readable string), "note type" being in
                XEP_0050.NOTE
        @param session_id: current session id
        @param request: original request (domish.Element)
        @return: deferred
        """
        payload, status, actions, note = callback_data
        assert isinstance(payload, domish.Element) or payload is None
        assert status in XEP_0050.STATUS
        if not actions:
            actions = [XEP_0050.ACTION.EXECUTE]
        result = domish.Element((None, "iq"))
        result["type"] = "result"
        result["id"] = request["id"]
        result["to"] = request["from"]
        command_elt = result.addElement("command", NS_COMMANDS)
        command_elt["sessionid"] = session_id
        command_elt["node"] = self.node
        command_elt["status"] = status

        if status != XEP_0050.STATUS.CANCELED:
            if status != XEP_0050.STATUS.COMPLETED:
                actions_elt = command_elt.addElement("actions")
                actions_elt["execute"] = actions[0]
                for action in actions:
                    actions_elt.addElement(action)

            if note is not None:
                note_type, note_mess = note
                note_elt = command_elt.addElement("note", content=note_mess)
                note_elt["type"] = note_type

            if payload is not None:
                command_elt.addChild(payload)

        self.client.send(result)
        if status in (XEP_0050.STATUS.COMPLETED, XEP_0050.STATUS.CANCELED):
            del self.sessions[session_id]

    def _sendError(self, error_constant, session_id, request):
        """ Send error stanza

        @param error_constant: one of XEP_OO50.ERROR
        @param request: original request (domish.Element)
        """
        xmpp_condition, cmd_condition = error_constant
        iq_elt = jabber.error.StanzaError(xmpp_condition).toResponse(request)
        if cmd_condition:
            error_elt = iq_elt.elements(None, "error").next()
            error_elt.addElement(cmd_condition, NS_COMMANDS)
        self.client.send(iq_elt)
        del self.sessions[session_id]

    def onRequest(self, command_elt, requestor, action, session_id):
        if not self.isAuthorised(requestor):
            return self._sendError(
                XEP_0050.ERROR.FORBIDDEN, session_id, command_elt.parent
            )
        if session_id:
            try:
                session_data = self.sessions[session_id]
            except KeyError:
                return self._sendError(
                    XEP_0050.ERROR.SESSION_EXPIRED, session_id, command_elt.parent
                )
            if session_data["requestor"] != requestor:
                return self._sendError(
                    XEP_0050.ERROR.FORBIDDEN, session_id, command_elt.parent
                )
        else:
            session_id, session_data = self.sessions.newSession()
            session_data["requestor"] = requestor
        if action == XEP_0050.ACTION.CANCEL:
            d = defer.succeed((None, XEP_0050.STATUS.CANCELED, None, None))
        else:
            d = defer.maybeDeferred(
                self.callback,
                self.client,
                command_elt,
                session_data,
                action,
                self.node,
            )
        d.addCallback(self._sendAnswer, session_id, command_elt.parent)
        d.addErrback(
            lambda failure, request: self._sendError(
                failure.value.callback_error, session_id, request
            ),
            command_elt.parent,
        )


class XEP_0050(object):
    STATUS = namedtuple("Status", ("EXECUTING", "COMPLETED", "CANCELED"))(
        "executing", "completed", "canceled"
    )
    ACTION = namedtuple("Action", ("EXECUTE", "CANCEL", "NEXT", "PREV"))(
        "execute", "cancel", "next", "prev"
    )
    NOTE = namedtuple("Note", ("INFO", "WARN", "ERROR"))("info", "warn", "error")
    ERROR = namedtuple(
        "Error",
        (
            "MALFORMED_ACTION",
            "BAD_ACTION",
            "BAD_LOCALE",
            "BAD_PAYLOAD",
            "BAD_SESSIONID",
            "SESSION_EXPIRED",
            "FORBIDDEN",
            "ITEM_NOT_FOUND",
            "FEATURE_NOT_IMPLEMENTED",
            "INTERNAL",
        ),
    )(
        ("bad-request", "malformed-action"),
        ("bad-request", "bad-action"),
        ("bad-request", "bad-locale"),
        ("bad-request", "bad-payload"),
        ("bad-request", "bad-sessionid"),
        ("not-allowed", "session-expired"),
        ("forbidden", None),
        ("item-not-found", None),
        ("feature-not-implemented", None),
        ("internal-server-error", None),
    )  # XEP-0050 §4.4 Table 5

    def __init__(self, host):
        log.info(_("plugin XEP-0050 initialization"))
        self.host = host
        self.requesting = Sessions()
        host.bridge.addMethod(
            "adHocRun",
            ".plugin",
            in_sign="sss",
            out_sign="s",
            method=self._run,
            async=True,
        )
        host.bridge.addMethod(
            "adHocList",
            ".plugin",
            in_sign="ss",
            out_sign="s",
            method=self._listUI,
            async=True,
        )
        self.__requesting_id = host.registerCallback(
            self._requestingEntity, with_data=True
        )
        host.importMenu(
            (D_("Service"), D_("Commands")),
            self._commandsMenu,
            security_limit=2,
            help_string=D_("Execute ad-hoc commands"),
        )
        host.registerNamespace(u'commands', NS_COMMANDS)

    def getHandler(self, client):
        return XEP_0050_handler(self)

    def profileConnected(self, client):
        # map from node to AdHocCommand instance
        client._XEP_0050_commands = {}
        if not client.is_component:
            self.addAdHocCommand(client, self._statusCallback, _("Status"))

    def do(self, client, entity, node, action=ACTION.EXECUTE, session_id=None,
           form_values=None, timeout=30):
        """Do an Ad-Hoc Command

        @param entity(jid.JID): entity which will execture the command
        @param node(unicode): node of the command
        @param action(unicode): one of XEP_0050.ACTION
        @param session_id(unicode, None): id of the ad-hoc session
            None if no session is involved
        @param form_values(dict, None): values to use to create command form
            values will be passed to data_form.Form.makeFields
        @return
        """
        iq_elt = client.IQ(timeout=timeout)
        iq_elt["to"] = entity.full()
        command_elt = iq_elt.addElement("command", NS_COMMANDS)
        command_elt["node"] = node
        command_elt["action"] = action
        if session_id is not None:
            command_elt["sessionid"] = session_id

        if form_values:
            # We add the XMLUI result to the command payload
            form = data_form.Form("submit")
            form.makeFields(form_values)
            command_elt.addChild(form.toElement())
        d = iq_elt.send()
        return d

    def getCommandElt(self, iq_elt):
        try:
            return iq_elt.elements(NS_COMMANDS, "command").next()
        except StopIteration:
            raise exceptions.NotFound(_(u"Missing command element"))

    def adHocError(self, error_type):
        """Shortcut to raise an AdHocError

        @param error_type(unicode): one of XEP_0050.ERROR
        """
        raise AdHocError(error_type)

    def _items2XMLUI(self, items, no_instructions):
        """Convert discovery items to XMLUI dialog """
        # TODO: manage items on different jids
        form_ui = xml_tools.XMLUI("form", submit_id=self.__requesting_id)

        if not no_instructions:
            form_ui.addText(_("Please select a command"), "instructions")

        options = [(item.nodeIdentifier, item.name) for item in items]
        form_ui.addList("node", options)
        return form_ui

    def _getDataLvl(self, type_):
        """Return the constant corresponding to <note/> type attribute value

        @param type_: note type (see XEP-0050 §4.3)
        @return: a C.XMLUI_DATA_LVL_* constant
        """
        if type_ == "error":
            return C.XMLUI_DATA_LVL_ERROR
        elif type_ == "warn":
            return C.XMLUI_DATA_LVL_WARNING
        else:
            if type_ != "info":
                log.warning(_(u"Invalid note type [%s], using info") % type_)
            return C.XMLUI_DATA_LVL_INFO

    def _mergeNotes(self, notes):
        """Merge notes with level prefix (e.g. "ERROR: the message")

        @param notes (list): list of tuple (level, message)
        @return: list of messages
        """
        lvl_map = {
            C.XMLUI_DATA_LVL_INFO: "",
            C.XMLUI_DATA_LVL_WARNING: "%s: " % _("WARNING"),
            C.XMLUI_DATA_LVL_ERROR: "%s: " % _("ERROR"),
        }
        return [u"%s%s" % (lvl_map[lvl], msg) for lvl, msg in notes]

    def _commandsAnswer2XMLUI(self, iq_elt, session_id, session_data):
        """Convert command answer to an ui for frontend

        @param iq_elt: command result
        @param session_id: id of the session used with the frontend
        @param profile_key: %(doc_profile_key)s
        """
        command_elt = self.getCommandElt(iq_elt)
        status = command_elt.getAttribute("status", XEP_0050.STATUS.EXECUTING)
        if status in [XEP_0050.STATUS.COMPLETED, XEP_0050.STATUS.CANCELED]:
            # the command session is finished, we purge our session
            del self.requesting[session_id]
            if status == XEP_0050.STATUS.COMPLETED:
                session_id = None
            else:
                return None
        remote_session_id = command_elt.getAttribute("sessionid")
        if remote_session_id:
            session_data["remote_id"] = remote_session_id
        notes = []
        for note_elt in command_elt.elements(NS_COMMANDS, "note"):
            notes.append(
                (
                    self._getDataLvl(note_elt.getAttribute("type", "info")),
                    unicode(note_elt),
                )
            )
        for data_elt in command_elt.elements(data_form.NS_X_DATA, "x"):
            if data_elt["type"] in ("form", "result"):
                break
        else:
            # no matching data element found
            if status != XEP_0050.STATUS.COMPLETED:
                log.warning(
                    _("No known payload found in ad-hoc command result, aborting")
                )
                del self.requesting[session_id]
                return xml_tools.XMLUI(
                    C.XMLUI_DIALOG,
                    dialog_opt={
                        C.XMLUI_DATA_TYPE: C.XMLUI_DIALOG_NOTE,
                        C.XMLUI_DATA_MESS: _("No payload found"),
                        C.XMLUI_DATA_LVL: C.XMLUI_DATA_LVL_ERROR,
                    },
                )
            if not notes:
                # the status is completed, and we have no note to show
                return None

            # if we have only one note, we show a dialog with the level of the note
            # if we have more, we show a dialog with "info" level, and all notes merged
            dlg_level = notes[0][0] if len(notes) == 1 else C.XMLUI_DATA_LVL_INFO
            return xml_tools.XMLUI(
                C.XMLUI_DIALOG,
                dialog_opt={
                    C.XMLUI_DATA_TYPE: C.XMLUI_DIALOG_NOTE,
                    C.XMLUI_DATA_MESS: u"\n".join(self._mergeNotes(notes)),
                    C.XMLUI_DATA_LVL: dlg_level,
                },
                session_id=session_id,
            )

        if session_id is None:
            return xml_tools.dataFormEltResult2XMLUI(data_elt)
        form = data_form.Form.fromElement(data_elt)
        # we add any present note to the instructions
        form.instructions.extend(self._mergeNotes(notes))
        return xml_tools.dataForm2XMLUI(form, self.__requesting_id, session_id=session_id)

    def _requestingEntity(self, data, profile):
        def serialise(ret_data):
            if "xmlui" in ret_data:
                ret_data["xmlui"] = ret_data["xmlui"].toXml()
            return ret_data

        d = self.requestingEntity(data, profile)
        d.addCallback(serialise)
        return d

    def requestingEntity(self, data, profile):
        """Request and entity and create XMLUI accordingly.

        @param data: data returned by previous XMLUI (first one must come from
                     self._commandsMenu)
        @param profile: %(doc_profile)s
        @return: callback dict result (with "xmlui" corresponding to the answering
                 dialog, or empty if it's finished without error)
        """
        if C.bool(data.get("cancelled", C.BOOL_FALSE)):
            return defer.succeed({})
        data_form_values = xml_tools.XMLUIResult2DataFormResult(data)
        client = self.host.getClient(profile)
        # TODO: cancel, prev and next are not managed
        # TODO: managed answerer errors
        # TODO: manage nodes with a non data form payload
        if "session_id" not in data:
            # we just had the jid, we now request it for the available commands
            session_id, session_data = self.requesting.newSession(profile=client.profile)
            entity = jid.JID(data[xml_tools.SAT_FORM_PREFIX + "jid"])
            session_data["jid"] = entity
            d = self.listUI(client, entity)

            def sendItems(xmlui):
                xmlui.session_id = session_id  # we need to keep track of the session
                return {"xmlui": xmlui}

            d.addCallback(sendItems)
        else:
            # we have started a several forms sessions
            try:
                session_data = self.requesting.profileGet(
                    data["session_id"], client.profile
                )
            except KeyError:
                log.warning("session id doesn't exist, session has probably expired")
                # TODO: send error dialog
                return defer.succeed({})
            session_id = data["session_id"]
            entity = session_data["jid"]
            try:
                session_data["node"]
                # node has already been received
            except KeyError:
                # it's the first time we know the node, we save it in session data
                session_data["node"] = data_form_values.pop("node")

            # remote_id is the XEP_0050 sessionid used by answering command
            # while session_id is our own session id used with the frontend
            remote_id = session_data.get("remote_id")

            # we request execute node's command
            d = self.do(client, entity, session_data["node"], action=XEP_0050.ACTION.EXECUTE,
                        session_id=remote_id, form_values=data_form_values)
            d.addCallback(self._commandsAnswer2XMLUI, session_id, session_data)
            d.addCallback(lambda xmlui: {"xmlui": xmlui} if xmlui is not None else {})

        return d

    def _commandsMenu(self, menu_data, profile):
        """First XMLUI activated by menu: ask for target jid

        @param profile: %(doc_profile)s
        """
        form_ui = xml_tools.XMLUI("form", submit_id=self.__requesting_id)
        form_ui.addText(_("Please enter target jid"), "instructions")
        form_ui.changeContainer("pairs")
        form_ui.addLabel("jid")
        form_ui.addString("jid", value=self.host.getClient(profile).jid.host)
        return {"xmlui": form_ui.toXml()}

    def _statusCallback(self, client, command_elt, session_data, action, node):
        """Ad-hoc command used to change the "show" part of status"""
        actions = session_data.setdefault("actions", [])
        actions.append(action)

        if len(actions) == 1:
            # it's our first request, we ask the desired new status
            status = XEP_0050.STATUS.EXECUTING
            form = data_form.Form("form", title=_("status selection"))
            show_options = [
                data_form.Option(name, label) for name, label in SHOWS.items()
            ]
            field = data_form.Field(
                "list-single", "show", options=show_options, required=True
            )
            form.addField(field)

            payload = form.toElement()
            note = None

        elif len(actions) == 2:
            # we should have the answer here
            try:
                x_elt = command_elt.elements(data_form.NS_X_DATA, "x").next()
                answer_form = data_form.Form.fromElement(x_elt)
                show = answer_form["show"]
            except (KeyError, StopIteration):
                self.adHocError(XEP_0050.ERROR.BAD_PAYLOAD)
            if show not in SHOWS:
                self.adHocError(XEP_0050.ERROR.BAD_PAYLOAD)
            if show == "disconnect":
                self.host.disconnect(client.profile)
            else:
                self.host.setPresence(show=show, profile_key=client.profile)

            # job done, we can end the session
            status = XEP_0050.STATUS.COMPLETED
            payload = None
            note = (self.NOTE.INFO, _(u"Status updated"))
        else:
            self.adHocError(XEP_0050.ERROR.INTERNAL)

        return (payload, status, None, note)

    def _run(self, service_jid_s="", node="", profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        service_jid = jid.JID(service_jid_s) if service_jid_s else None
        d = self.run(client, service_jid, node or None)
        d.addCallback(lambda xmlui: xmlui.toXml())
        return d

    @defer.inlineCallbacks
    def run(self, client, service_jid=None, node=None):
        """run an ad-hoc command

        @param service_jid(jid.JID, None): jid of the ad-hoc service
            None to use profile's server
        @param node(unicode, None): node of the ad-hoc commnad
            None to get initial list
        @return(unicode): command page XMLUI
        """
        if service_jid is None:
            service_jid = jid.JID(client.jid.host)
        session_id, session_data = self.requesting.newSession(profile=client.profile)
        session_data["jid"] = service_jid
        if node is None:
            xmlui = yield self.listUI(client, service_jid)
        else:
            session_data["node"] = node
            cb_data = yield self.requestingEntity(
                {"session_id": session_id}, client.profile
            )
            xmlui = cb_data["xmlui"]

        xmlui.session_id = session_id
        defer.returnValue(xmlui)

    def list(self, client, to_jid):
        """Request available commands

        @param to_jid(jid.JID, None): the entity answering the commands
            None to use profile's server
        @return D(disco.DiscoItems): found commands
        """
        d = self.host.getDiscoItems(client, to_jid, NS_COMMANDS)
        return d

    def _listUI(self, to_jid_s, profile_key):
        client = self.host.getClient(profile_key)
        to_jid = jid.JID(to_jid_s) if to_jid_s else None
        d = self.listUI(client, to_jid, no_instructions=True)
        d.addCallback(lambda xmlui: xmlui.toXml())
        return d

    def listUI(self, client, to_jid, no_instructions=False):
        """Request available commands and generate XMLUI

        @param to_jid(jid.JID, None): the entity answering the commands
            None to use profile's server
        @param no_instructions(bool): if True, don't add instructions widget
        @return D(xml_tools.XMLUI): UI with the commands
        """
        d = self.list(client, to_jid)
        d.addCallback(self._items2XMLUI, no_instructions)
        return d

    def addAdHocCommand(self, client, callback, label, node=None, features=None,
                        timeout=600, allowed_jids=None, allowed_groups=None,
                        allowed_magics=None, forbidden_jids=None, forbidden_groups=None,
                        ):
        """Add an ad-hoc command for the current profile

        @param callback: method associated with this ad-hoc command which return the
                         payload data (see AdHocCommand._sendAnswer), can return a
                         deferred
        @param label: label associated with this command on the main menu
        @param node: disco item node associated with this command. None to use
                     autogenerated node
        @param features: features associated with the payload (list of strings), usualy
                         data form
        @param timeout: delay between two requests before canceling the session (in
                        seconds)
        @param allowed_jids: list of allowed entities
        @param allowed_groups: list of allowed roster groups
        @param allowed_magics: list of allowed magic keys, can be:
                               @ALL@: allow everybody
                               @PROFILE_BAREJID@: allow only the jid of the profile
        @param forbidden_jids: black list of entities which can't access this command
        @param forbidden_groups: black list of groups which can't access this command
        @return: node of the added command, useful to remove the command later
        """
        # FIXME: "@ALL@" for profile_key seems useless and dangerous

        if node is None:
            node = "%s_%s" % ("COMMANDS", uuid4())

        if features is None:
            features = [data_form.NS_X_DATA]

        if allowed_jids is None:
            allowed_jids = []
        if allowed_groups is None:
            allowed_groups = []
        if allowed_magics is None:
            allowed_magics = ["@PROFILE_BAREJID@"]
        if forbidden_jids is None:
            forbidden_jids = []
        if forbidden_groups is None:
            forbidden_groups = []

        # TODO: manage newly created/removed profiles
        _allowed_jids = (
            (allowed_jids + [client.jid.userhostJID()])
            if "@PROFILE_BAREJID@" in allowed_magics
            else allowed_jids
        )
        ad_hoc_command = AdHocCommand(
            callback,
            label,
            node,
            features,
            timeout,
            _allowed_jids,
            allowed_groups,
            allowed_magics,
            forbidden_jids,
            forbidden_groups,
        )
        ad_hoc_command.setHandlerParent(client)
        commands = client._XEP_0050_commands
        commands[node] = ad_hoc_command

    def onCmdRequest(self, request, client):
        request.handled = True
        requestor = jid.JID(request["from"])
        command_elt = request.elements(NS_COMMANDS, "command").next()
        action = command_elt.getAttribute("action", self.ACTION.EXECUTE)
        node = command_elt.getAttribute("node")
        if not node:
            client.sendError(request, u"bad-request")
            return
        sessionid = command_elt.getAttribute("sessionid")
        commands = client._XEP_0050_commands
        try:
            command = commands[node]
        except KeyError:
            client.sendError(request, u"item-not-found")
            return
        command.onRequest(command_elt, requestor, action, sessionid)


class XEP_0050_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent

    @property
    def client(self):
        return self.parent

    def connectionInitialized(self):
        self.xmlstream.addObserver(
            CMD_REQUEST, self.plugin_parent.onCmdRequest, client=self.parent
        )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        identities = []
        if nodeIdentifier == NS_COMMANDS and self.client._XEP_0050_commands:
            # we only add the identity if we have registred commands
            identities.append(ID_CMD_LIST)
        return [disco.DiscoFeature(NS_COMMANDS)] + identities

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        ret = []
        if nodeIdentifier == NS_COMMANDS:
            commands = self.client._XEP_0050_commands
            for command in commands.values():
                if command.isAuthorised(requestor):
                    ret.append(
                        disco.DiscoItem(self.parent.jid, command.node, command.getName())
                    )  # TODO: manage name language
        return ret
