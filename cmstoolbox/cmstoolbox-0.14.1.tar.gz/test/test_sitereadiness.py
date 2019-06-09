#!/usr/bin/env python

import unittest

import cmstoolbox.sitereadiness as sr


class TestSiteReadiness(unittest.TestCase):

    def test_site_readiness(self):
        for site, stat, drain in sr.i_site_readiness():
            self.assertNotEqual(sr.site_readiness(site), 'none',
                                'Site not found: %s' % site)
            self.assertEqual(sr.site_readiness(site), stat,
                             'Inconsistent result: %s' % site)
            self.assertEqual(stat in ['green', 'yellow', 'red'], True,
                             'Status is not valid: %s' % site)
            self.assertEqual(drain in ['enabled', 'disabled', 'drain', 'test'], True,
                             'Drain status is not valid: %s' % site)

    def test_bad_site(self):
        self.assertEqual(sr.site_readiness('not_a_site'), 'none',
                         'Bad return on fake site')
        self.assertEqual(sr.site_drain_status('not_a_site'), 'none',
                         'Bad return on fake site')


if __name__ == '__main__':
    unittest.main()
