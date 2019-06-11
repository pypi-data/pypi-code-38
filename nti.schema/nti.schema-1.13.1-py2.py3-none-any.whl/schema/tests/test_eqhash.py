#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for eqhash.py

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# stdlib imports
import unittest


from ..eqhash import EqHash

from hamcrest import assert_that
from hamcrest import calling
from hamcrest import is_
from hamcrest import is_not
from hamcrest import raises

__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904



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

class TestEqHash(unittest.TestCase):

    def test_eq_hash(self):

        thing1 = Thing()
        thing2 = Thing()

        assert_that(thing1, is_(thing1)) # self
        assert_that(thing1, is_(thing2)) # commutative
        assert_that(thing2, is_(thing1))
        assert_that(hash(thing1), is_(hash(thing2)))

        assert_that(thing1, is_not(self)) # missing attr

        thing2.b = 'B'

        assert_that(thing1, is_not(thing2))
        assert_that(hash(thing1), is_not(hash(thing2)))

        # hamcrest calls == even for is_not
        assert thing1 != thing2
        assert thing1 != self # NotImplemented

    def test_eq_hash_mutates(self):

        thing_nosuperhash = Thing()
        thing_superhash = Thing2() # initially, no superhashing required

        assert_that(hash(thing_nosuperhash), is_(hash(thing_superhash)))

        # Ok, mutate one of the attributes to require superhashing
        thing_superhash.a = [1, 2]
        assert_that(hash(thing_superhash), is_(hash(thing_superhash)))

        thing_superhash2 = Thing2()
        thing_superhash2.a = [1, 2]
        assert_that(hash(thing_superhash2), is_(hash(thing_superhash)))
        # And again, to prove we don't change unnecessarily
        assert_that(hash(thing_superhash2), is_(hash(thing_superhash)))
        # But we can mutate the other attribute and we will change
        # hash strategies
        thing_superhash.b = {}
        thing_superhash2.b = {}
        assert_that(hash(thing_superhash2), is_(hash(thing_superhash)))
        assert_that(hash(thing_superhash2), is_(hash(thing_superhash)))

        # OK, now that we've mutated, mutate again to something that's
        # not a dictionary, but is hashable and isn't iterable.
        class AThing(object):
            pass
        athing = AThing()
        hash(athing)
        thing_superhash.b = athing
        thing_superhash2.b = athing
        assert_that(hash(thing_superhash2), is_(hash(thing_superhash)))
        assert_that(hash(thing_superhash2), is_(hash(thing_superhash)))

        # One more mutation for coverage
        thing_superhash.a = athing
        thing_superhash2.a = athing
        assert_that(hash(thing_superhash2), is_(hash(thing_superhash)))
        assert_that(hash(thing_superhash2), is_(hash(thing_superhash)))


    def test_eq_hash_classes(self):
        # Default doesn't include classes

        assert_that(Thing(), is_(Thing2()))
        assert_that(hash(Thing()), is_(hash(Thing2())))

        # We can ask for it, but note that the order of arguments
        # matters
        assert_that(Thing(), is_(NotThing()))
        assert_that(NotThing(), is_not(Thing()))

    def test_eq_hash_super(self):
        thing1 = ChildThing()
        thing2 = ChildThing()

        assert_that(thing1, is_(thing2))

        assert_that(hash(thing1), is_(hash(thing2)))

        thing1.a = 'A'
        assert_that(thing1, is_not(thing2))
        assert_that(hash(thing1), is_not(hash(thing2)))

        thing3 = ChildThingNoNames()
        thing4 = ChildThingNoNames()
        assert_that(thing3, is_(thing4))
        assert_that(hash(thing3), is_(hash(thing4)))

    def test_eq_hash_no_super(self):
        thing1 = ChildThingNoSuper()
        thing2 = ChildThingNoSuper()

        assert_that(thing1, is_(thing2))
        assert_that(hash(thing1), is_(hash(thing2)))

        thing1.a = 'A'
        assert_that(thing1, is_(thing2))
        assert_that(hash(thing1), is_(hash(thing2)))

        thing1.c = 'C'
        assert_that(thing1, is_not(thing2))
        assert_that(hash(thing1), is_not(hash(thing2)))

    def test_bad_construct(self):
        assert_that(calling(EqHash), raises(TypeError, "Asking to hash"))
        assert_that(calling(EqHash).with_args(foo=True),
                    raises(TypeError, "Unexpected keyword"))


class TestSuperHash(unittest.TestCase):

    def superhash(self, arg):
        # Use the old location to make sure it works
        from nti.schema import schema
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            return schema._superhash(arg) # pylint:disable=no-member

    def test_iterable(self):
        assert_that(hash(self.superhash([1, 3, 5])),
                    is_(hash(self.superhash([x for x in [1, 3, 5]]))))

        assert_that(self.superhash([1, 2]), is_not(self.superhash([2, 1])))
        assert_that(hash(self.superhash([1, 2])), is_not(hash(self.superhash([2, 1]))))

    def test_nested_dict(self):
        d = {1: 1,
             2: [1, 2, 3],
             3: {4: [4, 5, 6]}}

        assert_that(self.superhash(d),
                    is_(
                        ((1, 1),
                         (2, (1, 2, 3)),
                         (3, ((4, (4, 5, 6)),)))
                    ))

        assert_that(hash(self.superhash(d)),
                    is_(-6213620179105025536))


def test_suite():
    import doctest
    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    suite.addTest(
        doctest.DocTestSuite('nti.schema.eqhash')
    )

    return suite
