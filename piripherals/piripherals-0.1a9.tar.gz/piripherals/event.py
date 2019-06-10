from threading import current_thread
from queue import Queue
from functools import partial
from piripherals.util import fork, not_raising

__all__ = ['Event']


class EventLoop:
    """queue for processing function calls on a separate thread"""

    def __init__(self):
        self.events = Queue()
        self.loopthread = None

    def _start(self):
        if self.loopthread:
            return

        def loop():
            self.loopthread = current_thread()
            for f in self:
                f()

        fork(loop)
        return self

    def __iter__(self): return self

    def __next__(self): return self.remove()

    def in_loop(self):
        """test if currently in eventloop.

        Return:
            bool: True if on eventloop
        """
        return current_thread() is self.loopthread

    def add(self, func):
        """add to the queue

        Args:
            func(callable): func to put in the queue
        """
        self._start()
        self.events.put(not_raising(func))
        return self

    def remove(self):
        """get function from the queue and remove it. Blocks until there is
        something in the queue."""
        return self.events.get()

    __lshift__ = add


class Event:
    """Event with attached handlers and optional condition.

    Args:
        name (str): name of the event, usuful for debugging
        condition (callable): condition to suppress firing, if it evaluates
            to False
    """

    loop = EventLoop()

    def __init__(self, name='event', condition=lambda: True):
        self.name = name
        self.handlers = []
        self.condition = condition

    def __str__(self):
        return str(self.name)

    def add(self, handler):
        """add an event handler.

        Handlers can be added with ``Event >> handler``.

        Args:
            handler (callable): handler to attach. If the handler is an Event,
                its :meth:`fire` method will be attach as handler.
        """
        if isinstance(handler, Event):
            self.handlers.append(handler.fire)
        else:
            self.handlers.append(handler)
        return self

    def remove(self, handler):
        """remove an attached handler"""
        self.handlers.remove(handler)
        return self

    def queue(self, *args, **kwargs):
        """Enqueue the event on eventloop.

        This is equivalent to just calling the Event itself.

        :meth:`fire` will be enqueued in the eventloop, such that it will be
        called on the loop thread and not on the thread calling :meth:`queue`.
        All arguments are passed to the handlers.
        """
        Event.loop << partial(self.fire, *args, **kwargs)

    def fire(self, *args, **kwargs):
        """Fire the event, call all attached handlers.

        The event is only fired, if the condition evaluates to True.
        All arguments are passed to the handlers.
        """
        if self.condition():
            for handler in self.handlers:
                not_raising(handler)(*args, **kwargs)

    def conditional(self, cond):
        """derive a new conditional event

        A conditional Event can created with ``Event & condition``.

        Args:
            condition (callable): see :class:`Event`

        Return:
            Event: conditional Event, with this Event's :meth:`fire` as handler
        """
        return Event(self.name + '?', cond) >> self.fire

    def join(self, other):
        """derive Event as combination of two Events

        Events can be joined with ``EventA + EventB``. This differs from
        :meth:`add`, because it creates a new Event and leaves this untouched.

        Args:
            other (callable): handler to join with, can be another Event

        Return:
            Event: Event with this and other's :meth:`fire` as handlers
        """
        if isinstance(other, Event):
            return Event(self.name + '+' + other.name) >> self.fire >> other.fire
        else:
            return Event(self.name + '+other') >> self.fire >> other

    def partial(self, *args, **kwargs):
        """creat new Event with partially set arguments"""
        return Event('{}({}{})'.format(self, args, kwargs)) \
            >> partial(self.fire, *args, **kwargs)

    __call__ = queue
    __rshift__ = add
    __and__ = conditional
    __add__ = join
