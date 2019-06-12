from zope.interface import Interface
from zope import schema


class IMemberRegistry(Interface):
    member_nav_tree_query_path = schema.TextLine(
        title=u"Member navigation tree query path",
        description=u"Add the path to your contactdirectory: '/address'",
        default=u"",
        required=False)
