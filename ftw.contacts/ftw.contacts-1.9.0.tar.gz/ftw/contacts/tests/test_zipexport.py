from ftw.builder import Builder
from ftw.builder import create
from ftw.contacts.testing import FTW_CONTACTS_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from StringIO import StringIO
from unittest2 import TestCase
from zipfile import ZipFile

import os


def asset(filename):
    here = os.path.dirname(__file__)
    path = os.path.join(here, 'assets', filename)
    with open(path, 'r') as file_:
        return file_.read()


class TextVCardExport(TestCase):
    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    @browsing
    def test_zip_export(self, browser):
        contact = create(
            Builder('contact').with_maximal_info(u'Fr\xedtz', u'M\xe9ier'))

        browser.login().visit(contact, view='zip_export')
        self.assertEquals('application/zip', browser.headers['Content-Type'])

        zipfile = ZipFile(StringIO(browser.contents))
        self.assertEquals(['meier-fritz.vcf'], zipfile.namelist())
        self.assertMultiLineEqual(asset('fritz-meier.vcf'),
                                  zipfile.read('meier-fritz.vcf'))
