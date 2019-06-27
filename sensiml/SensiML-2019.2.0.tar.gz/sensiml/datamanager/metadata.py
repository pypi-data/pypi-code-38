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


import json
from numpy import float64, int64
import sensiml.base.utility as utility
import logging
import time


logger = logging.getLogger(__name__)


class MetadataType(object):
    Int = 'integer'
    Float = 'float'
    String = 'string'


class Metadata(object):
    """Base class for a metadata object."""

    def __init__(self, connection, project, capture):
        """Initialize a metadata object.

            Args:
                connection
                project
                capture
        """
        self._uuid = ''
        self._name = ''
        self._sample_start = 0
        self._sample_end = 0
        self._value = ''
        self._value_type = 'string'
        self._comments = ''
        self._connection = connection
        self._project = project
        self._capture = capture
        self._lastmodifiedby = ''
        self._lastmodifiedtime = ''

    @property
    def uuid(self):
        """Auto generated unique identifier for the metadata object"""
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value

    @property
    def name(self):
        """The name property of the metadata object"""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def value(self):
        """The value of the metadata object

        Note:
            The metadata value -1 (as an integer or string) has a special meaning. It is reserved by KnowledgeBuilder
            and means that the metadata name is not defined for a particular sample. You should never use -1 for a
            metadata value.
        """
        if self._value_type == MetadataType.Float:
            return float(self._value)
        elif self._value_type == MetadataType.Int:
            return int(self._value)
        else:
            return self._value

    @value.setter
    def value(self, value):
        if type(value) in (float, float64):
            self._value_type = MetadataType.Float
            self._value = str(value)
        elif type(value) in (int, int64):
            self._value_type = MetadataType.Int
            self._value = str(value)
        else:
            self._value_type = MetadataType.String
            self._value = str(value)

    @property
    def value_type(self):
        """The data type of the metadata object"""
        return self._value_type

    @property
    def lastmodifiedby(self):
        return self._lastmodifiedby

    @property
    def lastmodifiedtime(self):
        return self._lastmodifiedtime

    @property
    def comments(self):
        """The label comments"""
        return self._comments

    @comments.setter
    def comments(self, value):
        self._comments = value

    def insert(self):
        """Calls the REST API and inserts a metadata object onto the server using the local object's properties."""
        self._capture.await_ready()
        url = 'v2/project/{0}/capture/{1}/metadata-relationship/'.format(
            self._project.uuid, self._capture.uuid)
        label_info = {'name': self.name,
                      'type': self.value_type,
                      'value': self.value,
                      'comments': self._comments}
        response = self._connection.request('post', url, label_info)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.uuid = response_data['uuid']

    def update(self):
        """Calls the REST API and updates the object on the server."""
        self._capture.await_ready()
        url = 'v2/project/{0}/capture/{1}/metadata-relationship/{2}/'.format(
            self._project.uuid, self._capture.uuid, self.uuid)
        label_info = {'name': self.name,
                      'type': self.value_type,
                      'value': self.value,
                      'comments': self._comments}
        response = self._connection.request('put', url, label_info)
        response_data, err = utility.check_server_response(response)

    def delete(self):
        """Calls the REST API and deletes the object from the server."""
        url = 'v2/project/{0}/capture/{1}/metadata-relationship/{2}/'.format(
            self._project.uuid, self._capture.uuid, self.uuid)
        response = self._connection.request('delete', url,)
        response_data, err = utility.check_server_response(response)

    def refresh(self):
        """Calls the REST API and populates the local object's properties from the server."""
        url = 'v2/project/{0}/capture/{1}/metadata-relationship/{2}/'.format(
            self._project.uuid, self._capture.uuid, self.uuid)
        response = self._connection.request('get', url,)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.initialize_from_dict(response_data)

    def initialize_from_dict(self, dict):
        """Reads a json dictionary and populates a single metadata object.

            Args:
                dict (dict): contains the uuid, name, type, value, properties
        """
        self.uuid = dict['uuid']
        self.name = dict['name']
        if dict['type'] == MetadataType.Int:
            self.value = int(dict['value'])
        elif dict['type'] == MetadataType.Float:
            self.value = float(dict['value'])
        else:
            self.value = dict['value']
