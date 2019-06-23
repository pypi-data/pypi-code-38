#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# jp: a SàT command line tool
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


import base
from sat.core.i18n import _
from sat_frontends.jp.constants import Const as C
from sat.tools.common.ansi import ANSI as A
from sat.tools.common import data_format
from functools import partial

__commands__ = ["Invitation"]


class Create(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "create",
            use_profile=False,
            use_output=C.OUTPUT_DICT,
            help=_(u"create and send an invitation"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-j",
            "--jid",
            type=base.unicode_decoder,
            default="",
            help="jid of the invitee (default: generate one)",
        )
        self.parser.add_argument(
            "-P",
            "--password",
            type=base.unicode_decoder,
            default="",
            help="password of the invitee profile/XMPP account (default: generate one)",
        )
        self.parser.add_argument(
            "-n",
            "--name",
            type=base.unicode_decoder,
            default="",
            help="name of the invitee",
        )
        self.parser.add_argument(
            "-N",
            "--host-name",
            type=base.unicode_decoder,
            default="",
            help="name of the host",
        )
        self.parser.add_argument(
            "-e",
            "--email",
            action="append",
            type=base.unicode_decoder,
            default=[],
            help="email(s) to send the invitation to (if --no-email is set, email will just be saved)",
        )
        self.parser.add_argument(
            "--no-email", action="store_true", help="do NOT send invitation email"
        )
        self.parser.add_argument(
            "-l",
            "--lang",
            type=base.unicode_decoder,
            default="",
            help="main language spoken by the invitee",
        )
        self.parser.add_argument(
            "-u",
            "--url",
            type=base.unicode_decoder,
            default="",
            help="template to construct the URL",
        )
        self.parser.add_argument(
            "-s",
            "--subject",
            type=base.unicode_decoder,
            default="",
            help="subject of the invitation email (default: generic subject)",
        )
        self.parser.add_argument(
            "-b",
            "--body",
            type=base.unicode_decoder,
            default="",
            help="body of the invitation email (default: generic body)",
        )
        self.parser.add_argument(
            "-x",
            "--extra",
            metavar=("KEY", "VALUE"),
            type=base.unicode_decoder,
            action="append",
            nargs=2,
            default=[],
            help="extra data to associate with invitation/invitee",
        )
        self.parser.add_argument(
            "-p",
            "--profile",
            type=base.unicode_decoder,
            default="",
            help="profile doing the invitation (default: don't associate profile)",
        )

    def invitationCreateCb(self, invitation_data):
        self.output(invitation_data)
        self.host.quit(C.EXIT_OK)

    def invitationCreateEb(self, failure_):
        self.disp(
            u"can't create invitation: {reason}".format(reason=failure_), error=True
        )
        self.host.quit(C.EXIT_BRIDGE_ERRBACK)

    def start(self):
        extra = dict(self.args.extra)
        email = self.args.email[0] if self.args.email else None
        emails_extra = self.args.email[1:]
        if self.args.no_email:
            if email:
                extra["email"] = email
                data_format.iter2dict(u"emails_extra", emails_extra)
        else:
            if not email:
                self.parser.error(
                    _(u"you need to specify an email address to send email invitation")
                )

        self.host.bridge.invitationCreate(
            email,
            emails_extra,
            self.args.jid,
            self.args.password,
            self.args.name,
            self.args.host_name,
            self.args.lang,
            self.args.url,
            self.args.subject,
            self.args.body,
            extra,
            self.args.profile,
            callback=self.invitationCreateCb,
            errback=self.invitationCreateEb,
        )


class Get(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_profile=False,
            use_output=C.OUTPUT_DICT,
            help=_(u"get invitation data"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "id", type=base.unicode_decoder, help=_(u"invitation UUID")
        )
        self.parser.add_argument(
            "-j",
            "--with-jid",
            action="store_true",
            help=_(u"start profile session and retrieve jid"),
        )

    def output_data(self, data, jid_=None):
        if jid_ is not None:
            data["jid"] = jid_
        self.output(data)
        self.host.quit()

    def invitationGetCb(self, invitation_data):
        if self.args.with_jid:
            profile = invitation_data[u"guest_profile"]

            def session_started(__):
                self.host.bridge.asyncGetParamA(
                    u"JabberID",
                    u"Connection",
                    profile_key=profile,
                    callback=lambda jid_: self.output_data(invitation_data, jid_),
                    errback=partial(
                        self.errback,
                        msg=_(u"can't retrieve jid: {}"),
                        exit_code=C.EXIT_BRIDGE_ERRBACK,
                    ),
                )

            self.host.bridge.profileStartSession(
                invitation_data[u"password"],
                profile,
                callback=session_started,
                errback=partial(
                    self.errback,
                    msg=_(u"can't start session: {}"),
                    exit_code=C.EXIT_BRIDGE_ERRBACK,
                ),
            )
        else:
            self.output_data(invitation_data)

    def start(self):
        self.host.bridge.invitationGet(
            self.args.id,
            callback=self.invitationGetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't get invitation data: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class Modify(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self, host, "modify", use_profile=False, help=_(u"modify existing invitation")
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "--replace", action="store_true", help="replace the whole data"
        )
        self.parser.add_argument(
            "-n",
            "--name",
            type=base.unicode_decoder,
            default="",
            help="name of the invitee",
        )
        self.parser.add_argument(
            "-N",
            "--host-name",
            type=base.unicode_decoder,
            default="",
            help="name of the host",
        )
        self.parser.add_argument(
            "-e",
            "--email",
            type=base.unicode_decoder,
            default="",
            help="email to send the invitation to (if --no-email is set, email will just be saved)",
        )
        self.parser.add_argument(
            "-l",
            "--lang",
            dest="language",
            type=base.unicode_decoder,
            default="",
            help="main language spoken by the invitee",
        )
        self.parser.add_argument(
            "-x",
            "--extra",
            metavar=("KEY", "VALUE"),
            type=base.unicode_decoder,
            action="append",
            nargs=2,
            default=[],
            help="extra data to associate with invitation/invitee",
        )
        self.parser.add_argument(
            "-p",
            "--profile",
            type=base.unicode_decoder,
            default="",
            help="profile doing the invitation (default: don't associate profile",
        )
        self.parser.add_argument(
            "id", type=base.unicode_decoder, help=_(u"invitation UUID")
        )

    def invitationModifyCb(self):
        self.disp(_(u"invitations have been modified correctly"))
        self.host.quit(C.EXIT_OK)

    def invitationModifyEb(self, failure_):
        self.disp(
            u"can't create invitation: {reason}".format(reason=failure_), error=True
        )
        self.host.quit(C.EXIT_BRIDGE_ERRBACK)

    def start(self):
        extra = dict(self.args.extra)
        for arg_name in ("name", "host_name", "email", "language", "profile"):
            value = getattr(self.args, arg_name)
            if not value:
                continue
            if arg_name in extra:
                self.parser.error(
                    _(
                        u"you can't set {arg_name} in both optional argument and extra"
                    ).format(arg_name=arg_name)
                )
            extra[arg_name] = value
        self.host.bridge.invitationModify(
            self.args.id,
            extra,
            self.args.replace,
            callback=self.invitationModifyCb,
            errback=self.invitationModifyEb,
        )


class List(base.CommandBase):
    def __init__(self, host):
        extra_outputs = {"default": self.default_output}
        base.CommandBase.__init__(
            self,
            host,
            "list",
            use_profile=False,
            use_output=C.OUTPUT_COMPLEX,
            extra_outputs=extra_outputs,
            help=_(u"list invitations data"),
        )
        self.need_loop = True

    def default_output(self, data):
        for idx, datum in enumerate(data.iteritems()):
            if idx:
                self.disp(u"\n")
            key, invitation_data = datum
            self.disp(A.color(C.A_HEADER, key))
            indent = u"  "
            for k, v in invitation_data.iteritems():
                self.disp(indent + A.color(C.A_SUBHEADER, k + u":") + u" " + unicode(v))

    def add_parser_options(self):
        self.parser.add_argument(
            "-p",
            "--profile",
            default=C.PROF_KEY_NONE,
            help=_(u"return only invitations linked to this profile"),
        )

    def invitationListCb(self, data):
        self.output(data)
        self.host.quit()

    def start(self):
        self.host.bridge.invitationList(
            self.args.profile,
            callback=self.invitationListCb,
            errback=partial(
                self.errback,
                msg=_(u"can't list invitations: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class Invitation(base.CommandBase):
    subcommands = (Create, Get, Modify, List)

    def __init__(self, host):
        super(Invitation, self).__init__(
            host,
            "invitation",
            use_profile=False,
            help=_(u"invitation of user(s) without XMPP account"),
        )
