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
import json

from bs4 import BeautifulSoup
import dateutil.parser
import dateutil.tz
import inscriptis
import vobject

from email_assistant import plugin

class Plugin(plugin.Plugin):
    name = 'eventbrite'

    def match(self, msg):
        if ('orders@eventbrite.com' in msg['From'] and
            'Your Tickets for' in msg['Subject']):
            return True

    def get_events(self, msg):
        events = []
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                soup = BeautifulSoup(part.get_payload(decode=True).decode('utf8'), 'html.parser')
                data = json.loads(soup.find('script', type="application/ld+json").string)

                address = data['reservationFor']['location']['address']
                location = ' '.join((address['streetAddress'],
                                     address['addressLocality'],
                                     address['addressRegion'],
                                     address['postalCode'],
                                     address['addressCountry']))
                summary = data['reservationFor']['name']

                start = dateutil.parser.parse(data['reservationFor']['startDate'])
                end = dateutil.parser.parse(data['reservationFor']['endDate'])
                if start.date() != end.date():
                    # If it is a multi-day event, don't schedule a time.
                    start = start.date()
                    end = end.date()+datetime.timedelta(days=1)
                else:
                    # We do have a TZ offset, and could schedule this as a
                    # UTC event.  It would generally display correctly,
                    # but it would make it difficult to view the event
                    # when the viewer is in a different timezone (as they
                    # would have to mentally perform the UTC conversion,
                    # instead of being able to see the event's own "local"
                    # time.  To mitigate this, perform a location lookup.
                    tzinfo = self.assistant.get_tzinfo(location)
                    if tzinfo is not None:
                        start = start.replace(tzinfo=tzinfo)
                        end = end.replace(tzinfo=tzinfo)

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
