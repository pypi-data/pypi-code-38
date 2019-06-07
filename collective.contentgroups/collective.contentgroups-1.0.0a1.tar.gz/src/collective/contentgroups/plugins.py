# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from AccessControl.Permissions import manage_users
from collective.contentgroups.interfaces import IGroupMarker
from collective.contentgroups.utils import list_users
from plone import api
from Products.PlonePAS.interfaces import group as group_plugins
from Products.PluggableAuthService.interfaces import plugins as pas_plugins
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements

import logging


logger = logging.getLogger("collective.contentgroups")


class ContentGroupsPlugin(BasePlugin):
    """PAS Plugin which handles groups as content.
    """

    meta_type = "ContentGroups Plugin"
    security = ClassSecurityInfo()
    security.declareObjectProtected(manage_users)

    # Start of IGroupEnumerationPlugin

    def enumerateGroups(
        # C816 missing trailing comma in Python 3.6+, but black removes it
        self,
        id=None,
        exact_match=False,
        sort_by=None,
        max_results=None,
        **kw  # noqa C816
    ):

        """ -> (group_info_1, ... group_info_N)

        o Return mappings for groups matching the given criteria.

        o 'id' will return at most one mapping per supplied ID ('id'
          may be a sequence).

        o exact_match=False in combination with an id search is meant to be treated by
          the plugin as "contains" searches.  This is not supported by us.
          So we ignore the exact_match argument.
          Note that most searches in the UI are with title/name="Some name", not with id.

        o If 'sort_by' is passed, the results will be sorted accordingly.
          Valid values are 'id' or 'title' (or 'Title' or 'sortable_title' for the same effect.)

        o If 'max_results' is specified, it must be a positive integer,
          limiting the number of returned mappings.  If unspecified, the
          plugin should return mappings for all groups satisfying the
          criteria.

        o Minimal keys in the returned mappings:

          'id' -- (required) the group ID

          'pluginid' -- (required) the plugin ID (as returned by getId())

          'properties_url' -- (optional) the URL to a page for updating the
                              group's properties.

          'members_url' -- (optional) the URL to a page for updating the
                           principals who belong to the group.

        o Plugin *must* ignore unknown criteria.

        o Plugin may raise ValueError for invalid critera.

        o Insufficiently-specified criteria may have catastrophic
          scaling issues for some implementations.
        """
        query = {"object_provides": IGroupMarker}
        # Note that id could be a list or tuple of ids.
        if id:
            query["id"] = id
        # With PAS.searchGroups(name="a") we get passed both title=a and name=a.
        # If title is already in the kwargs, PAS does not override it.
        # So let's search for title first.
        title = kw.pop("title", None)
        name = kw.pop("name", None)
        if not title:
            title = name
        if title:
            query["Title"] = title
        # We can only support sorting by title or id.
        # Those are the only group-specific attributes that we pass back.
        # And actually it seems a good idea to always sort.
        if sort_by and sort_by in ("title", "Title", "sortable_title"):
            query["sort_on"] = "sortable_title"
        else:
            query["sort_on"] = "id"
        if max_results:
            try:
                max_results = int(max_results)
            except ValueError:
                pass
            else:
                # This is just a hint for the catalog.
                query["b_size"] = max_results
        if kw:
            # Add all remaining keyword arguments to the query. Seems fine.
            query.update(kw)
        groups = api.content.find(**query)
        results = []
        if max_results is not None:
            groups = groups[:max_results]
        for group in groups:
            results.append(
                {
                    "id": group.getId,
                    "pluginid": self.getId(),
                    "title": group.Title,
                    "uid": group.UID,
                }
            )
        return tuple(results)

    def _get_single_group_brain(self, group_id):
        """Helper method to get the brain of a single group by id."""
        query = {"object_provides": IGroupMarker, "id": group_id}
        groups = api.content.find(**query)
        if not groups:
            return
        return groups[0]

    # Start of IGroupsPlugin

    def getGroupsForPrincipal(self, principal, request=None):
        """ principal -> (group_1, ... group_N)

        o Return a sequence of group names to which the principal
          (either a user or another group) belongs.

        o May assign groups based on values in the REQUEST object, if present
        """
        groups = api.content.find(object_provides=IGroupMarker)
        principal_id = principal.getId()
        # We could use try to find groups recursively. So if user A belongs to sub content group S
        # and S belongs to content group G, we could report S and G as groups.
        # See utils.find_all_groups_for_principal_id in the git history.
        # But actually, if the PAS recursive_groups plugin is below us in the IGroupsPlugin
        # interface list, that plugin handles this for us.
        found = []
        for group in groups:
            obj = group.getObject()
            users = list_users(obj)
            if not users:
                continue
            if principal_id in users:
                found.append(obj.id)
        return tuple(found)

    # Start of IGroupIntrospection

    def getGroupById(self, group_id, default=None):
        """
        Returns the portal_groupdata-ish object for a group
        corresponding to this id.

        Taken over from Products.PlonePAS.plugins.group.
        """
        if group_id not in self.getGroupIds():
            return default
        brain = self._get_single_group_brain(group_id)
        if brain is None:
            return default
        group = group_plugins.IGroupData(brain.getObject(), None)
        if group is None:
            return default

        # Some of the next calls need a request, but it may be None.
        request = None

        # Determine the roles.
        pas = self._getPAS()
        plugins = pas._getOb("plugins")
        rolemakers = plugins.listPlugins(pas_plugins.IRolesPlugin)
        for rolemaker_id, rolemaker in rolemakers:
            roles = rolemaker.getRolesForPrincipal(group, request)
            if roles:
                group._addRoles(roles)
        group._addRoles(["Authenticated"])

        # PloneGroup does not fill _groups, but it seems a good idea to do it.
        # Then we calculate it only once here, instead of possibly multiple times.
        groups = pas._getGroupsForPrincipal(group, request, plugins=plugins)
        if groups:
            group._addGroups(groups)

        # Apparently it may help if this is acquisition wrapped.
        # But PlonePAS already does this, so it seems we may not need this.
        return group.__of__(self)
        # return group

    def getGroups(self):
        """Returns an iteration of the available groups

        Taken over from Products.PlonePAS.plugins.group.
        """
        return tuple([self.getGroupById(group_id) for group_id in self.getGroupIds()])

    def getGroupIds(self):
        """Returns a list of the available groups.
        """
        return tuple([group["id"] for group in self.enumerateGroups()])

    def getGroupMembers(self, group_id):
        """
        return the members of the given group
        """
        group = self._get_single_group_brain(group_id)
        if not group:
            return tuple()
        return tuple(list_users(group.getObject()))


InitializeClass(ContentGroupsPlugin)
classImplements(
    ContentGroupsPlugin,
    pas_plugins.IGroupEnumerationPlugin,
    pas_plugins.IGroupsPlugin,
    group_plugins.IGroupIntrospection,
)


def add_contentgroups_plugin():
    # Form for manually adding our plugin.
    # But we do this in setuphandlers.py always.
    pass
