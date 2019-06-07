"""
Alternate namespace for aiotoolz such that all functions are curried

Currying provides implicit partial evaluation of all functions

Example:

    Get usually requires two arguments, an index and a collection
    >>> from aiotoolz.curried import get
    >>> get(0, ('a', 'b'))
    'a'

    When we use it in higher order functions we often want to pass a partially
    evaluated form
    >>> data = [(1, 2), (11, 22), (111, 222)]
    >>> list(map(lambda seq: get(0, seq), data))
    [1, 11, 111]

    The curried version allows simple expression of partial evaluation
    >>> list(map(get(0), data))
    [1, 11, 111]

See Also:
    aiotoolz.functoolz.curry
"""
import aiotoolz
from . import operator
from aiotoolz import (
    comp,
    complement,
    compose,
    concat,
    concatv,
    count,
    curry,
    diff,
    dissoc,
    first,
    flip,
    frequencies,
    identity,
    interleave,
    isdistinct,
    isiterable,
    juxt,
    last,
    memoize,
    merge_sorted,
    peek,
    pipe,
    second,
    thread_first,
    thread_last,
)
from .exceptions import merge, merge_with

accumulate = aiotoolz.curry(aiotoolz.accumulate)
assoc = aiotoolz.curry(aiotoolz.assoc)
assoc_in = aiotoolz.curry(aiotoolz.assoc_in)
cons = aiotoolz.curry(aiotoolz.cons)
countby = aiotoolz.curry(aiotoolz.countby)
do = aiotoolz.curry(aiotoolz.do)
drop = aiotoolz.curry(aiotoolz.drop)
excepts = aiotoolz.curry(aiotoolz.excepts)
filter = aiotoolz.curry(aiotoolz.filter)
get = aiotoolz.curry(aiotoolz.get)
get_in = aiotoolz.curry(aiotoolz.get_in)
groupby = aiotoolz.curry(aiotoolz.groupby)
interpose = aiotoolz.curry(aiotoolz.interpose)
itemfilter = aiotoolz.curry(aiotoolz.itemfilter)
itemmap = aiotoolz.curry(aiotoolz.itemmap)
iterate = aiotoolz.curry(aiotoolz.iterate)
join = aiotoolz.curry(aiotoolz.join)
keyfilter = aiotoolz.curry(aiotoolz.keyfilter)
keymap = aiotoolz.curry(aiotoolz.keymap)
map = aiotoolz.curry(aiotoolz.map)
mapcat = aiotoolz.curry(aiotoolz.mapcat)
nth = aiotoolz.curry(aiotoolz.nth)
partial = aiotoolz.curry(aiotoolz.partial)
partition = aiotoolz.curry(aiotoolz.partition)
partition_all = aiotoolz.curry(aiotoolz.partition_all)
partitionby = aiotoolz.curry(aiotoolz.partitionby)
pluck = aiotoolz.curry(aiotoolz.pluck)
random_sample = aiotoolz.curry(aiotoolz.random_sample)
reduce = aiotoolz.curry(aiotoolz.reduce)
reduceby = aiotoolz.curry(aiotoolz.reduceby)
remove = aiotoolz.curry(aiotoolz.remove)
sliding_window = aiotoolz.curry(aiotoolz.sliding_window)
sorted = aiotoolz.curry(aiotoolz.sorted)
tail = aiotoolz.curry(aiotoolz.tail)
take = aiotoolz.curry(aiotoolz.take)
take_nth = aiotoolz.curry(aiotoolz.take_nth)
topk = aiotoolz.curry(aiotoolz.topk)
unique = aiotoolz.curry(aiotoolz.unique)
update_in = aiotoolz.curry(aiotoolz.update_in)
valfilter = aiotoolz.curry(aiotoolz.valfilter)
valmap = aiotoolz.curry(aiotoolz.valmap)

del exceptions
del aiotoolz
