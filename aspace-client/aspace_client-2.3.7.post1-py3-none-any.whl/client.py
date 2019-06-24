r"""
Contains the ASpaceClient class.
"""

from aspace import base_client
from aspace.client_extensions import (
    record_streams,
    user_management,
    enum_management,
    schema_query,
    jobs,
    top_containers,
)


class ASpaceClient(base_client.BaseASpaceClient):
    """
    Wraps the Session class from the requests package. Extends the 
    functionality of the BaseASpaceClient, by including instances
    of classes that leverage multiple endpoints of the ArchivesSpace
    API.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._streams = record_streams.RecordStreamingService(self)
        self._users = user_management.UserManagementService(self)
        self._enumerations = enum_management.EnumerationManagementService(self)
        self._schemas = schema_query.SchemaQueryingService(self)
        self._jobs = jobs.JobManagementService(self)
        self._top_containers = top_containers.TopContainerManagementService(
            self
        )

    @property
    def streams(self) -> record_streams.RecordStreamingService:
        """

        Returns an instance of the RecordStreamingService class, providing
        methods that allow a more fluent interface for streaming records and
        URIs from ArchivesSpace, via the ArchivesSpace API.

        """
        return self._streams

    @property
    def users(self) -> user_management.UserManagementService:
        """

        Returns an instance of the UserManagementService class, providing
        methods that allow more fluent access to the `/users` endpoint of the
        ArchivesSpace API.

        """
        return self._users

    @property
    def enumerations(self) -> enum_management.EnumerationManagementService:
        """

        Returns an instance of the EnumerationManagementService class,
        providing methods that allow more fluent access to managing
        ArchivesSpace's lists of controlled value.

        """
        return self._enumerations

    @property
    def schemas(self) -> schema_query.SchemaQueryingService:
        """

        Returns an instance of the SchemaQueryingService class, providing
        methods that allow more fluent read access for ArchivesSpace's JSON
        model schemas.

        """
        return self._schemas

    @property
    def jobs(self) -> jobs.JobManagementService:
        """

        Returns an instance of the JobManagementService class, providing
        methods that allow more fluent access to managing ArchivesSpace
        background jobs.

        """
        return self._jobs

    @property
    def top_containers(self) -> top_containers.TopContainerManagementService:
        """

        Returns an instance of the TopContainerManagementService class,
        providing methods that allow more flient access to managing and
        querying top containers and the objects they are linked to.

        """
        return self._top_containers
