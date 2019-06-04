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
from pandas import DataFrame, Series

from sensiml.base import utility
from sensiml.datamanager.sandbox import describe_pipeline


class PipelineSeed(object):
    """Base class for an automation pipeline seed object"""
    _id = 0
    _name = ''
    _description = ''
    _pipeline = ''
    _input_contract = {}

    def __init__(self, connection):
        self._connection = connection

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def description(self):
        return self._description

    @property
    def pipeline(self):
        return self._pipeline

    @property
    def input_contract(self):
        return self._input_contract

    def refresh(self):
        """Calls the REST API and populates the local object properties from the server."""
        url = 'seed/{0}/'.format(self.id)
        response = self._connection.request('get', url,)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self._name = response_data['name']
            self._description = response_data['description']
            self._id = response_data['id']
            self._pipeline = response_data['pipeline']
            self._input_contract = response_data['input_contract']

    def initialize_from_dict(self, input_dictionary):
        """Populates a single seed object from a dictionary of properties from the server."""
        self._id = input_dictionary['id']
        self._name = input_dictionary['name']
        self._description = input_dictionary['description']
        self._pipeline = input_dictionary['pipeline']
        self._input_contract = input_dictionary['input_contract']

    def __dict__(self):
        ret = {
            'Name': self.name,
            'Pipeline': self.pipeline,
            'Description': self.description,
            'Inputs': self.input_contract,
        }
        return ret

    def __call__(self):
        pd_dict = self.__dict__()
        pseries = Series(pd_dict, index=pd_dict.keys())
        df = DataFrame()
        df = df.append(pseries, ignore_index=True)
        return df.set_index('Name').reset_index()

    def describe(self, show_params=True):
        """Prints a formatted description of the pipeline seed"""
        describe_pipeline(self.pipeline, show_params=show_params)
