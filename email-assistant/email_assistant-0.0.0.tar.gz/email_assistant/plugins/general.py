
# An unused sketch of a generalized plugin that uses commonregex to
# find dates and addresses.

import re
import logging
import hashlib
import datetime

from bs4 import BeautifulSoup
import commonregex
import dateutil.parser
import dateutil.tz
import inscriptis
import vobject

def match(msg):
    if ('reservations@res-marriott.com' in msg['From'] and
        'Reservation Confirmation' in msg['Subject']):
        return True

def get_events(msg):
    events = []
    log = logging.getLogger('assistant.marriott')
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            soup = BeautifulSoup(part.get_payload(decode=True).decode('utf8'), 'html.parser')

            start = end = location = None
            for element in soup.descendants:
                if not hasattr(element, 'children') and element.string:
                    text = element.string.strip()
                    if not text:
                        continue
                    found = commonregex.CommonRegex(text)
                    for date in found.dates:
                        if not start:
                            start = dateutil.parser.parse(date).date()
                            continue
                        if not end:
                            end = dateutil.parser.parse(date).date()+datetime.timedelta(days=1)
                    if found.street_addresses and not location:
                        location = text
            if not (start and end and location):
                continue
            cal = vobject.iCalendar()
            event = cal.add('vevent')
            event.add('dtstart').value = start
            event.add('dtend').value = end
            summary = re.match('Reservation Confirmation .*? for (.*)', msg['Subject']).group(1).strip()
            event.add('summary').value = summary
            event.add('description').value = inscriptis.get_text(str(soup))
            event.add('location').value = location
            uid = hashlib.sha1((str(start) + summary).encode('utf8')).hexdigest()
            event.add('uid').value = uid
            events.append(cal)
            print(repr(cal.serialize()))
    return events
