# -*- coding: utf-8 -*-
from congo.maintenance.jobs import BaseJob
from decimal import Decimal

class Job(BaseJob):
    description = "Just exemplary job"

    def __init__(self):
        super(Job, self).__init__()

    def _run(self, user, *args, **kwargs):
        result = {
            'unicode_val': u"Zażółć gęślą jaźń",
            'str_val': "Typical string value",
            'int_val': 123,
            'float_val': .456,
            'decimal_val': Decimal("7.89"),
            'bool_val': True,
            'list_val': ['a', 1, False],
            'dict_val': {'key1': 'val1', 'key2': 2, 'key3': 3.0, 'key4': False},
        }

        print ""
        print "############################"
        print "#                          #"
        print "#     system.cron.test     #"
        print "#                          #"
        print "############################"
        print ""

        print 1 / 0

        return result
