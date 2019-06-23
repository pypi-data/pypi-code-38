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

"""This module permits to manage XMPP accounts using in-band registration (XEP-0077)"""

from sat_frontends.jp.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core.i18n import _
from sat_frontends.jp import base
from sat_frontends.tools import jid

__commands__ = ["Account"]


class AccountCreate(base.CommandBase):
    def __init__(self, host):
        super(AccountCreate, self).__init__(
            host,
            "create",
            use_profile=False,
            use_verbose=True,
            help=_(u"create a XMPP account"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "jid", type=base.unicode_decoder, help=_(u"jid to create")
        )
        self.parser.add_argument(
            "password", type=base.unicode_decoder, help=_(u"password of the account")
        )
        self.parser.add_argument(
            "-p",
            "--profile",
            type=base.unicode_decoder,
            help=_(
                u"create a profile to use this account (default: don't create profile)"
            ),
        )
        self.parser.add_argument(
            "-e",
            "--email",
            type=base.unicode_decoder,
            default="",
            help=_(u"email (usage depends of XMPP server)"),
        )
        self.parser.add_argument(
            "-H",
            "--host",
            type=base.unicode_decoder,
            default="",
            help=_(u"server host (IP address or domain, default: use localhost)"),
        )
        self.parser.add_argument(
            "-P",
            "--port",
            type=int,
            default=0,
            help=_(u"server port (IP address or domain, default: use localhost)"),
        )

    def _setParamCb(self):
        self.host.bridge.setParam(
            "Password",
            self.args.password,
            "Connection",
            profile_key=self.args.profile,
            callback=self.host.quit,
            errback=self.errback,
        )

    def _session_started(self, __):
        self.host.bridge.setParam(
            "JabberID",
            self.args.jid,
            "Connection",
            profile_key=self.args.profile,
            callback=self._setParamCb,
            errback=self.errback,
        )

    def _profileCreateCb(self):
        self.disp(_(u"profile created"), 1)
        self.host.bridge.profileStartSession(
            self.args.password,
            self.args.profile,
            callback=self._session_started,
            errback=self.errback,
        )

    def _profileCreateEb(self, failure_):
        self.disp(
            _(
                u"Can't create profile {profile} to associate with jid {jid}: {msg}"
            ).format(profile=self.args.profile, jid=self.args.jid, msg=failure_),
            error=True,
        )
        self.host.quit(C.EXIT_BRIDGE_ERRBACK)

    def accountNewCb(self):
        self.disp(_(u"XMPP account created"), 1)
        if self.args.profile is not None:
            self.disp(_(u"creating profile"), 2)
            self.host.bridge.profileCreate(
                self.args.profile,
                self.args.password,
                "",
                callback=self._profileCreateCb,
                errback=self._profileCreateEb,
            )
        else:
            self.host.quit()

    def accountNewEb(self, failure_):
        self.disp(
            _(u"Can't create new account on server {host} with jid {jid}: {msg}").format(
                host=self.args.host or u"localhost", jid=self.args.jid, msg=failure_
            ),
            error=True,
        )
        self.host.quit(C.EXIT_BRIDGE_ERRBACK)

    def start(self):
        self.host.bridge.inBandAccountNew(
            self.args.jid,
            self.args.password,
            self.args.email,
            self.args.host,
            self.args.port,
            callback=self.accountNewCb,
            errback=self.accountNewEb,
        )


class AccountModify(base.CommandBase):
    def __init__(self, host):
        super(AccountModify, self).__init__(
            host, "modify", help=_(u"change password for XMPP account")
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "password", type=base.unicode_decoder, help=_(u"new XMPP password")
        )

    def start(self):
        self.host.bridge.inBandPasswordChange(
            self.args.password,
            self.args.profile,
            callback=self.host.quit,
            errback=self.errback,
        )


class AccountDelete(base.CommandBase):
    def __init__(self, host):
        super(AccountDelete, self).__init__(
            host, "delete", help=_(u"delete a XMPP account")
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help=_(u"delete account without confirmation"),
        )

    def _got_jid(self, jid_str):
        jid_ = jid.JID(jid_str)
        if not self.args.force:
            message = (
                u"You are about to delete the XMPP account with jid {jid_}\n"
                u'This is the XMPP account of profile "{profile}"\n'
                u"Are you sure that you want to delete this account ?".format(
                    jid_=jid_, profile=self.profile
                )
            )
            res = raw_input("{} (y/N)? ".format(message))
            if res not in ("y", "Y"):
                self.disp(_(u"Account deletion cancelled"))
                self.host.quit(2)
        self.host.bridge.inBandUnregister(
            jid_.domain, self.args.profile, callback=self.host.quit, errback=self.errback
        )

    def start(self):
        self.host.bridge.asyncGetParamA(
            "JabberID",
            "Connection",
            profile_key=self.profile,
            callback=self._got_jid,
            errback=self.errback,
        )


class Account(base.CommandBase):
    subcommands = (AccountCreate, AccountModify, AccountDelete)

    def __init__(self, host):
        super(Account, self).__init__(
            host, "account", use_profile=False, help=(u"XMPP account management")
        )
