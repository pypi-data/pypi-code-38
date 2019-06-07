#!/usr/bin/env python3

import caldav, configparser
from caldav.elements import dav

d = {'date'        : '20160616T000000',
     'amount'      : '12.00',
     'description' : 'Test Vendor'}

d['prod'] = 'finctrl/0.1'
d['uid'] = '%s/%s/%s' % (d['date'], d['description'], d['amount'])
print(d)
exit()

s = '''BEGIN:VCALENDAR
VERSION:2.0
PRODID:{prod}
BEGIN:VEVENT
UID:{uid}@{prod}
DTSTART:{date}
DTEND:{date}
SUMMARY:{amount}
DESCRIPTION:{description}
END:VEVENT
END:VCALENDAR'''.format(**d)

# TODO: move to library
userconf = configparser.ConfigParser()
userconf.read('user.cfg')

host = userconf.sections()[1]

username = userconf[host]['username']
password = userconf[host]['password']
protocol = userconf[host]['protocol']

url = '%s://%s:%s@%s' % (protocol, username, password, host)
client = caldav.DAVClient(url)
principal = client.principal()
calendars = principal.calendars()
cal = None
for c in calendars:
  n = c.get_properties([dav.DisplayName(),])['{DAV:}displayname']
  if n == 'Cashcal':
    cal = c
    break

if not cal:
  print('Could not find "Cashcal" calendar.')
else:
  cal.add_event(s)
