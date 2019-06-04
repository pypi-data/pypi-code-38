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
from sensiml.base import utility


class Function(object):
    """Base class for a transform object"""
    _uuid = ''
    _type = None
    _name = None
    _function_in_file = ''
    _description = ''
    _input_contract = ''
    _subtype = ''
    _has_c_version = False

    def __init__(self, connection):
        self._connection = connection

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value

    @property
    def type(self):
        return self._type

    @property
    def has_c_version(self):
        return self._has_c_version

    @has_c_version.setter
    def has_c_version(self, value):
        self._has_c_version = value

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def input_contract(self):
        return self._input_contract

    @input_contract.setter
    def input_contract(self, value):
        self._input_contract = value

    @property
    def subtype(self):
        return self._subtype

    @subtype.setter
    def subtype(self, value):
        self._subtype = value

    def get_function_info(self):
        """Returns function properties after checking integrity constraints.

            Returns:
                (dict): containing the function's name, type, subtype, and has_c_version

            Raises:
                error if function does not have a name
                error if function does not have a type
        """
        # Sanity Checks
        try:
            assert(self.name is not None)
        except Exception as e:
            print("Function name cannot be None")
            raise(e)

        try:
            assert(self.type is not None)
        except Exception as e:
            print(
                "Function type cannot be None, please set to the correct type (ie. Transform, Optimizer, etc.)")
            raise(e)

        function_info = {'name': self.name,
                         'type': self.type,
                         'subtype': self.subtype,
                         'has_c_version': self.has_c_version,
                         }

        return function_info

    def refresh(self):
        """Calls the REST API and populates the local object properties from the server."""
        url = 'transform/{0}/'.format(self.uuid)
        response = self._connection.request('get', url,)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.name = response_data['name']
            self.type = response_data['type']
            self.subtype = response_data['subtype']
            self.description = response_data['description']
            self.input_contract = response_data['input_contract']
            self.has_c_version = response_data['has_c_version']

    def data(self):
        """Calls the REST API and request a transform file's binary data."""
        url = 'transform/{0}/data/'.format(self.uuid)
        response = self._connection.request('get', url,)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.initialize_from_dict(response_data)

    def initialize_from_dict(self, input_dictionary):
        """Populates a single transform object from a dictionary of properties from the server.

            Args:
                input_dictionary (dict): containing uuid, type, subtype, name, function_in_file, description,
                input_contract, and subtype
        """
        self.uuid = input_dictionary['uuid']
        self.type = input_dictionary['type']
        self.subtype = input_dictionary['subtype']
        self.name = input_dictionary['name']
        self.description = input_dictionary['description']
        self.input_contract = input_dictionary['input_contract']
        self.subtype = input_dictionary['subtype']
        self.has_c_version = input_dictionary['has_c_version']

    def __str__(self):
        input_string = ''
        for input_ in [i for i in self.input_contract if i['name'] not in ['classifiers', 'validation_methods',
                                                                           'number_of_times', 'sample_size']]:
            if 'element_type' in input_:
                input_string += '\n    {name} ({type} of {element_type})'.format(
                    **input_)
            else:
                input_string += '\n    {name} ({type})'.format(**input_)
            if 'options' in input_:
                options_string = ''
                for option in input_['options']:
                    options_string += '{name}, '.format(**option)
                input_string += ' {{options: {0}}}'.format(options_string[:-2])
            if 'description' in input_:
                input_string += ': {description}'.format(**input_)

        return ('NAME: {0}\n'
                'TYPE: {1}\n'
                'SUBTYPE: {2}\n'
                'DESCRIPTION: {3}\n'
                ).format(self.name, self.type, self.subtype,
                         self.description)
