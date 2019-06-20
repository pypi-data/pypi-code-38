# -*- coding: utf-8 -*-
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.testing import Layer
from zope.configuration import xmlconfig

import doctest


class PloneAppViewletmanagerLayer(Layer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.viewletmanager
        xmlconfig.file(
            'configure.zcml',
            plone.app.viewletmanager,
            context=configurationContext
        )


PLONE_APP_VIEWLETMANAGER_FIXTURE = PloneAppViewletmanagerLayer()
PLONE_APP_VIEWLETMANAGER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_VIEWLETMANAGER_FIXTURE, ),
    name='PloneAppViewletmanagerLayer:Integration'
)

optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
