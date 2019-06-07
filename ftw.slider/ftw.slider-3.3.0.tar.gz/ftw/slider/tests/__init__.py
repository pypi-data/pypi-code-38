import transaction
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from unittest2 import TestCase

from ftw.slider.testing import SLIDER_FUNCTIONAL_TESTING


class FunctionalTestCase(TestCase):
    layer = SLIDER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()
