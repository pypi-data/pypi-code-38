# -*- coding: utf-8 -*-

from operun.contactform.testing import OPERUN_CONTACTFORM_FUNCTIONAL_TESTING
from operun.contactform.testing import setup_sdm
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import SITE_OWNER_NAME
from plone.testing.z2 import Browser

import unittest


class TestContactForm(unittest.TestCase):

    layer = OPERUN_CONTACTFORM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.view = api.content.get_view(
            context=self.portal, request=self.request, name='contact'
        )
        setup_sdm(self.portal)
        app = self.layer['app']
        self.browser = Browser(app)
        self.browser.handleErrors = False

    def test_contact_view(self):
        """Form can be rendered as admin and user"""
        # Can be rendered as administrator
        login(self.portal, SITE_OWNER_NAME)
        self.assertTrue(self.view())
        # Can be rendered as anonymous user
        logout()
        self.assertTrue(self.view())
        # Contains specified form elements
        self.assertEqual(self.view().count('form-group'), 8)

    def test_contact_view_submit(self):
        contact_url = self.portal.absolute_url() + '/contact'
        self.browser.open(contact_url)
        validation_error = 'Something went wrong, please check the input!'
        # Submit with missing required field
        self.browser.getControl(name='name').value = 'Max Mustermann'
        self.browser.getControl(name='subject').value = 'We ♥ Plone'
        self.browser.getControl(
            name='message'
        ).value = 'Plone «ταБЬℓσ»: 1<2 & 4+1>3, is 100% awesome!'
        self.browser.getControl(name='dsgvo').value = 1
        self.browser.getControl(name='form.buttons.submit').click()
        self.assertIn(validation_error, self.browser.contents)
        # Form should fill fields from request
        self.assertTrue(self.browser.getControl(name='name').value)
        # DSGVO checkbox should reset
        self.assertFalse(self.browser.getControl(name='dsgvo').value)
        # Submit with incorrect E-Mail format
        self.browser.getControl(name='email').value = 'max.mustermann.com'
        self.browser.getControl(name='dsgvo').value = 1
        self.browser.getControl(name='form.buttons.submit').click()
        self.assertIn(validation_error, self.browser.contents)
        # Submit without accepting DSGVO
        self.browser.getControl(
            name='email'
        ).value = 'max.mustermann@example.com'
        self.browser.getControl(name='form.buttons.submit').click()
        self.assertIn(validation_error, self.browser.contents)
        # Check E-Mail log is empty
        self.assertFalse(self.portal.MailHost.messages)
        # Submit form with correct field values
        self.browser.getControl(name='dsgvo').value = 1
        self.browser.getControl(name='form.buttons.submit').click()
        # Check E-Mail log is not empty - 'admin' and 'user' messages
        self.assertEqual(len(self.portal.MailHost.messages), 2)
        admin_msg = self.portal.MailHost.messages[0]
        user_msg = self.portal.MailHost.messages[1]
        self.assertIn('max.mustermann@example.com', admin_msg)
        self.assertIn(
            'Hello <span>Max Mustermann</span>', user_msg
        )
