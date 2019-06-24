import re

from aspace import constants, base_client


VALID_REPO_URI_RE = re.compile(constants.VALID_REPO_URI_REGEX)


class RecordStreamingService(object):
    """
    Contains methods that can be used to stream all records from an instance
    of ArchivesSpace of a particular record type.
    """

    def __init__(self, client: base_client.BaseASpaceClient):
        self._client = client

    def repositories(self):
        """
        Streams all repository records from the ArchivesSpace instance.
        """
        return (
            repo for repo in
            self._client.get('/repositories').json()
        )

    def _get_repo_uris(self, repository_uris: list = None):
        """
        Returns a list of valid repository URIs in the ArchivesSpace
        instance, or raises an error.
        """
        repo_uris = (
            repository_uris
            if repository_uris is not None else
            [
                repo['uri']
                for repo in
                self.repositories()
            ]
        )

        def valid_repo_uri(repo_uri):
            return (
                (type(repo_uri) is str) and VALID_REPO_URI_RE.match(repo_uri)
            )

        assert all(map(valid_repo_uri, repo_uris)), (
            'All repository URIs must be strings and must be of the form: %s' %
            constants.VALID_REPO_URI_REGEX
        )

        return [uri.strip('/') for uri in repo_uris]

    def uris(self, plural_record_type: str,) -> iter:
        """
        Streams all URIs of a specific type from the ArchivesSpace instance,
        assuming that a `/:plural_record_type` endpoint exists, and supports
        the `all_ids=true` parameter.

        :plural_record_type: The desired record type, formatted as it
        appears in the documentation for the related API endpoint.
        """
        plural_record_type = plural_record_type.strip('/')

        return (
            '/%s/%d' % (plural_record_type, rec_id)

            for rec_id in self._client.get(
                '/%s?all_ids=true' % plural_record_type
            ).json()
        )

    def repository_relative_uris(self, plural_record_type: str,
                                 repository_uris: list = None,
                                 endpoint_extension: str = None,):
        """
        Streams all URIs of a specific type from the ArchivesSpace
        instance, assuming that a
        `/repositories/:repo_id/:plural_record_type` endpoint
        exists, and supports the `all_ids=true` parameter.

        :plural_record_type: The desired record type, formatted as it
        appears in the documentation for the related API endpoint.

        :repository_uris: Optional list of repository URIs, which limits the
        records that are downloaded. If omitted, records will be pulled from
        all repositories.

        :endpoint_extension: Optional extension to put at the end of each
        record URI. For example, specifying 'resources' and 
        endpoint_extension='tree' supports the
        '/repositories/:repo_id/resources/:id/tree' endpoint.
        """
        plural_record_type = plural_record_type.strip('/')

        return (
            '%s/%s/%d%s' %
            (
                repo_uri,
                plural_record_type,
                rec_id,
                '' if endpoint_extension is None else
                '/%s' % endpoint_extension.strip('/'),
            )

            for repo_uri in self._get_repo_uris(repository_uris)

            for rec_id in self._client.get(
                '%s/%s?all_ids=true' %
                (repo_uri, plural_record_type)
            ).json()
        )

    def records(self, plural_record_type: str,):
        """
        Streams all records of a specific type from the ArchivesSpace instance,
        assuming that a `/:plural_record_type` endpoint exists, and supports
        the `all_ids=true` parameter.

        :plural_record_type: The desired record type, formatted as it
        appears in the documentation for the related API endpoint.
        """
        return (
            self._client.get(uri).json()
            for uri in self.uris(plural_record_type)
        )

    def repository_relative_records(self, plural_record_type: str,
                                    repository_uris: list = None,
                                    endpoint_extension: str = None,):
        """
        Streams all records of a specific type from the ArchivesSpace 
        instance, assuming that a 
        `/repositories/:repo_id/:plural_record_type` endpoint
        exists, and supports the `all_ids=true` parameter.

        :plural_record_type: The desired record type, formatted as it
        appears in the documentation for the related API endpoint.

        :repository_uris: Optional list of repository URIs, which limits the
        records that are downloaded. If omitted, records will be pulled from
        all repositories.

        :endpoint_extension: Optional extension to put at the end of each
        record URI. For example, specifying 'resources' and 
        endpoint_extension='tree' supports the
        '/repositories/:repo_id/resources/:id/tree' endpoint.
        """

        return (
            self._client.get(uri).json()

            for uri in self.repository_relative_uris(
                plural_record_type,
                repository_uris=repository_uris,
                endpoint_extension=endpoint_extension,
            )
        )

    def resources(self, repository_uris: list = None, 
                  endpoint_extension: str = None,):
        """
        Streams all resources from the ArchivesSpace instance.

        :repository_uris: Optional list of repository URIs, which limits the
        records that are downloaded. If omitted, records will be pulled from
        all repositories.

        :endpoint_extension: Optional extension to put at the end of each
        record URI. For example, adding `'tree/root'` to generate tree uris
        like `/repositories/:repo_id/resources/:id/tree/root`
        """

        return self.repository_relative_records(
            plural_record_type='resources',
            repository_uris=repository_uris,
            endpoint_extension=endpoint_extension,
        )

    def resource_trees(self, repository_uris: list = None,
                       large_tree_extension: str = None):
        """
        Streams all resource trees from the ArchivesSpace instance, using the
        `/repositories/:repo_id/resources/:id/tree` endpoint. The base
        endpoint is considered deprecated (v2.0.0), but this method has
        support for pulling from the large-trees endpoints.

        :repository_uris: Optional list of repository URIs, which limits the
        records that are downloaded. If omitted, records will be pulled from
        all repositories.

        :large_tree_extension: Optional extension on the tree endpoint. If
        specified, the text is added to the end of the tree uris:
        `/repositories/:repo_id/resources/:id/tree/{tree_ext...}`
        """

        endpoint_extension = 'tree'

        if large_tree_extension:
            endpoint_extension = '%s/%s' % (
                endpoint_extension,
                large_tree_extension.lstrip('/ ')
            )

        return self.resources(
            repository_uris=repository_uris,
            endpoint_extension=endpoint_extension
        )

    def resource_ordered_records(self, repository_uris: list = None,):
        """
        Streams all resource ordered_records from the ArchivesSpace instance.

        :repository_uris: Optional list of repository URIs, which limits the
        records that are downloaded. If omitted, records will be pulled from
        all repositories.
        """

        return self.resources(
            repository_uris=repository_uris,
            endpoint_extension='ordered_records',
        )

    def accessions(self, repository_uris: list = None,):
        """
        Streams all accession records from the ArchivesSpace instance.

        :repository_uris: Optional list of repository URIs, which limits the
        records that are downloaded. If omitted, records will be pulled from
        all repositories.
        """

        return self.repository_relative_records(
            plural_record_type='accessions',
            repository_uris=repository_uris,
        )

    def archival_objects(self, repository_uris: list = None,):
        """
        Streams all archival object records from the ArchivesSpace instance.

        :repository_uris: Optional list of repository URIs, which limits the
        records that are downloaded. If omitted, records will be pulled from
        all repositories.
        """

        return self.repository_relative_records(
            plural_record_type='archival_objects',
            repository_uris=repository_uris,
        )

    def users(self):
        """
        Streams all user records from the ArchivesSpace instance.
        """
        return self.records('users')

    def people(self):
        """
        Streams all person agents from the ArchivesSpace instance.
        """
        return self.records('agents/people')

    def corporate_entities(self):
        """
        Streams all corporate entity agents from the ArchivesSpace instance.
        """
        return self.records('agents/corporate_entities')

    def families(self):
        """
        Streams all family agents from the ArchivesSpace instance.
        """
        return self.records('agents/families')

    def software(self):
        """
        Streams all software agents from the ArchivesSpace instance.
        """
        return self.records('agents/software')

    def all_agents(self):
        """
        Streams all agent records from the ArchivesSpace instance.
        """

        return (
            record

            for stream in [
                self.people,
                self.corporate_entities,
                self.families,
                self.software,
            ]

            for record in stream()
        )

    def top_containers(self, repository_uris: list = None,):
        """
        Streams all top_container records from the ArchivesSpace instance.

        :repository_uris: Optional list of repository URIs, which limits the
        records that are downloaded. If omitted, records will be pulled from
        all repositories.
        """

        return self.repository_relative_records(
            plural_record_type='top_containers',
            repository_uris=repository_uris,
        )

    def subjects(self):
        return self.records(
            plural_record_type='subjects'
        )
