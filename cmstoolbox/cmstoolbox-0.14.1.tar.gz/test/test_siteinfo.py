#!/usr/bin/env python

import unittest

import cmstoolbox.siteinfo as si

class TestSiteInfo(unittest.TestCase):

    def test_disk_tape_name(self):
        self.assertTrue(si.get_domain('T1_US_FNAL'))
        self.assertEqual(si.get_domain('T1_US_FNAL'),
                         si.get_domain('T1_US_FNAL_Disk'))

    def test_different_sites(self):
        self.assertTrue(si.get_domain('T2_US_MIT'))
        self.assertNotEqual(si.get_domain('T1_US_FNAL'),
                            si.get_domain('T2_US_MIT'))

    def test_no_site(self):
        self.assertFalse(si.get_domain('not_a_site'))

if __name__ == '__main__':
    unittest.main()
