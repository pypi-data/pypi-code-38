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

import logging

class Plugin:
    def __init__(self, assistant):
        self.assistant = assistant
        self.log = logging.getLogger('assistant.%s' % self.name)

    def match(self, msg):
        raise NotImplemented()

    def get_events(self, msg):
        raise NotImplemented()
