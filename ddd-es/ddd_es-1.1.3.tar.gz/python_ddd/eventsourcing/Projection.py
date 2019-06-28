"""This module contains classes used to project events."""

import abc
from typing import Any, Dict

from pymongo import MongoClient

from .DomainEventListener import DomainEventListener


class Projection(DomainEventListener):
    """Projection is an abstract class that represent a projection.

    All Projection sub classes must implement `project` method

    """

    def domainEventPublished(self, event: Dict[str, Any]) -> None:  # noqa: D102
        obj_id = event["object_id"]
        event_name = event["event_name"]
        event = event["event"]

        self.project(obj_id, event_name, event)

    @abc.abstractmethod
    def project(self, obj_id: str, event_name: str, event):
        """Project the domain event.

        Args:
            obj_id: the object id
            event_name: the type of event to be projected
            event: the event payload

        Requires:
            No argument is None

        """
        raise NotImplementedError()


class MongoProjection(Projection):
    def __init__(
        self,
        host="localhost",
        port=27017,
        database="fenrys",
        collection="event_store",
        username=None,
        password=None,
    ):
        super().__init__()
        self.__client = MongoClient(host, port)
        if username is not None and password is not None:
            self.__client = MongoClient(
                host, port, username=username, password=password
            )
        self.__db = self.__client[database]
        self.collection = self.__db[collection]

    @abc.abstractmethod
    def project(self, obj_id, event_name, event):  # noqa: D102
        raise NotImplementedError()


class InMemoryProjection(Projection):
    def __init__(self):
        super().__init__()
        self.collection = list()

    @abc.abstractmethod
    def project(self, obj_id, event_name, event):  # noqa: D102
        raise NotImplementedError()
