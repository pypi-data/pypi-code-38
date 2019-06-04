import json
from sensiml.datamanager.metadata import Metadata
import sensiml.base.utility as utility


class MetadataExistsError(Exception):
    """Base class for the metadata exists error"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class MetadataSet():
    """Base class for a collection of metadata"""

    def __init__(self, connection, project, capture):
        self._connection = connection
        self._project = project
        self._capture = capture

    def __getitem__(self, name):
        metadata = self.get_metadata_by_name(name)
        if metadata is not None:
            return metadata.get_metadata_value()
        else:
            return None

    def __setitem__(self, name, value):
        metadata = self.get_metadata_by_name(name)
        if metadata is not None:
            metadata.set_metadata_value(value)
            metadata.update()
        else:
            self.create_metadata(name, value)

    def create_metadata(self, name, capture):
        """Creates a metadata object using its name and capture properties.

            Args:
                name (str): name of the metadata object
                capture (capture): parent capture of the metadata
        """
        # TODO: This looks odd with capture having a _metadata attribute; make sure this is being unit tested
        if self.get_metadata_by_name(name) is not None:
            raise MetadataExistsError(
                "Metadata {0} already exists.".format(name))
        else:
            self._capture = capture
            self._capture.await_ready()
            metadata = self.new_metadata()
            metadata.name = name
            metadata.new_value = capture._metadata.new_value
            metadata.insert()
            return  # metadata

    def get_metadata_by_name(self, name):
        """Gets one metadata object by the name property.

            Args:
                name (str)

            Returns:
                metadata object or None

            Note:
                If more than one metadata of the same name exist for the capture, this will only return one of them
                at random.
        """
        metadata_list = self.get_metadataset()
        for metadata in metadata_list:
            if metadata.name == name:
                return metadata
        return None

    def new_metadata(self):
        """Initializes a new metadata object locally but does not insert it.

            Returns:
                metadata object
        """
        metadata = Metadata(self._connection, self._project, self._capture)
        return metadata

    def _new_metadata_from_dict(self, dict):
        """Creates a new metadata from data in the dictionary.

            Args:
                dict (dict): contains metadata properties uuid, name, type, value,

            Returns:
                metadata object

        """
        metadata = Metadata(self._connection, self._project, self._capture)
        metadata.initialize_from_dict(dict)
        return metadata

    def get_metadataset(self):
        """Gets all of the capture's metadata objects in a list.

            Returns:
                list[metadata]
        """
        # Query the server and get the json
        url = 'v2/project/{0}/capture/{1}/metadata-relationship/'.format(
            self._project.uuid, self._capture.uuid)
        response = self._connection.request('get', url,)
        try:
            response_data, err = utility.check_server_response(response)
        except ValueError:
            print(response)

        # Populate each metadata from the server
        metadataset = []
        if err is False:
            try:
                for metadata_params in response_data:
                    metadataset.append(
                        self._new_metadata_from_dict(metadata_params))
            except:
                pass
        return metadataset
