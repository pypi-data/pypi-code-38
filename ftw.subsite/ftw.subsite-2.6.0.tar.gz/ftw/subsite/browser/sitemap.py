from Acquisition import aq_inner
from ftw.subsite.utils import get_nav_root
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree
from Products.CMFPlone.browser import navigation
from Products.CMFPlone.browser import navtree
from zope.component import getMultiAdapter


class SubsiteSitemapQueryBuilder(navtree.SitemapQueryBuilder):

    def __init__(self, context):
        super(SubsiteSitemapQueryBuilder, self).__init__(context)

        root = get_nav_root(context)
        self.query['path']['query'] = '/'.join(root.getPhysicalPath())


class SubsiteCatalogSiteMap(navigation.CatalogSiteMap):

    def siteMap(self):
        context = aq_inner(self.context)

        queryBuilder = SubsiteSitemapQueryBuilder(context)
        query = queryBuilder()

        strategy = getMultiAdapter((context, self), INavtreeStrategy)

        return buildFolderTree(context, obj=context,
                               query=query, strategy=strategy)
