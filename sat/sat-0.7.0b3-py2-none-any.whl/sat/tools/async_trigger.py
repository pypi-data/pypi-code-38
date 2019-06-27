#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Misc usefull classes"""

from sat.tools import trigger as sync_trigger
from twisted.internet import defer

class TriggerManager(sync_trigger.TriggerManager):
    """This is a TriggerManager with an new asyncPoint method"""

    @defer.inlineCallbacks
    def asyncPoint(self, point_name, *args, **kwargs):
        """This put a trigger point with potentially async Deferred

        All the triggers for that point will be run
        @param point_name: name of the trigger point
        @param *args: args to transmit to trigger
        @param *kwargs: kwargs to transmit to trigger
            if "triggers_no_cancel" is present, it will be popped out
                when set to True, this argument don't let triggers stop
                the workflow
        @return D(bool): True if the action must be continued, False else
        """
        if point_name not in self.__triggers:
            defer.returnValue(True)

        can_cancel = not kwargs.pop('triggers_no_cancel', False)

        for priority, trigger in self.__triggers[point_name]:
            try:
                cont = yield trigger(*args, **kwargs)
                if can_cancel and not cont:
                    defer.returnValue(False)
            except sync_trigger.SkipOtherTriggers:
                break
        defer.returnValue(True)
