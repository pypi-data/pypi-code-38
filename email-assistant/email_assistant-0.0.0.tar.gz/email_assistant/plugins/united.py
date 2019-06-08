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

from bs4 import BeautifulSoup
import dateutil.parser
import dateutil.tz
import inscriptis
import vobject

from email_assistant import iata
from email_assistant import plugin

def parse_dep_arr(flight_date, dep_arr):
    flight_year = dateutil.parser.parse(flight_date).year
    city, br, code, flight_time = dep_arr.span.children
    city = city.strip()
    code = code.strip()[1:-1]
    code = code.split()[0]
    tz = iata.tzmap[code]
    flight_time = flight_time.get_text().strip()
    m = re.match(r'(.*) \((\d+[A-Z]+)\)', flight_time)
    if m:
        s = '%s%s %s' % (m.group(2), flight_year, m.group(1))
        flight_time = dateutil.parser.parse(s)
    else:
        flight_time = dateutil.parser.parse(flight_date +' '+ flight_time)
    flight_time = flight_time.replace(tzinfo=dateutil.tz.gettz(tz))
    return (city, code, flight_time)

class Plugin(plugin.Plugin):
    name = 'united'

    def match(self, msg):
        if ('unitedairlines@united.com' in msg['From'] and
            'Itinerary and Receipt' in msg['Subject']):
            return True

    def get_events(self, msg):
        events = []
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                soup = BeautifulSoup(part.get_payload(decode=True).decode('utf8'), 'html.parser')
                # confirmation_number = soup.find(class_="eTicketConfirmation").string

                index = 0
                while True:
                    info = soup.find(id="ShowSegments_ShowSegment_ctl%02i_Flight" % index)
                    if not info:
                        break
                    for row in info.parents:
                        if row.name == 'tr':
                            break
                    cols = row.find_all('td')
                    flight_date, flight_num, flight_class, dep, arr, ac, meal = cols
                    flight_date = flight_date.get_text().strip()
                    flight_num = flight_num.get_text().strip()
                    flight_class = flight_class.get_text().strip()

                    dep_city, dep_code, dep_time = parse_dep_arr(flight_date, dep)
                    arr_city, arr_code, arr_time = parse_dep_arr(flight_date, arr)
                    self.log.debug("dep: %s %s %s", dep_city, dep_code, dep_time)
                    self.log.debug("arr: %s %s %s", arr_city, arr_code, arr_time)

                    cal = vobject.iCalendar()
                    event = cal.add('vevent')
                    event.add('dtstart').value = dep_time
                    event.add('dtend').value = arr_time
                    summary = "Flight from %s to %s" % (dep_code, arr_code)
                    event.add('summary').value = summary
                    text = inscriptis.get_text(str(soup))
                    text = re.sub(r'([^ ]+)\s*\n', '\\1\n', text)
                    event.add('description').value = text
                    event.add('location').value = "%s airport" % (dep_code,)
                    uid = hashlib.sha1((str(dep_time) + summary).encode('utf8')).hexdigest()
                    event.add('uid').value = uid
                    events.append(cal)
                    index += 1
        return events
