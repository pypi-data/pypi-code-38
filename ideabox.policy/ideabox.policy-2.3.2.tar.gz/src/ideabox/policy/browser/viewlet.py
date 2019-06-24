# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets import ViewletBase
from zope.component import getMultiAdapter


class UserMenuViewlet(ViewletBase):

    index = ViewPageTemplateFile("templates/user_menu.pt")

    def user_actions(self):
        context_state = getMultiAdapter(
            (self.context, self.request), name=u"plone_context_state"
        )

        actions = context_state.actions("user_menu")
        return actions

    def user_name(self):
        user = api.user.get_current()
        return user
