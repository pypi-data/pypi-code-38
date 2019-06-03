import hashlib
import tempfile
from functools import partial

from keystoneauth1 import session
from keystoneauth1.identity import v3
from magic import Magic
from swiftclient import Connection

from minty import Base
from minty.exceptions import ConfigurationConflict


class SwiftWrapper(Base):
    """A SwiftWrapper for file actions(upload/download/remove) in Swift"""

    def __init__(
        self, filestore_config: list, container_name: str, segment_size: int
    ):
        """A swift wrapper handle to upload files to openstack-swift server in chunks.
        Returns a dictionary of the uploaded file data:  uuid, md5, file_size, mime_type, storage_location.

        Constructor for swift wrapper. It needs a connection, container name and segment_size.
        Default segments size `DEFAULT_CHUNK_SIZE` in SwiftInfrastructure.

        :param filestore_config: File store config params used to make the connection for upload.
        :type filestore_config: list
        :param container_name: The name of the container to connect to
        :type container_name: str
        :param segment_size: The size of the segment/chunk size of the file to send to swift when uploading
        :type segment_size: int
        """

        self.filestore_config = filestore_config
        self.segment_size = segment_size
        self.container_name = container_name

    def upload(self, file_handle, uuid):
        """Upload file to Swift in `segment_size` chunks.

        Reads the file handle, and uploads chunks to swift, while also
        calculating the MD5 of the file and determining its MIME type.

        :param file_handle: File-like object
        :param uuid: The uuid of the file te be handled
        :type uuid: uuid4
        :return: A dictionary of the data/metadata of the uploaded file into
            swift. Contains the keys: uuid, md5, file_size, mime_type, storage_location.
        :rtype: dict
        """
        try:
            connection = self._connect_to_swift(self.filestore_config[0])
        except IndexError as error:
            raise ConfigurationConflict(
                "No config found for Swift configuration"
            ) from error

        try:
            storage_location = self.filestore_config[0]["name"]
        except KeyError as error:
            raise ConfigurationConflict(
                "No name found for Swift configuration"
            ) from error

        hash_md5 = hashlib.md5()
        segment_count = 1
        total_size = 0

        timer = self.statsd.get_timer("file_upload")
        with timer.time(
            f"total"
        ), tempfile.NamedTemporaryFile() as temporary_file:
            for chunk in iter(
                partial(file_handle.read, self.segment_size), b""
            ):
                segment_name = "%s/%08d" % (uuid, segment_count)
                hash_md5.update(chunk)
                chunk_size = len(chunk)

                self._upload_chunk(
                    connection=connection,
                    segment_name=segment_name,
                    chunk=chunk,
                    chunk_size=chunk_size,
                )

                temporary_file.write(chunk)

                segment_count += 1
                total_size += chunk_size

            temporary_file.flush()
            mime_type = Magic(mime=True).from_file(temporary_file.name)

        self._finish(connection=connection, uuid=uuid, size=total_size)

        return {
            "uuid": uuid,
            "md5": hash_md5.hexdigest(),
            "size": total_size,
            "mime_type": mime_type,
            "storage_location": storage_location,
        }

    def _upload_chunk(self, connection, segment_name, chunk, chunk_size):
        """Uploads the file chunk to Swift.

        Creates a named temp file out of the chunks. Checks for mime type of the temp file.
        After finish sets attributes like size, mime type etc...

        :param connection: The connection which the chunk upload is taking place.
        :type connection: Connection
        :param segment_name: The segment name to be uploaded in the format of uuid/8-digit-number with the segment step
        that the file is being read
        :type segment_name: str
        :param chunk: The read block of file per step per chunk size
        :param chunk_size: the size of the chunk to read from the file
        :type chunk_size: int
        :return: void
        """
        timer = self.statsd.get_timer("file_chunk_upload")
        with timer.time(f"document.chunk.upload"):
            connection.put_object(
                container=self.container_name,
                obj=segment_name,
                contents=chunk,
                content_length=chunk_size,
            )

    def _finish(self, connection, uuid, size):
        """Send a request with the x_manifest_header and an empty content/body to swift.
        Needed to commit/finish the file chunks upload.

        :param connection: The connection to perform the finish chunk upload.
        :type connection: Connection
        :param uuid: The provided uuid to finish the upload.
        :type uuid: str uuid4()
        :return: void
        """
        obj_manifest_header = {
            "x-object-manifest": f"{self.container_name}/{uuid}"
        }
        connection.put_object(
            container=self.container_name,
            obj=str(uuid),
            contents=None,
            content_length=size,
            headers=obj_manifest_header,
        )

    def _connect_to_swift(self, file_store_config: dict):
        """Returns a connection to Swift based on the auth version.
        Supports V3, V2 and V1(Legacy)

        :param file_store_config: Configuration params for a file storage.
        :type file_store_config: dict
        :return: Connection V1 or V2 or V3 instance depending on the config params provided.
        :rtype: Connection
        """
        if file_store_config.get("auth") is None:
            raise ConfigurationConflict("Authentication params are missing")

        if file_store_config.get("auth_version") is None:
            raise ConfigurationConflict(
                "No auth_version specified for Swift configuration"
            )

        auth_config = {**file_store_config["auth"]}
        auth_config["timeout"] = int(auth_config.get("timeout", 60))
        auth_version = file_store_config["auth_version"]
        if auth_version == "v3":
            return self._connect_to_swift_v3(**auth_config, auth_version="3")
        elif auth_version in ["v1", "v2"]:
            # authentication version 2 and 1
            # accessing second index of string auth_version to get the version number
            auth_version = auth_version[1]
            return self._connect_to_swift_legacy_auth(
                **auth_config, auth_version=auth_version
            )
        else:
            raise ConfigurationConflict(
                f"Unsupported auth_version: '{auth_version}'"
            )

    def _connect_to_swift_v3(
        self,
        auth_url,
        username,
        password,
        auth_version=None,
        user_domain_name=None,
        project_name=None,
        project_domain_name=None,
        timeout=60,
    ) -> Connection:
        """A V3 auth type with keystone session to connect to swift.

        :param auth_url:
        :param username:
        :param password:
        :param user_domain_name:
        :param project_name:
        :param project_domain_name:
        :param timeout:
        :return  A connection Instance of V3 swift auth.
        :rtype: Connection
        """
        auth = v3.Password(
            auth_url=auth_url,
            username=username,
            password=password,
            user_domain_name=user_domain_name,
            project_name=project_name,
            project_domain_name=project_domain_name,
        )

        keystone_session = session.Session(auth=auth)

        return Connection(
            session=keystone_session,
            auth_version=auth_version,
            timeout=timeout,
        )

    def _connect_to_swift_legacy_auth(
        self,
        auth_url,
        username,
        password,
        auth_version=None,
        tenant_name=None,
        timeout=60,
    ) -> Connection:
        """Support for  auth type V1 & V2 to connect to swift.

        :param auth_url:
        :param username:
        :param password:
        :param auth_version:
        :param tenant_name:
        :param timeout:
        :return: A connection Instance of Legacy(V1) or V2 swift auth.
        :rtype: Connection
        """

        return Connection(
            authurl=auth_url,
            user=username,
            key=password,
            auth_version=auth_version,
            tenant_name=tenant_name,
            timeout=timeout,
        )
