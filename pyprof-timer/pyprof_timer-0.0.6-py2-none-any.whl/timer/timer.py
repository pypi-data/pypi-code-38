# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from operator import itemgetter

import monotonic
from tree_format import format_tree


class Timer(object):
    """The timer class that calculates and shows the consuming time
    of a given Python function or snippet.
    """

    _ctx_timers = '_Timer_timers'

    def __init__(self, name, start, parent_name=None):
        self._name = name
        self._start = start
        self._stop = None
        self._parent_name = parent_name
        self._children = []

        if parent_name is not None:
            self.parent.add_child(self._name, self)

    def _get_context(self):
        raise NotImplementedError()

    @property
    def timers(self):
        ctx = self._get_context()

        _timers = getattr(ctx, self._ctx_timers, None)
        if _timers is None:
            _timers = {}
            setattr(ctx, self._ctx_timers, _timers)

        return _timers

    @property
    def parent(self):
        _timers = self.timers
        if self._parent_name not in _timers:
            _timers[self._parent_name] = self._dummy(self._parent_name)
        return _timers[self._parent_name]

    def add_child(self, name, timer):
        # Add `timer` into the context global timers
        _timers = self.timers
        if name in _timers:
            raise RuntimeError('timer name "%s" is duplicated' % name)
        _timers[name] = timer

        self._children.append(timer)

    @classmethod
    def _dummy(cls, name):
        return cls(name, None)

    @classmethod
    def start(cls, name, parent_name=None):
        return cls(name, monotonic.monotonic(), parent_name)

    def stop(self):
        self._stop = monotonic.monotonic()
        return self

    def span(self, unit='s'):
        """Returns the elapsed time in fractional seconds."""
        multipliers = dict(s=1, ms=1000, us=1000000)
        assert unit in multipliers, '`unit` must be one of %s' % multipliers.keys()

        if self._start is None:
            # For dummy timer, return the sum of all children timers
            return sum(child.span(unit) for child in self._children)

        if self._stop is None:
            raise RuntimeError('timer[%s].stop() has not been called' % self._name)

        return (self._stop - self._start) * multipliers[unit]

    def tree(self, span_unit='ms', span_fmt='%.3f'):
        """Represents the timer and its children timers as a tree."""
        span = span_fmt % self.span(span_unit)
        node = '%s (%s %s)' % (self._name, span, span_unit)
        children = [child.tree(span_unit, span_fmt).nodes
                    for child in self._children]
        return Tree((node, children))


class Tree(object):

    def __init__(self, nodes):
        self.nodes = nodes

    def show(self):
        """Print out the timer tree (as an UTF-8 string)."""
        formatted = format_tree(
            self.nodes, format_node=itemgetter(0), get_children=itemgetter(1)
        )
        print(formatted.encode('utf-8'))
