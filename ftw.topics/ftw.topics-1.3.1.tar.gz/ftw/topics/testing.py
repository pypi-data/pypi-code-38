from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.testing import FunctionalSplinterTesting
from ftw.testing.layer import ComponentRegistryLayer
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import ploneSite
from plone.testing import Layer
from plone.testing import z2
from plone.testing import zca
from plone.testing import zodb
from zope.configuration import xmlconfig


class ZCMLLayer(ComponentRegistryLayer):

    def setUp(self):
        super(ZCMLLayer, self).setUp()
        import ftw.topics
        self.load_zcml_file('tests.zcml', ftw.topics.tests)
        self.load_zcml_file('configure.zcml', ftw.topics)

ZCML_LAYER = ZCMLLayer()


class TopicsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        import z3c.autoinclude
        xmlconfig.file('meta.zcml', z3c.autoinclude,
                       context=configurationContext)
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <includePlugins package="plone" />'
            '</configure>',
            context=configurationContext)

        import ftw.topics
        xmlconfig.file('functional_tests.zcml', ftw.topics.tests,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.topics:default')


TOPICS_FIXTURE = TopicsLayer()
TOPICS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(TOPICS_FIXTURE, ), name='ftw.topics:integration')
TOPICS_FUNCTIONAL_TESTING = FunctionalSplinterTesting(
    bases=(TOPICS_FIXTURE, ), name='ftw.topics:functional')


class ExampleContentLayer(Layer):

    defaultBases = (TOPICS_FIXTURE, )

    def setUp(self):
        # Stack the component registry
        self['configurationContext'] = zca.stackConfigurationContext(
            self.get('configurationContext'))

        # Stack the database
        self['zodbDB'] = zodb.stackDemoStorage(
            self.get('zodbDB'), name='SimplelayoutTopicsLayer')

        with ploneSite() as portal:
            applyProfile(portal, 'ftw.topics.tests:example')

    def tearDown(self):
        # Zap the stacked ZODB
        self['zodbDB'].close()
        del self['zodbDB']
        # Zap the stacked component registry
        del self['configurationContext']


EXAMPLE_CONTENT_FIXTURE = ExampleContentLayer()
EXAMPLE_CONTENT_DEFAULT_FUNCTIONAL = FunctionalTesting(
    bases=(EXAMPLE_CONTENT_FIXTURE, ),
    name='ftw.topics.examplecontent:default:functional')


class SimplelayoutTopicsLayer(Layer):

    defaultBases = (TOPICS_FIXTURE, )

    def setUp(self):
        # Stack a new DemoStorage
        self['zodbDB'] = zodb.stackDemoStorage(
            self.get('zodbDB'), name='SimplelayoutTopicsLayer')

        with z2.zopeApp() as app:
            z2.installProduct(app, 'simplelayout.types.common')
            z2.installProduct(app, 'ftw.contentpage')

        with ploneSite() as portal:
            applyProfile(portal, 'ftw.topics:simplelayout')

    def tearDown(self):
        # Zap the stacked ZODB
        self['zodbDB'].close()
        del self['zodbDB']


SIMPLELAYOUT_TOPICS_FIXTURE = SimplelayoutTopicsLayer()
SIMPLELAYOUT_TOPICS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(SIMPLELAYOUT_TOPICS_FIXTURE, ),
    name='ftw.topics:sl:integration')
SIMPLELAYOUT_TOPICS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SIMPLELAYOUT_TOPICS_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name='ftw.topics:sl:functional')


class SimplelayoutExampleContentLayer(SimplelayoutTopicsLayer):

    defaultBases = (EXAMPLE_CONTENT_FIXTURE, )


EXAMPLE_CONTENT_SIMPLELAYOUT_FIXTURE = SimplelayoutExampleContentLayer()
EXAMPLE_CONTENT_SIMPLELAYOUT_FUNCTIONAL = FunctionalTesting(
    bases=(EXAMPLE_CONTENT_SIMPLELAYOUT_FIXTURE, ),
    name='ftw.topics.examplecontent:sl:functional')
