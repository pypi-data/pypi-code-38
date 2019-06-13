from ftw.referencewidget.widget import ReferenceBrowserWidget
from ftw.topics import _
from ftw.topics.interfaces import ITopicRootFinder
from plone.app.relationfield.event import extract_relations
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from plone.directives.form import widget
from z3c.relationfield.event import _setRelation
from z3c.relationfield.schema import RelationList
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import Interface


def get_topic_root(widget):
    finder = getMultiAdapter((widget.context, widget.request),
                             ITopicRootFinder)
    return finder.get_topic_root_path()


class ITopicSupportSchema(Interface):
    """Schema interface for the `ITopicSupport` behavior, adding
    a reference field `topics` to the content type.
    """

    widget('topics',
           ReferenceBrowserWidget,
           override=True,
           start=get_topic_root,
           allow_traversal=["ftw.topics.Topic", "ftw.topics.TopicTree"],
           selectable=["ftw.topics.Topic"])
    form.write_permission(topics='ftw.topics.SetTopicReference')
    topics = RelationList(
        title=_(u'label_topics', default=u'Topics'),
        required=False,
    )


alsoProvides(ITopicSupportSchema, IFormFieldProvider)


# From: https://github.com/4teamwork/opengever.core/commit/88e015d
def add_behavior_relations(obj, event):
    """Register relations in behaviors.

    This event handler fixes a bug in plone.app.relationfield, which only
    updates the zc.catalog when an object gets modified, but not when it gets
    added.
    """
    for behavior_interface, name, relation in extract_relations(obj):
        _setRelation(obj, name, relation)
