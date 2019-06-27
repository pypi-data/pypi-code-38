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

import sys
from sat_frontends.jp import base
from sat_frontends.jp.constants import Const as C
from sat_frontends.tools import jid
from sat.core.i18n import _
from sat.tools.utils import clean_ustr
from sat.tools.common import data_format
from sat.tools.common.ansi import ANSI as A
from functools import partial

__commands__ = ["Message"]


class Send(base.CommandBase):
    def __init__(self, host):
        super(Send, self).__init__(host, "send", help=_("send a message to a contact"))
        self.need_loop=True

    def add_parser_options(self):
        self.parser.add_argument(
            "-l", "--lang", type=str, default="", help=_(u"language of the message")
        )
        self.parser.add_argument(
            "-s",
            "--separate",
            action="store_true",
            help=_(
                u"separate xmpp messages: send one message per line instead of one "
                u"message alone."
            ),
        )
        self.parser.add_argument(
            "-n",
            "--new-line",
            action="store_true",
            help=_(
                u"add a new line at the beginning of the input (usefull for ascii art ;))"
            ),
        )
        self.parser.add_argument(
            "-S",
            "--subject",
            type=base.unicode_decoder,
            help=_(u"subject of the message"),
        )
        self.parser.add_argument(
            "-L", "--subject_lang", type=str, default="", help=_(u"language of subject")
        )
        self.parser.add_argument(
            "-t",
            "--type",
            choices=C.MESS_TYPE_STANDARD + (C.MESS_TYPE_AUTO,),
            default=C.MESS_TYPE_AUTO,
            help=_("type of the message"),
        )
        self.parser.add_argument("-e", "--encrypt", metavar="ALGORITHM",
                                 help=_(u"encrypt message using given algorithm"))
        self.parser.add_argument(
            "--encrypt-noreplace",
            action="store_true",
            help=_(u"don't replace encryption algorithm if an other one is already used"))
        syntax = self.parser.add_mutually_exclusive_group()
        syntax.add_argument("-x", "--xhtml", action="store_true", help=_(u"XHTML body"))
        syntax.add_argument("-r", "--rich", action="store_true", help=_(u"rich body"))
        self.parser.add_argument(
            "jid", type=base.unicode_decoder, help=_(u"the destination jid")
        )

    def multi_send_cb(self):
        self.sent += 1
        if self.sent == self.to_send:
            self.host.quit(self.errcode)

    def multi_send_eb(self, failure_, msg):
        self.disp(_(u"Can't send message [{msg}]: {reason}").format(
            msg=msg, reason=failure_))
        self.errcode = C.EXIT_BRIDGE_ERRBACK
        self.multi_send_cb()

    def sendStdin(self, dest_jid):
        """Send incomming data on stdin to jabber contact

        @param dest_jid: destination jid
        """
        header = "\n" if self.args.new_line else ""
        stdin_lines = [
            stream.decode("utf-8", "ignore") for stream in sys.stdin.readlines()
        ]
        extra = {}
        if self.args.subject is None:
            subject = {}
        else:
            subject = {self.args.subject_lang: self.args.subject}

        if self.args.xhtml or self.args.rich:
            key = u"xhtml" if self.args.xhtml else u"rich"
            if self.args.lang:
                key = u"{}_{}".format(key, self.args.lang)
            extra[key] = clean_ustr(u"".join(stdin_lines))
            stdin_lines = []

        if self.args.separate:  # we send stdin in several messages
            self.to_send = 0
            self.sent = 0
            self.errcode = 0

            if header:
                self.to_send += 1
                self.host.bridge.messageSend(
                    dest_jid,
                    {self.args.lang: header},
                    subject,
                    self.args.type,
                    profile_key=self.profile,
                    callback=lambda: None,
                    errback=lambda ignore: ignore,
                )

            self.to_send += len(stdin_lines)
            for line in stdin_lines:
                self.host.bridge.messageSend(
                    dest_jid,
                    {self.args.lang: line.replace("\n", "")},
                    subject,
                    self.args.type,
                    extra,
                    profile_key=self.host.profile,
                    callback=self.multi_send_cb,
                    errback=partial(self.multi_send_eb, msg=line),
                )

        else:
            msg = (
                {self.args.lang: header + clean_ustr(u"".join(stdin_lines))}
                if not (self.args.xhtml or self.args.rich)
                else {}
            )
            self.host.bridge.messageSend(
                dest_jid,
                msg,
                subject,
                self.args.type,
                extra,
                profile_key=self.host.profile,
                callback=self.host.quit,
                errback=partial(self.errback,
                                msg=_(u"Can't send message: {}")))

    def encryptionNamespaceGetCb(self, namespace, jid_):
        self.host.bridge.messageEncryptionStart(
            jid_, namespace, not self.args.encrypt_noreplace,
            self.profile,
            callback=lambda: self.sendStdin(jid_),
            errback=partial(self.errback,
                            msg=_(u"Can't start encryption session: {}"),
                            exit_code=C.EXIT_BRIDGE_ERRBACK,
                            ))


    def start(self):
        if self.args.xhtml and self.args.separate:
            self.disp(
                u"argument -s/--separate is not compatible yet with argument -x/--xhtml",
                error=True,
            )
            self.host.quit(2)

        jids = self.host.check_jids([self.args.jid])
        jid_ = jids[0]

        if self.args.encrypt_noreplace and self.args.encrypt is None:
            self.parser.error("You need to use --encrypt if you use --encrypt-noreplace")

        if self.args.encrypt is not None:
            self.host.bridge.encryptionNamespaceGet(self.args.encrypt,
                callback=partial(self.encryptionNamespaceGetCb, jid_=jid_),
                errback=partial(self.errback,
                                msg=_(u"Can't get encryption namespace: {}"),
                                exit_code=C.EXIT_BRIDGE_ERRBACK,
                                ))
        else:
            self.sendStdin(jid_)


class MAM(base.CommandBase):

    def __init__(self, host):
        super(MAM, self).__init__(
            host, "mam", use_output=C.OUTPUT_MESS, use_verbose=True, help=_(u"query archives using MAM"))
        self.need_loop=True

    def add_parser_options(self):
        self.parser.add_argument(
            "-s", "--service", type=base.unicode_decoder, default=u"",
            help=_(u"jid of the service (default: profile's server"))
        self.parser.add_argument(
            "-S", "--start", dest="mam_start", type=base.date_decoder,
            help=_(
                u"start fetching archive from this date (default: from the beginning)"))
        self.parser.add_argument(
            "-E", "--end", dest="mam_end", type=base.date_decoder,
            help=_(u"end fetching archive after this date (default: no limit)"))
        self.parser.add_argument(
            "-W", "--with", dest="mam_with", type=base.unicode_decoder,
            help=_(u"retrieve only archives with this jid"))
        self.parser.add_argument(
            "-m", "--max", dest="rsm_max", type=int, default=20,
            help=_(u"maximum number of items to retrieve, using RSM (default: 20))"))
        rsm_page_group = self.parser.add_mutually_exclusive_group()
        rsm_page_group.add_argument(
            "-a", "--after", dest="rsm_after", type=base.unicode_decoder,
            help=_(u"find page after this item"), metavar='ITEM_ID')
        rsm_page_group.add_argument(
            "-b", "--before", dest="rsm_before", type=base.unicode_decoder,
            help=_(u"find page before this item"), metavar='ITEM_ID')
        rsm_page_group.add_argument(
            "--index", dest="rsm_index", type=int,
            help=_(u"index of the page to retrieve"))

    def _sessionInfosGetCb(self, session_info, data, metadata):
        self.host.own_jid = jid.JID(session_info[u"jid"])
        self.output(data)
        # FIXME: metadata are not displayed correctly and don't play nice with output
        #        they should be added to output data somehow
        if self.verbosity:
            for value in (u"rsm_first", u"rsm_last", u"rsm_index", u"rsm_count",
                          u"mam_complete", u"mam_stable"):
                if value in metadata:
                    label = value.split(u"_")[1]
                    self.disp(A.color(
                        C.A_HEADER, label, u': ' , A.RESET, metadata[value]))

        self.host.quit()

    def _MAMGetCb(self, result):
        data, metadata, profile = result
        self.host.bridge.sessionInfosGet(self.profile,
            callback=partial(self._sessionInfosGetCb, data=data, metadata=metadata),
            errback=self.errback)

    def start(self):
        extra = {}
        if self.args.mam_start is not None:
            extra[u"mam_start"] = float(self.args.mam_start)
        if self.args.mam_end is not None:
            extra[u"mam_end"] = float(self.args.mam_end)
        if self.args.mam_with is not None:
            extra[u"mam_with"] = self.args.mam_with
        for suff in ('max', 'after', 'before', 'index'):
            key = u'rsm_' + suff
            value = getattr(self.args,key)
            if value is not None:
                extra[key] = unicode(value)
        self.host.bridge.MAMGet(
            self.args.service, data_format.serialise(extra), self.profile,
            callback=self._MAMGetCb, errback=self.errback)


class Message(base.CommandBase):
    subcommands = (Send, MAM)

    def __init__(self, host):
        super(Message, self).__init__(
            host, "message", use_profile=False, help=_("messages handling")
        )
