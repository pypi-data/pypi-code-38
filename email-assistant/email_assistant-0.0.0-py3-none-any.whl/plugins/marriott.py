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

import re
import logging
import hashlib
import datetime

from bs4 import BeautifulSoup
import dateutil.parser
import dateutil.tz
import inscriptis
import vobject

from email_assistant import plugin

class Plugin(plugin.Plugin):
    name = 'marriott'

    def match(self, msg):
        if ('reservations@res-marriott.com' in msg['From'] and
            'Reservation Confirmation' in msg['Subject']):
            return True

    def get_events(self, msg):
        events = []
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                soup = BeautifulSoup(part.get_payload(decode=True).decode('utf8'), 'html.parser')
                summary = soup.find_all('table')[7].a.string.strip()
                location = soup.find_all('table')[9].a.string.strip()
                start = (soup.find('th', string=re.compile('Check-In:')).
                         find_next_sibling('th').string.strip())
                end = (soup.find('td', string=re.compile('Check-Out:')).
                         find_next_sibling('td').string.strip())
                start = dateutil.parser.parse(start).date()
                end = dateutil.parser.parse(end).date()+datetime.timedelta(days=1)
                cal = vobject.iCalendar()
                event = cal.add('vevent')
                event.add('dtstart').value = start
                event.add('dtend').value = end
                event.add('summary').value = summary
                text = inscriptis.get_text(str(soup))
                text = re.sub(r'([^ ]+)\s*\n', '\\1\n', text)
                event.add('description').value = text
                event.add('location').value = location
                uid = hashlib.sha1((str(start) + summary).encode('utf8')).hexdigest()
                event.add('uid').value = uid
                events.append(cal)
        return events
