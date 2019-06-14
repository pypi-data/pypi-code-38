#! /usr/bin/env python

# This is to allow operators to disable a site and separately
# kill the process without un-disabling the site

import unittest

from dynamo_consistency import signaling
from dynamo_consistency import summary
from dynamo_consistency import main
from dynamo_consistency import picker

import base

class TestSignaling(base.TestSimple):
    def test_signaling(self):
        site = picker.pick_site()
        main.main(site)
        summary.unlock_site(site)

        self.assertEqual(summary.get_status(site), summary.READY)

        signaling.halt(2, 'dummy')

        self.assertEqual(summary.get_status(site), summary.HALT)

        summary.set_status(site, summary.DISABLED)
        signaling.halt(2, 'dummy')

        self.assertEqual(summary.get_status(site), summary.DISABLED)

if __name__ == '__main__':
    unittest.main(argv=base.ARGS)
