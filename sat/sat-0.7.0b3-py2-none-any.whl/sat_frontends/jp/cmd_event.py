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
from sat.tools.common.ansi import ANSI as A
from sat_frontends.jp.constants import Const as C
from sat_frontends.jp import common
from functools import partial
from dateutil import parser as du_parser
import calendar
import time

__commands__ = ["Event"]

OUTPUT_OPT_TABLE = u"table"

# TODO: move date parsing to base, it may be useful for other commands


class Get(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            pubsub_flags={C.SINGLE_ITEM},
            use_verbose=True,
            help=_(u"get event data"),
        )
        self.need_loop = True

    def add_parser_options(self):
        pass

    def eventInviteeGetCb(self, result):
        event_date, event_data = result
        event_data["date"] = event_date
        self.output(event_data)
        self.host.quit()

    def start(self):
        self.host.bridge.eventGet(
            self.args.service,
            self.args.node,
            self.args.item,
            self.profile,
            callback=self.eventInviteeGetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't get event data: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class EventBase(object):
    def add_parser_options(self):
        self.parser.add_argument(
            "-i",
            "--id",
            type=base.unicode_decoder,
            default=u"",
            help=_(u"ID of the PubSub Item"),
        )
        self.parser.add_argument(
            "-d", "--date", type=unicode, help=_(u"date of the event")
        )
        self.parser.add_argument(
            "-f",
            "--field",
            type=base.unicode_decoder,
            action="append",
            nargs=2,
            dest="fields",
            metavar=(u"KEY", u"VALUE"),
            help=_(u"configuration field to set"),
        )

    def parseFields(self):
        return dict(self.args.fields) if self.args.fields else {}

    def parseDate(self):
        if self.args.date:
            try:
                date = int(self.args.date)
            except ValueError:
                try:
                    date_time = du_parser.parse(
                        self.args.date, dayfirst=not (u"-" in self.args.date)
                    )
                except ValueError as e:
                    self.parser.error(_(u"Can't parse date: {msg}").format(msg=e))
                if date_time.tzinfo is None:
                    date = calendar.timegm(date_time.timetuple())
                else:
                    date = time.mktime(date_time.timetuple())
        else:
            date = -1
        return date


class Create(EventBase, base.CommandBase):
    def __init__(self, host):
        super(Create, self).__init__(
            host,
            "create",
            use_pubsub=True,
            help=_("create or replace event"),
        )
        EventBase.__init__(self)
        self.need_loop = True

    def eventCreateCb(self, node):
        self.disp(_(u"Event created successfuly on node {node}").format(node=node))
        self.host.quit()

    def start(self):
        fields = self.parseFields()
        date = self.parseDate()
        self.host.bridge.eventCreate(
            date,
            fields,
            self.args.service,
            self.args.node,
            self.args.id,
            self.profile,
            callback=self.eventCreateCb,
            errback=partial(
                self.errback,
                msg=_(u"can't create event: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class Modify(EventBase, base.CommandBase):
    def __init__(self, host):
        super(Modify, self).__init__(
            host,
            "modify",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_("modify an existing event"),
        )
        EventBase.__init__(self)
        self.need_loop = True

    def start(self):
        fields = self.parseFields()
        date = 0 if not self.args.date else self.parseDate()
        self.host.bridge.eventModify(
            self.args.service,
            self.args.node,
            self.args.id,
            date,
            fields,
            self.profile,
            callback=self.host.quit,
            errback=partial(
                self.errback,
                msg=_(u"can't update event data: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class InviteeGet(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            pubsub_flags={C.NODE, C.ITEM, C.SINGLE_ITEM},
            use_verbose=True,
            help=_(u"get event attendance"),
        )
        self.need_loop = True

    def add_parser_options(self):
        pass

    def eventInviteeGetCb(self, event_data):
        self.output(event_data)
        self.host.quit()

    def start(self):
        self.host.bridge.eventInviteeGet(
            self.args.service,
            self.args.node,
            self.profile,
            callback=self.eventInviteeGetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't get event data: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class InviteeSet(base.CommandBase):
    def __init__(self, host):
        super(InviteeSet, self).__init__(
            host,
            "set",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_("set event attendance"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-f",
            "--field",
            type=base.unicode_decoder,
            action="append",
            nargs=2,
            dest="fields",
            metavar=(u"KEY", u"VALUE"),
            help=_(u"configuration field to set"),
        )

    def start(self):
        fields = dict(self.args.fields) if self.args.fields else {}
        self.host.bridge.eventInviteeSet(
            self.args.service,
            self.args.node,
            fields,
            self.profile,
            callback=self.host.quit,
            errback=partial(
                self.errback,
                msg=_(u"can't set event data: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class InviteesList(base.CommandBase):
    def __init__(self, host):
        extra_outputs = {"default": self.default_output}
        base.CommandBase.__init__(
            self,
            host,
            "list",
            use_output=C.OUTPUT_DICT_DICT,
            extra_outputs=extra_outputs,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_(u"get event attendance"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-m",
            "--missing",
            action="store_true",
            help=_(u"show missing people (invited but no R.S.V.P. so far)"),
        )
        self.parser.add_argument(
            "-R",
            "--no-rsvp",
            action="store_true",
            help=_(u"don't show people which gave R.S.V.P."),
        )

    def _attend_filter(self, attend, row):
        if attend == u"yes":
            attend_color = C.A_SUCCESS
        elif attend == u"no":
            attend_color = C.A_FAILURE
        else:
            attend_color = A.FG_WHITE
        return A.color(attend_color, attend)

    def _guests_filter(self, guests):
        return u"(" + unicode(guests) + ")" if guests else u""

    def default_output(self, event_data):
        data = []
        attendees_yes = 0
        attendees_maybe = 0
        attendees_no = 0
        attendees_missing = 0
        guests = 0
        guests_maybe = 0
        for jid_, jid_data in event_data.iteritems():
            jid_data[u"jid"] = jid_
            try:
                guests_int = int(jid_data["guests"])
            except (ValueError, KeyError):
                pass
            attend = jid_data.get(u"attend", u"")
            if attend == "yes":
                attendees_yes += 1
                guests += guests_int
            elif attend == "maybe":
                attendees_maybe += 1
                guests_maybe += guests_int
            elif attend == "no":
                attendees_no += 1
                jid_data[u"guests"] = ""
            else:
                attendees_missing += 1
                jid_data[u"guests"] = ""
            data.append(jid_data)

        show_table = OUTPUT_OPT_TABLE in self.args.output_opts

        table = common.Table.fromDict(
            self.host,
            data,
            (u"nick",)
            + ((u"jid",) if self.host.verbosity else ())
            + (u"attend", "guests"),
            headers=None,
            filters={
                u"nick": A.color(C.A_HEADER, u"{}" if show_table else u"{} "),
                u"jid": u"{}" if show_table else u"{} ",
                u"attend": self._attend_filter,
                u"guests": u"{}" if show_table else self._guests_filter,
            },
            defaults={u"nick": u"", u"attend": u"", u"guests": 1},
        )
        if show_table:
            table.display()
        else:
            table.display_blank(show_header=False, col_sep=u"")

        if not self.args.no_rsvp:
            self.disp(u"")
            self.disp(
                A.color(
                    C.A_SUBHEADER,
                    _(u"Attendees: "),
                    A.RESET,
                    unicode(len(data)),
                    _(u" ("),
                    C.A_SUCCESS,
                    _(u"yes: "),
                    unicode(attendees_yes),
                    A.FG_WHITE,
                    _(u", maybe: "),
                    unicode(attendees_maybe),
                    u", ",
                    C.A_FAILURE,
                    _(u"no: "),
                    unicode(attendees_no),
                    A.RESET,
                    u")",
                )
            )
            self.disp(
                A.color(C.A_SUBHEADER, _(u"confirmed guests: "), A.RESET, unicode(guests))
            )
            self.disp(
                A.color(
                    C.A_SUBHEADER,
                    _(u"unconfirmed guests: "),
                    A.RESET,
                    unicode(guests_maybe),
                )
            )
            self.disp(
                A.color(
                    C.A_SUBHEADER, _(u"total: "), A.RESET, unicode(guests + guests_maybe)
                )
            )
        if attendees_missing:
            self.disp("")
            self.disp(
                A.color(
                    C.A_SUBHEADER,
                    _(u"missing people (no reply): "),
                    A.RESET,
                    unicode(attendees_missing),
                )
            )

    def eventInviteesListCb(self, event_data, prefilled_data):
        """fill nicknames and keep only requested people

        @param event_data(dict): R.S.V.P. answers
        @param prefilled_data(dict): prefilled data with all people
            only filled if --missing is used
        """
        if self.args.no_rsvp:
            for jid_ in event_data:
                # if there is a jid in event_data
                # it must be there in prefilled_data too
                # so no need to check for KeyError
                del prefilled_data[jid_]
        else:
            # we replace empty dicts for existing people with R.S.V.P. data
            prefilled_data.update(event_data)

        # we get nicknames for everybody, make it easier for organisers
        for jid_, data in prefilled_data.iteritems():
            id_data = self.host.bridge.identityGet(jid_, self.profile)
            data[u"nick"] = id_data.get(u"nick", u"")

        self.output(prefilled_data)
        self.host.quit()

    def getList(self, prefilled_data={}):
        self.host.bridge.eventInviteesList(
            self.args.service,
            self.args.node,
            self.profile,
            callback=partial(self.eventInviteesListCb, prefilled_data=prefilled_data),
            errback=partial(
                self.errback,
                msg=_(u"can't get event data: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )

    def psNodeAffiliationsGetCb(self, affiliations):
        # we fill all affiliations with empty data
        # answered one will be filled in eventInviteesListCb
        # we only consider people with "publisher" affiliation as invited, creators are not, and members can just observe
        prefilled = {
            jid_: {}
            for jid_, affiliation in affiliations.iteritems()
            if affiliation in (u"publisher",)
        }
        self.getList(prefilled)

    def start(self):
        if self.args.no_rsvp and not self.args.missing:
            self.parser.error(_(u"you need to use --missing if you use --no-rsvp"))
        if self.args.missing:
            self.host.bridge.psNodeAffiliationsGet(
                self.args.service,
                self.args.node,
                self.profile,
                callback=self.psNodeAffiliationsGetCb,
                errback=partial(
                    self.errback,
                    msg=_(u"can't get event data: {}"),
                    exit_code=C.EXIT_BRIDGE_ERRBACK,
                ),
            )
        else:
            self.getList()


class InviteeInvite(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "invite",
            use_pubsub=True,
            pubsub_flags={C.NODE, C.SINGLE_ITEM},
            help=_(u"invite someone to the event through email"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-e",
            "--email",
            action="append",
            type=base.unicode_decoder,
            default=[],
            help="email(s) to send the invitation to",
        )
        self.parser.add_argument(
            "-N",
            "--name",
            type=base.unicode_decoder,
            default="",
            help="name of the invitee",
        )
        self.parser.add_argument(
            "-H",
            "--host-name",
            type=base.unicode_decoder,
            default="",
            help="name of the host",
        )
        self.parser.add_argument(
            "-l",
            "--lang",
            type=base.unicode_decoder,
            default="",
            help="main language spoken by the invitee",
        )
        self.parser.add_argument(
            "-U",
            "--url-template",
            type=base.unicode_decoder,
            default="",
            help="template to construct the URL",
        )
        self.parser.add_argument(
            "-S",
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

    def start(self):
        email = self.args.email[0] if self.args.email else None
        emails_extra = self.args.email[1:]

        self.host.bridge.eventInviteByEmail(
            self.args.service,
            self.args.node,
            self.args.item,
            email,
            emails_extra,
            self.args.name,
            self.args.host_name,
            self.args.lang,
            self.args.url_template,
            self.args.subject,
            self.args.body,
            self.args.profile,
            callback=self.host.quit,
            errback=partial(
                self.errback,
                msg=_(u"can't create invitation: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class Invitee(base.CommandBase):
    subcommands = (InviteeGet, InviteeSet, InviteesList, InviteeInvite)

    def __init__(self, host):
        super(Invitee, self).__init__(
            host, "invitee", use_profile=False, help=_(u"manage invities")
        )


class Event(base.CommandBase):
    subcommands = (Get, Create, Modify, Invitee)

    def __init__(self, host):
        super(Event, self).__init__(
            host, "event", use_profile=False, help=_("event management")
        )
