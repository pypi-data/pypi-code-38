from typing import List, Union
from datalogue.clients.http import _HttpClient, HttpMethod
from datalogue.models.datastore_collection import DatastoreCollection, _datastore_collection_from_dict
from datalogue.errors import DtlError
from uuid import UUID
from datalogue.utils import _parse_list


class _DatastoreCollectionClient:
    """
    Client to interact with the datastore collection objects
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"

    def create(self, datastore_collection: DatastoreCollection) -> Union[DtlError, DatastoreCollection]:
        """
        Creates the Datastore Collection as specified.

        :param datastore_collection: Datastore Collection to be created
        :return: string with error message if failed, uuid otherwise
        """
        assert isinstance(datastore_collection, DatastoreCollection), 'Input is not a Datastore Collection instance.'
        # todo?? assert datastore indeed is a datastore

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastore-collections", HttpMethod.POST,
            datastore_collection._as_payload())

        if isinstance(res, DtlError):
            return res

        return _datastore_collection_from_dict(res)

    def update(self, datastore_collection_id: UUID, datastore_collection: DatastoreCollection) -> Union[DtlError, bool]:
        """
        Updates the Datastore Collection for the given datastore_collection_id

        :param datastore_collection_id: Id of the datastore collection to update
        :param datastore_collection: Datastore Collection to be updated
        :return: string with error message if failed, uuid otherwise
        """
        assert isinstance(datastore_collection, DatastoreCollection), 'Input is not a Datastore Collection instance.'

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastore-collections/" + str(datastore_collection_id), HttpMethod.PUT,
            datastore_collection._as_payload())


        if isinstance(res, DtlError):
            return res
        else:
            return True

    def search(self, query: str, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[DatastoreCollection]]:
        """
        Search through the Datastore Collections

        :param query: text query to be used to make the search
        :param page: page to be retrieved
        :param item_per_page: number of items to be put in a page
        :return: Returns a List of all the available streams or an error message as a string
        """

        assert isinstance(query, str), 'Input query must be a string.'

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastore-collections?", HttpMethod.GET, )

        if isinstance(res, DtlError):
            return res

        out_list = []

        for i in range(len(res)):
            for content in res[i].values():
                if query in str(content):
                    out_list.append(res[i])
                    break

        # Todo build pagination
        return _parse_list(_datastore_collection_from_dict)(out_list)

    def list(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[DatastoreCollection]]:
        """
        List the Datastore Collection

        :param page: page to be retrieved
        :param item_per_page: number of items to be put in a page
        :return: Returns a List of all the available datastore collections or an error message as a string
        """

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastore-collections?", HttpMethod.GET, )

        if isinstance(res, DtlError):
            return res

        # Todo build pagination
        return _parse_list(_datastore_collection_from_dict)(res)

    def get(self, datastore_collection_id: UUID) -> Union[DtlError, DatastoreCollection]:
        """
        From the provided id, get the corresponding Datastore Collection

        :param datastore_collection_id:
        :return:
        """
        assert isinstance(datastore_collection_id, UUID), 'Input is not a UUID instance.'

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastore-collections/" + str(datastore_collection_id),
            HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return _datastore_collection_from_dict(res)

    def delete(self, datastore_collection_id: UUID) -> Union[DtlError, bool]:
        """
        Deletes the given Datastore Collection

        :param datastore-collection_id: id of the datastore collection to be deleted
        :return: true if successful, the error otherwise
        """
        assert isinstance(datastore_collection_id, UUID), 'Input is not a UUID instance.'

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastore-collections/" + str(datastore_collection_id),
            HttpMethod.DELETE
        )

        if isinstance(res, DtlError):
            return res
        else:
            return True
