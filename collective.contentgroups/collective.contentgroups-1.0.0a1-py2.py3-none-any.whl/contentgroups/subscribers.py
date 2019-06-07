# -*- coding: utf-8 -*-
from collective.contentgroups import config
from plone import api


def added_group(obj, event):
    """A Group has been added (or moved or removed).

    We can check oldParent, oldName, newParent, newName.
    For the moment, newName is the most interesting for us: there should not be
    a group or user with that name already.

    If in the future we use a utility to store an index of our groups and users,
    we may need to handle more in here.
    """
    if event.oldName == event.newName:
        # Group moved to different folder.  Not interesting.
        return
    if not event.newName:
        # Looks like a removal.
        return
    pas = api.portal.get_tool(name="acl_users")
    principals = pas.searchPrincipals(id=event.newName, exact_match=True)
    if not principals:
        return
    # Maybe we can abort the transaction and add a portal status message, but for now a ValueError is fine.
    # Also, aborting may mess with test isolation.
    error = "A user or group with this name ({0}) already exists.".format(event.newName)
    if len(principals) > 1:
        # Definitely bad.  Happens when checking Administrators or Reviewers.
        raise ValueError(error)
    principal = principals[0]
    # The found principal may be the content group that we are now adding.
    if principal.get("pluginid") != config.PLUGIN_ID:
        # Other plugin.
        raise ValueError(error)
    # The info from our plugin adds the UID.
    if principal.get("uid") != obj.UID():
        raise ValueError(error)
