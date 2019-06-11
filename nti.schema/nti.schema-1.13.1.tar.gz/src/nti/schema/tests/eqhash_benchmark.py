#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Benchmark for eqhash.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ..eqhash import EqHash

@EqHash('a', 'b')
class Thing(object):
    a = 'a'
    b = 'b'

@EqHash('a', 'b', superhash=True)
class Thing2(object):
    a = 'a'
    b = 'b'

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

@EqHash('a', 'b', include_type=True)
class NotThing(object):
    a = 'a'
    b = 'b'

@EqHash('c', include_super=True)
class ChildThing(Thing):
    c = 'c'

@EqHash('c', include_super=False)
class ChildThingNoSuper(Thing):
    c = 'c'

@EqHash(include_super=True)
class ChildThingNoNames(Thing):
    pass

@EqHash('a', 'b', 'c', 'd', 'e', 'f')
class ManyThing(object):
    a = 'a'
    b = 'b'
    c = 'c'
    d = 'd'
    e = 'e'
    f = 'f'

# pylint:disable=line-too-long

def bench_hash(): # pragma: no cover
    import timeit
    import statistics


    timer = timeit.Timer('hash(thing)',
                         'from nti.schema.tests.eqhash_benchmark import Thing as Thing; thing=Thing()')
    times = timer.repeat()
    print("Avg Base  hash", statistics.mean(times), "stddev", statistics.stdev(times))

    timer = timeit.Timer('hash(thing)',
                         'from nti.schema.tests.eqhash_benchmark import ChildThing as Thing; thing=Thing()')
    times = timer.repeat()
    print("Avg Child hash", statistics.mean(times), "stddev", statistics.stdev(times))

    timer = timeit.Timer('hash(thing)', 'from nti.schema.tests.eqhash_benchmark import Thing2 as Thing; thing=Thing()')
    times = timer.repeat()
    print("Avg Super  hash", statistics.mean(times), "stddev", statistics.stdev(times))

    timer = timeit.Timer('hash(thing)', 'from nti.schema.tests.eqhash_benchmark import Thing2 as Thing; thing=Thing(a={})')
#    import cProfile
#    import pstats
#    pr = cProfile.Profile()
#    pr.enable()
    times = timer.repeat()
#    pr.disable()
#    ps = pstats.Stats(pr).sort_stats('cumulative')
#    ps.print_stats(.4)

    print("Avg Super2  hash", statistics.mean(times), "stddev", statistics.stdev(times))


def bench_eq(): # pragma: no cover
    import timeit
    import statistics


    timer = timeit.Timer('thing == thing2', 'from nti.schema.tests.eqhash_benchmark import Thing as Thing; thing=Thing(); thing2 = Thing()')
    times = timer.repeat()
    print("Avg Base  eq", statistics.mean(times), "stddev", statistics.stdev(times))

    timer = timeit.Timer('thing == thing2', 'from nti.schema.tests.eqhash_benchmark import ChildThing as Thing; thing=Thing(); thing2 = Thing()')
    times = timer.repeat()
    print("Avg Child eq", statistics.mean(times), "stddev", statistics.stdev(times))

    timer = timeit.Timer('thing == thing2', 'from nti.schema.tests.eqhash_benchmark import Thing2 as Thing; thing=Thing(); thing2 = Thing()')
    times = timer.repeat()
    print("Avg Super  eq", statistics.mean(times), "stddev", statistics.stdev(times))

    timer = timeit.Timer('thing == thing', 'from nti.schema.tests.eqhash_benchmark import Thing2 as Thing; thing=Thing(a={}); thing2 = Thing(a={})')
#    import cProfile
#    import pstats
#    pr = cProfile.Profile()
#    pr.enable()
    times = timer.repeat()
#    pr.disable()
#    ps = pstats.Stats(pr).sort_stats('cumulative')
#    ps.print_stats(.4)




    print("Avg Super2  eq", statistics.mean(times), "stddev", statistics.stdev(times))

    timer = timeit.Timer('thing == thing2', 'from nti.schema.tests.eqhash_benchmark import ManyThing as Thing; thing=Thing(); thing2 = Thing()')
    times = timer.repeat()
    print("Avg many  eq", statistics.mean(times), "stddev", statistics.stdev(times))


# Before
#
# Avg Base  eq 0.790581703186 stddev 0.00709198228224
# Avg Child eq 1.44241364797 stddev 0.00058100921717
# Avg Super  eq 0.772551695506 stddev 0.0120497874892
# Avg Super2  eq 0.230642795563 stddev 0.00981929676758

# Best attrgetter, params as keywords:
# Avg Base  eq 0.57781457901 stddev 0.00472933000447
# Avg Child eq 1.13719065984 stddev 0.00751860996924
# Avg Super  eq 0.576888004939 stddev 0.0073053209526
# Avg Super2  eq 0.221588929494 stddev 0.00154292380992

# Code generation
# Avg Base  eq 0.436311562856 stddev 0.0159609115497
# Avg Child eq 0.93773595492 stddev 0.0244992238919
# Avg Super  eq 0.443862199783 stddev 0.00816548353324
# Avg Super2  eq 0.216485659281 stddev 0.00651497010124

## Many attributes
# Before
# Avg Base  eq 0.762074232101 stddev 0.00893669830878
# Avg Child eq 1.46989099185 stddev 0.0260021505811
# Avg Super  eq 0.776515642802 stddev 0.011819047442
# Avg Super2  eq 0.2257057031 stddev 0.0025750486944
# Avg many  eq 1.56614136696 stddev 0.0195022584734

# Code generation
# Avg Base  eq 0.410983006159 stddev 0.00708241719015
# Avg Child eq 0.903119166692 stddev 0.0051626944104
# Avg Super  eq 0.41703470548 stddev 0.00604558003878
# Avg Super2  eq 0.208957354228 stddev 0.00508863378261
# Avg many  eq 0.797417243322 stddev 0.0198358058579

if __name__ == '__main__':
    import sys
    if '--timehash' in sys.argv:
        bench_hash()
    elif '--timeeq' in sys.argv:
        bench_eq()
