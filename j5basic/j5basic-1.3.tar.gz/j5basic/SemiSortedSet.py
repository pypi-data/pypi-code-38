#!/usr/bin/env python

import operator
import threading
from j5basic import Decorators

_base_min = min
_base_max = max

class SemiSortedSet(set):
    """A set that remembers its minimum and maximum, and can do inplace slicing at a certain point in a reasonably optimal way"""
    def __new__(cls, iterable=None):
        self = set.__new__(cls)
        self.lock = threading.RLock()
        if iterable is not None:
            set.__init__(self, iterable)
        else:
            set.__init__(self)
        self._recalculate()
        return self

    @Decorators.SelfLocking.runwithlock
    def copy(self):
        """makes a copy of this SemiSortedSet (with a new lock)"""
        new_self = SemiSortedSet(set.copy(self))
        new_self.lock = threading.RLock()
        if hasattr(self, "__min__"):
            new_self.__min__ = self.__min__
        if hasattr(self, "__max__"):
            new_self.__max__ = self.__max__
        return new_self

    @Decorators.SelfLocking.runwithlock
    def min(self):
        """Returns the minimum element in the set"""
        if not self:
            raise ValueError("No elements in set")
        return self.__min__

    @Decorators.SelfLocking.runwithlock
    def max(self):
        """Returns the maximum element in the set"""
        if not self:
            raise ValueError("No elements in set")
        return self.__max__

    @Decorators.SelfLocking.runwithlock
    def remove_cmp_op(self, cmp_op, comparator):
        """Removes all items in the set that satisfy cmp_op(item, comparator)"""
        items_satisfy = set(item for item in self if cmp_op(item, comparator))
        self.difference_update(items_satisfy)

    @Decorators.SelfLocking.runwithlock
    def remove_lt(self, minimum):
        """Removes all items in the set that are less than the given minimum"""
        self.remove_cmp_op(operator.lt, minimum)

    @Decorators.SelfLocking.runwithlock
    def remove_le(self, minimum):
        """Removes all items in the set that are less than or equal to the given minimum"""
        self.remove_cmp_op(operator.le, minimum)

    @Decorators.SelfLocking.runwithlock
    def remove_gt(self, maximum):
        """Removes all items in the set that are greater than the given maximum"""
        self.remove_cmp_op(operator.gt, maximum)

    @Decorators.SelfLocking.runwithlock
    def remove_ge(self, maximum):
        """Removes all items in the set that are greater than or equal to the given maximum"""
        self.remove_cmp_op(operator.ge, maximum)

    def _recalculate(self):
        """internal method for recalculating the cached minimum and maximum. not to be called without holding self.lock"""
        if self:
            self.__min__ = min(self)
            self.__max__ = max(self)
        else:
            if hasattr(self, "__min__"):
                delattr(self, "__min__")
            if hasattr(self, "__max__"):
                delattr(self, "__max__")

    def _recalculate_after_add(self, element):
        """internal method for recalculating the cached minimum and maximum after element is added. not to be called without holding self.lock"""
        if not hasattr(self, "__min__") or element < self.__min__:
            self.__min__ = element
        if not hasattr(self, "__max__") or element > self.__max__:
            self.__max__ = element

    def _recalculate_after_remove(self):
        """internal method for recalculating the cached minimum and maximum after an item is removed. not to be called without holding self.lock"""
        if self:
            if self.__min__ not in self:
                self.__min__ = min(self)
            if self.__max__ not in self:
                self.__max__ = max(self)
        else:
            if hasattr(self, "__min__"):
                delattr(self, "__min__")
            if hasattr(self, "__max__"):
                delattr(self, "__max__")

    @Decorators.SelfLocking.runwithlock
    def add(self, element):
        """Add an element to a set. This has no effect if the element is already present."""
        set.add(self, element)
        self._recalculate_after_add(element)

def lock_wrapper(f, target_function):
    def wrapper(self,*args,**kws):
        try:
            self.lock.acquire()
            result = f(self,*args,**kws)
            target_function(self)
        finally:
            self.lock.release()
        return result
    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = getattr(f, 'func_name', getattr(f, '__name__', 'locked_function'))
    return wrapper

# Override all inherited methods from set so that they lock safely
def _wrap_set_methods():
    method_descriptor = type(set.add)
    wrapper_descriptor = type(set.__or__)
    target_methods = {}
    for method in ("__init__", "__delattr__", "__getattribute__", "__setattr__"):
        target_methods[method] = None
    for method in ("difference_update", "intersection_update", "symmetric_difference_update", "update", "__iand__", "__ior__", "__isub__", "__ixor__"):
        target_methods[method] = SemiSortedSet._recalculate
    for method in ("clear", "discard", "pop", "remove"):
        target_methods[method] = SemiSortedSet._recalculate_after_remove
    for function_name in dir(set):
        set_function = getattr(set, function_name)
        if not isinstance(set_function, (method_descriptor, wrapper_descriptor)):
            continue
        override_function = getattr(SemiSortedSet, function_name)
        if override_function is not set_function:
            continue
        if function_name in target_methods:
            target_function = target_methods[function_name]
            if target_function is None:
                continue
            new_function = lock_wrapper(set_function, target_function)
        else:
            new_function = Decorators.SelfLocking.runwithlock(set_function)
        new_function = Decorators.wraptimer(new_function)
        setattr(SemiSortedSet, function_name, new_function)

# Set up function wrapping, and clean up the setup method
_wrap_set_methods()
del _wrap_set_methods

