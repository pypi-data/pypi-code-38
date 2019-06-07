# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from AccessControl.users import BasicUser
from Acquisition import aq_parent
from collective.contentgroups.utils import list_users
from plone import api

import logging


logger = logging.getLogger(__name__)


class GroupAdapter(BasicUser):
    """This adapts items with our group behavior to IGroupData from PlonePAS.

    The IGroupData interface says this "is an abstract interface for accessing
    properties on a group object."

    We may not want to fill in everything: we *could* support setting properties
    in the Users and Groups control panel, but this should just be done in the
    edit form of the Group itself.
    """

    security = ClassSecurityInfo()
    security.declareObjectPrivate()

    def __init__(self, group):
        self.group = group
        self.id = group.id
        self._title = self.group.Title() or group.id
        self._groups = set()
        self._roles = set()
        self._userids = list_users(self.group)

    # from Products.PlonePAS.plugins.group.PloneGroup:

    def getId(self):
        """Return the string id of this group.

        This is from IBasicUser.
        """
        return self.id

    def getMemberIds(self, transitive=1):
        """Return member ids of this group.

        With transitive=1, this should include transitive groups.
        But the standard PloneGroup from PlonePAS ignores this argument,
        so we ignore it too.
        The PAS recursive_groups plugin automatically handles this for all groups,
        at least for all plugins that are above it in the IGroupsPlugin interface.
        In our setuphandlers.py we arrange that our plugin is indeed above it.
        """
        return self._userids

    def getRolesInContext(self, object):
        """Since groups can't actually log in, do nothing.
        """
        return []

    def allowed(self, object, object_roles=None):
        """Since groups can't actually log in, do nothing.
        """
        return 0

    # from Products.PlonePAS.plugins.ufactory.PloneUser:

    def isGroup(self):
        """Return 1/True if this user is a group abstraction."""
        return True

    def getName(self):
        """Get user's or group's name.
        This is the id. PAS doesn't do prefixes and such like GRUF.
        """
        return self.getId()

    def getUserId(self):
        """Get user's or group's name. This is the id.
        """
        return self.getId()

    # Next we need some methods from
    # Products.PluggableAuthService.PropertiedUser.PropertiedUser
    # which implements
    # Products.PluggableAuthService.interfaces.authservice.IPropertiedUser
    # But that is only for users that have property sheets associated,
    # implementing addPropertysheet, listPropertysheets, getPropertysheet.
    # We only need authservice.IBasicUser, which IPropertiedUser subclasses.

    def getUserName(self):
        """Return the name used by the user to log into the system.

        Groups do not login, but Plone needs this anyway.
        """
        return self.getId()

    def getRoles(self):
        """Return the roles assigned to a user "globally".

        The roles should have been added in plugins.py in getGroupById
        by calling group._addRoles.
        """
        return sorted(self._roles)

    def getDomains(self):
        """Return the list of domain restrictions for a user.

        This is only really used in OFS.users.BasicUser.authenticate.
        If getDomains returns a result, it does an extra check
        domainSpecMatch(domains, request) to see if the user is allowed
        to authenticate on this domain.
        The 'authenticate' method won't actually get called for groups.

        So anyway, it is safe to return an empty list.
        """
        return []

    def getGroups(self):
        """Return the groups the user is in.

        This does not seem to be in any interface.
        But PropertiedUser has it, and RecursiveGroupsPlugin calls it.
        """
        return sorted(self._groups)

    # PropertiedUser defines methods to allow user folder plugins to annotate the user.

    def _addGroups(self, groups=()):
        """Extend our set of groups.

        o Don't complain about duplicates.
        """
        if groups:
            self._groups.update(set(groups))

    def _addRoles(self, roles=()):
        """Extend our set of roles.

        o Don't complain about duplicates.
        """
        if roles:
            self._roles.update(set(roles))

    # IGroupData

    def setProperties(self, properties=None, **kw):
        """Allows setting of group properties en masse.

        Properties can be given either as a dict or a keyword parameters list.
        """
        if not (properties or kw):
            # Do not bother complaining.
            return
        raise NotImplementedError

    def getProperty(self, id, default=None):
        """Return the value of the property specified by 'id'."""
        if id == "title":
            return self._title
        return default

    def getProperties(self):
        """Return the properties of this group.

        Properties are as usual in Zope.
        """
        return {"title": self._title}

    def getGroupId(self):
        """Return the string id of this group, WITHOUT group prefix."""
        return self.getId()

    def getMemberId(self):
        """This exists only for a basic user/group API compatibility."""
        return self.getId()

    def getGroupName(self):
        """Return the name of the group.

        Plone seems to expect an id, not a title.
        """
        return self.getId()

    def getGroupMembers(self):
        """Return a list of the portal_memberdata-ish members of the group."""
        if not self._userids:
            return []
        # The memberdata-ish part is the problem.
        # Following code adapted from Products.PlonePAS.tools.groupdata.GroupData.
        pas = api.portal.get_tool("acl_users")
        md = api.portal.get_tool("portal_memberdata")
        ret = []
        for u_name in self._userids:
            usr = pas.getUserById(u_name)
            # getUserById is from PluggableAuthService, so not yet wrapped.
            if usr:
                ret.append(md.wrapUser(usr))
                continue
            # No user found, may be a group.
            usr = pas.getGroupById(u_name)
            # getGroupById is from PlonePAS, and is already wrapped.
            if not usr:
                logger.debug("Group has a non-existing principal %s", u_name)
                continue
            ret.append(usr)
        return ret

    def getAllGroupMembers(self):
        """Return a list of the portal_memberdata-ish members of the group.

        According to the PloneGroup docstring this should include transitive ones
        (ie. users or groups of a group in that group).  But that was never implemented.
        So we do not do this either.
        """
        return self.getGroupMembers()

    def getGroupMemberIds(self):
        """Return a list of the user ids of the group."""
        return self._userids

    def getAllGroupMemberIds(self):
        """Return a list of the user ids of the group.

        According to the PloneGroup docstring this should include transitive ones
        (ie. users or groups of a group in that group).  But that was never implemented.
        So we do not do this either.
        """
        return self.getGroupMemberIds()

    def addMember(self, id):
        """Add the existing member with the given id to the group."""
        raise NotImplementedError

    def removeMember(self, id):
        """Remove the member with the provided id from the group."""
        raise NotImplementedError

    def getGroup(self):
        """Returns the actual group implementation."""
        return self.group

    def getGroupTitleOrName(self):
        """Get the Title property of the group.

        If there is none then return the name.
        Method is on GroupData object, but is not defined in the interface.
        Plone needs it anyway.
        """
        return self._title

    def setGroupProperties(self, mapping):
        """PAS-specific method to set the properties of a group.

        Part of GroupData.
        """
        if not mapping:
            # Do not bother complaining.
            return
        raise NotImplementedError

    # Products.PlonePAS.interfaces.capabilities.IManageCapabilities:
    # Interface for MemberData/GroupData to provide information as to whether
    # or not the member can be deleted, reset password, modify a property.
    # Several of these are called by
    # Products.CMFPlone.controlpanel.browser.usergroups_groupsoverview
    # in doSearch.
    # Most of this we do not support: you should use the content UI.

    def canDelete(self):
        """True if group can be removed from the Plone UI."""
        return False

    def canPasswordSet(self):
        """True if group can change password."""
        return False

    def passwordInClear(self):
        """True if password can be retrieved in the clear (not hashed.)"""
        return False

    def canWriteProperty(self, id):
        """Check if a property can be modified."""
        return False

    def _group_id_in_plugin(self, group_id):
        # Is group id part of our plugin?
        plugin = aq_parent(self)
        if plugin is None:
            # happens in basic unit tests
            return False
        return group_id in plugin.getGroupIds()

    def canAddToGroup(self, group_id):
        """True if group can be added to other group.

        We allow this, because this does not require code of ourselves.
        Well, maybe if the other group_id is also a content group...
        Indeed, that gives a KeyError in
        Products.PluggableAuthService.plugins.ZODBGroupManager in addPrincipalToGroup.
        """
        return not self._group_id_in_plugin(group_id)

    def canRemoveFromGroup(self, group_id):
        """True if group can be removed from other group.

        We allow this, because this does not require code of ourselves.
        Well, maybe if the other group_id is also a content group...
        """
        return not self._group_id_in_plugin(group_id)

    def canAssignRole(self, role_id):
        """True if group can be assigned role. Role id is string."""
        return False


InitializeClass(GroupAdapter)
