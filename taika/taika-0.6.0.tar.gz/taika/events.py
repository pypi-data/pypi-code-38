"""
:mod:`taika.events` -- Basic event managment
============================================

This module offers a simple event manager implemented in the class
:class:`taika.events.EventManager`.
"""
from collections import defaultdict

__all__ = ["events", "EventNotFound", "EventManager"]

events = set(["doc-post-read", "site-post-read"])
"""The events that the event manager can register functions to."""


class EventNotFound(Exception):
    """Exception raised when an event does not exists."""


class EventManager(object):
    """Register functions to events and passes them arguments and keyword arguments when called."""

    def __init__(self):
        self.funcs = defaultdict(dict)
        self.next_id = 0

    def register(self, event, func):
        """Register a callable `func` to an `event`.

        Parameters
        ----------
        event : str
            The event to which `func` will be registered.
        func : callable
            A callable that will recieve arguments and keywords arguments when `event` is triggered.

        Returns
        -------
        current_id : int
            The ID assigned to the function.

        Raises
        ------
        :exc:`EventNotFound`
            If the `event` that is being triggered does not exist.
        """
        _event_exists(event)

        current_id = self.next_id
        self.next_id += 1
        self.funcs[event][current_id] = func
        return current_id

    def call(self, event, *args, **kwargs):
        r"""Call all the functions registered to `event` passing `*args` and `*kwargs`.

        Parameters
        ----------
        event : str
            The event which be triggered.

        Raises
        ------
        :exc:`EventNotFound`
            If the `event` that is being triggered does not exist.
        """
        _event_exists(event)

        results = []
        for func in self.funcs[event].values():
            results.append(func(*args, **kwargs))
        return results


def _event_exists(event):
    """Check if `event` is inside :data:`events`.

    Parameters
    ----------
    event : str
        The name of the event.

    Raises
    ------
    :exc:`EventNotFound`
        When the event is not in :data:`events`.
    """
    if event not in events:
        raise EventNotFound(f"The event '{event}' does not exists.'")
    return True
