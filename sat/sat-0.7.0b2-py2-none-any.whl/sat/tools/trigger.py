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

from sat.core.i18n import _
from sat.core.log import getLogger

log = getLogger(__name__)


class TriggerException(Exception):
    pass


class SkipOtherTriggers(Exception):
    """ Exception to raise if normal behaviour must be followed instead of following triggers list """

    pass


class TriggerManager(object):
    """This class manage triggers: code which interact to change the behaviour of SàT"""

    try:  # FIXME: to be removed when a better solution is found
        MIN_PRIORITY = float("-inf")
        MAX_PRIORITY = float("+inf")
    except:  # XXX: Pyjamas will bug if you specify ValueError here
        # Pyjamas uses the JS Float class
        MIN_PRIORITY = Number.NEGATIVE_INFINITY
        MAX_PRIORITY = Number.POSITIVE_INFINITY

    def __init__(self):
        self.__triggers = {}

    def add(self, point_name, callback, priority=0):
        """Add a trigger to a point

        @param point_name: name of the point when the trigger should be run
        @param callback: method to call at the trigger point
        @param priority: callback will be called in priority order, biggest
        first
        """
        if point_name not in self.__triggers:
            self.__triggers[point_name] = []
        if priority != 0 and priority in [
            trigger_tuple[0] for trigger_tuple in self.__triggers[point_name]
        ]:
            if priority in (self.MIN_PRIORITY, self.MAX_PRIORITY):
                log.warning(_(u"There is already a bound priority [%s]") % point_name)
            else:
                log.debug(
                    _(u"There is already a trigger with the same priority [%s]")
                    % point_name
                )
        self.__triggers[point_name].append((priority, callback))
        self.__triggers[point_name].sort(
            key=lambda trigger_tuple: trigger_tuple[0], reverse=True
        )

    def remove(self, point_name, callback):
        """Remove a trigger from a point

        @param point_name: name of the point when the trigger should be run
        @param callback: method to remove, must exists in the trigger point
        """
        for trigger_tuple in self.__triggers[point_name]:
            if trigger_tuple[1] == callback:
                self.__triggers[point_name].remove(trigger_tuple)
                return
        raise TriggerException("Trying to remove an unexisting trigger")

    def point(self, point_name, *args, **kwargs):
        """This put a trigger point

        All the triggers for that point will be run
        @param point_name: name of the trigger point
        @param *args: args to transmit to trigger
        @param *kwargs: kwargs to transmit to trigger
            if "triggers_no_cancel" is present, it will be popup out
                when set to True, this argument don't let triggers stop
                the workflow
        @return: True if the action must be continued, False else
        """
        if point_name not in self.__triggers:
            return True

        can_cancel = not kwargs.pop('triggers_no_cancel', False)

        for priority, trigger in self.__triggers[point_name]:
            try:
                if not trigger(*args, **kwargs) and can_cancel:
                    return False
            except SkipOtherTriggers:
                break
        return True

    def returnPoint(self, point_name, *args, **kwargs):
        """Like point but trigger must return (continue, return_value)

        All triggers for that point must return a tuple with 2 values:
            - continue, same as for point, if False action must be finished
            - return_value: value to return ONLY IF CONTINUE IS FALSE
        @param point_name: name of the trigger point
        @return: True if the action must be continued, False else
        """

        if point_name not in self.__triggers:
            return True

        for priority, trigger in self.__triggers[point_name]:
            try:
                cont, ret_value = trigger(*args, **kwargs)
                if not cont:
                    return False, ret_value
            except SkipOtherTriggers:
                break
        return True, None
