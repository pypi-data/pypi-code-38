##################################################################################
#  SENSIML CONFIDENTIAL                                                          #
#                                                                                #
#  Copyright (c) 2017  SensiML Corporation.                                      #
#                                                                                #
#  The source code contained or  described  herein and all documents related     #
#  to the  source  code ("Material")  are  owned by SensiML Corporation or its   #
#  suppliers or licensors. Title to the Material remains with SensiML Corpora-   #
#  tion  or  its  suppliers  and  licensors. The Material may contain trade      #
#  secrets and proprietary and confidential information of SensiML Corporation   #
#  and its suppliers and licensors, and is protected by worldwide copyright      #
#  and trade secret laws and treaty provisions. No part of the Material may      #
#  be used,  copied,  reproduced,  modified,  published,  uploaded,  posted,     #
#  transmitted, distributed,  or disclosed in any way without SensiML's prior    #
#  express written permission.                                                   #
#                                                                                #
#  No license under any patent, copyright,trade secret or other intellectual     #
#  property  right  is  granted  to  or  conferred upon you by disclosure or     #
#  delivery of the Materials, either expressly, by implication,  inducement,     #
#  estoppel or otherwise.Any license under such intellectual property rights     #
#  must be express and approved by SensiML in writing.                           #
#                                                                                #
#  Unless otherwise agreed by SensiML in writing, you may not remove or alter    #
#  this notice or any other notice embedded in Materials by SensiML or SensiML's #
#  suppliers or licensors in any way.                                            #
#                                                                                #
##################################################################################
import logging
import time
from requests.exceptions import *
import sensiml.base.utility as utility
from sensiml.datamanager.errors import CaptureUploadFailureError
from sensiml.datamanager.metadataset import MetadataSet
from sensiml.datamanager.labelset import LabelSet
import pandas as pd
from pandas import DataFrame
import os.path

EXCEPTION_STATES = frozenset(['FAILURE', 'RETRY', 'REVOKED'])

# Custom ready states because sync or nonexistent task state is set to NONE
READY_STATES = frozenset(['FAILURE', 'REVOKED', 'SUCCESS', None])

# Custom unready states because celery's PENDING state is unreliable
UNREADY_STATES = frozenset(['STARTED', 'RECEIVED', 'RETRY', 'SENT'])


logger = logging.getLogger(__name__)


class CaptureTaskFailedError(Exception):
    """Raised if Capture task failed"""


class Capture(object):
    """Base class for an Capture."""

    def __init__(self, connection, project, filename='', path='', uuid='', capture_configuration_uuid=None, capture_info=None, **kwargs):
        """Initialize an Capture instance."""
        self._connection = connection
        self._project = project
        self._filename = filename
        self._path = path
        self._uuid = uuid
        self._capture_info = capture_info
        self._metadata = MetadataSet(self._connection, self._project, self)
        self._labels = LabelSet(self._connection, self._project, self)

    @property
    def uuid(self):
        """Auto generated unique identifier for the Capture object"""
        return self._uuid

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    @property
    def path(self):
        """The local or server path to the Capture file data"""
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def metadataset(self):
        return self._metadata

    @property
    def labelset(self):
        return self._labels

    @property
    def capture_info(self):
        """Info about capture"""
        return self._capture_info

    @capture_info.setter
    def capture_info(self, value):
        self._capture_info = {}
        if value.get('CalculatedSampleRate', None) is not None:
            self._capture_info['calculated_sample_rate'] = value.get(
                'CalculatedSampleRate')
        if value.get('SampleRate', None) is not None:
            self._capture_info['set_sample_rate'] = value.get(
                'SampleRate', None)
        if value.get('capture_configuration_uuid', None) is not None:
            self._capture_info['capture_configuration_uuid'] = value.get(
                'capture_configuration_uuid', None)

        if not self._capture_info:
            self._caputre_info = None

    @property
    def ready(self):
        """Returns if Capture (Capture) is ready or not

        Returns:
            Boolean: True if task is ready or False if task is pending. Raises Exception if task failed.
        """
        url = 'project/{0}/capture/{1}/'.format(self._project.uuid, self.uuid)
        response = self._connection.request('get', url)
        response_data, err = utility.check_server_response(response)
        if not response_data['task_state'] or response_data['task_state'] in READY_STATES:
            return True

        if response_data['task_state'] in EXCEPTION_STATES:
            logger.error(response_data['task_result'])
            raise CaptureTaskFailedError()

        return False

    def await_ready(self, sleep=3, retries=0):
        """Blocks until Capture (Capture) is ready or failed

        Args:
            sleep (int): Number of seconds to sleep between polling
            retries (int): Number of times to retry before unblocking and returning False.
                           Use 0 for infinite.

        Returns:
            None or raises CaptureUploadFailureError if upload failed.
        """
        try_ = 0
        url = 'project/{0}/capture/{1}/'.format(self._project.uuid, self.uuid)

        while retries is 0 or try_ <= retries:
            try_ += 1
            response = self._connection.request('get', url)
            response_data, err = utility.check_server_response(response)
            # Uses custom UNREADY_STATES because we do NOT want to sleep forever on "PENDING"
            if response_data['task_state'] in UNREADY_STATES:
                time.sleep(sleep)
            elif not response_data['task_state'] or response_data['task_state'] in READY_STATES:
                return True
            else:
                raise CaptureUploadFailureError(response_data['task_result'])

    def insert(self, asynchronous=False):
        """Calls the REST API to insert a new Capture."""
        url = 'project/{0}/capture/'.format(self._project.uuid)
        capture_info = {'name': self.filename, 'asynchronous': asynchronous}
        if self.capture_info is not None:
            capture_info.update(self._capture_info)
        response = self._connection.file_request(
            url, self.path, capture_info, "rb")
        response_data, err = utility.check_server_response(response)
        if err is False:
            self._uuid = response_data['uuid']

    def update(self):
        """Calls the REST API to update the capture."""
        url = 'project/{0}/capture/{1}/'.format(self._project.uuid, self._uuid)

        capture_info = {'name': self.filename}
        if self._capture_info is not None:
            capture_info.update(self._capture_info)
        if self.path:
            response = self._connection.file_request(
                url, self.path, capture_info, 'rb', 'patch')
        else:
            response = self._connection.request(url, 'post', capture_info)
        response_data, err = utility.check_server_response(response)

    def delete(self):
        """Calls the REST API to delete the capture from the server."""
        url = 'project/{0}/capture/{1}/'.format(self._project.uuid, self._uuid)
        response = self._connection.request('delete', url,)
        response_data, err = utility.check_server_response(response)

    def refresh(self):
        """Calls the REST API and self populates properties from the server."""
        url = 'project/{0}/capture/{1}/'.format(self._project.uuid, self._uuid)
        response = self._connection.request('get', url,)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.filename = response_data['name']

    @classmethod
    def initialize_from_dict(cls, capture_dict):
        """Reads a dictionary or properties and populates a single capture.

            Args:
                capture_dict (dict): contains the capture's 'name' property

            Returns:
                capture object
        """
        assert isinstance(capture_dict, dict)
        new_dict = capture_dict.copy()
        new_dict['filename'] = str(new_dict.get(
            'filename',  # capture object attribute
            new_dict.pop('name', '')  # API object key
        ))
        return Capture(**new_dict)

    def data(self, cloud=True):
        """Calls the REST API and retrieves an capture's sensor data.

            Returns:
                data (DataFrame): all sensor data associated with the capture
        """
        url = 'project/{0}/capture/{1}/capture-sample/'.format(
            self._project.uuid, self.uuid)
        data = []

        if cloud:
            try:
                response = self._connection.request('get', url)
                response_data, err = utility.check_server_response(response)
                if err is False:
                    data = DataFrame(response_data)
            except HTTPError:
                utility.read_response_json_data(response)
                raise

        else:
            try:
                paged_response = self._connection.paged_request('get', url)
                for results in paged_response:
                    data.append(DataFrame(results))
            except HTTPError:
                utility.read_response_json_data(paged_response.response)
                raise
            data = pd.concat(data)

        # Post-processing to get numeric index
        data['sequence'] = data.sequence.astype(int)
        data = data.sort_values(by='sequence').reset_index(drop=True)
        data.drop('sequence', axis=1, inplace=True)

        return data

    # methods to make this instance hashable and comparable
    def __hash__(self):
        return hash(self._uuid)

    def __eq__(self, other):
        return ((self._uuid,) == (other._uuid,))

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return ((self._uuid,) < (other._uuid,))

    def __gt__(self, other):
        return ((self._uuid,) > (other._uuid,))

    def __le__(self, other):
        return (self < other) or (self == other)

    def __ge__(self, other):
        return (self > other) or (self == other)
