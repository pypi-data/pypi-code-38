#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Event handlers.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from zope.component import adapter
from zope.component import handle

from nti.schema.interfaces import IBeforeSchemaFieldAssignedEvent

__docformat__ = "restructuredtext en"


@adapter(IBeforeSchemaFieldAssignedEvent)
def before_object_assigned_event_dispatcher(event):
    """
    Listens for :mod:`zope.schema` fields to fire
    :class:`~nti.schema.interfaces.IBeforeSchemaFieldAssignedEvent`, and re-dispatches
    these events based on the value being assigned, the object being
    assigned to, and of course the event (note that
    :class:`~zope.schema.interfaces.IBeforeObjectAssignedEvent` is a
    sub-interface of :class:`~nti.schema.interfaces.IBeforeSchemaFieldAssignedEvent`).

    This is analogous to
    :func:`zope.component.event.objectEventNotify`
    """
    handle(event.object, event.context, event)
