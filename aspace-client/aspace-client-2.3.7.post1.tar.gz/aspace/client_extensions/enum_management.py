import re
from typing import Union, Iterable
import enum

from aspace import base_client
from aspace import enums
from aspace import constants
from aspace import util

VALID_ENUM_URI_RE = re.compile(constants.VALID_ENUM_URI_REGEX)


class EnumerationManagementService(object):
    """
    Contains methods that can be used to perform batch updates and formatting
    for enumerations.
    """

    def __init__(self, client: base_client.BaseASpaceClient):
        self._client = client

    def get_all(self) -> list:
        """
        Dowloads a list of all of the controlled value lists.
        """
        return self._client.get('/config/enumerations').json()

    @staticmethod
    def enumeration_uri(enum_id: Union[int, enums.Enumeration]) -> str:
        """
        Returns a uri of the form `'/config/enumerations/%d'`
        """
        if isinstance(enum_id, enums.Enumeration):
            return '/config/enumerations/%d' % enum_id.value

        if isinstance(enum_id, int):
            return '/config/enumerations/%d' % enum_id

        raise 'Invalid value type for parameter enum_id: %s' % repr(enum_id)

    @staticmethod
    def is_valid_enumeration_uri(enum_uri: str) -> bool:
        """
        Returns true if enum_uri matches
        `aspace.constants.VALID_ENUM_URI_REGEX`.
        """
        match = VALID_ENUM_URI_RE.match(enum_uri)
        return bool(match)

    def get_by_name(self, enum_name: str) -> dict:
        """
        GETs an enumeration using the `/config/enumerations/names/:enum_name`
        endpoint.
        """
        resp = self._client.get('/config/enumerations/names/%s' % enum_name)
        return resp.json()

    def get(self, enum_id: Union[str, int, enums.Enumeration]
            ) -> dict:
        """
        Gets an enumeration (controlled value list) using the enumeration's
        name, uri, id, or the enumeration specified in the enums module.
        """
        if isinstance(enum_id, (int, enums.Enumeration)):
            uri = self.enumeration_uri(enum_id)
            return self._client.get(uri).json()

        if isinstance(enum_id, str):
            if self.is_valid_enumeration_uri(enum_id):
                resp = self._client.get(enum_id)
                return resp.json()
            return self.get_by_name(enum_id)

        raise Exception(
            'Invalid value type for parameter enum_id: {}'.format(
                repr(enum_id)
            )
        )

    def sort_values(self, enum_id: Union[str, int, enums.Enumeration]):
        """
        Sorts all of the values of an enumeration based on their value.
        Does not return a value, but will fail if any of the HTTP requests
        fail.
        """

        enumeration = self.get(enum_id)
        sorted_enum_vals = sorted(
            enumeration['enumeration_values'],
            key=lambda ev: ev['value']
        )

        for index, enum_val in enumerate(sorted_enum_vals):
            resp = self._client.post(
                '%s/position' % enum_val['uri'],
                params={'position': index}
            )
            assert resp.ok, resp.text

    @staticmethod
    def convert_to_enumeration_value(value: str) -> str:
        """
        Alias for `util.convert_to_enumeration_value`
        """
        return util.convert_to_enumeration_value(value)

    def update_enumeration(self, enum_id: Union[str, int, enums.Enumeration],
                           new_values: Iterable, cleanup_new_values=True,
                           reorder_enumeration=False):
        """
        Updates the specified enumeration using distinct values from the
        specified iterable of string. Creates a `set` for the values currently
        associated with the enumeration, and uploads a list of those results,
        so there are no issues with duplicates.

        Optionally, you can specify whether or not the new values are run
        through the convert_to_enumeration_value function, and whether the
        client should re-order the enumeration after updating.
        """

        new_enum_values = {_ for _ in new_values}

        if cleanup_new_values:
            new_enum_values = {
                self.convert_to_enumeration_value(value)
                for value in new_enum_values
            }

        enumeration = self.get(enum_id)
        enumeration['values'] = list(
            new_enum_values.union(enumeration['values'])
        )

        update_resp = self._client.post(enumeration['uri'], json=enumeration)
        assert update_resp.ok, update_resp.text

        if reorder_enumeration:
            self.sort_values(enum_id)

    def merge(self, enum_id: Union[str, int, enums.Enumeration],
              from_value: str, to_value: str) -> dict:
        """
        Uses the `/config/enumerations/migration` endpoint to merge 2 values
        under an enumeration (controlled value list). All of the records that
        currently use the "from_value" will be switched to "to_value", and the
        "from_value" will be deleted.

        The enum_id parameter can be specified as a uri, id, or by using the
        Enumeration enum, from the enums module.

        The from_value and to_value parameters should be specified as strings
        that exactly match values of the specified enumeration.

        Returns the JSON response from the API that is returned when a merge
        request is attempted.
        """

        enum_uri = (
            self.enumeration_uri(enum_id)
            if isinstance(enum_id, (enums.Enumeration, int)) else
            enum_id
            if self.is_valid_enumeration_uri(enum_id) else
            None
        )

        assert enum_uri, (
            'Invalid value for parameter enum_id: %s' % repr(enum_id)
        )

        resp = self._client.post(
            '/config/enumerations/migration',
            json={
                'enum_uri': enum_uri,
                'from': from_value,
                'to': to_value
            }
        )

        return resp.json()
