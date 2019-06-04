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

from sensiml.datamanager.pipeline import PipelineStep


class TrainAndValidationCall(PipelineStep):
    """The base class for a train-and-validation call."""

    def __init__(self, name=''):
        super(TrainAndValidationCall, self).__init__(
            name=name, step_type='TrainAndValidationCall')
        self._validation_methods = []
        self._classifiers = []
        self._optimizers = []
        self._input_data = ''
        self._feature_table = ''
        self._label_column = None
        self._ignore_columns = None
        self._outputs = []
        self._validation_seed = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def validation_methods(self):
        return self._validation_methods

    @validation_methods.setter
    def validation_methods(self, value):
        self._validation_methods = value

    @property
    def classifiers(self):
        return self._classifiers

    @classifiers.setter
    def classifiers(self, value):
        self._classfiers = value

    @property
    def optimizers(self):
        return self._optimizers

    @optimizers.setter
    def optimizers(self, value):
        self._optimizers = value

    @property
    def input_data(self):
        return self._input_data

    @input_data.setter
    def input_data(self, value):
        self._input_data = value

    @property
    def feature_table(self):
        return self._feature_table

    @feature_table.setter
    def feature_table(self, value):
        self._feature_table = value

    @property
    def label_column(self):
        return self._label_column

    @label_column.setter
    def label_column(self, value):
        self._label_column = value

    @property
    def ignore_columns(self):
        return self._ignore_columns

    @ignore_columns.setter
    def ignore_columns(self, value):
        self._ignore_columns = value

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, value):
        self._outputs = value

    @property
    def validation_seed(self):
        return self._validation_seed

    @validation_seed.setter
    def validation_seed(self, value):
        self._validation_seed = value

    def add_validation_method(self, validation_method_call):
        """Adds a validation method call to the train-and-validation call.

            Args:
                validation_method_call (ValidationMethodCall): object to append
        """
        self._validation_methods.append(validation_method_call)

    def remove_validation_method(self, validation_method_call):
        """Removes a validation method call from the train-and-validation call.

            Args:
                validation_method_call (ValidationMethodCall): object to remove
        """
        self._validation_methods = [
            f for f in self._validation_methods if f != validation_method_call]

    def add_classifier(self, classifier_call):
        """Adds a classifier call to the train-and-validation call.

            Args:
                classifier_call (ClassifierCall): object to append
        """
        self._classifiers.append(classifier_call)

    def remove_classifier(self, classifier_call):
        """Removes a classifier call from the train-and-validation call.

            Args:
                classifier_call (ClassifierCall): object to remove
        """
        self._classifiers = [
            f for f in self._classifiers if f != classifier_call]

    def add_optimizer(self, optimizer_call):
        """Adds an optimizer call to the train-and-validation call.

            Args:
                optimizer_call (OptimizerCall): object to append
        """
        self._optimizers.append(optimizer_call)

    def remove_optimizer(self, optimizer_call):
        """Removes an optimizer call from the train-and-validation call.

            Args:
                optimizer_call (OptimizerCall): object to remove
        """
        self._optimizers = [f for f in self._optimizers if f != optimizer_call]

    def _to_dict(self):
        d = {}
        d['name'] = self.name
        d['type'] = 'tvo'
        d['input_data'] = self.input_data
        d['feature_table'] = self.feature_table
        d['label_column'] = self.label_column
        d['ignore_columns'] = self.ignore_columns
        d['outputs'] = self._outputs
        d['validation_seed'] = self._validation_seed

        d['optimizers'] = []
        for item in self._optimizers:
            d['optimizers'].append(item._to_dict())

        d['classifiers'] = []
        for item in self._classifiers:
            d['classifiers'].append(item._to_dict())

        d['validation_methods'] = []
        for item in self._validation_methods:
            d['validation_methods'].append(item._to_dict())

        return d
