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

# Delete all events from a calendar

import sys
import os
import configparser
import email
import logging
import imaplib
import json

import caldav

url = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]
calendar_name = sys.argv[4]

client = caldav.DAVClient(url, username=username, password=password)
principal = client.principal()
calendar = None
for c in principal.calendars():
    if c.name == calendar_name:
        calendar = c
existing_events = []
for e in calendar.events():
    print(e.url)
    existing_events.append((e.instance.vevent.dtstart.value,
                            e.instance.vevent.summary.value))
    e.delete()
