"""Picked volunteer for stormbot"""
import os
import math
import isodate
import datetime
import random

from stormbot.bot import Plugin
from stormbot.storage import Storage

class Volunteer:
    def __init__(self, name, role):
        self.name = name
        self.role = role

    def appoint(self):
        return Actor(self)

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash((self.name, self.role))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and (self.name, self.role) == (other.name, other.role)

    def __ne__(self, other):
        return not (self == other)

class Actor:
    def __init__(self, volunteer):
        self.volunteer = volunteer
        now = datetime.datetime.now()
        self.start = self.role.last_start()

    @property
    def name(self):
        return self.volunteer.name

    @property
    def role(self):
        return self.volunteer.role

    @property
    def remaining(self):
        now = datetime.datetime.now()
        return self.start + self.role.duration - now

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash((self.volunteer, self.start))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and (self.volunteer, self.start) == (other.volunteer, other.start)

    def __ne__(self, other):
        return not (self == other)

class Role:
    def __init__(self, name, start, duration):
        self.name = name
        self.start = start
        self.duration = duration

    def last_start(self):
        now = datetime.datetime.now()
        return math.floor((now - self.start) / self.duration) * self.duration + self.start

    def next_start(self):
        now = datetime.datetime.now()
        return math.ceil((now - self.start) / self.duration) * self.duration + self.start

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    def __ne__(self, other):
        return not (self == other)

class VolunteerPicker(Plugin):
    def __init__(self, bot, args):
        self._bot = bot
        self.args = args
        self._cache = Storage(self.args.role_cache)
        if "actors" not in self._cache:
            self._cache["actors"] = {}
        self.actors = self._cache["actors"]
        if "volunteers" not in self._cache:
            self._cache["volunteers"] = {}
        self.volunteers = self._cache["volunteers"]

        self.roles = []
        for index, role in enumerate(args.role):
            self.roles.append(Role(role, args.role_start[index], args.role_duration[index]))

        roster = list(self._bot.plugin['xep_0045'].getRoster(self._bot.room))
        for role in self.roles:
            if role not in self.volunteers:
                self.volunteers[role] = []
            if self.args.role_all:
                for name in roster:
                    if name != self._bot.nick:
                        self.volunteers[role].append(Volunteer(name, role))

            now = datetime.datetime.now()
            self._bot.schedule(role, (role.next_start() - now).total_seconds(),
                               self.renew, args=(role,))

        random.seed()

        for role in self.roles:
            self.write_volunteers(role)
            self._bot.subscribe(role.name, self)

    def got_online(self, presence):
        if self.args.role_all:
            for role in self.roles:
                self.volunteers[role].append(Volunteer(presence['muc']['nick'], role))

    def write_volunteers(self, role):
        volunteers = self.volunteers[role]
        self._bot.write("{} {} for {}".format(", ".join([str(volunteer) for volunteer in volunteers])
                                              if len(volunteers) > 0 else "nobody",
                                              "are volunteers" if len(volunteers) > 1 else "is volunteer",
                                              role.name))

    def write_actors(self, role):
        if not role in self.actors or self.actors[role].remaining < datetime.timedelta(0):
            if len(self.volunteers[role]) < 1:
                self._bot.write("nobody is willing to be {}".format(role))
                return

            self.pick(random.choice(self.volunteers[role]))

        actor = self.actors[role]
        self._bot.write("{} is {} for {}".format(actor.name, actor.role.name, actor.remaining))

    @classmethod
    def argparser(cls, parser):
        parser.add_argument("--role-all", action='store_true', default=False, help="Consider all participants as volunteers")
        parser.add_argument("--role-cache", type=str, default="/var/cache/stormbot/role.p", help="Cache file (default: %(default)s)")
        parser.add_argument("--role", type=str, action='append')
        parser.add_argument("--role-start", type=isodate.parse_datetime, action='append')
        parser.add_argument("--role-duration", type=isodate.parse_duration, action='append')

    def role(self, rolename):
        return next((role for role in self.roles if role.name == rolename), rolename)

    def cmdparser(self, parser):
        subparser = parser.add_parser('whois', bot=self._bot)
        subparser.set_defaults(command=self.whois)
        subparser.add_argument("role", type=self.role, choices=self.roles)

        subparser = parser.add_parser('iam', bot=self._bot)
        subparser.set_defaults(command=self.iam)
        subparser.add_argument("role", type=self.role, choices=self.roles)

        subparser = parser.add_parser('whocouldbe', bot=self._bot)
        subparser.set_defaults(command=self.whocouldbe)
        subparser.add_argument("role", type=self.role, choices=self.roles)

        subparser = parser.add_parser('icouldbe', bot=self._bot)
        subparser.set_defaults(command=self.icouldbe)
        subparser.add_argument("role", type=self.role, choices=self.roles)

        subparser = parser.add_parser('icantbe', bot=self._bot)
        subparser.set_defaults(command=self.icantbe)
        subparser.add_argument("role", type=self.role, choices=self.roles)

        subparser = parser.add_parser('sit-out', bot=self._bot)
        subparser.set_defaults(command=self.sitout)
        subparser.add_argument("role", type=self.role, choices=self.roles)

    def message(self, nick, msg):
        target = None
        for role in self.roles:
            if role.name == nick:
                target = role

        if target is None:
            return

        if target not in self.actors:
            self._bot.write("{}: nobody is volunteer for {}".format(msg['mucnick'], target))
        else:
            self._bot.write("{}: {}".format(self.actors[target], msg['body']))

    def whois(self, msg, parser, args, peer):
        self.write_actors(args.role)

    def iam(self, msg, parser, args, peer):
        volunteer = Volunteer(msg['mucnick'], args.role)
        if volunteer not in self.volunteers[args.role]:
            self.volunteers[args.role].append(volunteer)
        self._bot.write("{}: thanks !".format(volunteer.name))
        if args.role in self.actors:
            self._bot.write("{}: you are no longer {} thanks to {}".format(self.actors[args.role],
                                                                           args.role,
                                                                           volunteer))
        self.pick(volunteer)
        self.write_actors(args.role)

    def whocouldbe(self, msg, parser, args, peer):
        self.write_volunteers(args.role)

    def icouldbe(self, msg, parser, args, peer):
        volunteer = Volunteer(msg['mucnick'], args.role)
        if volunteer not in self.volunteers[args.role]:
            self.volunteers[args.role].append(volunteer)
            self._bot.write("{}: glad to here that".format(msg['mucnick']))
            self.write_volunteers(args.role)
        else:
            self._bot.write("{}: you already volunteered for {}".format(msg['mucnick'], args.role))

    def icantbe(self, msg, parser, args, peer):
        volunteer = Volunteer(msg['mucnick'], args.role)
        if volunteer in self.volunteers[args.role]:
            self.volunteers[args.role].remove(volunteer)
            self._bot.write("{}: sad news…".format(msg['mucnick']))
            self.write_volunteers(args.role)
        else:
            self._bot.write("{}: I know, I know, you can't be {}".format(msg['mucnick'], args.role))

    def sitout(self, msg, parser, args, peer):
        if msg['mucnick'] != self.actors[args.role].name:
            self._bot.write("{}: you are not {}, you dumbass!",
                            msg['mucnick'], args.role)
        else:
            self._bot.write("{}: coward!", msg['mucnick'])
            self.pick(random.choice(self.volunteers[args.role]))
            if msg['mucnick'] == self.actors[args.role].name:
                self._bot.write("{}: ahah fair randomness has choosen you again! https://xkcd.com/221/",
                                self.actors[args.role])
            else:
                self._bot.write("{}: you are now {} thanks to {}'s cowardice",
                                self.actors[args.role], args.role, msg['mucnick'])


    def pick(self, volunteer):
        self.actors[volunteer.role] = volunteer.appoint()

    def renew(self, role):
        self.write_actors(role)
        now = datetime.datetime.now()
        self._bot.schedule(role, (role.next_start() - now).total_seconds(),
                           self.renew, args=(role,))

if __name__ == "__main__":
    from stormbot.bot import main
    main(VolunteerPicker)
