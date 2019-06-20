# -*- coding: utf-8 -*-
from congo.maintenance.tests import BaseTest
import random

class Test(BaseTest):
    def __init__(self):
        super(Test, self).__init__()
        self.description = "Just exemplary test"

    def _run(self, *args, **kwargs):
        result = {
            'result': bool(random.randint(0, 1)),
            'details': u'Lorem ipsum dolor sit amet, consecteteur adipiscing elit.'
        }

        print ""
        print "#############################"
        print "#                           #"
        print "#     system.audit.test     #"
        print "#                           #"
        print "#############################"
        print ""

#        print 1 / 0

        return result
