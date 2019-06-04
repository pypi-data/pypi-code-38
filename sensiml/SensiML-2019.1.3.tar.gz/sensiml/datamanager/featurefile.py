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

import os
import json
import sensiml.base.utility as utility


class FeatureFile(object):
    """Base class for a featurefile object."""

    def __init__(self, connection, project, name='', path=''):
        self._connection = connection
        self._project = project
        self.uuid = None
        self.name = name
        self.path = path

    # Maintain campatibility with old filename attr
    @property
    def filename(self):
        """The name of the file as stored on the server

        Note:
            Filename must contain a .csv or .arff extension
        """
        return self.name

    @filename.setter
    def filename(self, value):
        self.name = value

    def insert(self):
        """Calls the REST API to insert a new featurefile."""
        url = 'project/{0}/featurefile/'.format(
            self._project.uuid)
        featurefile_info = {'name': self.name}

        if not os.path.exists(self.path):
            raise OSError("Cannot update featurefile because the system cannot find the file path: '{0}'. "
                          "Please update the file's path attribute.".format(self.path))

        response = self._connection.file_request(url,
                                                 self.path, featurefile_info, "rb")
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.uuid = response_data['uuid']

    def update(self):
        """Calls the REST API to update the featurefile's properties on the server."""
        url = 'project/{0}/featurefile/{1}/'.format(
            self._project.uuid, self.uuid)
        featurefile_info = {'name': self.name}

        if not os.path.exists(self.path):
            raise OSError("Cannot update featurefile because the system cannot find the file path: '{0}'. "
                          "Please update the file's path attribute.".format(self.path))

        response = self._connection.file_request(url,
                                                 self.path, featurefile_info, "rb", method='put')
        response_data, err = utility.check_server_response(response)

    def delete(self):
        """Calls the REST API and deletes the featurefile from the server."""
        url = 'project/{0}/featurefile/{1}/'.format(
            self._project.uuid, self.uuid)
        response = self._connection.request('delete', url,)
        response_data, err = utility.check_server_response(response)

    def refresh(self):
        """Calls the REST API and populate the featurefile's properties from the server."""
        url = 'project/{0}/featurefile/{1}/'.format(
            self._project.uuid, self.uuid)
        response = self._connection.request('get', url,)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.name = response_data['name']

    def data(self):
        """Calls the REST API and retrieves the featurefile's binary data.

        Returns:
            featurefile contents
        """
        url = 'project/{0}/featurefile/{1}/data/'.format(
            self._project.uuid, self.uuid)
        response = self._connection.request(
            'get',
            url,
        )
        return response.content

    def initialize_from_dict(self, dict):
        """Makes a new featurefile using the dictionary.

        Args:
            dict (dict): contains the featurefile's 'name' and 'uuid' properties
        """
        self.uuid = dict['uuid']
        self.name = dict['name']
