from ftw.builder import Builder
from ftw.builder import create
from ftw.contacts.browser.vcard import DownloadVCardView
from ftw.contacts.testing import FTW_CONTACTS_FUNCTIONAL_TESTING
from ftw.contacts.utils import generate_vcard
from unittest2 import TestCase

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

    def test_detailed_contact_works(self):
        contact = create(Builder('contact').with_maximal_info(
            firstname=u'Fr\xedtz',
            lastname=u'M\xe9ier'
            ))

        self.assertMultiLineEqual(
            asset('fritz-meier.vcf'), generate_vcard(contact).getvalue())

    def test_minimal_contact_works(self):
        contact = create(Builder('contact').with_minimal_info(
            firstname='Minho',
            lastname='Blau'))

        self.assertMultiLineEqual(
            asset('blau-minho.vcf'), generate_vcard(contact).getvalue())

    def test_call_vcard_download_view(self):
        contact = create(Builder('contact').with_minimal_info(
            firstname='Minho',
            lastname='Blau'))

        vcard_view = DownloadVCardView(contact, self.request)

        self.assertMultiLineEqual(asset('blau-minho.vcf'), vcard_view())
