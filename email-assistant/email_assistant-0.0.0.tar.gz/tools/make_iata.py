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

# Create the iata.py file from upstream data.

import urllib.request

f = urllib.request.urlopen("https://raw.githubusercontent.com/hroptatyr/dateutils/tzmaps/iata.tzmap")
data = f.read().decode('ascii')

with open('iata.py', 'w') as out:
    out.write('tzmap = {\n')
    for line in data.split('\n'):
        if not line: continue
        code, tz = [x.strip() for x in line.split()]
        out.write("    '%s': '%s',\n" % (code, tz))
    out.write('}\n')
