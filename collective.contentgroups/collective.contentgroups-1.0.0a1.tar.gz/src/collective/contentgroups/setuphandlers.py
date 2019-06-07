# -*- coding: utf-8 -*-
from collective.contentgroups.config import PLUGIN_ID
from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

import logging


logger = logging.getLogger("collective.contentgroups")


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return ["collective.contentgroups:uninstall"]


def post_install(context):
    """Post install script.

    Setup our contentgroups plugin.
    """
    pas = api.portal.get_tool("acl_users")
    ID = PLUGIN_ID

    # Create plugin if it does not exist.
    if ID not in pas.objectIds():
        from collective.contentgroups.plugins import ContentGroupsPlugin

        plugin = ContentGroupsPlugin(title="Content Groups plugin")
        plugin.id = ID
        pas._setObject(ID, plugin)
        logger.info("Created %s in acl_users.", ID)
    plugin = getattr(pas, ID)

    # Activate all supported interfaces for this plugin.
    activate = []
    plugins = pas.plugins
    for info in plugins.listPluginTypeInfo():
        interface = info["interface"]
        interface_name = info["id"]
        if plugin.testImplements(interface):
            activate.append(interface_name)
            logger.info(
                "Activating interface %s for plugin %s", interface_name, info["title"]
            )

    plugin.manage_activateInterfaces(activate)
    logger.info("Plugins activated.")

    # Order some plugins to make sure our plugin is at the top.
    # This is needed for IGroupsPlugin to put us above the recursive_groups plugin.
    for info in plugins.listPluginTypeInfo():
        interface_name = info["id"]
        if interface_name != "IGroupsPlugin":
            continue
        iface = plugins._getInterfaceFromName(interface_name)
        plugin_ids = plugins.listPluginIds(iface)
        rec_id = "recursive_groups"
        if rec_id in plugin_ids:
            target_index = plugin_ids.index(rec_id)
            moves = len(plugin_ids) - target_index - 1
            for _move in range(moves):
                plugins.movePluginsUp(iface, [PLUGIN_ID])
            logger.info(
                "Moved %s above the recursive groups plugin in %s.",
                PLUGIN_ID,
                interface_name,
            )
        # We only need to handle one interface, so we can break here.
        break


def uninstall(context):
    """Uninstall script

    Remove our contentgroups plugin.
    """
    pas = api.portal.get_tool("acl_users")
    ID = PLUGIN_ID
    if ID in pas.objectIds():
        pas._delObject(ID)
        logger.info("Removed %s from acl_users.", ID)
