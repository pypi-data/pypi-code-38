from typing import List, Union, Optional
from uuid import UUID
from pyarrow import csv, Table

from datalogue.clients.http import _HttpClient, HttpMethod, MultiPartData, MultiPartFile
from datalogue.models.datastore import Datastore, _datastore_from_payload, FileFormat, Cell, _cell_from_payload

from datalogue.errors import DtlError
from datalogue.utils import _parse_list, ResponseStream


class _DatastoreClient:
    """
    Client to interact with the Datastores objects
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"

    def create(self, datastore: Datastore) -> Union[DtlError, Datastore]:
        """
        Creates a data source

        :param datastore: data source to be created
        :return: string with error message if failed, the data source otherwise
        """
        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores", HttpMethod.POST, datastore._as_payload())

        if isinstance(res, DtlError):
            return res

        return _datastore_from_payload(res)

    def update(self, datastore: Datastore) -> Union[DtlError, Datastore]:
        """
        Updates the backend with the new status of the existing datastore

        :param datastore: to be persisted
        :return:
        """

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore.id),
            HttpMethod.PUT,
            datastore._as_payload()
        )

        if isinstance(res, DtlError):
            return res

        return _datastore_from_payload(res)

    def list(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[Datastore]]:
        """
        List all the datastores that are saved

        TODO pagination

        :param page: page to be retrieved (ignored)
        :param item_per_page: number of items to be put in a page (ignored)
        :return: Returns a List of all the available datastores or an error message as a string
        """

        res = self.http_client.make_authed_request(self.service_uri + "/datastores", HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return _parse_list(_datastore_from_payload)(res)

    def get_schema(self, datastore_id: UUID) -> Union[DtlError, List[List[Cell]]]:
        """
        From the provided id, get the corresponding Datastore schema

        :param datastore_id: id of the datastore to be retrieved
        :return:
        """
        res = self.http_client.make_authed_request(self.service_uri + "/datastores/" + str(datastore_id) + "/schema-samples", HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return _parse_list(_parse_list(_cell_from_payload))(res['schema'])

    def get(self, datastore_id: UUID) -> Union[DtlError, Datastore]:
        """
        From the provided id, get the corresponding Datastore

        :param datastore_id: id of the datastore to be retrieved
        :return:
        """

        res = self.http_client.make_authed_request(self.service_uri + "/datastores/" + str(datastore_id), HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return _datastore_from_payload(res)

    def delete(self, datastore_id: UUID) -> Union[DtlError, bool]:
        """
        Deletes the given Datastore

        :param datastore_id: id of the datastore to be deleted
        :return: true if successful, false otherwise
        """

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore_id), HttpMethod.DELETE)

        if isinstance(res, DtlError):
            return res
        else:
            return True

    def download(self, datastore_id: UUID, file_format: FileFormat, path: str, limit: Optional[int] = None) -> Union[DtlError, str]:
        """
        Downloads the resource in a file

        :param datastore_id: id of the resource to download
        :param file_format: File format of the downloaded resource
        :param path: location to save the file
        :param limit: limit the number of elements to be downloaded
        :return: An error or the path to the downloaded file
        """

        params = {
            "fileFormat": file_format.value,
        }

        if limit is not None:
            if not isinstance(limit, int) or limit < 0:
                return DtlError("limit should be a positive integer")

            params["limit"] = limit

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore_id) + "/download",
            HttpMethod.GET, params=params, stream=True
        )

        if isinstance(res, DtlError):
            return res

        with open(path, 'wb') as f:
            for chunk in res.iter_content(chunk_size=1024 * 32):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        return path

    def load_arrow_table(self, datastore_id: UUID, limit: Optional[int] = None, batch_size: int = 1024) -> \
            Union[DtlError, Table]:
        """
        Loads the resource in an in memory arrow buffer.
        This can be used either with Nvidia RAPIDS or pandas

        pandas:
        df = dtl.client.datastore.load_arrow_table(datastore_id).to_pandas()

        :param datastore_id: if of the resource to load
        :param limit: elements to be loaded in the frame
        :param batch_size: size of the batch to be retrieved at a time from the collection
        :return:
        """

        params = {
            "fileFormat": FileFormat.Csv.value
        }

        if limit is not None:
            if not isinstance(limit, int) or limit < 0:
                return DtlError("limit should be a positive integer")

            params["limit"] = limit

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore_id) + "/download",
            HttpMethod.GET, params=params, stream=True
        )

        if isinstance(res, DtlError):
            return res

        stream = ResponseStream(res.iter_content(batch_size))

        return csv.read_csv(stream)

    def upload(self, datastore_id: UUID, file_format: FileFormat, path: str, params: dict = {}) -> Union[DtlError, None]:
        """
        Enable to upload a file to the specified resource through the platform

        :param datastore_id: id of the resource to upload the data through
        :param file_format: format of the file to be uploaded
        :param path: location of the file to upload on disk
        :return:
        """

        with open(path, 'rb') as f:
            files = [MultiPartFile("content", f)]

            data = [
                MultiPartData("file-format", file_format.value),
                MultiPartData("params", "{}"),
            ]

            res = self.http_client.post_multipart_data(
                self.service_uri + "/datastores/" + str(datastore_id) + "/upload",
                files, data
            )

            if isinstance(res, DtlError):
                return res

