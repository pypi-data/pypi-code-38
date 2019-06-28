"""This module contains DomainEvent listening and publishing logic."""

import abc
from queue import Empty
from threading import Thread
from multiprocessing import Queue
from typing import Dict, Any


class DomainEventListener(metaclass=abc.ABCMeta):
    """DomainEventListener is the interface for domain event listening."""

    @abc.abstractmethod
    def domainEventPublished(self, event: Dict[str, Any]) -> None:
        """React to domain event.

        Args:
            event: the event that have been published

        Requires:
            event is not None
        """
        raise NotImplementedError()


class AsyncDomainEventListener(Thread, metaclass=abc.ABCMeta):
    """Interface for async domain event listening."""

    def __init__(self):
        """Make it be a new AsyncDomainEventListener."""
        Thread.__init__(self)

        self.queue = Queue()
        self.__must_run = True
        self.__is_running = True

    def run(self):  # noqa: D102
        while self.__must_run:
            try:
                event = self.queue.get(timeout=5)
                self.domainEventPublished(event)
            except Empty:
                pass
            self.post_publish()
        self.__is_running = False

    def terminate(self) -> None:
        """Flag this domain event listener to be stopped soon."""
        self.__must_run = False

    def post_publish(self) -> None:
        """Overridable method called just after domainEventPublished."""  # noqa: D401
        pass

    def is_running(self) -> bool:
        """Check if this domain event listener is running.

        Returns:
            True if the domain event listener is running. False otherwise.

        """
        return self.__is_running

    @abc.abstractmethod
    def domainEventPublished(self, event):  # noqa: D102
        raise NotImplementedError()


class ApplicationDomainEventPublisher:
    """Event publisher for an application.

    Listener must be registered with `register_listener` method.
    They can be unregistered with `unregister_listener`.
    All listeners must implement DomainEventListener interface

    """

    class __ApplicationDomainEventPublisher(DomainEventListener):
        def __init__(self):
            self.__sync_listeners = list()
            self.__async_listeners = list()

        def domainEventPublished(self, event):
            for listener in self.__async_listeners:
                listener.put(event)

            for listener in self.__sync_listeners:
                assert isinstance(listener, DomainEventListener)
                listener.domainEventPublished(event)

        def register_listener(self, obj):
            assert obj is not None
            assert isinstance(obj, DomainEventListener) or isinstance(
                obj, AsyncDomainEventListener
            )

            if isinstance(obj, DomainEventListener):
                self.__sync_listeners.append(obj)
            else:
                self.__async_listeners.append(obj.queue)

        def unregister_listener(self, listener):
            assert listener is not None
            assert isinstance(listener, DomainEventListener) or isinstance(
                listener, AsyncDomainEventListener
            )

            if isinstance(listener, DomainEventListener):
                self.__sync_listeners.remove(listener)
            else:
                self.__async_listeners.remove(listener.queue)

        def contains_listener(self, listener):
            assert listener is not None
            assert isinstance(listener, DomainEventListener) or isinstance(
                listener, AsyncDomainEventListener
            )

            if isinstance(listener, DomainEventListener):
                return listener in self.__sync_listeners
            else:
                return listener.queue in self.__async_listeners

    instance = None

    def __init__(self):
        if ApplicationDomainEventPublisher.instance is None:
            ApplicationDomainEventPublisher.instance = (
                ApplicationDomainEventPublisher.__ApplicationDomainEventPublisher()
            )

    def __getattr__(self, name):
        return getattr(ApplicationDomainEventPublisher.instance, name)
