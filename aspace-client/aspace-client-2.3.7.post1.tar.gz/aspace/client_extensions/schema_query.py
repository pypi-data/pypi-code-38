import re

from aspace import constants, base_client


class SchemaQueryingService(object):
    """
    Contains methods that can be used to pull information from the `/schemas`
    ArchivesSpace endpoint.
    """

    def __init__(self, client: base_client.BaseASpaceClient):
        self._client = client
        self._schema_cache = {}

    def get_schema(self, schema_name: str) -> dict:
        """
        Gets the schema for the specified schema_name. The schema name must be
        singular. Gets the object from `/schemas/:schema_name`. Any issues
        with the format of the parameter will be handled via an assertion on
        the response from the API.

        Caches the result if a schema is found.
        """
        
        if schema_name in self._schema_cache:
            return self._schema_cache[schema_name]
        
        resp = self._client.get('/schemas/{}'.format(schema_name))
        assert resp.ok, resp.text

        schema = resp.json()
        self._schema_cache[schema_name] = schema

        return schema
