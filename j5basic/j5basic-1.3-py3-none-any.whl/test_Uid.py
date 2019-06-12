#!/usr/bin/env python

from j5basic import Uid
import re
import time
from functools import reduce

def birthday_problem(g, n):
     """returns the probability that n independent choices from a set of g objects are all unique"""
     return reduce(operator.mul, [float(g-i)/g for i in range(0, n)])

class TestUid(object):
    def test_uid_digit_str(self):
        ids = {}
        for i in range(10000):
            ids[Uid.uid_digit_str()] = None
        print(len(ids))
        assert len(ids) == 10000 # no duplicates

        # check format
        uid_re = re.compile("[0-9]{17,22}")
        for uid in ids:
            if not uid_re.match(uid):
                print(uid)
                assert uid_re.match(uid)

    def test_uid_digit_str_with_time(self):
        # at exactly the same time, we should be able to generate 100 different uids
        # our minimum random digit string is 6 digits - the chance of a collision in that case is
        # 1 in 200, so this could still fail occasionally
        # see the birthday problem calculation above to estimate this
        ids = {}
        timestamp = time.time()
        for i in range(100):
            ids[Uid.uid_digit_str(timestamp)] = None
        print(len(ids))
        assert len(ids) == 100 # no duplicates

        # check format
        uid_re = re.compile("[0-9]{17,22}")
        # the start sequence should be consistent
        initial_letters = None
        for uid in ids:
            if initial_letters is None:
                initial_letters = uid[:12]
            if not uid_re.match(uid):
                print(uid)
                assert uid_re.match(uid)
            assert uid.startswith(initial_letters)

    def test_uid_id_str(self):
        ids = {}
        for i in range(10000):
            ids[Uid.uid_id_str()] = None

        print(len(ids))
        assert len(ids) == 10000 # no duplicates

        # check format
        uid_re = re.compile("ID[0-9]{17,22}")
        for uid in ids:
            if not uid_re.match(uid):
                print(uid)
                assert uid_re.match(uid)

