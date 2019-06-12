#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tools for profiling object usage.
   """

# Copyright 2007 St James Software

import gc

class ObjTracker(object):
    """Tracker for watching changes in program object usage.

       To use, add something like:

         from j5basic import ObjTracker
         ot = ObjTracker.ObjTracker()

       to the top of a module, and then call

         ot.print_changes()

       where you want the changes in object usage to be printed out.
       """

    def __init__(self):
        self._prev_objs = {}

    def _gather_changes(self):
        """Create a dictionary containing the changes in object usage
           (by object type) since the last call to this method.

           Returns (diff dictionary, number of unreachable objects found by gc.collect, number of objects in gc.garbage).
           """
        unreachable = gc.collect()
        garbage = len(gc.garbage)
        objs = gc.get_objects()

        usage = {}
        diff = {}

        for x in objs:
            key = type(x)
            usage[key] = usage.setdefault(key,0) + 1

        for key, count in usage.items():
            if key in self._prev_objs:
                diff[key] = count - self._prev_objs[key]
                del self._prev_objs[key]
            else:
                diff[key] = count

        for key, count in self._prev_objs.items():
            diff[key] = -count

        self._prev_objs = usage

        return diff, unreachable, garbage

    def top_items(self,diff,size):
        """Return the object types whose usage has increased the most (or decreased the least).

           Returns a list (length=size) of (type, increase) tuples.
           """
        top_items = list(diff.items())
        top_items.sort(key=lambda x: x[1],reverse=True)
        top_items = top_items[:size]
        return top_items

    def bottom_items(self,diff,size):
        """Return the object types whose usage has decreased the most (or increased the least).

           Returns a list (length=size) of (type, -decrease) tuples.
           """
        bottom_items = list(diff.items())
        bottom_items.sort(key=lambda x: x[1],reverse=False)
        bottom_items = bottom_items[:size]
        bottom_items.reverse()
        return bottom_items

    def print_changes(self):
        diff, unreachable, garbage = self._gather_changes()

        print("BIGGEST INCREASES:")
        for objtype, inc in self.top_items(diff,10):
            print("\t", inc, objtype)

        print("SMALLEST INCREASES:")
        for objtype, inc in self.bottom_items(diff,10):
            print("\t", inc, objtype)

        print("# COLLECTED:", unreachable - garbage)
        print("# GC.GARBAGE:", garbage)

        print("----")
