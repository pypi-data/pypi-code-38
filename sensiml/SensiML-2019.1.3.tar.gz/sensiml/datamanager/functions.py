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

from six import string_types
import sensiml.base.utility as utility
from sensiml.datamanager.function import Function
from sensiml.method_calls import FeatureFileCall, QueryCall, FunctionCall, \
    TrainAndValidationCall, GeneratorCall, GeneratorCallSet, SelectorCall, \
    SelectorCallSet, ValidationMethodCall, ClassifierCall, OptimizerCall, \
    TrainingAlgorithmCall, CaptureFileCall


class FunctionExistsError(Exception):
    """Base class for a function exists error"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Functions():
    """Base class for a collection of functions"""

    def __init__(self, connection):
        self._connection = connection
        self._function_list = {}
        self.build_function_list()

    @property
    def function_list(self):
        if not self._function_list:
            self.build_function_list()

        return self._function_list

    @function_list.setter
    def function_list(self, value):
        self._function_list = value

    def build_function_list(self):
        """Populates the function_list property from the server."""
        function_list = {}

        function_response = self.get_functions()
        for function in function_response:
            function_list[function.name] = function

        self.function_list = function_list

    def get_function_by_name(self, name):
        """Gets a function from the server by name.

            Args:
                name (str): function name

            Returns:
                function
        """
        return self.function_list.get(name, None)

    def _new_function_from_dict(self, dict):
        """Creates and populates a function from a set of properties.

            Args:
                dict (dict): contains properties of a function

            Returns:
                function
        """
        function = Function(self._connection)
        function.initialize_from_dict(dict)
        return function

    def get_functions(self, function_type=''):
        """Gets all functions as function objects.

            Args:
                function_type (optional[str]): type of function to retrieve

            Returns:
                list of functions
        """
        url = 'transform'
        response = self._connection.request(
            'get', url)
        try:
            response_data, err = utility.check_server_response(response)
        except ValueError:
            print(response)

        functions = []
        for function_params in response_data:
            functions.append(self._new_function_from_dict(function_params))

        if function_type:
            functions = [f for f in functions if f.type == function_type]

        return functions

    def create_query_call(self, name='Query'):
        """Creates a query call.

            Returns:
                QueryCall
        """
        qy = QueryCall(name)
        return qy

    def create_featurefile_call(self, name):
        """Creates a featurefile call.

            Args:
                name: name of the featurefile

            Returns:
                FeatureFileCall
        """
        ff = FeatureFileCall(name)
        return ff

    def create_capturefile_call(self, name):
        """Creates a capturefile call.

            Args:
                name: name of the featurefile

            Returns:
                FeatureFileCall
        """
        ff = CaptureFileCall(name)
        return ff

    def create_train_and_validation_call(self, name='TVO'):
        """Creates an empty train and validation call.

            Returns:
                TrainAndValidationCall
        """
        tvo = TrainAndValidationCall()
        tvo.name = name
        return tvo

    def get_functions_by_type(self, function_type='', subtype=''):
        """Gets all functions or functions of a particular function ype or all functions
            of a particular subtype as function objects.

            Args:
                subtype (optional[str]): subtype to retrieve

            Returns:
                list of functions
        """
        # Populate each function from the server

        if function_type:
            functions = [f for f in self.function_list.values()
                         if f.type == function_type]

        elif subtype:
            functions = [f for f in self.function_list.values()
                         if f.subtype == subtype]

        else:
            functions = [f for f in self.function_list.values()]

        return functions

    def __str__(self, function_type=''):
        output_string = ''
        all_functions = self.get_functions_by_type(function_type=function_type)
        for s in set([f.type for f in all_functions]):
            output_string += '{0}:\n'.format(s)
            for t in [tr for tr in all_functions if tr.type == s and (tr.has_c_version or
                                                                      tr.type not in ['Transform', 'Segmenter', 'Feature Generator'])]:
                if t.subtype:
                    output_string += '    {0} ({1})\n'.format(t.name,
                                                              t.subtype)
                else:
                    output_string += '    {0}\n'.format(t.name)
            output_string += '\n'

        return output_string

    def __call__(self, function_type):
        return self.__str__(function_type)

    def __getitem__(self, key):
        return self.get_function_by_name(key).__str__()

    def _initialize_docstring(self, function):
        ic_dict = function.input_contract
        #oc_dict = function.output_contract
        inputs = {i['name']: None for i in ic_dict if not i.get(
            'handle_by_set', False)}  # Parse arguments from the input contract

        # Construct a user-friendly docstring using the description and input/output contracts
        docstring = function.description
        docstring += '\n \nInputs\n---------- \n'

        for i in ic_dict:
            if i.get('default', None):
                docstring += '  {0}: {1} - (default: {2})\n'.format(
                    i['name'], i['type'], i['default'])
            else:
                docstring += '  {0}: {1} \n'.format(i['name'], i['type'])

        # docstring += '\nOutputs\n---------- \n'
        # for i in oc_dict:
        #     docstring += '  {0} \n'.format(i['type'])

        docstring += '\nUsage\n---------- \n'
        docstring += 'For DataFrame inputs, provide a string reference to the\nDataFrame output of a previous step in the pipeline.\n'
        docstring += 'For Dataframe output, provide a string name that subsequent\noperations can refer to.'

        return ic_dict, inputs, docstring

    def _warn_if_not_transcoded(self, function):
        if function.type in ('Transform', 'Segmenter', 'Feature Generator') and not function.has_c_version:
            print('Warning: {0} is not supported by KnowledgePack code generation. \n'
                  'It can be used for cloud-based modeling but cannot be downloaded or flashed to a device. \n'.format(function.name))

    def create_function_call(self, function, name=None):
        """Creates a function call object.

            Args:
                function (Function object or str): the function for which to create a call object or its
                string name

            Returns:
                function call object or None if the function is not found

            Raises:
                error if no call object can be initialized for the function type
        """
        if name:
            print(
                "The use of the second input parameter is no longer necessary and will be deprecated.")

        if isinstance(function, string_types):
            function = self.function_list.get(function, None)

            if function is None:
                print('No function found')
                return None

        self._warn_if_not_transcoded(function)

        try:
            return getattr(self, 'create_{}_call'.format(function.type.lower().replace(' ', '_')))(function)
        except Exception as e:
            print('No function call for function type "{}" found.'.format(
                function.type.lower()))
            raise(e)

    def _create_base_call(self, function, CallFunction, ignore_columns=[]):
        """Creates a base subclass on the fly for the specified function.

        Parses the passed function's I/O contracts and builds class properties accordingly. Returns an instance of the
        new class.
        """

        if isinstance(function, string_types):
            function = self.function_list[function]

        self._warn_if_not_transcoded(function)
        ic_dict, inputs, docstring = self._initialize_docstring(function)

        for column in ignore_columns:
            inputs.pop(column, None)

        for contract in ic_dict:
            if 'default' in contract.keys():
                inputs[contract['name']] = contract['default']

        # Add docstring to inputs structure and create the new class
        inputs['__doc__'] = docstring
        fname = str(function.name)

        Call = type(fname, (CallFunction,), inputs)

        return Call(function.name, function_type=function.type.lower())

    def create_transform_call(self, function, name=None):
        """Creates a FunctionCall for the specified transform.

        Parses the passed function's I/O contracts and builds class properties accordingly. Returns an instance of the
        new class.

            Args:
                function (Function): function with which to create a transform call

            Returns:
                instance of FunctionCall customized for the input function
        """

        ic_dict, inputs, docstring = self._initialize_docstring(function)

        # Add docstring to inputs structure and create the new class
        inputs['__doc__'] = docstring
        fname = str('kb_'+function.name.lower().replace(' ', '_'))

        for contract in ic_dict:
            if 'default' in contract.keys():
                inputs[contract['name']] = contract['default']

        Call = type(fname, (FunctionCall,), dict(
            {'_input_contract': ic_dict}, **inputs))
        return Call(name=function.name, function_type=function.type.lower())

    def create_segmenter_call(self, function, name=None):

        return self.create_transform_call(function, name=name)

    def create_sampler_call(self, function, name=None):

        return self.create_transform_call(function, name=name)

    def create_feature_generator_call(self, function):
        """Creates a GeneratorCall for the specified generator.

            Args:
                function (Function): function with which to create a feature generator call

            Returns:
                instance of GeneratorCall customized for the input function
        """
        ignore_columns = ['group_columns', 'input_data']

        return self._create_base_call(function, GeneratorCall, ignore_columns=ignore_columns)

    def create_feature_selector_call(self, function):
        """Creates a SelectorCall for the specified selector.

            Args:
                function (Function): function with which to create a feature selector call

            Returns:
                instance of SelectorCall customized for the input function
        """
        ignore_columns = ['ignore_columns',
                          'input_data', 'label_column', 'num_features']

        return self._create_base_call(function, SelectorCall, ignore_columns=ignore_columns)

    def create_validation_method_call(self, function, name=None):
        """Creates a ValidationMethodCall for the specified function.

            Args:
                function (Function): function with which to create a validation method call

            Returns:
                instance of ValidationMethodCall customized for the input function
        """
        return self._create_base_call(function, ValidationMethodCall)

    def create_classifier_call(self, function):
        """Creates a ClassifierCall for the specified function.

            Args:
                function (Function): function with which to create a classifier call

            Returns:
                instance of ClassifierCall customized for the input function
        """
        return self._create_base_call(function, ClassifierCall)

    def create_optimizer_call(self, function, name=None):
        """Creates an OptimizerCall for the specified function.

            Args:
                function (Function): function with which to create an optimizer call

            Returns:
                instance of OptimizerCall customized for the input function
        """
        return self._create_base_call(function, OptimizerCall)

    def create_generator_subtype_call(self, subtype):
        """Creates a GeneratorCall for the specified subtype of generators.

        Uses the input contract of one function of the subtype (assumed to be constant for all generators of the subtype),
        and builds class properties accordingly.

            Args:
                subtype (str): name of the subtype for which to create a generator call

            Returns:
                instance of GeneratorCall customized for the subtype
        """

        function_list = self.get_functions_by_type(subtype=subtype)
        if len(function_list) > 0:
            function = function_list[0]
            ic_dict, inputs, docstring = self._initialize_docstring(function)
        else:
            print("Error: No generators of subtype {0}; length of function list {1}".format(
                subtype, len(function_list)))
            return None

        for function in function_list:
            self._warn_if_not_transcoded(function)

        ignore_columns = ['group_columns', 'input_data']

        for column in ignore_columns:
            inputs.pop(column, None)

        for contract in ic_dict:
            if 'default' in contract.keys():
                inputs[contract['name']] = contract['default']

        # Add docstring to inputs structure and create the new class
        inputs['__doc__'] = docstring
        inputs['_subtype'] = subtype

        Call = type(subtype, (GeneratorCall,), inputs)
        return Call(function.name, 'generator')

    def create_generator_call_set(self, name='GeneratorCallSet'):
        """Creates an empty generator call set."""
        gcs = GeneratorCallSet(name)
        return gcs

    def create_selector_call_set(self, name='SelectorCallSet'):
        """Creates an empty selector call set."""
        scs = SelectorCallSet(name)
        return scs

    def create_training_algorithm_call(self, function, name=None):
        """Creates a training algorithm method call for the specified function.

            Args:
                function (Function): function with which to create an training algorithm call

            Returns:
                instance of TrainingAlgorithmCall customized for the input function
        """
        return self._create_base_call(function, TrainingAlgorithmCall)
