# Copyright 2015 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
from __future__ import absolute_import

from collections import defaultdict
from fresco.compat import get_ident

__all__ = 'context', 'RequestContext'


class RequestContext(object):
    """\
    A local storage class that maintains different values for each request
    context in which it is used.

    Requires an ``ident_func`` that returns a hashable identifier that will
    give a different value per request. In a threaded environment this would be
    ``thread.get_ident``. If using a different execution model, a different
    strategy would need to be found.

    During a request the context object will contain the following keys:

    - ``app``: the currently executing FrescoApp object.
    - ``route_traversal``: a :class:`~fresco.routing.RouteTraversal` object.
    - ``view_self``: the instance of the current class based view if
      applicable, otherwise ``None``.
    - ``request``: the current :class:`~fresco.request.Request` object.
    """
    __slots__ = ['_contexts', '_ident_func']

    def __init__(self, ident_func=get_ident, setattr=object.__setattr__):
        c = defaultdict(list)
        c[ident_func()] = [{}]
        setattr(self, '_contexts', c)
        setattr(self, '_ident_func', ident_func)

    def push(self, **bindnames):
        self._contexts[self._ident_func()].append(bindnames)

    def pop(self):
        ident = self._ident_func()
        self._contexts[ident].pop()
        if not self._contexts[ident]:
            del self._contexts[ident]

    def currentcontext(self):
        return self._contexts[self._ident_func()][-1]

    def __getattr__(self, item):
        try:
            return self._contexts[self._ident_func()][-1][item]
        except (KeyError, IndexError):
            raise AttributeError(item)

    def __setattr__(self, item, ob):
        self._contexts[self._ident_func()][-1][item] = ob

    def __delattr__(self, item):
        try:
            del self._contexts[self._ident_func()][-1][item]
        except KeyError:
            raise AttributeError(item)

    # Emulate dictionary access methods
    __getitem__ = __getattr__
    __setitem__ = __setattr__
    __delitem__ = __delattr__

    def get(self, item, default=None):
        return self.currentcontext().get(item, default)

    def __repr__(self):
        return "<%s localdepth=%d; total=%d; current=%r>" % (
                            self.__class__.__name__,
                            len(self._contexts[self._ident_func()]),
                            sum(len(ctx) for ctx in self._contexts.values()),
                            self.currentcontext())


#: The Context for the current request; allows apps to access the current
#: request context as a pseudo-global var
context = RequestContext()
