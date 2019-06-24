from typing import List, Union, Optional

from datalogue.models.transformations import Transformation
from datalogue.anduin.models.datastore import Datastore
from datalogue.errors import DtlError

from datetime import datetime
from datalogue.errors import _enum_parse_error
from datalogue.utils import SerializableStringEnum
from dateutil.parser import parse

from uuid import UUID


class StreamCollection:
    def __init__(self, transformations: List[Transformation], pipelines: List['StreamCollection'], target: Datastore):
        self.transformations = transformations
        self.pipelines = pipelines
        self.target = target

    def _as_payload(self) -> Union[DtlError, dict]:
        return {
            "transformations": list(map(lambda s: s._as_payload(), self.transformations)),
            "pipelines": list(map(lambda s: s._as_payload(), self.pipelines)),
            "target": self.target._as_payload()
        }


class Stream:
    def __init__(self, datastore: Datastore, stream_collection: List[StreamCollection]):
        self.datastore = datastore
        self.stream_collection = stream_collection

    def _as_payload(self):
        return {
            "source": self.datastore._as_payload(),
            "pipelines": list(map(lambda s: s._as_payload(), self.stream_collection))
        }

    @staticmethod
    def simple_stream(datastore: Datastore, transformations: List[Transformation], target: Datastore):
        return Stream(datastore, [StreamCollection(transformations, [], target)])


class StreamState(SerializableStringEnum):
    Succeeded = "Succeeded"
    Failed = "Failed"
    Running = "Running"
    Defined = "Defined"
    Unknown = "Unknown"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("stream state", s))

    @staticmethod
    def stream_state_from_str(string: str) -> Union[DtlError, 'StreamState']:
        return SerializableStringEnum.from_str(StreamState)(string)


class StreamStatus:
    def __init__(self, stream_id: UUID, state: StreamState, timestamp: datetime, details: Optional[str] = None):
        self.stream_id = stream_id
        self.state = state
        self.timestamp = timestamp
        self.details = details

    def __repr__(self):
        return f"StreamStatus(id: {self.stream_id}, state: {self.state.value}, ts: {self.timestamp}, details: {self.details})"

    @staticmethod
    def from_payload(payload: dict) -> Union[DtlError, 'StreamStatus']:
        stream_id = payload.get("id")
        if stream_id is None:
            return DtlError("'stream_id' needs to be defined!")

        ts = payload.get("timestamp")
        if ts is None:
            return DtlError("'timestamp' needs to be defined!")
        else:
            try:
                ts = parse(ts)
            except ValueError:
                return DtlError("'timestamp' could not be parsed as a valid date")

        stream_state = payload.get("status")
        if stream_state is None:
            return DtlError("'status' needs to be defined!")
        else:
            stream_state = StreamState.stream_state_from_str(stream_state)
            if isinstance(stream_state, DtlError):
                return stream_state

        return StreamStatus(UUID(stream_id), stream_state, ts, payload["details"])
