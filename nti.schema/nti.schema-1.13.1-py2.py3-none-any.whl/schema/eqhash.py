#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helpers for hashing and equality based on a list of names.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import operator

import six

__docformat__ = "restructuredtext en"

def _superhash_force(value):
    # Called when we know that we can't hash the value.
    # Dict?
    try:
        # Sort these, they have no order
        items = sorted(value.items())
    except AttributeError:
        # mutable iterable, which we must not sort
        items = value

    return tuple([_superhash(item)
                  for item
                  in items])

def _superhash(value):
    """
    Returns something that's hashable, either the value itself,
    or a tuple that can in turn be hashed
    """
    try:
        # We used to think that by returning the original value, if it was hashable,
        # we may get better ultimate hash results;
        # the cost is hashing that value twice.
        # However, Python guarantees that the hash of an integer
        # *is* the integer (with a few exceptions), so we should be
        # just fine returning the hash value....except, Python 3 changes this
        # and the hash is less often the same. So we go back to hashing things twice.
        hash(value)
    except TypeError:
        return _superhash_force(value)
    else:
        return value

def EqHash(*names,
           **kwargs):
    """
    EqHash(*names, include_super=False, superhash=False, include_type=False)

    A class decorator factory for the common pattern of writing
    ``__eq__``/``__ne__`` and ``__hash__`` methods that check the same
    list of attributes on a given object.

    Right now, you must pass as individual arguments the property
    names to check; in the future, you may be able to pass a schema
    interface that defines the property names. Property names are compared
    for equality in the order they are given, so place the cheapest first.

    Additional parameters are only available via keywords::

      >>> @EqHash('a', 'b')
      ... class Thing(object):
      ...   a = 1
      ...   b = 2
      >>> hash(Thing()) == (hash(('a', 'b')) ^ hash((1, 2)))
      True

      >>> @EqHash('c', include_super=True)
      ... class ChildThing(Thing):
      ...   c = 3
      >>> hash(ChildThing()) != hash(Thing()) != 0
      True

    :keyword include_super: If set to ``True`` (*not* the default)
        then the equality (and perhaps hash) values of super will be considered.
    :keyword superhash: If set to ``True`` (*not* the default),
        then the hash function will be made to support certain
        mutable types (lists and dictionaries) that ordinarily cannot
        be hashed. Use this only when those items are functionally
        treated as immutable.
    :keyword include_type: If set to ``True`` (*not* the default),
        equality will only be true if the other object is an instance
        of the class this is declared on. Use this only when there are
        a series of subclasses who differ in no attributes but should not
        compare equal to each other. Note that this can lead to violating
        the commutative property.

    """

    _include_super = kwargs.pop('include_super', False)
    superhash = kwargs.pop("superhash", False)
    _include_type = kwargs.pop('include_type', False)

    if kwargs:
        raise TypeError("Unexpected keyword args", kwargs)
    if not names and not _include_super and not _include_type:
        raise TypeError("Asking to hash/eq nothing, but not including super or type")


    def x(cls):
        __eq__, __hash__, __ne__ = _eq_hash(cls, names,
                                            _include_super, _include_type, superhash)
        cls.__eq__ = __eq__
        cls.__hash__ = __hash__
        cls.__ne__ = __ne__
        return cls
    return x

def _make_eq(cls, names, include_super, include_type):
    # 1 and 0 are constants and faster to load than the globals True/False
    # (in python 2)

    eq_stmt = 'def __eq__(self, other'
    if include_type or include_super:
        # capture the type
        eq_stmt += ', cls=cls'
    eq_stmt += '):\n'
    eq_stmt += '    if self is other: return 1\n'
    if include_type:
        eq_stmt += '    if not isinstance(other, cls): return 0\n'
    if include_super:
        eq_stmt += '    s = super(cls, self).__eq__(other)\n'
        eq_stmt += '    if s is NotImplemented or not s: return s\n'

    # We take these one at a time (rather than using
    # operator.attrgetter). In the cases where some attributes
    # are computed, this can be more efficient if we discover
    # a mismatch early. Also, it lets us easily distinguish
    # between an AttributeError on self (which is a
    # programming error in calling EqHash) or the other object
    for name in names:
        eq_stmt += '    a = self.' + name + '\n'
        eq_stmt += '    try:\n        b = other.' + name + '\n'
        eq_stmt += '    except AttributeError: return NotImplemented\n'
        eq_stmt += '    if a != b: return 0\n\n'

    eq_stmt += '    return 1'

    # Must use a custom dictionary under Py3
    lcls = dict(locals())
    six.exec_(eq_stmt, globals(), lcls)

    return lcls['__eq__']

def _eq_hash(cls, names, include_super, include_type, superhash): # pylint:disable=I0011,W0622,R0912
    names = tuple((str(x) for x in names)) # make sure they're native strings, not unicode on Py2
    # We assume the class hierarchy of these objects does not change
    if include_super:
        superclass = cls.__mro__[1]
        superclass_hash = superclass.__hash__

    __eq__ = _make_eq(cls, names, include_super, include_type)

    def __ne__(self, other):
        eq = __eq__(self, other)
        if eq is NotImplemented:
            return eq
        return not eq

    # Our contract for include_super says that hashing
    # may or may not be included. It shouldn't affect the results
    # if we do not actually include it, unless there are no values
    # being hashed from this object. However, for consistency,
    # we always include it if asked
    seed = hash(names)
    if include_type:
        seed += hash(cls)

    if superhash:
        # We assume that instances that use superhash will have
        # roughly the same shape, and not all attributes will need to be
        # super-hashed. When an attribute does need to be super-hashed, it will
        # need to be super-hashed for all instances. Worst case scenario, this winds up
        # always using the superhash for all attributes of all instances, but if we're lucky
        # only a small number of the same attributes will need to be superhashed.

        class Transformers(list):
            mutated = False

        transformers = Transformers([None for _ in names])

        def _hash(values):
            # Hopefully in most cases everything is actually hashable.
            # This gets our overhead down to the lowest possible.
            if not transformers.mutated:
                try:
                    return hash(values)
                except TypeError:
                    pass

            # Ok, we found something that can't actually be hashed. Darn.
            # Replace every non-Hashable transformer with a call to superhash.
            transformers.mutated = True
            # Snap. Lets hope that we already checked on what needs to be superhashed
            # and if so we'll try that.
            try:
                return hash(tuple([transformer(value) if transformer is not None else value
                                   for transformer, value
                                   in zip(transformers, values)]))
            except TypeError:
                # Snap. Something changed.
                for i, value in enumerate(values):
                    if transformers[i] is _superhash:
                        # We've reached our limit. Nothing else to do
                        # for this one.
                        continue

                    if transformers[i] is _superhash_force:
                        try:
                            _superhash_force(value)
                        except TypeError:
                            # OK, this field alternates between
                            # being hashable and nat being hashable. Deal with that.
                            transformers[i] = _superhash

                    try:
                        # We could check isinstance(value, collections.Hashable), but
                        # this is slightly more general, albeit probably slower.
                        hash(value)
                    except TypeError:
                        transformers[i] = _superhash_force

            # Ok, good to go. Let's try it.
            return hash(tuple([transformer(value) if transformer is not None else value
                               for transformer, value
                               in zip(transformers, values)]))
    else:
        # No need to try to wrap in a tuple or anything, we can
        # just directly call the hash builtin. We'll get passed either
        # a tuple of values.
        _hash = hash

    # Unlike __eq__, we use operator.attrgetter because we're always
    # going to request all the names. In tests, this is ~30% faster than
    # a manual loop (for two to three names).
    if not names:
        # Well, ok, nothing special in this class. We can't pass that to attrgetter,
        # though, it needs at least one name. Make sure to return a tuple for
        # consistency.
        def attrgetter(_):
            return ()
    else:
        # This will return a tuple of the values of the names.
        attrgetter = operator.attrgetter(*names)

    def __hash__(self):
        h = seed
        if include_super:
            h ^= superclass_hash(self) << 2

        # If we or-equal for every attribute separately, we
        # easily run the risk of saturating the integer. So we callect
        # all attributes down to one tuple to hash
        h ^= _hash(attrgetter(self))
        return h

    return __eq__, __hash__, __ne__
