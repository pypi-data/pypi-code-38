"""This module contains repositories code."""

import abc
import json
from collections import Iterable
from copy import deepcopy
from typing import Any, Dict, List, Union

import pymysql.cursors
from pymongo import ASCENDING, DESCENDING, MongoClient

from .DomainEventListener import ApplicationDomainEventPublisher, DomainEventListener
from .DomainObject import DomainObject


class Repository(metaclass=abc.ABCMeta):
    """Repository is the base interface that all repo must implement."""

    @abc.abstractmethod
    def load(self, object_id: str) -> DomainObject:
        """Load a domain object based on its id.

        Args:
            object_id: the id of the object to be loaded

        Requires:
            object_id is not None and is a valid id

        Returns:
            The loaded domain object

        """
        raise NotImplementedError()

    @abc.abstractmethod
    def exists(self, object_id: str) -> bool:
        """Check if a domain object exist based on its id.

        Args:
            object_id: the identifier for this object

        Requires:
            object_id is not None and is a valid id

        Returns:
            True if the object exists. False otherwise

        """
        raise NotImplementedError()

    @abc.abstractmethod
    def save(self, obj: DomainObject) -> None:
        """Save a domain object.

        Args:
            obj: the received domain object

        Requires:
            obj is not None and is a valid DomainObject

        Effects:
            Modifications made of the domain object are saved

        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_event_stream_for(self, object_id: str) -> List[Dict[str, Any]]:
        """Return the event stream for an object.

        Args:
            object_id: the identifier of this object

        Requires:
            object_id is not None and is a valid object id

        Returns:
            A sorted list of all the events for this domain object

        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_event_stream_since(self, event_id: str) -> List[Dict[str, Any]]:
        """Return all the events that occurs since a event.

        **The event with event_id==event_id is returned too**

        Args:
            event_id: the event id

        Requires:
            event_id is not None and represent an existing event

        Returns:
            A sorted list of all the event that occurs since the specified event
            The specified event is the firt of this list

        """
        raise NotImplementedError()

    @abc.abstractmethod
    def first_event_id(self) -> Union[str, None]:
        """Return the first known event id for sync.

        If there is no event yet, None is returned

        Returns:
            the firdt event id as a string. None if there is
            no events

        """
        raise NotImplementedError()

    @abc.abstractmethod
    def max_version_for_object(self, object_id: str) -> int:
        """Return the max known version for a domain object.

        Args:
            object_id: the object identifier

        Requires:
            object_id is not None and represent an existing domain object

        Returns:
            The last known version of this object

        """
        raise NotImplementedError()

    @abc.abstractmethod
    def create_blank_domain_object(self) -> DomainObject:
        """Create an empty domain event of the appropriate type.

        Returns:
            an empty domain event of the appropriate type

        """
        raise NotImplementedError()

    @staticmethod
    def merge_event_streams(prioritary_event_stream, other_event_stream):
        """Merge two event streams and manage possible conflit.

        Conflicts in event stream are event streams with repeating event number

        If there is a conflit, the first stream is considered prioritary.
        The conflict is then resolved by appending the additional elements of the second stream
        after these from the first. Events numbers are then correctly modified

        Requires:
            The two event streams are for the same object_id

        Returns:
            The merged event stream

        """
        diff1, diff2 = DomainObject.diff_event_streams(
            prioritary_event_stream, other_event_stream
        )

        if len(diff1) == 0 and len(diff2) == 0:
            return prioritary_event_stream
        elif len(diff1) == 0 and len(diff2) != 0:
            return other_event_stream
        elif len(diff1) != 0 and len(diff2) == 0:
            return prioritary_event_stream
        else:
            result_stream = deepcopy(prioritary_event_stream)
            actual_version = result_stream[-1]["version"] + 1
            for event in diff2:
                event["version"] = actual_version
                actual_version += 1
                result_stream.append(event)
            return result_stream


class EventPublisherRepository(Repository, metaclass=abc.ABCMeta):
    """Repository that publishes its saved events to domain event publisher."""

    def __init__(self):  # noqa: D102
        self.listeners = list()
        self.register_listener(ApplicationDomainEventPublisher().instance)

    def save(self, obj: DomainObject) -> None:  # noqa: D102
        to_emit = self.append_to_stream(obj)

        assert to_emit is not None
        assert isinstance(to_emit, Iterable)

        for event in to_emit:
            for listener in self.listeners:
                assert isinstance(listener, DomainEventListener)
                listener.domainEventPublished(event)

    def register_listener(self, listener: DomainEventListener) -> None:
        """Register a new listener in this.

        Args:
            listener: the given listener

        Requires:
            listener must not be None and must implemnt DomainEventListener

        Effects:
            The listener is added in self

        """
        assert listener is not None
        assert isinstance(listener, DomainEventListener)

        if listener not in self.listeners:
            self.listeners.append(listener)

    @abc.abstractmethod
    def append_to_stream(self, obj: DomainObject) -> List[Dict[str, Any]]:
        """Save modification made on the domain object.

        Args:
            obj: the domain object to be saved

        Requires:
            obj is not None

        Returns:
            the newly persisted events

        """
        raise NotImplementedError()


class MongoEventSourceRepository(EventPublisherRepository, metaclass=abc.ABCMeta):
    """EventSource repository that persist event in mongodb."""

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
        self.__collection = self.__db[collection]
        self.__create_indexes()

    def append_to_stream(self, obj):  # noqa: D102
        assert obj is not None
        assert isinstance(obj, DomainObject)

        max_known_version = self.max_version_for_object(obj.object_id)
        merged_stream = self.merge_event_streams(
            self.get_event_stream_for(obj.object_id), obj.event_stream
        )
        merged_stream_version = merged_stream[-1]["version"]

        events_to_add = list()
        if merged_stream_version > max_known_version:
            for event in filter(
                lambda e: e["version"] > max_known_version, merged_stream
            ):
                events_to_add.append(deepcopy(event))

        if len(events_to_add) > 0:
            self.__collection.insert_many(events_to_add)

        return deepcopy(events_to_add)

    def load(self, object_id):  # noqa: D102
        obj = self.create_blank_domain_object()
        assert isinstance(obj, DomainObject)

        stream = self.get_event_stream_for(object_id)
        obj.rehydrate(stream)

        return obj

    def exists(self, object_id):  # noqa: D102
        return self.__collection.count_documents({"object_id": object_id}) > 0

    def get_event_stream_for(self, object_id):  # noqa: D102
        return list(self.__collection.find({"object_id": object_id}, {"_id": 0}))

    def max_version_for_object(self, object_id):  # noqa: D102
        max_version_event = list(
            self.__collection.find({"object_id": object_id})
            .sort([("version", -1)])
            .limit(1)
        )

        if len(max_version_event) == 0:
            return 0
        else:
            return max_version_event[0]["version"]

    def get_event_stream_since(self, event_id):  # noqa: D102
        event = self.__collection.find_one({"event_id": event_id})

        if event is None:
            raise ValueError("This event id cannot be found")

        event_timestamp = event["event_timestamp"]
        events_iterator = self.__collection.find(
            {"event_timestamp": {"$gte": event_timestamp}}
        ).sort([("event_timestamp", 1)])

        for event in events_iterator:
            yield event

    def first_event_id(self) -> Union[str, None]:  # noqa: D102
        events = list(
            self.__collection.find({"version": 1})
            .sort([("event_timestamp", 1)])
            .limit(1)
        )

        if len(events) == 1:
            return events[0]["event_id"]
        else:
            return None

    def __create_indexes(self):
        self.__collection.create_index(
            [("event_id", ASCENDING)], name="eventid_unique", unique=True
        )
        self.__collection.create_index(
            [("object_id", ASCENDING), ("version", ASCENDING)],
            name="objectid_version_unique",
            unique=True,
        )
        self.__collection.create_index(
            [("event_timestamp", DESCENDING)], name="timestamp_ascending"
        )


class MySQLSourceRepository(EventPublisherRepository, metaclass=abc.ABCMeta):

    __CREATE_STREAM = """create table `{}`(`object_id` varchar(255) not null, `version` int not null, `event_name` varchar(255) not null, `event` longtext not null, `event_timestamp` double not null, primary key(`object_id`, `version`))"""
    __SELECT_OBJECT_STREAM = "select * from `{}` where object_id = %s"
    __INSERT_OBJECT_STREAM = "insert into `{}`(`object_id`, `version`, `event_name`, `event`, `event_timestamp`) values(%s, %s, %s, %s, %s)"
    __CHECK_TABLE_EXISTS = "show tables like %s"
    __TABLE_EXISTS = False

    def __init__(
        self,
        user="fenrys",
        password="fenrys",
        host="localhost",
        database="fenrys",
        table="event_store",
    ):
        super().__init__()
        self.__connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=database,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.__table = table

        self.__create_table()

    def __del__(self):
        self.__connection.close()

    def __create_table(self):
        if not self.__table_exists():
            try:
                with self.__connection.cursor() as cursor:
                    cursor.execute(
                        MySQLSourceRepository.__CREATE_STREAM.format(self.__table)
                    )
                self.__connection.commit()
            except Exception as e:
                self.__connection.rollback()
                raise e

    def __table_exists(self):
        if not MySQLSourceRepository.__TABLE_EXISTS:
            with self.__connection.cursor() as cursor:
                cursor.execute(
                    MySQLSourceRepository.__CHECK_TABLE_EXISTS, (self.__table)
                )
                result = cursor.fetchone()
                if result:
                    MySQLSourceRepository.__TABLE_EXISTS = True
                    return True
                else:
                    return False
        else:
            return True

    def append_to_stream(self, obj):
        assert obj is not None
        assert isinstance(obj, DomainObject)

        max_known_version = self.max_version_for_object(obj.object_id)

        events_to_add = list()
        if obj.version_number > max_known_version:
            for event in obj.event_stream:
                if event["version"] > max_known_version:
                    events_to_add.append(deepcopy(event))

        if len(events_to_add) > 0:
            try:
                with self.__connection.cursor() as cursor:
                    cursor.executemany(
                        MySQLSourceRepository.__INSERT_OBJECT_STREAM.format(
                            self.__table
                        ),
                        map(
                            lambda event: (
                                event["object_id"],
                                int(event["version"]),
                                event["event_name"],
                                json.dumps(event["event"]),
                                "{:10.15f}".format(float(event["event_timestamp"])),
                            ),
                            events_to_add,
                        ),
                    )
                self.__connection.commit()
            except Exception as e:
                self.__connection.rollback()
                raise e

        return deepcopy(events_to_add)

    def load(self, object_id):
        obj = self.create_blank_domain_object()
        assert isinstance(obj, DomainObject)

        stream = self.get_event_stream_for(object_id)
        obj.rehydrate(stream)

        return obj

    def exists(self, object_id):
        return len(self.get_event_stream_for(object_id)) > 0

    def get_event_stream_for(self, object_id):
        stream = list()

        with self.__connection.cursor() as cursor:
            cursor.execute(
                MySQLSourceRepository.__SELECT_OBJECT_STREAM.format(self.__table),
                (object_id),
            )
            results = cursor.fetchall()
            for result in results:
                r = dict()
                r["object_id"] = result["object_id"]
                r["version"] = int(result["version"])
                r["event_name"] = result["event_name"]
                r["event"] = json.loads(result["event"])
                r["event_timestamp"] = float(result["event_timestamp"])
                stream.append(r)

        return stream

    def max_version_for_object(self, object_id):
        stream = self.get_event_stream_for(object_id)

        return max(map(lambda x: x["version"], stream)) if len(stream) > 0 else 0


class InMemoryEventSourceRepository(EventPublisherRepository, metaclass=abc.ABCMeta):
    def __init__(self):
        super().__init__()
        self.__repo = list()

    def append_to_stream(self, obj):
        assert obj is not None
        assert isinstance(obj, DomainObject)

        max_known_version = self.max_version_for_object(obj.object_id)
        merged_stream = self.merge_event_streams(
            self.get_event_stream_for(obj.object_id), obj.event_stream
        )
        merged_stream_version = merged_stream[-1]["version"]

        events_to_add = list()
        if merged_stream_version > max_known_version:
            for event in merged_stream:
                if event["version"] > max_known_version:
                    events_to_add.append(event)
                    self.__repo.append(event)

        return deepcopy(events_to_add)

    def load(self, object_id):
        obj = self.create_blank_domain_object()
        assert isinstance(obj, DomainObject)

        stream = self.get_event_stream_for(object_id)
        obj.rehydrate(stream)

        return obj

    def exists(self, object_id):
        return len(self.get_event_stream_for(object_id)) > 0

    def get_event_stream_for(self, object_id):
        stream = list()
        for event in self.__repo:
            if event["object_id"] == object_id:
                stream.append(event)
        return stream

    def get_event_stream_since(self, event_id):
        ignore = True
        for event in sorted(self.__repo, key=lambda x: x["event_timestamp"]):
            if event["event_id"] == event_id:
                ignore = False

            if not ignore:
                yield event

    def max_version_for_object(self, object_id):
        max_known_version = 0
        stream = self.get_event_stream_for(object_id)

        for event in stream:
            if event["version"] > max_known_version:
                max_known_version = event["version"]

        return max_known_version

    def first_event_id(self):
        if len(self.__repo) == 0:
            return None
        else:
            return self.__repo[0]["event_id"]
