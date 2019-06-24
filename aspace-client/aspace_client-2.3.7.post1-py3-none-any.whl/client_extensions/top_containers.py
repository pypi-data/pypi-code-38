import re
from typing import Union, Iterable, List
import enum
import json

from aspace import base_client
from aspace import enums
from aspace import constants
from aspace import util

VALID_TOP_CONTAINER_URI_RE = re.compile(
    constants.VALID_TOP_CONTAINER_URI_REGEX)


class TopContainerManagementService(object):
    """
    Contains methods that can be used to extend the functionality of the API,
    allowing top container records to be more easily managed.
    """

    def __init__(self, client: base_client.BaseASpaceClient):
        self._client = client

    @staticmethod
    def is_valid_top_container_uri(top_container_uri: str) -> bool:
        """
        Returns true if `top_container_uri` matches
        `aspace.constants.VALID_TOP_CONTAINER_URI_REGEX`.
        """
        match = VALID_TOP_CONTAINER_URI_RE.match(top_container_uri)
        return bool(match)

    def get(self, tc_uri: str) -> dict:
        """
        Gets a top container using a top container URI.

        :tc_uri: The uri of the top container.
        """
        return self._client.get(tc_uri).json()

    def linked_record_uris(self, top_container: Union[str, dict], 
                           linked_record_type: str = None,
                           ) -> List[str]:
        """
        Returns a list of all of the URIs for the records that are linked to
        the specified top container.

        :top_container: The specific top container to pull record URIs for. Can
        be specified as either a top container URI, or a Top Container
        JSONModel object.

        :record_type: The record type to query. Defaults to all types if not
        specified.
        """

        if isinstance(top_container, str):
            match = VALID_TOP_CONTAINER_URI_RE.match(top_container)
            repo_uri = match.group(1)
            tc_uri = match.group(0)
        else:
            repo_uri = top_container['repository']['ref']
            tc_uri = top_container['uri']

        page_num = 0
        linked_record_uris = set()

        while True:
            page_num += 1
            page_resp = self._client.post(
                '{}/search'.format(repo_uri),
                params={
                    'page': page_num,
                    'type': linked_record_type,
                    'filter': json.dumps({
                        'query': {
                            'jsonmodel_type': 'field_query', 
                            'field': 'top_container_uri_u_sstr',
                            'value': tc_uri,
                        }
                    })
                }
            )

            assert page_resp.ok, page_resp.text
            results = page_resp.json()['results']

            if not any(results):
                return list(linked_record_uris)

            for result in results:
                linked_record_uris.add(result['uri'])

    def linked_records(self, top_container: Union[str, dict], 
                       linked_record_type: str = None,
                       ) -> List[str]:
        """
        Returns a list of all of the records that are linked to the specified
        top container.

        :top_container: The specific top container to pull records for. Can
        be specified as either a top container URI, or a Top Container
        JSONModel object.

        :record_type: The record type to query. Defaults to all types if not
        specified.
        """
        return [
            self.get(_uri)
            for _uri in
            self.linked_record_uris(
                top_container,
                linked_record_type=linked_record_type,
            )
        ]
