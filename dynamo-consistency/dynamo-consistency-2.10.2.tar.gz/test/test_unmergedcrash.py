#! /usr/bin/env python

import unittest

from dynamo_consistency import opts


opts.UNMERGED = True


from dynamo_consistency import history
from dynamo_consistency import main
from dynamo_consistency import picker
from dynamo_consistency import summary
from dynamo_consistency.backend import test
from dynamo_consistency.cms import unmerged

import base

test._FILES.extend([
    ('/store/unmerged/logs/000/logfile.tar.gz', 20),
    ('/store/unmerged/notprot/000/qwert.root', 20)
])


class TestUnmergedCrash(base.TestSimple):

    def do_more_setup(self):
        print 'here'
        # Empty list should cause crash
        unmerged.listdeletable.get_protected = lambda: []

    def test_crash(self):
        site = picker.pick_site()
        summary.running(site)

        main.main(site)

        summary.unlock_site(site)

        self.assertFalse(history.unmerged_files(site))

        # Test for completed run report
        conn = summary.LockedConn()
        results = conn.execute('SELECT * FROM stats;')
        self.assertTrue(list(results))


def exception_maker():
    raise unmerged.listdeletable.SuspiciousConditions()


class TestException(TestUnmergedCrash):
    def do_more_setup(self):
        # Exception should also be handled
        unmerged.listdeletable.get_protected = lambda: exception_maker()


if __name__ == '__main__':
    unittest.main(argv=base.ARGS)
