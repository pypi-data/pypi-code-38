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

# Empty list should cause crash
unmerged.listdeletable.get_protected = lambda: []


class TestUnmergedCrash(base.TestSimple):

    def test_crash(self):
        site = picker.pick_site()
        summary.running(site)

        main.main(site)

        summary.unlock_site(site)

        self.assertFalse(history.unmerged_files(site))


if __name__ == '__main__':
    unittest.main(argv=base.ARGS)
