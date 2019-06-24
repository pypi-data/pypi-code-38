from typing import Optional, Union, List
from datalogue.clients.http import _HttpClient, HttpMethod
from datalogue.models.ontology import Ontology
from datalogue.utils import _parse_list
from datalogue.errors import DtlError
from uuid import UUID


class _OntologyClient:
    """
    Client to interact with the ontology
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/yggy"

    def create(self, ontology: Ontology) -> Union[DtlError, Ontology]:
        res = self.http_client.make_authed_request(self.service_uri + '/ontology/import', HttpMethod.POST, body=Ontology.as_payload(ontology))

        if isinstance(res, DtlError):
            return res
            
        return Ontology.from_payload(res)

    def get(self, ontology_id: UUID) -> Union[DtlError, Ontology]:
        """
        Get :class:`Ontology` object given ontology_id
        :return: :class:`Ontology` object
        """
        res = self.http_client.make_authed_request(self.service_uri + f'/ontology/{str(ontology_id)}', HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return Ontology.from_payload(res)

    def update(self, ontology: Ontology) -> Union[DtlError, Ontology]:
        res = self.http_client.make_authed_request(self.service_uri + f'/ontology/{str(ontology.ontology_id)}', HttpMethod.PUT, body=Ontology.as_payload(ontology))

        if isinstance(res, DtlError):
            return res

        return Ontology.from_payload(res)

    def delete(self, ontology_id: UUID) -> Union[DtlError, bool]:
        """
        Delete :class:`Ontology` based on the given ontology_id
        :return: True if successful, else returns :class:`DtlError`
        """
        res = self.http_client.make_authed_request(self.service_uri + f'/ontology/{str(ontology_id)}', HttpMethod.DELETE)
        if isinstance(res, DtlError):
            return res
        else:
            return True

    def list(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[Ontology]]:
        """
        List the ontologies

        TODO Pagination

        :param page: page to be retrieved
        :param item_per_page: number of items to be put in a page
        :return: Returns a List of all the available Ontologies or an error message as a string

        """
        res = self.http_client.make_authed_request(self.service_uri + f'/ontologies', HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return _parse_list(Ontology.from_payload)(res)
