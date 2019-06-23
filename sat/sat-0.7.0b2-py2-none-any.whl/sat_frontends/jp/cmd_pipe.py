#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# jp: a SAT command line tool
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

from sat_frontends.jp import base

from sat_frontends.jp.constants import Const as C
import sys
from sat.core.i18n import _
from sat_frontends.tools import jid
import xml.etree.ElementTree as ET  # FIXME: used temporarily to manage XMLUI
from functools import partial
import socket
import SocketServer
import errno

__commands__ = ["Pipe"]

START_PORT = 9999


class PipeOut(base.CommandBase):
    def __init__(self, host):
        super(PipeOut, self).__init__(host, "out", help=_("send a pipe a stream"))
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "jid", type=base.unicode_decoder, help=_("the destination jid")
        )

    def streamOutCb(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", int(port)))
        while True:
            buf = sys.stdin.read(4096)
            if not buf:
                break
            try:
                s.sendall(buf)
            except socket.error as e:
                if e.errno == errno.EPIPE:
                    sys.stderr.write(str(e) + "\n")
                    self.host.quit(1)
                else:
                    raise e
        self.host.quit()

    def start(self):
        """ Create named pipe, and send stdin to it """
        self.host.bridge.streamOut(
            self.host.get_full_jid(self.args.jid),
            self.profile,
            callback=self.streamOutCb,
            errback=partial(
                self.errback,
                msg=_(u"can't start stream: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class StreamServer(SocketServer.BaseRequestHandler):
    def handle(self):
        while True:
            data = self.request.recv(4096)
            if not data:
                break
            sys.stdout.write(data)
            try:
                sys.stdout.flush()
            except IOError as e:
                sys.stderr.write(str(e) + "\n")
                break
        #  calling shutdown will do a deadlock as we don't use separate thread
        # this is a workaround (cf. https://stackoverflow.com/a/36017741)
        self.server._BaseServer__shutdown_request = True


class PipeIn(base.CommandAnswering):
    def __init__(self, host):
        super(PipeIn, self).__init__(host, "in", help=_("receive a pipe stream"))
        self.action_callbacks = {"STREAM": self.onStreamAction}

    def add_parser_options(self):
        self.parser.add_argument(
            "jids",
            type=base.unicode_decoder,
            nargs="*",
            help=_('Jids accepted (none means "accept everything")'),
        )

    def getXmluiId(self, action_data):
        # FIXME: we temporarily use ElementTree, but a real XMLUI managing module
        #        should be available in the future
        # TODO: XMLUI module
        try:
            xml_ui = action_data["xmlui"]
        except KeyError:
            self.disp(_(u"Action has no XMLUI"), 1)
        else:
            ui = ET.fromstring(xml_ui.encode("utf-8"))
            xmlui_id = ui.get("submit")
            if not xmlui_id:
                self.disp(_(u"Invalid XMLUI received"), error=True)
            return xmlui_id

    def onStreamAction(self, action_data, action_id, security_limit, profile):
        xmlui_id = self.getXmluiId(action_data)
        if xmlui_id is None:
            return self.host.quitFromSignal(1)
        try:
            from_jid = jid.JID(action_data["meta_from_jid"])
        except KeyError:
            self.disp(_(u"Ignoring action without from_jid data"), 1)
            return

        if not self.bare_jids or from_jid.bare in self.bare_jids:
            host, port = "localhost", START_PORT
            while True:
                try:
                    server = SocketServer.TCPServer((host, port), StreamServer)
                except socket.error as e:
                    if e.errno == errno.EADDRINUSE:
                        port += 1
                    else:
                        raise e
                else:
                    break
            xmlui_data = {"answer": C.BOOL_TRUE, "port": unicode(port)}
            self.host.bridge.launchAction(xmlui_id, xmlui_data, profile_key=profile)
            server.serve_forever()
            self.host.quitFromSignal()

    def start(self):
        self.bare_jids = [jid.JID(jid_).bare for jid_ in self.args.jids]


class Pipe(base.CommandBase):
    subcommands = (PipeOut, PipeIn)

    def __init__(self, host):
        super(Pipe, self).__init__(
            host, "pipe", use_profile=False, help=_("stream piping through XMPP")
        )
