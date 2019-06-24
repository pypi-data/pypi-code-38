from typing import List, Union, Optional
from datalogue.clients.http import _HttpClient, HttpMethod
from datalogue.models.stream import Stream
from datalogue.models.stream_collection import StreamCollection, _stream_collection_from_payload, _stream_metadata_from_payload
from datalogue.utils import _parse_list
from datalogue.models.job import _job_from_payload
from datalogue.errors import DtlError
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dateutil.tz import UTC


class _StreamCollectionClient:
    """
    Right now interactions on Stream Collections as they are currently called in the API. Or Stream Collection as they are
    called in the UI.

    To simplify things, right now the SDK allows interactions with Stream Collection of one stream
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"

    def create(self, streams: List[Stream], name: Optional[str]) -> Union[DtlError, StreamCollection]:
        """
        Creates the stream as specified.
        Right now this creates a Stream Collection with only one stream

        TODO think about creating datastores when they are references in the Stream that don't exist

        :param streams: Streams to be created
        :param name: name of the stream to be created. If None supplied, one will be generated
        :return: string with error message if failed, uuid otherwise
        """

        if name is None:
            name = "stream-" + str(uuid4())[0:8]

        # save Stream Collection
        res1 = self.http_client.make_authed_request(
            self.service_uri + '/stream-collections', HttpMethod.POST, { "name": name }
        )

        stream_collection_id = res1.get("id")
        if stream_collection_id is None:
            return DtlError("Created response did not return an id")

        created_streams = []
        # add stream
        for stream in streams:
            res2 = self.http_client.make_authed_request(
                self.service_uri + '/stream-collections/' + stream_collection_id + "/stream", HttpMethod.POST, stream._as_payload()
            )

            if isinstance(res2, DtlError):
                return res2
            
            stream_meta = _stream_metadata_from_payload(res2)
            if isinstance(stream_meta, DtlError):
                return stream_meta

            created_streams.append(stream_meta)

        return StreamCollection(stream_collection_id, name, created_streams)

    def update(self, stream_collection_id: UUID, name: Optional[str] = None, streams: Optional[List[Stream]] = None) \
            -> Union[DtlError, StreamCollection]:
        """
        Updates the Stream Collection

        :param stream_collection_id: id of the Stream Collection to update
        :param name: new name of the Stream Collection
        :param streams: new set of streams for the Stream Collection (overrides the previous set)
        :return: Either an error message in a string or the Stream Collection
        """

        ref_stream_collection = self.get(stream_collection_id)
        if isinstance(ref_stream_collection, DtlError):
            return DtlError("It looks like you are trying to update a Stream Collection that doesn't exist", ref_stream_collection)

        if isinstance(name, str):

            res = self.http_client.make_authed_request(
                f"{self.service_uri}/stream-collections/{stream_collection_id}", HttpMethod.PUT, {"name": name}
            )

            if isinstance(res, DtlError):
                return res

        if isinstance(streams, list):

            # We start by removing all the existing streams
            for stream in ref_stream_collection.streams:
                res = self.http_client.make_authed_request(f"{self.service_uri}/streams/{stream.id}", HttpMethod.DELETE)

                if isinstance(res, DtlError):
                    return DtlError("Could not delete all previously existing streams, interrupting update", res)

            # Then we attach all the new ones
            for stream in streams:
                res = self.http_client.make_authed_request(
                    f"{self.service_uri}/stream-collections/{stream_collection_id}/stream", HttpMethod.POST, stream._as_payload()
                )
                if isinstance(res, DtlError):
                    return DtlError("Could not add all the new streams to the Stream Collection, interrupting update", res)

        return self.get(stream_collection_id)

    def schedule(self, stream_collection_id: UUID, date: datetime) -> Union[DtlError, bool]:
        """
        Creates a job to be run at the given date

        :param stream_collection_id: id of the stream to be run
        :param date: date at which to run the stream, expected to be localized
        :return: Either an error message in a string or the UUID for the new job
        """

        res = self.http_client.make_authed_request(
            self.service_uri + '/stream-collections/' + str(stream_collection_id) + "/schedules",
            HttpMethod.POST,
            {"runDate": date.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")}
        )

        if isinstance(res, DtlError):
            return res

        return _parse_list(_job_from_payload)(res)

    def run(self, pipeline_id: UUID) -> Union[DtlError, bool]:
        """
        Runs the pipeline right now + 2 secs

        :param pipeline_id: id of the pipeline to run
        :return:
        """

        return self.schedule(pipeline_id, datetime.now() + timedelta(seconds=2))

    def list(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[StreamCollection]]:
        """
        Retrieves a list of the available streams (Stream Collections)

        TODO pagination
        :param page: page to be retrieved
        :param item_per_page: number of items to be put in a page
        :return: Returns a List of all the available streams or an error message as a string
        """
        res = self.http_client.make_authed_request(self.service_uri + "/stream-collections", HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return _parse_list(_stream_collection_from_payload)(res)

    def get(self, stream_collection_id: UUID) -> Union[DtlError, StreamCollection]:
        """
        From the provided id, get the corresponding stream (Stream Collection)

        :param stream_collection_id:
        :return:
        """
        res = self.http_client.make_authed_request(
            self.service_uri + "/stream-collections/" + str(stream_collection_id), HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return _stream_collection_from_payload(res)

    def delete(self, stream_collection_id: UUID) -> Union[DtlError, bool]:
        """
        Deletes the given stream (Stream Collection)

        :param Stream Collection_id: id of the stream (Stream Collection) to be deleted
        :return: true if successful, false otherwise
        """

        res = self.http_client.make_authed_request(
            self.service_uri + "/stream-collections/" + str(stream_collection_id), HttpMethod.DELETE)

        if isinstance(res, DtlError):
            return res
        else:
            return True
