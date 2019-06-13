# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument


from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.interface import Interface


class ITopicBrowserLayer(Interface):
    """ftw.topics specific browser layer.
    """


class ITopicTree(Interface):
    """Marker interface for the root object of the topic tree.
    """


class ITopic(Interface):
    """Marker interface for topic objects.
    """


class ITopicRootFinder(Interface):
    """This adapter is used for finding the root of the selectable
    topic trees for the widget.
    Usually all topics in the plone site are referenceable.
    """

    def __init__(context, request):
        """Adapts any object and the request.
        """

    def get_topic_root_path():
        """Returns the path to the topic root.
        A topic root is usually the parent of the ITopicTree.
        """


class ITopicSupport(Interface):
    """Archetypes object providing this interface are extended
    with an additional reference field "topics" for adding
    references on the topic.
    """


class ITopicReferencePresentation(Interface):
    """Representation adapter of backreferences"""

    def __init__(context, request):
        """Adapts context and request"""

    def consume(objects):
        """Stores the objects, which this adapter can display, yields not
        consumed objects"""

    def title():
        """Group title"""

    def position():
        """Order of adapter call"""

    def available():
        """Determines availability"""


class IBackReferenceCollector(Interface):
    """The back reference collector adapter collects the back references
    from the adapted topic object.
    It groups the results into groups.
    The presentation in the topic views is filtered by group.

    The default implementation uses INavigationRoot for grouping.
    """

    def __init__(context, request):
        """The multi-adapter adapts the topic and the request (for easier
        customiziation using browserlayers).
        """

    def __call__(group_by=INavigationRoot):
        """By default the result is grouped by INavigationRoot.
        This means that each object which is providing INavigationRoot may
        act as a group and the content within this object is assigned
        to this group.
        """
