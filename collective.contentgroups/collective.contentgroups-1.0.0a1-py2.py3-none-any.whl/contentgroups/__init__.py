# -*- coding: utf-8 -*-
from AccessControl.Permissions import manage_users as ManageUsers
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("collective.contentgroups")


def initialize(context):  # pragma: no cover
    """Initializer called when used as a Zope 2 product."""
    from collective.contentgroups import plugins

    registerMultiPlugin(plugins.ContentGroupsPlugin.meta_type)
    context.registerClass(
        plugins.ContentGroupsPlugin,
        permission=ManageUsers,
        constructors=(plugins.add_contentgroups_plugin,),
        # icon='www/PluggableAuthService.png',
    )
