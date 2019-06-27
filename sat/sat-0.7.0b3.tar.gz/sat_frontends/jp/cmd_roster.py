#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# jp: a SAT command line tool
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2003-2016 Adrien Cossa (souliane@mailoo.org)

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
from collections import OrderedDict
from functools import partial
from sat.core.i18n import _
from sat_frontends.jp.constants import Const as C
from twisted.words.protocols.jabber import jid

__commands__ = ["Roster"]



class Purge(base.CommandBase):

    def __init__(self, host):
        super(Purge, self).__init__(host, 'purge', help=_('Purge the roster from its contacts with no subscription'))
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument("--no_from", action="store_true", help=_("Also purge contacts with no 'from' subscription"))
        self.parser.add_argument("--no_to", action="store_true", help=_("Also purge contacts with no 'to' subscription"))

    def start(self):
        self.host.bridge.getContacts(profile_key=self.host.profile, callback=self.gotContacts, errback=self.error)

    def error(self, failure):
        print (_("Error while retrieving the contacts [%s]") % failure)
        self.host.quit(1)

    def ask_confirmation(self, no_sub, no_from, no_to):
        """Ask the confirmation before removing contacts.

        @param no_sub (list[unicode]): list of contacts with no subscription
        @param no_from (list[unicode]): list of contacts with no 'from' subscription
        @param no_to (list[unicode]): list of contacts with no 'to' subscription
        @return bool
        """
        if no_sub:
            print "There's no subscription between profile [%s] and the following contacts:" % self.host.profile
            print "    " + "\n    ".join(no_sub)
        if no_from:
            print "There's no 'from' subscription between profile [%s] and the following contacts:" % self.host.profile
            print "    " + "\n    ".join(no_from)
        if no_to:
            print "There's no 'to' subscription between profile [%s] and the following contacts:" % self.host.profile
            print "    " + "\n    ".join(no_to)
        message = "REMOVE them from profile [%s]'s roster" % self.host.profile
        while True:
            res = raw_input("%s (y/N)? " % message)
            if not res or res.lower() == 'n':
                return False
            if res.lower() == 'y':
                return True

    def gotContacts(self, contacts):
        """Process the list of contacts.

        @param contacts(list[tuple]): list of contacts with their attributes and groups
        """
        no_sub, no_from, no_to = [], [], []
        for contact, attrs, groups in contacts:
            from_, to = C.bool(attrs["from"]), C.bool(attrs["to"])
            if not from_:
                if not to:
                    no_sub.append(contact)
                elif self.args.no_from:
                    no_from.append(contact)
            elif not to and self.args.no_to:
                no_to.append(contact)
        if not no_sub and not no_from and not no_to:
            print "Nothing to do - there's a from and/or to subscription(s) between profile [%s] and each of its contacts" % self.host.profile
        elif self.ask_confirmation(no_sub, no_from, no_to):
            for contact in no_sub + no_from + no_to:
                self.host.bridge.delContact(contact, profile_key=self.host.profile, callback=lambda __: None, errback=lambda failure: None)
        self.host.quit()


class Stats(base.CommandBase):

    def __init__(self, host):
        super(Stats, self).__init__(host, 'stats', help=_('Show statistics about a roster'))
        self.need_loop = True

    def add_parser_options(self):
        pass

    def start(self):
        self.host.bridge.getContacts(profile_key=self.host.profile, callback=self.gotContacts, errback=self.error)

    def error(self, failure):
        print (_("Error while retrieving the contacts [%s]") % failure)
        self.host.quit(1)

    def gotContacts(self, contacts):
        """Process the list of contacts.

        @param contacts(list[tuple]): list of contacts with their attributes and groups
        """
        hosts = {}
        unique_groups = set()
        no_sub, no_from, no_to, no_group, total_group_subscription = 0, 0, 0, 0, 0
        for contact, attrs, groups in contacts:
            from_, to = C.bool(attrs["from"]), C.bool(attrs["to"])
            if not from_:
                if not to:
                    no_sub += 1
                else:
                    no_from += 1
            elif not to:
                no_to += 1
            host = jid.JID(contact).host
            hosts.setdefault(host, 0)
            hosts[host] += 1
            if groups:
                unique_groups.update(groups)
                total_group_subscription += len(groups)
            if not groups:
                no_group += 1
        hosts = OrderedDict(sorted(hosts.items(), key=lambda item:-item[1]))

        print
        print "Total number of contacts: %d" % len(contacts)
        print "Number of different hosts: %d" % len(hosts)
        print
        for host, count in hosts.iteritems():
            print "Contacts on {host}: {count} ({rate:.1f}%)".format(host=host, count=count, rate=100 * float(count) / len(contacts))
        print
        print "Contacts with no 'from' subscription: %d" % no_from
        print "Contacts with no 'to' subscription: %d" % no_to
        print "Contacts with no subscription at all: %d" % no_sub
        print
        print "Total number of groups: %d" % len(unique_groups)
        try:
            contacts_per_group = float(total_group_subscription) / len(unique_groups)
        except ZeroDivisionError:
            contacts_per_group = 0
        print "Average contacts per group: {:.1f}".format(contacts_per_group)
        try:
            groups_per_contact = float(total_group_subscription) / len(contacts)
        except ZeroDivisionError:
            groups_per_contact = 0
        print "Average groups' subscriptions per contact: {:.1f}".format(groups_per_contact)
        print "Contacts not assigned to any group: %d" % no_group
        self.host.quit()


class Get(base.CommandBase):

    def __init__(self, host):
        super(Get, self).__init__(host, 'get', help=_('Retrieve the roster contacts'))
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument("--subscriptions", action="store_true", help=_("Show the contacts' subscriptions"))
        self.parser.add_argument("--groups", action="store_true", help=_("Show the contacts' groups"))
        self.parser.add_argument("--name", action="store_true", help=_("Show the contacts' names"))

    def start(self):
        self.host.bridge.getContacts(profile_key=self.host.profile, callback=self.gotContacts, errback=self.error)

    def error(self, failure):
        print (_("Error while retrieving the contacts [%s]") % failure)
        self.host.quit(1)

    def gotContacts(self, contacts):
        """Process the list of contacts.

        @param contacts(list[tuple]): list of contacts with their attributes and groups
        """
        field_count = 1  # only display the contact by default
        if self.args.subscriptions:
            field_count += 3  # ask, from, to
        if self.args.name:
            field_count += 1
        if self.args.groups:
            field_count += 1
        for contact, attrs, groups in contacts:
            args = [contact]
            if self.args.subscriptions:
                args.append("ask" if C.bool(attrs["ask"]) else "")
                args.append("from" if C.bool(attrs["from"]) else "")
                args.append("to" if C.bool(attrs["to"]) else "")
            if self.args.name:
                args.append(unicode(attrs.get("name", "")))
            if self.args.groups:
                args.append(u"\t".join(groups) if groups else "")
            print u";".join(["{}"] * field_count).format(*args).encode("utf-8")
        self.host.quit()


class Resync(base.CommandBase):

    def __init__(self, host):
        super(Resync, self).__init__(
            host, 'resync', help=_(u'do a full resynchronisation of roster with server'))
        self.need_loop = True

    def add_parser_options(self):
        pass

    def rosterResyncCb(self):
        self.disp(_(u"Roster resynchronized"))
        self.host.quit(C.EXIT_OK)

    def start(self):
        self.host.bridge.rosterResync(profile_key=self.host.profile,
                                      callback=self.rosterResyncCb,
                                      errback=partial(
                                          self.errback,
                                          msg=_(u"can't resynchronise roster: {}"),
                                          exit_code=C.EXIT_BRIDGE_ERRBACK,
                                      ))


class Roster(base.CommandBase):
    subcommands = (Get, Stats, Purge, Resync)

    def __init__(self, host):
        super(Roster, self).__init__(host, 'roster', use_profile=True, help=_("Manage an entity's roster"))
