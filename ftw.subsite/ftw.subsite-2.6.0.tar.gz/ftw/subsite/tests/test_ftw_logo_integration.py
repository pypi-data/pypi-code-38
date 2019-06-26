from ftw.builder import Builder
from ftw.builder import create
from ftw.subsite.testing import FTW_SUBSITE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from unittest2 import TestCase
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(CURRENT_DIR, 'assets/4dreamwork.svg')


class TestFtwLogoIntegration(TestCase):

    layer = FTW_SUBSITE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    @browsing
    def test_logo_edit_view_exists_on_site_root(self, browser):
        browser.login()
        # ftw-logo-overrides/edit
        browser.open(self.portal, view='logo-and-icon-overrides')
        # I assert the title because I assume that if the title
        # is loaded we successfully loaded the page
        self.assertEqual('Manually set site Logos and Icons',
                         browser.css('h1').first.text,
                         'The pages title should be different')

    @browsing
    def test_logo_on_site_root_comming_from_ftw_logo_source(self, browser):
        browser.login()
        page = create(Builder('sl content page').titled(u'Hugo'))
        browser.open(page)
        logo_link = browser.css('#portal-logo img').first.node.attrib.get('src')
        logo_link_without_query = logo_link.split('?')[0]
        self.assertEqual('http://nohost/plone/@@logo/logo/get_logo',
                         logo_link_without_query,
                         'The logo should be implemented from ftw.logo')

    @browsing
    def test_logo_can_be_changed_for_plone_root(self, browser):
        browser.login()
        upload_context = self.portal
        logos = self.upload_image_and_return_actual_and_expected_image(
            browser, upload_context)

        self.assertEqual(logos['expected'],
                         logos['actual'],
                         'We expect that the logo on the page is the same as '
                         'the one we\'ve uploaded with ftw.logo')

    @browsing
    def test_logo_can_be_changed_for_subsite(self, browser):
        page = create(Builder('sl content page').titled(u'Wrapper Page'))
        subsite = create(Builder('subsite').titled(u'Subsite').within(page))

        browser.login()
        upload_context = subsite
        logos = self.upload_image_and_return_actual_and_expected_image(
            browser, upload_context)

        self.assertEqual(logos['expected'],
                         logos['actual'],
                         'We expect that the logo on the page is the same as '
                         'the one we\'ve uploaded with ftw.logo')

    @browsing
    def test_subsite_logo_change_does_not_affect_other_sl_page(self, browser):
        page_one = create(Builder('sl content page').titled(u'Wrapper Page 1'))
        subsite = create(Builder('subsite').titled(u'Subsite').within(page_one))
        page_two = create(Builder('sl content page').titled(u'Wrapper Page 2'))

        browser.login()

        logos_changed = self.upload_image_and_return_actual_and_expected_image(
            browser, subsite)
        self.assertEqual(logos_changed['expected'],
                         logos_changed['actual'],
                         'We expect that the logo on the first page is the '
                         'same as the one we\'ve uploaded with ftw.logo')

        logos_unchanged = self.return_actual_and_expected_image_but_do_not_upload(
            browser, page_two)
        self.assertNotEqual(logos_unchanged['expected'],
                            logos_unchanged['actual'],
                            'We expect that the second pages logo is not the '
                            'the one we\'ve uploaded on page one.')

    @browsing
    def test_subsite_logo_change_does_not_affect_other_subsite(self, browser):
        page_one = create(Builder('sl content page').titled(u'Wrapper Page 1'))
        subsite = create(Builder('subsite').titled(u'Subsite').within(page_one))
        page_two = create(Builder('sl content page').titled(u'Wrapper Page 2'))
        subsite_two = create(Builder(
            'subsite').titled(u'Subsite').within(page_two))

        browser.login()

        logos_changed = self.upload_image_and_return_actual_and_expected_image(
            browser, subsite)
        self.assertEqual(logos_changed['expected'],
                         logos_changed['actual'],
                         'We expect that the logo on the first subsite is the '
                         'same as the one we\'ve uploaded with ftw.logo')

        logos_unchanged = self.return_actual_and_expected_image_but_do_not_upload(
            browser, subsite_two)
        self.assertNotEqual(logos_unchanged['expected'],
                            logos_unchanged['actual'],
                            'We expect that the second subsites logo is not '
                            'the same as the one we\'ve uploaded on first.')

    @browsing
    def test_subsite_logo_change_changes_sl_pages_logo_in_subsite(self, browser):
        wrapper_page = create(Builder('sl content page').titled(u'Wrapper Page 2'))
        subsite = create(Builder(
            'subsite').titled(u'Subsite').within(wrapper_page))
        page = create(Builder('sl content page').titled(
            u'Test Page').within(subsite))

        browser.login()

        # upload new base logo
        browser.open(subsite, view='logo-and-icon-overrides')
        with open(IMAGE_PATH) as file_:
            expected_logo = file_.read()
            browser.fill({'form.widgets.logo_BASE': file_}).submit()

        # open actual image to compare with the expected
        browser.open(page)
        logo_link = browser.css(
            '#portal-logo img').first.node.attrib.get('src')
        logo_link_without_query = logo_link.split('?')[0]
        browser.open(logo_link_without_query)
        actual_logo = browser.contents

        self.assertEqual(expected_logo,
                         actual_logo,
                         'We expect, that the logo of a page within a subsite '
                         'of which we changed the logo has the subsites logo.')

    @staticmethod
    def upload_image_and_return_actual_and_expected_image(
            browser, upload_context):

        # upload new base logo
        browser.open(upload_context, view='logo-and-icon-overrides')
        with open(IMAGE_PATH) as file_:
            expected_logo = file_.read()
            browser.fill({'form.widgets.logo_BASE': file_}).submit()

        # open actual image to compare with the expected
        browser.open(upload_context)
        logo_link = browser.css(
            '#portal-logo img').first.node.attrib.get('src')
        logo_link_without_query = logo_link.split('?')[0]
        browser.open(logo_link_without_query)
        actual_logo = browser.contents

        return {'expected': expected_logo, 'actual': actual_logo}

    @staticmethod
    def return_actual_and_expected_image_but_do_not_upload(
            browser, context):

        with open(IMAGE_PATH) as file_:
            expected_logo = file_.read()

        # open actual image to compare with the expected
        browser.open(context)
        logo_link = browser.css(
            '#portal-logo img').first.node.attrib.get('src')
        logo_link_without_query = logo_link.split('?')[0]
        browser.open(logo_link_without_query)
        actual_logo = browser.contents

        return {'expected': expected_logo, 'actual': actual_logo}
