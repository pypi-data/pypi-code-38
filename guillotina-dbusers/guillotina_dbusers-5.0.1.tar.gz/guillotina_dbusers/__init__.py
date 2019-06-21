# -*- coding: utf-8 -*-
from guillotina import configure
from guillotina.i18n import MessageFactory

_ = MessageFactory('guillotina_dbusers')


app_settings = {
    "auth_user_identifiers": [
        "guillotina_dbusers.users.DBUserIdentifier"
    ]
}

configure.permission("guillotina.NotAuthenticated", "")
configure.permission("guillotina.Authenticated", "")
configure.permission("guillotina.AddUser", title="Add plone user")
configure.permission("guillotina.AddGroup", title="Add plone group")
configure.grant(permission="guillotina.AccessContent",
                role="guillotina.Anonymous")
configure.grant(permission="guillotina.NotAuthenticated",
                role="guillotina.Anonymous")
configure.grant(permission="guillotina.Authenticated",
                role="guillotina.Authenticated")
configure.grant(permission="guillotina.AddUser",
                role="guillotina.ContainerAdmin")
configure.grant(permission="guillotina.AddGroup",
                role="guillotina.ContainerAdmin")


def includeme(root, settings):
    configure.scan('guillotina_dbusers.content.users')
    configure.scan('guillotina_dbusers.content.groups')
    configure.scan('guillotina_dbusers.install')
    configure.scan('guillotina_dbusers.services')
    configure.scan('guillotina_dbusers.subscribers')
    configure.scan('guillotina_dbusers.permissions')
    configure.scan("guillotina_dbusers.serializers")
