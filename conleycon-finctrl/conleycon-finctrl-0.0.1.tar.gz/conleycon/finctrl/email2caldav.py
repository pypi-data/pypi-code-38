#!/usr/bin/env python3

import caldav, codecs, configparser, datetime, re, imaplib, os, quopri, sys
from datetime import datetime, timedelta
from caldav.elements import dav

userconf = configparser.ConfigParser()
userconf.read('user.cfg')

messageconf = configparser.ConfigParser(allow_no_value=True, delimiters='=')
# Don't lowercase options
messageconf.optionxform = lambda option: option
messageconf.read(sys.argv[1])

#since = sys.argv[2]
since = '{:%d-%b-%Y}'.format(datetime.now() - timedelta(days=1))
search = 'SINCE %s' % since

sections = messageconf.sections()

for option, value in messageconf.items('search'):
  search += ' %s "%s"' % (option, value)
sections.remove('search')

# Build up send and receive/checking versions of the fetch arguments
fetch = { 'send': [], 'receive' : [] }
decode = []
extract = []
output = []
for sec in sections:
  val = messageconf[sec]['fetch']
  fetch['send'].append(('BODY.PEEK[%s]' % val).encode('ascii'))
  regex = '[\\( ]' + re.escape('BODY[%s]' % val)
  fetch['receive'].append(regex.encode('ascii'))
  try:
    substring = messageconf[sec]['fetch.bytes']
    fetch['send'][-1] += ('<%s>' % substring).encode('ascii')
    sep = substring.index('.')
    s = '\\<%s\\> \\{(%s)\\}\r\n' % (substring[:sep], substring[sep + 1:])
    fetch['receive'][-1] += s.encode('ascii')
  except KeyError:
    fetch['receive'][-1] += b' \\{([0-9]+)\\}\r\n'

  decode.append(codecs.getdecoder(messageconf[sec]['decode']))

  extract.append(re.compile(messageconf[sec]['extract']))

mailconf = userconf['imap']
mail = imaplib.IMAP4_SSL(mailconf['hostname'])
mail.login(mailconf['username'], mailconf['password'])
mail.select('CashCal/Mail')
# TODO: check success, make configurable
response, data = mail.search(None, search)
assert response == 'OK'

vals = data[0].split()

command = b'1 FETCH ' + \
          b','.join(vals) + \
          b' (' + \
          b' '.join(fetch['send']) + \
          b')\r\n'

mail.send(command)

for i in vals:
  line = mail.readline()
  beginning = b'* ' + i + b' FETCH '
  assert line.startswith(beginning)
  line = line[len(beginning):]
  result = {}
  for j in range(0, len(fetch['receive'])):
    octets = int(re.fullmatch(fetch['receive'][j], line).group(1).decode('ascii'))
    if decode[j]:
      string, length = decode[j](mail.read(octets))
      assert length == octets
    else:
      string = mail.read(octets)
    if not isinstance(string, str):
      string = string.decode('ascii')
    for l in string.splitlines():
      try:
        for key, value in extract[j].match(l).groupdict().items():
          if value:
            result[key] = value
      except AttributeError:
        pass
    line = mail.readline()
  assert line == b')\r\n'
  output.append(result)
  # TODO: Check that j is in sync with the length of decode
assert mail.readline().startswith(b'1 OK')

mail.logout()

calconf = userconf['caldav']
url = '%s://%s:%s@%s' % (calconf['protocol'], calconf['username'],
  calconf['password'], calconf['hostname'])
client = caldav.DAVClient(url)
principal = client.principal()
calendars = principal.calendars()
print(calendars)
cal = None
for c in calendars:
  n = c.get_properties([dav.DisplayName(),])['{DAV:}displayname']
  # TODO: check folder naming on other hosts
  if n == 'CashCal » Transactions':
    cal = c
    break
assert cal

for o in output:
  # TODO: handle timezone
  if 'zone' in o:
    o.pop('zone')

  hour = int(o.pop('hour'))
  meridiem = o.pop('meridiem')
  if meridiem == 'PM':
    hour += 12
  else:
    assert meridiem == 'AM'

  o['date'] = '%04d%02d%02dT%02d%02d%02d' % (
    int(o.pop('year')), int(o.pop('month')), int(o.pop('day')),
    hour, int(o.pop('minute')), int(o.pop('second'))
  )

  # TODO: print pretty with commas and consistently
  if 'expense' in o:
    if not o['expense'].startswith('-'):
      o['amount'] = '-'
    o['amount'] += o.pop('expense')

  # TODO: Look up pretty names for merchants (description)

  o['seconds'] = '{:%s}'.format(datetime.now())
  print(o)

  e = '''BEGIN:VCALENDAR
VERSION:2.0
PRODID:finctrl/0.1
BEGIN:VEVENT
UID:{date}@{amount}@{seconds}
DTSTART:{date}
DTEND:{date}
SUMMARY:{amount}
DESCRIPTION:{description}
END:VEVENT
END:VCALENDAR'''.format(**o)
  print(e)
  cal.add_event(e)
