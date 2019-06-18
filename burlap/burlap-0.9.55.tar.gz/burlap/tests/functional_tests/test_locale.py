from __future__ import print_function

from burlap.locale import LocalesSatchel
from burlap.tests.functional_tests.base import TestCase

class LocaleTests(TestCase):

    def test_locale(self):
        ts = LocalesSatchel()
        ts.verbose = True

        locale0 = ts.cat_locale()
        print('locale0:', locale0)
        locale_dict0 = ts.get_locale_dict()
        language0 = locale_dict0.get('LANGUAGE')
        print('language0:', language0)
        lang0 = locale_dict0.get('LANG')
        print('lang0:', lang0)
        lc_all0 = locale_dict0.get('LC_ALL')
        print('lc_all0:', lc_all0)

        try:
            print('Setting custom locale...')
            ts.env.language = 'en_US.UTF-8'
            ts.env.lang = 'en_US.UTF-8'
            ts.env.lc_all = 'en_US.UTF-8'
            ts.configure()

            locale1 = ts.cat_locale()
            print('locale1:', locale1)
            locale_dict1 = ts.get_locale_dict()
            language1 = locale_dict1.get('LANGUAGE')
            print('language1:', language1)
            lang1 = locale_dict1.get('LANG')
            print('lang1:', lang1)
            lc_all1 = locale_dict1.get('LC_ALL')
            print('lc_all1:', lc_all1)
            assert language1 == ts.env.language
            assert lang1 == ts.env.lang
            assert lc_all1 == ts.env.lc_all

        finally:
            print('Resetting to default locale...')
            ts.env.language = language0
            ts.env.lang = lang0
            ts.env.lc_all = lc_all0
            ts.configure()
