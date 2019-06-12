# -*- coding: utf-8 -*-
from collective.embeddedpage.testing import COLLECTIVE_EMBEDDEDPAGE_INTEGRATION_TESTING  # noqa
from httmock import all_requests
from httmock import HTTMock
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from zope.component import getMultiAdapter

import lxml
import unittest


class EmbeddedPageViewIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_EMBEDDEDPAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory(
            'EmbeddedPage',
            id='epage',
            title='Embedded Page',
            before=RichTextValue('Before', 'text/html', 'text/html'),
            after=RichTextValue('After', 'text/html', 'text/html'),
        )
        self.portal.epage.url = 'https://plone.org'
        self.epage = self.portal.epage

    def test_view_with_get_multi_adapter(self):
        # Get the view
        view = getMultiAdapter((self.epage, self.request), name="view")
        # Put the view into the acquisition chain
        view = view.__of__(self.epage)
        # Call the view
        self.assertTrue(view())

    def test_view_with_restricted_traverse(self):
        view = self.epage.restrictedTraverse('view')
        self.assertTrue(view())

    def test_view_with_unrestricted_traverse(self):
        view = self.epage.unrestrictedTraverse('view')
        self.assertTrue(view())

    def get_parsed_data(self):
        view = getMultiAdapter((self.epage, self.request), name="view")
        view = view.__of__(self.epage)
        return lxml.html.fromstring(view())

    def test_view_html_structure(self):
        output = self.get_parsed_data()
        before = output.cssselect('.before-embeddedpage')
        embedded = output.cssselect('.embeddedpage')
        after = output.cssselect('.after-embeddedpage')
        self.assertEqual(1, len(before))
        self.assertEqual(1, len(embedded))
        self.assertEqual(1, len(after))

    def test_view_data_embedded(self):
        output = self.get_parsed_data()
        embedded = output.cssselect('.embeddedpage')[0]
        self.assertEqual('https://plone.org', embedded.attrib['data-embedded'])

    def test_view_script(self):
        @all_requests
        def response_script(url, request):
            return {
                'status_code': 200,
                'content': '''
                    <div>
                        <script src="https://plone/org/main.js"></script>
                    </div>
                ''',
            }
        with HTTMock(response_script):
            output = self.get_parsed_data()
        script = output.cssselect('.embeddedpage script')[0]
        expected = (
            'http://nohost/plone/epage?embeddedpage_get_resource='
            'https://plone/org/main.js'
        )
        self.assertEqual(expected, script.attrib['src'])

    def test_view_iframe(self):
        @all_requests
        def response_iframe(url, request):
            return {
                'status_code': 200,
                'content': '''
                    <div>
                        <iframe src="main.php"></iframe>
                    </div>
                ''',
            }
        with HTTMock(response_iframe):
            output = self.get_parsed_data()
        iframe = output.cssselect('.embeddedpage iframe')[0]
        expected = 'https://plone.org/main.php'
        self.assertEqual(expected, iframe.attrib['src'])

    def test_view_link(self):
        @all_requests
        def response_link(url, request):
            return {
                'status_code': 200,
                'content': '''
                    <head>
                        <link rel="stylesheet" href="main.css">
                    </head>
                    <body>
                        <div>Content</div>
                    </body>
                ''',
            }
        with HTTMock(response_link):
            output = self.get_parsed_data()
        link = output.cssselect('.embeddedpage link')[0]
        expected = 'main.css'
        self.assertEqual(expected, link.attrib['href'])

    def test_encoding_utf8(self):
        @all_requests
        def response_link(url, request):
            return {
                'status_code': 200,
                'content': u'''
                    <div>
                        Nach Ihrer Anmeldung werden Sie auf die Seite der
                        Projektverwaltung weitergeleitet. Dort haben Sie
                        die Möglichkeit, ein neues Projekt zu registrieren,
                        bestehende Projekte zu bearbeiten und Ihren Projekten
                        sogenannte Projektkontakte hinzuzufügen.

                        Dieser Bereich ist geschützt. Bitte melden Sie sich
                        mit Ihrem HU-Account und Ihrem Passwort an.
                    </div>
                '''.encode('utf-8'),
            }
        with HTTMock(response_link):
            output = self.get_parsed_data()
        self.assertIn(u'Möglichkeit', output.text_content())

    def test_encoding_iso88591(self):
        @all_requests
        def response_link(url, request):
            return {
                'status_code': 200,
                'content': u'''
                    <div>
                        Nach Ihrer Anmeldung werden Sie auf die Seite der
                        Projektverwaltung weitergeleitet. Dort haben Sie
                        die Möglichkeit, ein neues Projekt zu registrieren,
                        bestehende Projekte zu bearbeiten und Ihren Projekten
                        sogenannte Projektkontakte hinzuzufügen.

                        Dieser Bereich ist geschützt. Bitte melden Sie sich
                        mit Ihrem HU-Account und Ihrem Passwort an.
                    </div>
                '''.encode('iso-8859-1'),
            }
        with HTTMock(response_link):
            output = self.get_parsed_data()
        self.assertIn(u'Möglichkeit', output.text_content())

    def test_forward_headers(self):
        @all_requests
        def response_link(url, request):
            return {
                'status_code': 200,
                'headers': request.headers,
                'content': u'''
                    <div>
                        Nach Ihrer Anmeldung werden Sie auf die Seite der
                        Projektverwaltung weitergeleitet. Dort haben Sie
                        die Möglichkeit, ein neues Projekt zu registrieren,
                        bestehende Projekte zu bearbeiten und Ihren Projekten
                        sogenannte Projektkontakte hinzuzufügen.

                        Dieser Bereich ist geschützt. Bitte melden Sie sich
                        mit Ihrem HU-Account und Ihrem Passwort an.
                    </div>
                '''
            }
        with HTTMock(response_link):
            self.request.environ['HTTP_X_FORWARDED_FOR'] = '1.2.3.4'
            self.get_parsed_data()
        self.assertEquals(
            self.request.response.headers['x-forwarded-for'], '1.2.3.4')

    def test_twice_decode(self):
        @all_requests
        def response_link(url, request):
            return {
                'status_code': 200,
                'content': '''<?xml version="1.1" encoding="utf-8"?>
                    <html xmlns="http://www.w3.org/1999/xhtml">
                        <head>
                            <link rel="stylesheet" href="main.css">
                        </head>
                        <body>
                            <div>
                                Nach Ihrer Anmeldung werden Sie auf die Seite
                                der Projektverwaltung weitergeleitet. Dort
                                haben Sie die Möglichkeit, ein neues Projekt
                                zu registrieren, bestehende Projekte zu
                                bearbeiten und Ihren Projekten sogenannte
                                Projektkontakte hinzuzufügen.
                                Dieser Bereich ist geschützt. Bitte melden
                                Sie sich mit Ihrem HU-Account und Ihrem
                                Passwort an.
                            </div>
                        </body>
                    </html>
                '''
            }
        with HTTMock(response_link):
            output = self.get_parsed_data()
        self.assertIn(u'Möglichkeit', output.text_content())
