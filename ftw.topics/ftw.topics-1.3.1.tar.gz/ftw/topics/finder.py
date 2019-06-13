from Acquisition import aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.topics.interfaces import ITopicRootFinder
from ftw.topics.interfaces import ITopicTree
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.component import adapts
from zope.component.hooks import getSite
from zope.interface import Interface
from zope.interface import implements


class DefaultTopicTreeFinder(object):
    """The topic tree finder is used for deciding where the topic
    trees are to select from in the "topics" widget.

    It walks up from the current context and returns the next
    INavigationRoot which contains ITopicTree objects,
    or the IPloneSiteRoot if it is reached.
    """

    implements(ITopicRootFinder)
    adapts(Interface, Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_topic_root_path(self):
        obj = self.context
        while obj:
            if INavigationRoot.providedBy(obj) and \
                    self._has_direct_topic_trees(obj):
                return '/'.join(obj.getPhysicalPath())

            if IPloneSiteRoot.providedBy(obj):
                return '/'.join(obj.getPhysicalPath())

            obj = aq_parent(obj)

        return '/'.join(getSite().getPhysicalPath())

    def _has_direct_topic_trees(self, context):
        for obj in context.objectValues():
            if ITopicTree.providedBy(obj):
                return True

        return False
