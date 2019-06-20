# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import override

from . import Dashboards_appTestCase


class TestI18N(Dashboards_appTestCase):

    def test_absolute_url_fallback(self):
        # Create an EN dashboard
        with override('en'):
            dashboard = self.create_dashboard(
                title='God Save the Queen!', slug='god-save-queen')
        # Add a DE translation
        dashboard.create_translation('de',
            title='Einigkeit und Recht und Freiheit!',
            slug='einigkeit-und-recht-und-freiheit')

        # Reload for good measure
        dashboard = self.reload(dashboard)

        self.assertEquals(dashboard.get_absolute_url(language='en'),
            '/en/page/god-save-queen/')
        # Test that we can request the other defined language too
        self.assertEquals(dashboard.get_absolute_url(language='de'),
            '/de/page/einigkeit-und-recht-und-freiheit/')

        # Now, let's request a language that dashboard has not yet been translated
        # to, but has fallbacks defined, we should get EN
        self.assertEquals(dashboard.get_absolute_url(language='fr'),
            '/en/page/god-save-queen/')

        # With settings changed to 'redirect_on_fallback': False, test again.
        with self.settings(CMS_LANGUAGES=self.NO_REDIRECT_CMS_SETTINGS):
            self.assertEquals(dashboard.get_absolute_url(language='fr'),
                '/fr/page/god-save-queen/')

        # Now, let's request a language that has a fallback defined, but it is
        # not available either (should raise NoReverseMatch)
        with self.assertRaises(NoReverseMatch):
            dashboard.get_absolute_url(language='it')
