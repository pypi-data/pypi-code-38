# -*- coding: utf-8 -*-
#
# File: adapters.py
#
# Copyright (c) 2014 by Imio.be
#
# GNU General Public License (GPL)
#

from Products.CMFCore.permissions import DeleteObjects
from plone import api


class ContentDeletableAdapter(object):
    """
      Manage the mayDelete on every objects.
    """

    def __init__(self, context):
        self.context = context

    def mayDelete(self, **kwargs):
        '''See docstring in interfaces.py'''
        member = api.user.get_current()
        return bool(member.has_permission(DeleteObjects, self.context))
