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


class PlatformDescription(object):
    """Base class for a PlatformDescription object"""
    _id = 0
    _board_name = ''
    _hardware_accelerators = dict()
    _manufacturer = ''
    _can_build_binary = False
    _platform = ''
    _platform_version = ''
    _description = ''
    _supported_source_drivers = {}
    _supported_outputs = {}
    _ota_capable = False
    _target_os_options = {}
    _execution_parameters = {}

    def __init__(self, connection):
        self._connection = connection

    @property
    def board_name(self):
        return self._board_name

    @property
    def manufacturer(self):
        return self._manufacturer

    @property
    def id(self):
        return self._id

    @property
    def hardware_accelerators(self):
        return self._hardware_accelerators

    @property
    def can_build_binary(self):
        return self._can_build_binary

    @property
    def platform(self):
        return self._platform

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def platform_version(self):
        return self._platform_version

    @property
    def ota_capable(self):
        return self._ota_capable

    @property
    def supported_outputs(self):
        return self._supported_outputs

    @property
    def supported_source_drivers(self):
        return self._supported_source_drivers

    @property
    def target_os_options(self):
        return self._target_os_options

    @property
    def execution_parameters(self):
        return self._execution_parameters

    def get_config(self, test_data='', debug=False):
        """ Generates a default configuation dictionary for downloading a knowledgepack using this platform progrmatically

            Args:
                test_data (str): name of test data file to load onto knowledge pack,
                debug (bool): Build option for knowledge pack. Debug mode will have extra printouts to help with debugging issues.

        """

        if self.supported_source_drivers:
            source = self.supported_source_drivers['Default'][0]
        else:
            source = "Custom"

        if self.supported_outputs:
            outputs = [x.lower() for x in self.supported_outputs]
        else:
            outputs = ['serial']

        config = {'target_platform': self.id,
                  'test_data': test_data,
                  "debug": debug,
                  'application': self.execution_parameters.get('application', 'Default'),
                  'output_options': outputs,
                  'sample_rate': self.supported_source_drivers.get('Default', [None, ''])[1],
                  'source': source
                  }

        return config

    def refresh(self):
        """Calls the REST API and populates the local object properties from the server."""
        url = 'platforms/{0}/'.format(self.id)
        response = self._connection.request('get', url, )
        response_data, err = utility.check_server_response(response)
        if err is False:
            self._board_name = response_data['board_name']
            self._hardware_accelerators = response_data['hardware_accelerators']
            self._platform = response_data['platform']
            self._platform_version = response_data['platform_version']
            self._description = response_data['description']
            self._can_build_binary = response_data['can_build_binary']
            self._ota_capable = response_data['ota_capable']
            self._supported_source_drivers = response_data['supported_source_drivers']
            self._supported_outputs = response_data['supported_outputs']
            self._target_os_options = response_data['target_os_options']
            self._execution_parameters = response_data['execution_parameters']

    def initialize_from_dict(self, input_dictionary):
        """Populates a single transform object from a dictionary of properties from the server.

            Args:
                input_dictionary (dict): containing uuid, type, subtype, name, function_in_file, description,
                input_contract, and subtype
        """
        self._id = input_dictionary['id']
        self._board_name = input_dictionary['board_name']
        self._hardware_accelerators = input_dictionary['hardware_accelerators']
        self._platform = input_dictionary['platform']
        self._platform_version = input_dictionary[u'platform_version']
        self._description = input_dictionary['description']
        self._can_build_binary = input_dictionary['can_build_binary']
        self._ota_capable = input_dictionary.get('ota_capable', False)
        self._supported_source_drivers = input_dictionary.get(
            'supported_source_drivers',
            {"Motion": [200, 100, 50, 25], "Audio": [16000], "Default": ["Motion", 100], "Custom": []})
        self._supported_outputs = input_dictionary.get(
            'supported_outputs', ["BLE", "SERIAL", "LED"])
        self._target_os_options = input_dictionary.get(
            'target_os_options', ["ARM GCC Generic"])
        self._execution_parameters = input_dictionary.get(
            'execution_parameters', {"application": "Default"})

    def __dict__(self):
        ret = {
            'Id': int(self.id),
            'Board': self.board_name,
            'Hardware Accelerated': 'Yes' if len(self.hardware_accelerators.items()) > 0 else 'No',
            'Software Platform': self.platform,
            'Platform Version': self.platform_version,
            'Description': self.description,
        }
        return ret

    def __call__(self):
        pd_dict = self.__dict__()
        pseries = Series(pd_dict, index=pd_dict.keys())
        df = DataFrame()
        df = df.append(pseries, ignore_index=True)
        return df.drop(labels=['Id'], axis=1)
