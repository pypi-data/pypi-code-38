__version__ = "0.0.1"

from minty import Base
from minty.exceptions import ConfigurationConflict

from .swiftwrapper import SwiftWrapper

DEFAULT_CHUNK_SIZE = 1024 * 1024  # 1 megabyte


class SwiftInfrastructure(Base):
    """Infrastructure Class for OpenStack/Swift Connection."""

    def __call__(self, config):
        """Create a new Swift connection using the specified configuration

        :param config: The configuration params necessary to connect to a swift container.
        :return: A Swift handle for a bucket on a connection to an OpenStack server.
        :rtype: SwiftWrapper
        """

        try:
            container_name = config["storage_bucket"]
        except KeyError:
            try:
                container_name = config["instance_uuid"]
            except KeyError as k:
                raise ConfigurationConflict(
                    "No container name specified for Swift configuration"
                ) from k

        try:
            filestore_config = config["filestore"]
            if type(filestore_config) is not list:
                filestore_config = [filestore_config]
        except KeyError as error:
            raise ConfigurationConflict(
                "No file store configuration specified for openstack/swift"
            ) from error

        return SwiftWrapper(
            filestore_config=filestore_config,
            container_name=container_name,
            segment_size=config.get("chunk_size", DEFAULT_CHUNK_SIZE),
        )
