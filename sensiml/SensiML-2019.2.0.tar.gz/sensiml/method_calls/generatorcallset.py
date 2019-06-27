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


from sensiml.method_calls.generatorcall import GeneratorCall
from sensiml.datamanager.pipeline import PipelineStep


class GeneratorCallSet(PipelineStep):
    """The base class for a collection of generator calls"""

    def __init__(self, name=''):
        super(GeneratorCallSet, self).__init__(
            name=name, step_type='GeneratorCallSet')
        self._input_data = ''
        self._generator_calls = []
        self._group_columns = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def input_data(self):
        return self._input_data

    @input_data.setter
    def input_data(self, value):
        self._input_data = value

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, value):
        self._outputs = value

    @property
    def generator_calls(self):
        return self._generator_calls

    def add_generator_call(self, *generator_call):
        """Adds one or more generator calls to the collection.

            Args:
                generator_call (GeneratorCall or list[GeneratorCall]): object(s) to append
        """
        for g in generator_call:
            self._generator_calls.append(g)

    def remove_generator_call(self, *generator_calls):
        """Removes a generator call from the collection.

            Args:
                generator_calls (GeneratorCall): object to remove
        """
        for generator_call in generator_calls:
            self._generator_calls = [
                f for f in self._generator_calls if f != generator_call]
        # Note:  We should probably re-populate inputs and outputs here

    @property
    def group_columns(self):
        return self._group_columns

    @group_columns.setter
    def group_columns(self, value):
        self._group_columns = value

    def _to_list(self):
        gencalls = []
        for item in self._generator_calls:
            gencalls.append(item._to_dict())
        return gencalls

    def _to_dict(self):
        gencalls_set = []
        set_dict = {}
        for item in self._generator_calls:
            gencalls_set.append(item._to_dict())
        set_dict['name'] = self._name
        set_dict['type'] = 'generatorset'
        set_dict['set'] = gencalls_set
        set_dict['inputs'] = {}
        set_dict['inputs']['group_columns'] = self._group_columns
        set_dict['inputs']['input_data'] = self._input_data
        set_dict['outputs'] = self._outputs
        return set_dict
