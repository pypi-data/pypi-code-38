from typing import List, Union, Optional
from datalogue.clients.http import _HttpClient, HttpMethod
from datalogue.models.datastore import Datastore
from datalogue.models.credentials import Credentials, _credentials_ref_from_payload, CredentialsReference
from datalogue.utils import _parse_list
from uuid import UUID
from datalogue.errors import DtlError


class _CredentialsClient:
    """
    Client to interact with the Credentials objects
    """
    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout/public"
        self.admin = _AdminCredentialsClient(http_client)

    def list(self, credential_type: Optional[str] = None, page: int = 1, item_per_page: int = 25) -> Union[
        DtlError, List[Datastore]]:
        """
        Lists available credentials that user has Use Permission

        :param credential_type: type of the credentials (S3, GCS, Jdbc, etc)
        :param page: page to be retrieved
        :param item_per_page: number of items to be put in a page
        :return: Returns a List of all the available credentials or an error message as a string
        """

        res = self.http_client.make_authed_request(
            self.service_uri +
            f"/credentials?page={page}&size={item_per_page}{'' if credential_type is None else f'&type={credential_type}'}",
            HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return _parse_list(_credentials_ref_from_payload)(res)


class _AdminCredentialsClient:
    """
    Client to interact with the Credentials objects
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout/admin"

    def create(self, credentials_definition: Credentials, name: Optional[str] = None) -> Union[DtlError, CredentialsReference]:
        """
        Creates the Credentials as specified.

        :param credentials_definition: Credentials Definition to be creates
        :param name: Name to be given to the Credentials to be able to find it later
        :return: string with error message if failed, uuid otherwise
        """
        res = self.http_client.make_authed_request(self.service_uri + "/credentials", HttpMethod.POST, {
            "name": name,
            "credentials": credentials_definition._as_payload()
        })

        if isinstance(res, DtlError):
            return res

        return _credentials_ref_from_payload(res)

    def update(self, credentials_id: UUID, credentials_definition: Credentials,
               name: Optional[str] = None) -> Union[DtlError, CredentialsReference]:
        """
        Updates the given Credentials id with name and credentials

        TODO rework the api so that you can only update the name without the Credentials themselves

        :param credentials_id: id of te Credentials to update
        :param name: if specified, will overwrite current name
        :param credentials_definition: new Credentials definition
        :return:
        """

        body = {}
        if name is not None:
            body["name"] = name

        body["credentials"] = credentials_definition._as_payload()

        res = self.http_client.make_authed_request(
            self.service_uri + "/credentials/" + str(credentials_id),
            HttpMethod.PUT,
            body)

        if isinstance(res, DtlError):
            return res

        return _credentials_ref_from_payload(res)

    def list(self, credential_type: Optional[str] = None, page: int = 1, item_per_page: int = 25) \
            -> Union[DtlError, List[CredentialsReference]]:
        """
        Lists available credentials that Organization has

        :param credential_type: type of the credentials (S3, GCS, Jdbc, etc)
        :param page: page to be retrieved
        :param item_per_page: number of items to be put in a page
        :return: Returns a List of all the available credentials or an error message as a string
        """

        res = self.http_client.make_authed_request(
            self.service_uri +
            f"/credentials?page={page}&size={item_per_page}{'' if credential_type is None else f'&type={credential_type}'}", HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return _parse_list(_credentials_ref_from_payload)(res)

    def delete(self, credentials_id: UUID) -> Union[DtlError, bool]:
        """
        Deletes the given Credentials

        :param credentials_id: id of the credentials to be deleted
        :return: true if successful, false otherwise
        """

        res = self.http_client.make_authed_request(
            self.service_uri + "/credentials/" + str(credentials_id),
            HttpMethod.DELETE
        )

        if isinstance(res, DtlError):
            return res
        else:
            return True

    def share(self, credentials_id: UUID, group_id: UUID) -> Union[DtlError, bool]:
        res = self.http_client.make_authed_request(
            self.service_uri + f"/credentials/{str(credentials_id)}/permissions/groups/{str(group_id)}",
            HttpMethod.PUT)

        if isinstance(res, DtlError):
            return res

        return True
