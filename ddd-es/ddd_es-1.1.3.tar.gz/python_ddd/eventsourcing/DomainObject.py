"""This package is aimed to manage a DDD domain object with event sourcing."""

from collections import Iterable
from multiprocessing import Lock
import datetime
import uuid
import json
from copy import deepcopy
from itertools import zip_longest


class DomainObject:
    """The domain object with event sourcing.

    It should be able to :
    - mutate from a received event
    - store events together with their version number
    - store its version
    - be rehydrated from its events
    """

    def __init__(self):
        """Initialises this with it's first event."""

        self.object_id = "{}-{}".format(self.__class__.__name__, str(uuid.uuid4()))
        self.version_number = 0
        self.event_stream = list()
        self.lock = Lock()
        self.mutate("DomainObjectCreated", {"id": self.object_id})

    def mutate(self, event_name, event):
        """Add an event to the stream of events.

        :param event: the received event. That object must be JSON serializable.
        :param event_name: The name of the received event. Must be a not None string
        :raise ValueError: if event is not JSON serializable
        """
        assert event_name is not None
        assert isinstance(event_name, str)

        if not self.__is_json_serializable(event):
            raise ValueError("Event must be JSON serializable")

        self.lock.acquire()

        self.version_number += 1
        self.event_stream.append(
            {
                "object_id": self.object_id,
                "object_type": self.__class__.__name__,
                "version": self.version_number,
                "event_id": f"{self.object_id}-{str(uuid.uuid4())}",
                "event_name": event_name,
                "event": event,
                "event_timestamp": datetime.datetime.now().timestamp(),
            }
        )

        self.lock.release()

        self.__apply_event(event_name, event)

    def rehydrate(self, event_list):
        """Rehydrate the object from it's event list.

        :param event_list: the list of events for rehydratation
        """
        assert isinstance(event_list, Iterable)

        event_list.sort(key=lambda x: x["version"])

        self.lock.acquire()

        self.__clear_stream()
        for event in event_list:
            if event["version"] < self.version_number:
                raise ValueError(
                    "Rehydrated version number is {} but actual version number is {}".format(
                        event["version"], self.version_number
                    )
                )

            self.__apply_event(event["event_name"], event["event"])

            self.version_number += 1
            self.object_id = event["object_id"]
            self.event_stream.append(
                {
                    "object_id": self.object_id,
                    "object_type": event["object_type"],
                    "version": event["version"],
                    "event_name": event["event_name"],
                    "event_id": event["event_id"],
                    "event": event["event"],
                    "event_timestamp": event["event_timestamp"],
                }
            )

        self.lock.release()

    @staticmethod
    def diff_event_streams(event_stream1, event_stream2):
        """Compute the difference between two event streams.

        Diff is computed using the longest prefix of event ids.
        So returned d1 and d2 contains the event streams from the first different element

        Requires:
            The two event streams are for the same object_id

        Returns:
            A tuple (d1, d2) with d1, d2, two lists.
            d1 contains all events of event_stream1 that are different from event_stream2
            d2 contains all events of event_stream2 that are different from event_stream1

        """
        assert (
            len(event_stream1) == 0
            or len(event_stream2) == 0
            or event_stream1[0]["object_id"] == event_stream2[0]["object_id"]
        )
        assert (
            len(set(map(lambda x: x["object_id"], event_stream1))) <= 1
            and len(set(map(lambda x: x["object_id"], event_stream2))) <= 1
        )
        diff_stream1 = []
        diff_stream2 = []

        sorted_event_stream1 = sorted(
            deepcopy(event_stream1), key=lambda x: x["version"]
        )
        sorted_event_stream2 = sorted(
            deepcopy(event_stream2), key=lambda x: x["version"]
        )
        for (idx, (event1, event2)) in enumerate(
            zip_longest(sorted_event_stream1, sorted_event_stream2, fillvalue=None)
        ):
            one_stream_finished = event1 is None or event2 is None
            if one_stream_finished:
                if event1 is not None:
                    diff_stream1 = event_stream1[idx:]
                if event2 is not None:
                    diff_stream2 = event_stream2[idx:]
                break
            elif not one_stream_finished and event1["event_id"] != event2["event_id"]:
                diff_stream1 = event_stream1[idx:]
                diff_stream2 = event_stream2[idx:]
                break

        return diff_stream1, diff_stream2

    def __clear_stream(self):
        self.event_stream = list()
        self.version_number = 0

    def __apply_event(self, event_name, event):
        function_name = "on_{}".format(event_name)
        if function_name in self.__dir__():
            getattr(self, function_name)(event)

    @staticmethod
    def __is_json_serializable(event):
        assert event is not None
        try:
            json.dumps(event)
            return True
        except Exception:
            return False
