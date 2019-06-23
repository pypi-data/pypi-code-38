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

"""This module permits to manage profiles. It can list, create, delete
and retrieve information about a profile."""

from sat_frontends.jp.constants import Const as C
from sat.core.log import getLogger
log = getLogger(__name__)
from sat.core.i18n import _
from sat_frontends.jp import base
from functools import partial

__commands__ = ["Profile"]

PROFILE_HELP = _('The name of the profile')


class ProfileConnect(base.CommandBase):
    """Dummy command to use profile_session parent, i.e. to be able to connect without doing anything else"""

    def __init__(self, host):
        # it's weird to have a command named "connect" with need_connect=False, but it can be handy to be able
        # to launch just the session, so some paradoxes don't hurt
        super(ProfileConnect, self).__init__(host, 'connect', need_connect=False, help=(u'connect a profile'))

    def add_parser_options(self):
        pass


class ProfileDisconnect(base.CommandBase):

    def __init__(self, host):
        super(ProfileDisconnect, self).__init__(host, 'disconnect', need_connect=False, help=(u'disconnect a profile'))
        self.need_loop = True

    def add_parser_options(self):
        pass

    def start(self):
        self.host.bridge.disconnect(self.args.profile, callback=self.host.quit)


class ProfileDefault(base.CommandBase):
    def __init__(self, host):
        super(ProfileDefault, self).__init__(host, 'default', use_profile=False, help=(u'print default profile'))

    def add_parser_options(self):
        pass

    def start(self):
        print self.host.bridge.profileNameGet('@DEFAULT@')


class ProfileDelete(base.CommandBase):
    def __init__(self, host):
        super(ProfileDelete, self).__init__(host, 'delete', use_profile=False, help=(u'delete a profile'))

    def add_parser_options(self):
        self.parser.add_argument('profile', type=str, help=PROFILE_HELP)
        self.parser.add_argument('-f', '--force', action='store_true', help=_(u'delete profile without confirmation'))

    def start(self):
        if self.args.profile not in self.host.bridge.profilesListGet():
            log.error("Profile %s doesn't exist." % self.args.profile)
            self.host.quit(1)
        if not self.args.force:
            message = u"Are you sure to delete profile [{}] ?".format(self.args.profile)
            res = raw_input("{} (y/N)? ".format(message))
            if res not in ("y", "Y"):
                self.disp(_(u"Profile deletion cancelled"))
                self.host.quit(2)

        self.host.bridge.asyncDeleteProfile(self.args.profile, callback=lambda __: None)


class ProfileInfo(base.CommandBase):
    def __init__(self, host):
        super(ProfileInfo, self).__init__(host, 'info', need_connect=False, help=_(u'get information about a profile'))
        self.need_loop = True
        self.to_show = [(_(u"jid"), "Connection", "JabberID"),]
        self.largest = max([len(item[0]) for item in self.to_show])


    def add_parser_options(self):
        self.parser.add_argument('--show-password', action='store_true', help=_(u'show the XMPP password IN CLEAR TEXT'))

    def showNextValue(self, label=None, category=None, value=None):
        """Show next value from self.to_show and quit on last one"""
        if label is not None:
            print((u"{label:<"+unicode(self.largest+2)+"}{value}").format(label=label+": ", value=value))
        try:
            label, category, name = self.to_show.pop(0)
        except IndexError:
            self.host.quit()
        else:
            self.host.bridge.asyncGetParamA(name, category, profile_key=self.host.profile,
                                            callback=lambda value: self.showNextValue(label, category, value))

    def start(self):
        if self.args.show_password:
            self.to_show.append((_(u"XMPP password"), "Connection", "Password"))
        self.showNextValue()


class ProfileList(base.CommandBase):
    def __init__(self, host):
        super(ProfileList, self).__init__(host, 'list', use_profile=False, use_output='list', help=(u'list profiles'))

    def add_parser_options(self):
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument('-c', '--clients', action='store_true', help=_(u'get clients profiles only'))
        group.add_argument('-C', '--components', action='store_true', help=(u'get components profiles only'))


    def start(self):
        if self.args.clients:
            clients, components = True, False
        elif self.args.components:
            clients, components = False, True
        else:
            clients, components = True, True
        self.output(self.host.bridge.profilesListGet(clients, components))


class ProfileCreate(base.CommandBase):
    def __init__(self, host):
        super(ProfileCreate, self).__init__(host, 'create', use_profile=False, help=(u'create a new profile'))
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument('profile', type=str, help=_(u'the name of the profile'))
        self.parser.add_argument('-p', '--password', type=str, default='', help=_(u'the password of the profile'))
        self.parser.add_argument('-j', '--jid', type=str, help=_(u'the jid of the profile'))
        self.parser.add_argument('-x', '--xmpp-password', type=str, help=_(u'the password of the XMPP account (use profile password if not specified)'),
                                 metavar='PASSWORD')
        self.parser.add_argument('-C', '--component', type=base.unicode_decoder, default='',
                                 help=_(u'set to component import name (entry point) if this is a component'))

    def _session_started(self, __):
        if self.args.jid:
            self.host.bridge.setParam("JabberID", self.args.jid, "Connection", profile_key=self.args.profile)
        xmpp_pwd = self.args.password or self.args.xmpp_password
        if xmpp_pwd:
            self.host.bridge.setParam("Password", xmpp_pwd, "Connection", profile_key=self.args.profile)
        self.host.quit()

    def _profile_created(self):
        self.host.bridge.profileStartSession(self.args.password, self.args.profile, callback=self._session_started, errback=None)

    def start(self):
        """Create a new profile"""
        if self.args.profile in self.host.bridge.profilesListGet():
            log.error("Profile %s already exists." % self.args.profile)
            self.host.quit(1)
        self.host.bridge.profileCreate(self.args.profile, self.args.password, self.args.component,
                                       callback=self._profile_created,
                                       errback=partial(self.errback,
                                                       msg=_(u"can't create profile: {}"),
                                                       exit_code=C.EXIT_BRIDGE_ERRBACK))


class ProfileModify(base.CommandBase):
    def __init__(self, host):
        super(ProfileModify, self).__init__(host, 'modify', need_connect=False, help=_(u'modify an existing profile'))

    def add_parser_options(self):
        profile_pwd_group = self.parser.add_mutually_exclusive_group()
        profile_pwd_group.add_argument('-w', '--password', type=base.unicode_decoder, help=_(u'change the password of the profile'))
        profile_pwd_group.add_argument('--disable-password', action='store_true', help=_(u'disable profile password (dangerous!)'))
        self.parser.add_argument('-j', '--jid', type=base.unicode_decoder, help=_(u'the jid of the profile'))
        self.parser.add_argument('-x', '--xmpp-password', type=base.unicode_decoder, help=_(u'change the password of the XMPP account'),
                                 metavar='PASSWORD')
        self.parser.add_argument('-D', '--default', action='store_true', help=_(u'set as default profile'))

    def start(self):
        if self.args.disable_password:
            self.args.password = ''
        if self.args.password is not None:
            self.host.bridge.setParam("Password", self.args.password, "General", profile_key=self.host.profile)
        if self.args.jid is not None:
            self.host.bridge.setParam("JabberID", self.args.jid, "Connection", profile_key=self.host.profile)
        if self.args.xmpp_password is not None:
            self.host.bridge.setParam("Password", self.args.xmpp_password, "Connection", profile_key=self.host.profile)
        if self.args.default:
            self.host.bridge.profileSetDefault(self.host.profile)


class Profile(base.CommandBase):
    subcommands = (ProfileConnect, ProfileDisconnect, ProfileCreate, ProfileDefault, ProfileDelete, ProfileInfo, ProfileList, ProfileModify)

    def __init__(self, host):
        super(Profile, self).__init__(host, 'profile', use_profile=False, help=_(u'profile commands'))
