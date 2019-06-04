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


from sensiml.method_calls.selectorcall import SelectorCall
from sensiml.datamanager.pipeline import PipelineStep


class SelectorCallSet(PipelineStep):
    """The base class for a collection of selector calls"""

    def __init__(self, name=''):
        super(SelectorCallSet, self).__init__(
            name=name, step_type='SelectorCallSet')
        self._selectors = []
        self._input_data = ''
        self._label_column = None
        self._number_of_features = 10
        self._feature_table = ''
        self._cost_function = ''
        self._remove_columns = []
        self._passthrough_columns = None
        self._refinement = {}

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
    def label_column(self):
        return self._label_column

    @label_column.setter
    def label_column(self, value):
        self._label_column = value

    @property
    def number_of_features(self):
        return self._number_of_features

    @number_of_features.setter
    def number_of_features(self, value):
        self._number_of_features = value

    @property
    def feature_table(self):
        return self._feature_table

    @feature_table.setter
    def feature_table(self, value):
        self._feature_table = value

    @property
    def cost_function(self):
        return self._cost_function

    @cost_function.setter
    def cost_function(self, value):
        self._cost_function = value

    @property
    def refinement(self):
        return self._refinement

    @refinement.setter
    def refinement(self, value):
        self._refinement = value

    @property
    def selectors(self):
        return self._selectors

    def add_selector_call(self, *selectors):
        """Adds one or more selector calls to the collection.

            Args:
                selectors (SelectorCall or list[SelectorCall]): object(s) to append
        """
        for selector in selectors:
            self._selectors.append(selector)

    def remove_selector_call(self, *selectors):
        """Removes one or more selector call from the collection.

            Args:
                selectors (SelectorCall or list[SelectorCall]): object(s) to remove
        """
        for selector in selectors:
            self._selectors = [f for f in self._selectors if f != selector]
        # Note:  We should probably re-populate inputs and outputs here

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, value):
        self._outputs = value

    @property
    def passthrough_columns(self):
        return self._passthrough_columns

    @passthrough_columns.setter
    def passthrough_columns(self, value):
        self._passthrough_columns = value

    @property
    def remove_columns(self):
        return self._remove_columns

    @remove_columns.setter
    def remove_columns(self, value):
        self._remove_columns = value

    def _to_list(self):
        gencalls = []
        for item in self._selectors:
            gencalls.append(item._to_dict())
        return gencalls

    def _to_dict(self):
        selcalls_set = []
        set_dict = {}
        for item in self._selectors:
            selcalls_set.append(item._to_dict())
        set_dict['type'] = 'selectorset'
        set_dict['name'] = getattr(self, '_name')
        set_dict['set'] = selcalls_set
        set_dict['inputs'] = {}
        set_dict['inputs']['remove_columns'] = getattr(self, '_remove_columns')
        set_dict['inputs']['passthrough_columns'] = getattr(
            self, '_passthrough_columns')
        set_dict['inputs']['input_data'] = getattr(self, '_input_data')
        set_dict['inputs']['label_column'] = getattr(self, '_label_column')
        set_dict['inputs']['number_of_features'] = getattr(
            self, '_number_of_features')
        set_dict['inputs']['feature_table'] = getattr(self, '_feature_table')
        if self._cost_function == '':
            self._cost_function = 'sum'
        set_dict['inputs']['cost_function'] = getattr(self, '_cost_function')
        set_dict['outputs'] = self._outputs
        set_dict['refinement'] = getattr(self, '_refinement')
        return set_dict
