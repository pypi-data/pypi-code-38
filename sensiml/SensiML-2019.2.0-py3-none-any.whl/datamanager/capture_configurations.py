import json
from sensiml.datamanager.capture_configuration import CaptureConfiguration
import sensiml.base.utility as utility


class CaptureConfigurationExistsError(Exception):
    """Base class for an Capture exists error"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class CaptureConfigurations():
    """Base class for a collection of Captures."""

    def __init__(self, connection, project):
        self._connection = connection
        self._project = project

    def create_capture_configuration(self, name, configuration, uuid=None):
        """Creates an capture object from the given filename and filepath.

            Args:
                name (str): desired name of the file on the server
                configuration (dict): configuration file
                uuid (str): Specify the uuid this configuration will be created with

            Returns:
                capture_configuration object

            Raises:
                CaptureClonfigurationExistsError, if the Capture already exists on the server
        """
        data = {
            'connection': self._connection,
            'project': self._project,
            'name': name,
        }

        if self.get_capture_configuration_by_name(name) is not None:
            raise CaptureConfigurationExistsError(
                "capture configuration {0} already exists.".format(name))
        else:
            instance = CaptureConfiguration.initialize_from_dict(data)
            instance.configuration = configuration
            instance.uuid = uuid
            instance.insert()

        return instance

    def build_capture_list(self):
        """Populates the function_list property from the server."""
        capture_list = {}

        response = self.get_capture_configurations()
        for capture_configuration in response:
            capture_list[capture_configuration.name] = capture_configuration

        return capture_list

    def get_capture_configuration_by_name(self, name):
        """Gets an capture configuration object from the server using its name property.

            Args:
                name (str): the capture configuration's name

            Returns:
                capture configuration  object or None if it does not exist
        """
        capture_list = self.get_capture_configurations()
        for capture in capture_list:
            if capture.name == name:
                return capture
        return None

    def __getitem__(self, key):
        if type(key) == str:
            return self.get_capture_configuration_by_filename(key)
        else:
            return self.get_capture_configurations()[key]

    def _new_capture_configuration_from_dict(self, data):
        """Creates a new capture using the dictionary.

            Args:
                data (dict): dictionary of capture properties

            Returns:
                capture configuration object
        """
        data.update({
            'connection': self._connection,
            'project': self._project
        })
        return CaptureConfiguration.initialize_from_dict(data)

    def get_capture_configurations(self):
        """Gets all capture configurations from the server.

            Returns:
                list of capture configurations for the project
        """
        # Query the server and get the json
        url = 'project/{0}/captureconfiguration/'.format(self._project.uuid)
        response = self._connection.request('get', url,)
        response_data, err = utility.check_server_response(response)

        # Populate each capture from the server
        data = []
        if err is False:
            for params in response_data:
                data.append(self._new_capture_configuration_from_dict(params))

        return data
