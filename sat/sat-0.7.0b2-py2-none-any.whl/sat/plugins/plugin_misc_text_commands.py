#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin for managing text commands
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
from sat.core.constants import Const as C
from sat.core import exceptions
from twisted.words.protocols.jabber import jid
from twisted.internet import defer
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.python import failure
from collections import OrderedDict

PLUGIN_INFO = {
    C.PI_NAME: "Text commands",
    C.PI_IMPORT_NAME: C.TEXT_CMDS,
    C.PI_TYPE: "Misc",
    C.PI_PROTOCOLS: ["XEP-0245"],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "TextCommands",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""IRC like text commands"""),
}


class InvalidCommandSyntax(Exception):
    """Throwed while parsing @command in docstring if syntax is invalid"""

    pass


CMD_KEY = "@command"
CMD_TYPES = ("group", "one2one", "all")
FEEDBACK_INFO_TYPE = "TEXT_CMD"


class TextCommands(object):
    # FIXME: doc strings for commands have to be translatable
    #       plugins need a dynamic translation system (translation
    #       should be downloadable independently)

    HELP_SUGGESTION = _(
        u"Type '/help' to get a list of the available commands. If you didn't want to "
        u"use a command, please start your message with '//' to escape the slash."
    )

    def __init__(self, host):
        log.info(_("Text commands initialization"))
        self.host = host
        # this is internal command, so we set high priority
        host.trigger.add("sendMessage", self.sendMessageTrigger, priority=1000000)
        self._commands = {}
        self._whois = []
        self.registerTextCommands(self)

    def _parseDocString(self, cmd, cmd_name):
        """Parse a docstring to get text command data

        @param cmd: function or method callback for the command,
            its docstring will be used for self documentation in the following way:
            - first line is the command short documentation, shown with /help
            - @command keyword can be used,
              see http://wiki.goffi.org/wiki/Coding_style/en for documentation
        @return (dict): dictionary with parsed data where key can be:
            - "doc_short_help" (default: ""): the untranslated short documentation
            - "type" (default "all"): the command type as specified in documentation
            - "args" (default: ""): the arguments available, using syntax specified in documentation.
            - "doc_arg_[name]": the doc of [name] argument
        """
        data = OrderedDict([("doc_short_help", ""), ("type", "all"), ("args", "")])
        docstring = cmd.__doc__
        if docstring is None:
            log.warning(u"No docstring found for command {}".format(cmd_name))
            docstring = ""

        doc_data = docstring.split("\n")
        data["doc_short_help"] = doc_data[0]

        try:
            cmd_indent = 0  # >0 when @command is found are we are parsing it

            for line in doc_data:
                stripped = line.strip()
                if cmd_indent and line[cmd_indent : cmd_indent + 5] == "    -":
                    colon_idx = line.find(":")
                    if colon_idx == -1:
                        raise InvalidCommandSyntax(
                            "No colon found in argument description"
                        )
                    arg_name = line[cmd_indent + 6 : colon_idx].strip()
                    if not arg_name:
                        raise InvalidCommandSyntax(
                            "No name found in argument description"
                        )
                    arg_help = line[colon_idx + 1 :].strip()
                    data["doc_arg_{}".format(arg_name)] = arg_help
                elif cmd_indent:
                    # we are parsing command and indent level is not good, it's finished
                    break
                elif stripped.startswith(CMD_KEY):
                    cmd_indent = line.find(CMD_KEY)

                    # type
                    colon_idx = stripped.find(":")
                    if colon_idx == -1:
                        raise InvalidCommandSyntax("missing colon")
                    type_data = stripped[len(CMD_KEY) : colon_idx].strip()
                    if len(type_data) == 0:
                        type_data = "(all)"
                    elif (
                        len(type_data) <= 2 or type_data[0] != "(" or type_data[-1] != ")"
                    ):
                        raise InvalidCommandSyntax("Bad type data syntax")
                    type_ = type_data[1:-1]
                    if type_ not in CMD_TYPES:
                        raise InvalidCommandSyntax("Unknown type {}".format(type_))
                    data["type"] = type_

                    # args
                    data["args"] = stripped[colon_idx + 1 :].strip()
        except InvalidCommandSyntax as e:
            log.warning(
                u"Invalid command syntax for command {command}: {message}".format(
                    command=cmd_name, message=e.message
                )
            )

        return data

    def registerTextCommands(self, instance):
        """ Add a text command

        @param instance: instance of a class containing text commands
        """
        for attr in dir(instance):
            if attr.startswith("cmd_"):
                cmd = getattr(instance, attr)
                if not callable(cmd):
                    log.warning(_(u"Skipping not callable [%s] attribute") % attr)
                    continue
                cmd_name = attr[4:]
                if not cmd_name:
                    log.warning(_("Skipping cmd_ method"))
                if cmd_name in self._commands:
                    suff = 2
                    while (cmd_name + str(suff)) in self._commands:
                        suff += 1
                    new_name = cmd_name + str(suff)
                    log.warning(
                        _(
                            u"Conflict for command [{old_name}], renaming it to [{new_name}]"
                        ).format(old_name=cmd_name, new_name=new_name)
                    )
                    cmd_name = new_name
                self._commands[cmd_name] = cmd_data = OrderedDict(
                    {"callback": cmd}
                )  # We use an Ordered dict to keep documenation order
                cmd_data.update(self._parseDocString(cmd, cmd_name))
                log.info(_("Registered text command [%s]") % cmd_name)

    def addWhoIsCb(self, callback, priority=0):
        """Add a callback which give information to the /whois command

        @param callback: a callback which will be called with the following arguments
            - whois_msg: list of information strings to display, callback need to append
                         its own strings to it
            - target_jid: full jid from whom we want information
            - profile: %(doc_profile)s
        @param priority: priority of the information to show (the highest priority will
            be displayed first)
        """
        self._whois.append((priority, callback))
        self._whois.sort(key=lambda item: item[0], reverse=True)

    def sendMessageTrigger(
        self, client, mess_data, pre_xml_treatments, post_xml_treatments
    ):
        """Install SendMessage command hook """
        pre_xml_treatments.addCallback(self._sendMessageCmdHook, client)
        return True

    def _sendMessageCmdHook(self, mess_data, client):
        """ Check text commands in message, and react consequently

        msg starting with / are potential command. If a command is found, it is executed,
        else an help message is sent.
        msg starting with // are escaped: they are sent with a single /
        commands can abord message sending (if they return anything evaluating to False),
        or continue it (if they return True), eventually after modifying the message
        an "unparsed" key is added to message, containing part of the message not yet
        parsed.
        Commands can be deferred or not
        @param mess_data(dict): data comming from sendMessage trigger
        @param profile: %(doc_profile)s
        """
        try:
            msg = mess_data["message"][""]
            msg_lang = ""
        except KeyError:
            try:
                # we have not default message, we try to take the first found
                msg_lang, msg = mess_data["message"].iteritems().next()
            except StopIteration:
                log.debug(u"No message found, skipping text commands")
                return mess_data

        try:
            if msg[:2] == "//":
                # we have a double '/', it's the escape sequence
                mess_data["message"][msg_lang] = msg[1:]
                return mess_data
            if msg[0] != "/":
                return mess_data
        except IndexError:
            return mess_data

        # we have a command
        d = None
        command = msg[1:].partition(" ")[0].lower()
        if command.isalpha():
            # looks like an actual command, we try to call the corresponding method
            def retHandling(ret):
                """ Handle command return value:
                if ret is True, normally send message (possibly modified by command)
                else, abord message sending
                """
                if ret:
                    return mess_data
                else:
                    log.debug(u"text command detected ({})".format(command))
                    raise failure.Failure(exceptions.CancelError())

            def genericErrback(failure):
                try:
                    msg = u"with condition {}".format(failure.value.condition)
                except AttributeError:
                    msg = u"with error {}".format(failure.value)
                self.feedBack(client, u"Command failed {}".format(msg), mess_data)
                return False

            mess_data["unparsed"] = msg[
                1 + len(command) :
            ]  # part not yet parsed of the message
            try:
                cmd_data = self._commands[command]
            except KeyError:
                self.feedBack(
                    client,
                    _("Unknown command /%s. ") % command + self.HELP_SUGGESTION,
                    mess_data,
                )
                log.debug("text command help message")
                raise failure.Failure(exceptions.CancelError())
            else:
                if not self._contextValid(mess_data, cmd_data):
                    # The command is not launched in the right context, we throw a message with help instructions
                    context_txt = (
                        _("group discussions")
                        if cmd_data["type"] == "group"
                        else _("one to one discussions")
                    )
                    feedback = _("/{command} command only applies in {context}.").format(
                        command=command, context=context_txt
                    )
                    self.feedBack(
                        client, u"{} {}".format(feedback, self.HELP_SUGGESTION), mess_data
                    )
                    log.debug("text command invalid message")
                    raise failure.Failure(exceptions.CancelError())
                else:
                    d = defer.maybeDeferred(cmd_data["callback"], client, mess_data)
                    d.addErrback(genericErrback)
                    d.addCallback(retHandling)

        return (
            d or mess_data
        )  # if a command is detected, we should have a deferred, else we send the message normally

    def _contextValid(self, mess_data, cmd_data):
        """Tell if a command can be used in the given context

        @param mess_data(dict): message data as given in sendMessage trigger
        @param cmd_data(dict): command data as returned by self._parseDocString
        @return (bool): True if command can be used in this context
        """
        if (cmd_data["type"] == "group" and mess_data["type"] != "groupchat") or (
            cmd_data["type"] == "one2one" and mess_data["type"] == "groupchat"
        ):
            return False
        return True

    def getRoomJID(self, arg, service_jid):
        """Return a room jid with a shortcut

        @param arg: argument: can be a full room jid (e.g.: sat@chat.jabberfr.org)
                    or a shortcut (e.g.: sat or sat@ for sat on current service)
        @param service_jid: jid of the current service (e.g.: chat.jabberfr.org)
        """
        nb_arobas = arg.count("@")
        if nb_arobas == 1:
            if arg[-1] != "@":
                return jid.JID(arg)
            return jid.JID(arg + service_jid)
        return jid.JID(u"%s@%s" % (arg, service_jid))

    def feedBack(self, client, message, mess_data, info_type=FEEDBACK_INFO_TYPE):
        """Give a message back to the user"""
        if mess_data["type"] == "groupchat":
            to_ = mess_data["to"].userhostJID()
        else:
            to_ = client.jid

        # we need to invert send message back, so sender need to original destinee
        mess_data["from"] = mess_data["to"]
        mess_data["to"] = to_
        mess_data["type"] = C.MESS_TYPE_INFO
        mess_data["message"] = {"": message}
        mess_data["extra"]["info_type"] = info_type
        client.messageSendToBridge(mess_data)

    def cmd_whois(self, client, mess_data):
        """show informations on entity

        @command: [JID|ROOM_NICK]
            - JID: entity to request
            - ROOM_NICK: nick of the room to request
        """
        log.debug("Catched whois command")

        entity = mess_data["unparsed"].strip()

        if mess_data["type"] == "groupchat":
            room = mess_data["to"].userhostJID()
            try:
                if self.host.plugins["XEP-0045"].isNickInRoom(client, room, entity):
                    entity = u"%s/%s" % (room, entity)
            except KeyError:
                log.warning("plugin XEP-0045 is not present")

        if not entity:
            target_jid = mess_data["to"]
        else:
            try:
                target_jid = jid.JID(entity)
                if not target_jid.user or not target_jid.host:
                    raise jid.InvalidFormat
            except (RuntimeError, jid.InvalidFormat, AttributeError):
                self.feedBack(client, _("Invalid jid, can't whois"), mess_data)
                return False

        if not target_jid.resource:
            target_jid.resource = self.host.memory.getMainResource(client, target_jid)

        whois_msg = [_(u"whois for %(jid)s") % {"jid": target_jid}]

        d = defer.succeed(None)
        for ignore, callback in self._whois:
            d.addCallback(
                lambda ignore: callback(client, whois_msg, mess_data, target_jid)
            )

        def feedBack(ignore):
            self.feedBack(client, u"\n".join(whois_msg), mess_data)
            return False

        d.addCallback(feedBack)
        return d

    def _getArgsHelp(self, cmd_data):
        """Return help string for args of cmd_name, according to docstring data

        @param cmd_data: command data
        @return (list[unicode]): help strings
        """
        strings = []
        for doc_name, doc_help in cmd_data.iteritems():
            if doc_name.startswith("doc_arg_"):
                arg_name = doc_name[8:]
                strings.append(
                    u"- {name}: {doc_help}".format(name=arg_name, doc_help=_(doc_help))
                )

        return strings

    def cmd_me(self, client, mess_data):
        """display a message at third person

        @command (all): message
            - message: message to show at third person
                e.g.: "/me clenches his fist" will give "[YOUR_NICK] clenches his fist"
        """
        # We just ignore the command as the match is done on receiption by clients
        return True

    def cmd_whoami(self, client, mess_data):
        """give your own jid"""
        self.feedBack(client, client.jid.full(), mess_data)

    def cmd_help(self, client, mess_data):
        """show help on available commands

        @command: [cmd_name]
            - cmd_name: name of the command for detailed help
        """
        cmd_name = mess_data["unparsed"].strip()
        if cmd_name and cmd_name[0] == "/":
            cmd_name = cmd_name[1:]
        if cmd_name and cmd_name not in self._commands:
            self.feedBack(
                client, _(u"Invalid command name [{}]\n".format(cmd_name)), mess_data
            )
            cmd_name = ""
        if not cmd_name:
            # we show the global help
            longuest = max([len(command) for command in self._commands])
            help_cmds = []

            for command in sorted(self._commands):
                cmd_data = self._commands[command]
                if not self._contextValid(mess_data, cmd_data):
                    continue
                spaces = (longuest - len(command)) * " "
                help_cmds.append(
                    "    /{command}: {spaces} {short_help}".format(
                        command=command,
                        spaces=spaces,
                        short_help=cmd_data["doc_short_help"],
                    )
                )

            help_mess = _(u"Text commands available:\n%s") % (u"\n".join(help_cmds),)
        else:
            # we show detailled help for a command
            cmd_data = self._commands[cmd_name]
            syntax = cmd_data["args"]
            help_mess = _(u"/{name}: {short_help}\n{syntax}{args_help}").format(
                name=cmd_name,
                short_help=cmd_data["doc_short_help"],
                syntax=_(" " * 4 + "syntax: {}\n").format(syntax) if syntax else "",
                args_help=u"\n".join(
                    [u" " * 8 + "{}".format(line) for line in self._getArgsHelp(cmd_data)]
                ),
            )

        self.feedBack(client, help_mess, mess_data)
