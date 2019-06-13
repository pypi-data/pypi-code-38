from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from ftw.topics import _
from ftw.topics.interfaces import ITopicBrowserLayer
from ftw.topics.interfaces import ITopicRootFinder
from ftw.topics.interfaces import ITopicSupport
from Products.Archetypes.public import ReferenceField
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implements


class ExtendedReferenceField(ExtensionField, ReferenceField):
    """Schemaextender reference field
    """


class ATTopicSupportExtender(object):
    adapts(ITopicSupport)
    implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)

    layer = ITopicBrowserLayer

    def __init__(self, context):
        self.context = context

    def getFields(self):
        startup_directory = self.get_startup_directory()

        return [
            ExtendedReferenceField(
                name='topics',
                relationship='ftw.topics',
                allowed_types=('ftw.topics.Topic',),
                multiValued=True,
                write_permission='ftw.topics: Set Topic Reference',
                schemata='categorization',

                widget=ReferenceBrowserWidget(
                    label=_(u'label_topics', default=u'Topics'),
                    startup_directory=startup_directory,
                    )

                )]

    def get_startup_directory(self):
        site = getSite()  # CMFEditions support
        finder = getMultiAdapter((self.context, site.REQUEST),
                                 ITopicRootFinder)
        return finder.get_topic_root_path()

    def getOrder(self, schematas):
        return schematas
