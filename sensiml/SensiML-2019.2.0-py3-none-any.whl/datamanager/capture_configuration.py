import logging
import time
from requests.exceptions import *
import datetime
import sensiml.base.utility as utility
import pandas as pd
from pandas import DataFrame
import os.path

logger = logging.getLogger(__name__)


class CaptureConfiguration(object):
    """Base class for an Capture."""

    def __init__(self, connection, project, name='', uuid='', configuration=None, created_at=None, **kwargs):
        """Initialize an Capture instance."""
        self._connection = connection
        self._project = project
        self._uuid = uuid
        self._configuration = configuration
        self._name = name
        self._created_at = None

        self.created_at = created_at

    @property
    def uuid(self):
        """Auto generated unique identifier for the Capture object"""
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        """Auto generated unique identifier for the Capture object"""
        self._uuid = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def created_at(self):
        """Date of the Pipeline creation"""
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        self._created_at = datetime.datetime.strptime(
            value[:-6], '%Y-%m-%dT%H:%M:%S.%f')

    @property
    def configuration(self):
        """The local or server path to the Capture file data"""
        return self._configuration

    @configuration.setter
    def configuration(self, value):
        self._configuration = value

    def insert(self, asynchronous=False):
        """Calls the REST API to insert a new Capture."""
        url = 'project/{0}/captureconfiguration/'.format(self._project.uuid)
        data = {'name': self.name, 'configuration': self.configuration}
        if self.uuid:
            data['uuid'] = self.uuid
        response = self._connection.request('post', url, data)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self._uuid = response_data['uuid']

    def update(self):
        """Calls the REST API to update the capture."""
        url = 'project/{0}/captureconfiguration/{1}/'.format(
            self._project.uuid, self._uuid)

        data = {'name': self.name}
        if self.configuration is not None:
            data['configuration'] = self.configuration

        response = self._connection.request('put', url, data)
        response_data, err = utility.check_server_response(response)

    def delete(self):
        """Calls the REST API to delete the capture from the server."""
        url = 'project/{0}/captureconfiguration/{1}/'.format(
            self._project.uuid, self._uuid)
        response = self._connection.request('delete', url,)
        response_data, err = utility.check_server_response(response)

    def refresh(self):
        """Calls the REST API and self populates properties from the server."""
        url = 'project/{0}/captureconfiguration/{1}/'.format(
            self._project.uuid, self._uuid)
        response = self._connection.request('get', url,)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.name = response_data['name']
            self.configuration = response_data['configuration']

    @classmethod
    def initialize_from_dict(cls, data):
        """Reads a dictionary or properties and populates a single capture.

            Args:
                capture_dict (dict): contains the capture's 'name' property

            Returns:
                capture object
        """
        assert isinstance(data, dict)

        return CaptureConfiguration(**data)
