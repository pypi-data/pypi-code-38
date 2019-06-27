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
from sensiml.datamanager.featurefile import FeatureFile
import sensiml.base.utility as utility


class FeatureFileExistsError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class FeatureFiles():
    """Base class for a collection of featurefiles."""

    def __init__(self, connection, project):
        self._connection = connection
        self._project = project

    def create_featurefile(self, filename, path):
        """Creates a featurefile object from the filename and path.

        Args:
            filename (str): desired name of the featurefile on the server, must have a .csv or .arff extension
            path (str): full local path to the file, including the file's local name and extension

        Returns:
            featurefile object

        Raises:
            FeatureFileExistsError, if the featurefile already exists on the server
        """
        if self.get_featurefile_by_name(filename) is not None:
            raise FeatureFileExistsError("featurefile {0} already exists.".
                                         format(filename))
        else:
            featurefile = self.new_featurefile()
            featurefile.name = filename
            featurefile.path = path
            featurefile.insert()
            return featurefile

    def build_featurefile_list(self):
        """Populates the function_list property from the server."""
        featurefile_list = {}

        featurefile_response = self.get_featurefiles()
        for featurefile in featurefile_response:
            featurefile_list[featurefile.name] = featurefile

        return featurefile_list

    def get_featurefile_by_name(self, filename):
        """Gets a featurefile from the server.

        Args:
            filename: name of the featurefile as stored on the server

        Returns:
            featurefile object or None if it does not exist
        """
        featurefile_list = self.build_featurefile_list()
        return featurefile_list.get(filename, None)

    def new_featurefile(self):
        """Initializes a new featurefile object, but does not insert it."""
        featurefile = FeatureFile(self._connection, self._project)
        return featurefile

    def _new_featurefile_from_dict(self, dict):
        """Creates a featurefile object from a dictionary of properties.

        Args:
            dict (dict): contains featurefile's 'name' and 'uuid' properties

        Returns:
            featurefile object
        """
        featurefile = FeatureFile(self._connection, self._project)
        featurefile.initialize_from_dict(dict)
        return featurefile

    def get_featurefiles(self):
        """Gets a list of all featurefiles in the project.

        Returns:
            list (featurefiles)
        """
        err = False
        url = 'project/{0}/featurefile/'.format(self._project.uuid)
        response = self._connection.request('get', url,)
        try:
            response_data, err = utility.check_server_response(response)
        except ValueError:
            print(response)
        # Populate the retrieved featurefiles
        featurefiles = []
        if err is False:
            try:
                for featurefile_params in response_data:
                    featurefiles.append(
                        self._new_featurefile_from_dict(featurefile_params))
            except:
                pass

        return featurefiles
