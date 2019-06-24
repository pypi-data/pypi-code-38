from typing import Optional, Union
from datalogue.clients.http import _HttpClient, HttpMethod
from datalogue.anduin.models.stream import Stream, StreamStatus
from datalogue.errors import DtlError
from uuid import UUID


class _AnduinClient:
    """
    Client to interact with the Anduin APIs
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client

    def run(self, stream: Stream, stream_id: Optional[UUID]=None) -> Union[DtlError, UUID]:
        """
        Run given stream directly through Anduin
        :param stream: Stream to run
        :param stream_id: Id to be used by the stream
        :return: Returns stream id
        """

        params = {}
        if id is not None:
            params = {"id": stream_id}

        res = self.http_client.make_authed_request('/run', HttpMethod.POST, stream._as_payload(), params=params)

        if isinstance(res, DtlError):
            return res

        return res["streamId"]

    def status(self, stream_id: UUID) -> Union[DtlError, StreamStatus]:
        """
        Returns the status of given stream id
        :param stream_id: Id of the stream
        :return: Returns status of the stream
        """
        res = self.http_client.make_authed_request('/status/' + str(stream_id), HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return StreamStatus.from_payload(res)
