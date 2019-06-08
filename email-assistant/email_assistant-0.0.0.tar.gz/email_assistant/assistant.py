#!/usr/bin/env python3

# Copyright (C) 2019 James E. Blair <corvus@gnu.org>
#
# This file is part of Email-assistant.
#
# Email-assistant is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# Email-assistant is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Email-assistant.  If not, see
# <https://www.gnu.org/licenses/>.

import os
import argparse
import configparser
import email
import logging
import imaplib
import json

import caldav
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import dateutil.tz
import pbr.version

from email_assistant import plugins

# Number of days to look backwards when scanning a mailbox for the first time:
IMAP_BACKFILL = 180

class Mailbox:
    def __init__(self, name, host, username, password, folders):
        self.log = logging.getLogger('assistant.mailbox')
        self.name = name
        self.imap = imaplib.IMAP4_SSL(host)
        self.imap.login(username, password)
        self.folders = folders
        self.uidinfo = {}
        self.state_file = os.path.expanduser('~/.config/email-assistant/%s.mailbox' % name)
        if os.path.exists(self.state_file):
            with open(self.state_file) as f:
                self.uidinfo = json.load(f)

    def get_messages(self):
        for folder in self.folders:
            status = self.imap.status(folder, '(UIDNEXT UIDVALIDITY)')
            status = status[1][0].split(b' ', 1)[1][1:-1].split()
            uidnext = int(status[1])
            uidvalidity = int(status[3])
            self.log.debug("%s uidnext:%s uidvalidity:%s", folder, uidnext, uidvalidity)
            self.imap.select(folder)
            state = self.uidinfo.setdefault(folder, {})
            if uidvalidity != state.get('uidvalidity'):
                # fetch backlog of msgs
                self.log.info("%s uidvalidity changed", folder)
                uids = self.imap.uid('search', 'younger %i' % (IMAP_BACKFILL*24*60*60))
                prev = None
            else:
                # fetch new msgs
                prev = state.get('uidnext')
                uids = self.imap.uid('search', 'uid %s:*' % prev)
            uids = [int(x) for x in uids[1][0].split()]
            if prev is not None:
                if prev-1 in uids:
                    uids.remove(prev-1)
            self.log.debug("uids: %s", uids)
            state['uidnext'] = uidnext
            state['uidvalidity'] = uidvalidity
            for uid in uids:
                msg = self.imap.uid('fetch', str(uid), '(BODY.PEEK[])')
                msg = msg[1][0][1]
                self.log.debug("fetch %s %s" % (uid, len(msg)))
                yield msg

    def save(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.uidinfo, f)

class Calendar:
    def __init__(self, url, username, password, calendar):
        self.log = logging.getLogger('assistant.calendar')
        self.client = caldav.DAVClient(url, username=username, password=password)
        self.calendar_name = calendar
        principal = self.client.principal()
        self.calendar = None
        for c in principal.calendars():
            if c.name == self.calendar_name:
                self.calendar = c
        if not self.calendar:
            raise Exception("Unable to find calendar %s" % (self.calendar,))

    def get_events(self):
        return self.calendar.events()

    def add_events(self, events):
        for event in events:
            try:
                self.calendar.event_by_uid(event.vevent.uid.value)
                found = True
            except caldav.lib.error.NotFoundError:
                found = False
            if found:
                self.log.info("Found existing event: %s", event.vevent.summary.value)
            else:
                self.log.info("Adding event: %s", event.vevent.summary.value)
                self.calendar.add_event(event.serialize())

class Assistant:
    def __init__(self):
        self.log = logging.getLogger('main')
        self.geolocator = None
        self.tzfinder = None
        self.plugins = []
        for p in plugins.plugins:
            self.plugins.append(p(self))

    def get_tzinfo(self, location):
        if self.geolocator is None:
            return None
        try:
            loc = self.geolocator.geocode(location)
            tzname = self.tzfinder.timezone_at(lat=loc.point[0], lng=loc.point[1])
            return(dateutil.tz.gettz(tzname))
        except Exception:
            self.log.exception("Unable to geolocate %s", location)
        return None

    def main(self):
        config = configparser.ConfigParser()
        config.read(os.path.expanduser('~/.config/email-assistant/config'))

        if config.has_option('general', 'geocode'):
            if config['general']['geocode'].lower() == 'nominatim':
                version_info = pbr.version.VersionInfo('email-assistant')
                release_string = version_info.release_string()
                self.geolocator = Nominatim(user_agent="email-assistant %s" % release_string)
                self.tzfinder = TimezoneFinder()

        calendars = {}
        mailboxes = {}
        targets = {}
        for section in config.sections():
            if section.startswith('mailbox '):
                name = section.split()[1]
                mailboxes[name] = Mailbox(
                    name,
                    config[section]['host'],
                    config[section]['username'],
                    config[section]['password'],
                    config[section]['folders'].split(','))
            elif section.startswith('calendar '):
                name = section.split()[1]
                calendars[name] = Calendar(
                    config[section]['url'],
                    config[section]['username'],
                    config[section]['password'],
                    config[section]['calendar'])
            elif section.startswith('pair'):
                t = targets.setdefault(config[section]['mailbox'], set())
                t.add(config[section]['calendar'])
        for mb, cs in targets.items():
            self.sync(mailboxes[mb], [calendars[c] for c in cs])

    def sync(self, mailbox, calendars):
        for msg in mailbox.get_messages():
            msg = email.message_from_bytes(msg)
            self.log.debug("Processing %s", msg['subject'])
            events = None
            try:
                for p in self.plugins:
                    if p.match(msg):
                        events = p.get_events(msg)
                        break
            except Exception:
                self.log.exception("Error parsing %s", msg['subject'])
            if events:
                for calendar in calendars:
                    calendar.add_events(events)
        mailbox.save()

def main():
    parser = argparse.ArgumentParser(
        description='Create calendar events from emails.')
    parser.add_argument('-v', dest='verbose', action='store_true',
                        help='Output verbose debug info')
    parser.add_argument('-vv', dest='very_verbose', action='store_true',
                        help='Output verbose debug info (including client libraries)')
    parser.add_argument('-q', dest='quiet', action='store_true',
                        help='Only output errors')
    args = parser.parse_args()
    level = None
    if args.quiet:
        level = logging.ERROR
    elif args.very_verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    if level:
        logger = logging.getLogger('assistant')
        logger.setLevel(level)
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    Assistant().main()
