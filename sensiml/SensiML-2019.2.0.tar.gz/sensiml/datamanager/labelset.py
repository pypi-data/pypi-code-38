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
from sensiml.datamanager.label import Label
import sensiml.base.utility as utility


class LabelExistsError(Exception):
    """Base class for the label exists error"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class LabelSet():
    """Base class for a collection of label"""

    def __init__(self, connection, project, capture):
        self._connection = connection
        self._project = project
        self._capture = capture

    def __getitem__(self, name):
        label = self.get_label_by_name(name)
        if label is not None:
            return label.get_label_value()
        else:
            return None

    def __setitem__(self, name, value):
        label = self.get_label_by_name(name)
        if label is not None:
            label.set_label_value(value)
            label.update()
        else:
            self.create_label(name, value)

    def create_label(self, name, capture):
        """Creates a label object using its name and capture properties.

            Args:
                name (str): name of the label object
                capture (capture): parent capture of the label
        """
        # TODO: This looks odd with capture having a _label attribute; make sure this is being unit tested
        if self.get_label_by_name(name) is not None:
            raise labelExistsError(
                "label {0} already exists.".format(name))
        else:
            self._capture = capture
            self._capture.await_ready()
            label = self.new_label()
            label.name = name
            label.new_value = capture._label.new_value
            label.sample_start = capture._label.sample_start
            label.sample_end = capture._label.sample_end
            label.insert()
            return  # label

    def get_label_by_name(self, name):
        """Gets one label object by the name property.

            Args:
                name (str)

            Returns:
                label object or None

            Note:
                If more than one label of the same name exist for the capture, this will only return one of them
                at random.
        """
        label_list = self.get_labelset()
        for label in label_list:
            if label.name == name:
                return label
        return None

    def new_label(self):
        """Initializes a new label object locally but does not insert it.

            Returns:
                label object
        """
        label = Label(self._connection, self._project, self._capture)
        return label

    def _new_label_from_dict(self, dict):
        """Creates a new label from data in the dictionary.

            Args:
                dict (dict): contains label properties uuid, name, type, value, capture_sample_sequence_start, and
                capture_sample_sequence_end

            Returns:
                label object

        """
        label = Label(self._connection, self._project, self._capture)
        label.initialize_from_dict(dict)
        return label

    def get_labelset(self):
        """Gets all of the capture's label objects in a list.

            Returns:
                list[label]
        """
        # Query the server and get the json
        url = 'project/{0}/capture/{1}/label-relationship/'.format(
            self._project.uuid, self._capture.uuid)
        response = self._connection.request('get', url,)
        try:
            response_data, err = utility.check_server_response(response)
        except ValueError:
            print(response)

        # Populate each label from the server
        labelset = []
        if err is False:
            try:
                for label_params in response_data:
                    labelset.append(
                        self._new_label_from_dict(label_params))
            except:
                pass
        return labelset
