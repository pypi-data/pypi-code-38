from Acquisition import aq_base
from functools import partial
from operator import itemgetter
from pkg_resources import get_distribution
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFPlone.browser.navigation import get_view_url
from Products.Five.browser import BrowserView
from zExceptions import Unauthorized
import hashlib
import json
import logging


LOG = logging.getLogger('ftw.mobile')


def is_external_link(brain):
    if brain.portal_type == 'Link':
        url = brain.getRemoteUrl
        return not url.startswith(api.portal.get().absolute_url())
    else:
        return False


class MobileNavigation(BrowserView):
    """Compute navigation based on global settings and some given paramters.
    The return value is always a nested structure, which can be represented
    as json.

    Node representation:
     {'title': '<String>',
      'description': '<String>',
      'id' <String>:
      'url': '<String>',
      'externallink': '<Boolean>'}
    """

    def startup(self):
        """Return all nodes relevant for starting up a mobile navigation
        on the current context.
        """
        if not api.user.has_permission('View', obj=self.context):
            raise Unauthorized()

        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')

        if self.request.get('cachekey'):
            # Only cache when there is a cache_key in the request.
            # Representations may be cached by any cache.
            # The cached representation is to be considered fresh for 1 year
            # http://stackoverflow.com/a/3001556/880628
            if api.user.is_anonymous():
                visibility = 'public'
            else:
                visibility = 'private'

            response.setHeader('Cache-Control',
                               '{}, max-age=31536000'.format(visibility))

        query = self.get_startup_query()
        nodes = self.get_nodes_by_query(query)
        nodes = self.prepend_unauthorized_parents(nodes)
        map(partial(self.set_children_loaded_flag, query), nodes)

        return json.dumps(nodes)

    def get_startup_query(self):
        query = self.get_default_query()
        query['path'] = {'query': (list(self.parent_paths_to_nav_root()) +
                                   list(self.get_toplevel_paths())),
                         'depth': 4}
        return query

    def get_startup_cachekey(self):
        cachekey = hashlib.md5()
        query = self.get_startup_query()
        query['sort_on'] = 'modified'
        query['sort_order'] = 'reverse'
        query['sort_limit'] = 50
        brains = self.get_brains(query)[:query['sort_limit']]
        map(cachekey.update, map(str, map(itemgetter('modified'), brains)))
        cachekey.update(api.user.get_current().getId() or '')
        cachekey.update(get_distribution('ftw.mobile').version)
        return cachekey.hexdigest()

    def children(self):
        """Return all nodes
        """
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')

        query = self.get_default_query()
        query['path'] = {'query': ['/'.join(self.context.getPhysicalPath())],
                         'depth': int(self.request.get('depth', 2))}
        return json.dumps(self.get_nodes_by_query(query))

    def parent_paths_to_nav_root(self):
        """Generator of the paths of all parents up to the navigation_root.
        """
        for obj in self.context.aq_chain:
            if hasattr(aq_base(obj), 'getPhysicalPath'):
                yield '/'.join(obj.getPhysicalPath())
            if INavigationRoot.providedBy(obj):
                return

    def prepend_unauthorized_parents(self, nodes):
        """For the navigation to work properly, we need to make sure that
        the parents are included on startup.
        Otherwise no tree can be built and the navigation would not work.
        There might be the problem that the current user is not authorized
        to access a parent (View permission).
        For beeing consistent with other Plone navigations such as the
        navigation portlet or breadcrumbs we want to render the parents
        anyway and let the user hit an "Anauthorized"-error when the user
        clicks.
        This has the advantage that we can build the navigation tree properly.

        This method prepends the missing parents by doing an unrestricted
        catalog query.
        """

        nodes_paths = map(itemgetter('absolute_path'), nodes)
        paths_to_check = list(self.parent_paths_to_nav_root())

        # Append current context path also, because the current obj may
        # be excluded from nav.
        paths_to_check.append('/'.join(self.context.getPhysicalPath()))

        missing_paths = filter(lambda path: path not in nodes_paths,
                               paths_to_check)

        if not missing_paths:
            return nodes

        query = self.get_default_query()
        query['path'] = {'query': missing_paths,
                         'depth': 0}
        parents = self.get_nodes_by_query(query, unrestricted_search=True,
                                          filter_exclude_from_nav=False)
        return parents + nodes

    def get_toplevel_paths(self):
        navroot = api.portal.get_navigation_root(self.context)
        for child in navroot.getFolderContents():
            yield child.getPath()

    def get_nodes_by_query(self, query, unrestricted_search=False,
                           filter_exclude_from_nav=True):
        nodes = map(self.brain_to_node,
                    self.get_brains(
                        query,
                        unrestricted_search=unrestricted_search,
                        filter_exclude_from_nav=filter_exclude_from_nav))
        return nodes

    def get_brains(self, query, unrestricted_search=False,
                   filter_exclude_from_nav=True):
        catalog = api.portal.get_tool('portal_catalog')

        if unrestricted_search:
            brains = catalog.unrestrictedSearchResults(query)
        else:
            brains = catalog.searchResults(query)

        warnsize = 5000
        if len(brains) > warnsize:
            LOG.warning('Query results in more than {} results ({})'
                            .format(warnsize, len(brains)))

        if filter_exclude_from_nav:
            brains = [brain for brain in brains if not brain.exclude_from_nav]

        return brains

    def get_default_query(self):
        portal_types = api.portal.get_tool('portal_types')
        portal_properties = api.portal.get_tool('portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')

        exclude_types = getattr(navtree_properties, 'metaTypesNotToList', None)
        include_types = list(set(portal_types.keys()) - set(exclude_types))

        sort_on = getattr(navtree_properties,
                          'sortAttribute',
                          'getObjPositionInParent')

        sort_order = getattr(navtree_properties,
                             'sortOrder',
                             'asc')

        query = {'portal_type': include_types,
                 'sort_on': sort_on,
                 'sort_order': sort_order,
                 'is_default_page': False}
        return query

    def brain_to_node(self, brain):
        return {'title': brain.Title,
                'id': brain.id,
                'description': brain.Description,
                'url': get_view_url(brain)[1],
                'absolute_path': brain.getPath(),
                'externallink': is_external_link(brain)}

    def set_children_loaded_flag(self, query, node):
        if not isinstance(query.get('path', None), dict) \
           or 'depth' not in query.get('path', {}):
            # Since we have no path depth limitation we assume that all
            # items were provided in a single response, thus
            # all children are assumed to be loaded.
            node['children_loaded'] = True
            return

        depth = query['path']['depth']
        if depth == -1:
            # Since we have no path depth limitation we assume that all
            # items were provided in a single response, thus
            # all children are assumed to be loaded.
            node['children_loaded'] = True
            return

        path_partials = node['absolute_path'].split('/')
        for _ in range(depth - 1):
            if '/'.join(path_partials) in query['path']['query']:
                node['children_loaded'] = True
                return

            path_partials.pop()
