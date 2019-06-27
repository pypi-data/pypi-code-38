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
from pandas import DataFrame, Series
from numpy import NaN
import logging
from sensiml.datamanager.confusion_matrix import ConfusionMatrix, ConfusionMatrixException
import sensiml.base.utility as utility

logger = logging.getLogger('ModelMetrics')


class ModelException(Exception):
    pass


class ModelMetrics(object):
    """Base class for a model metrics object.

    Attributes:
        confusion_matrix_stats (list[ConfusionMatrix]): comprehensive metrics returned for the model
        train_set (list): indices of the input data that the model was trained with
        validation_set (list): indices of the input data that the model was validated with
        test_set (list): indices of the input data that the model was tested with
        debug (dict): structure containing debug information for some models
        neurons (list[dict]): model neuron array
        parameters (dict): model parameters
        knowledgepack (KnowledgePack): knowledgepack associated with the model
    """

    def _order_columns(self, confusion_matrix):
        """Orders the columns such that the classes come first, then UNK and UNC."""
        columns = confusion_matrix.index.tolist() + ['UNK', 'UNC']
        return confusion_matrix[columns]

    def __init__(self, configuration, sandbox, index, model_result):
        """Initializes a model result set instance

        Args:
            configuration (dict)
            sandbox (Sandbox)
            index (str)
            model_result (dict)
        """
        self._configuration = configuration
        self._sandbox = sandbox
        self._kp_uuid = model_result['KnowledgePackID'] if 'KnowledgePackID' in model_result else None
        self._index = index
        self._number_of_neurons = model_result['metrics']['validation'].get(
            'NeuronsUsed', 0)
        self._confusion_matrix = {'train': None,
                                  'validation': None, 'test': None}
        self.confusion_matrix_stats = {
            'train': None, 'validation': None, 'test': None}
        self._accuracy = {'train': None, 'validation': None, 'test': None}
        if model_result['metrics']['train']:
            try:
                self.confusion_matrix_stats['train'] = ConfusionMatrix(
                    model_result['metrics']['train'])
            except ConfusionMatrixException:
                pass
            self._confusion_matrix['train'] = self._order_columns(DataFrame.from_dict(
                model_result['metrics']['train']['ConfusionMatrix']).transpose())
            self._accuracy['train'] = model_result['metrics']['train']['ProperClassificationPercent']
        if model_result['metrics']['validation']:
            try:
                self.confusion_matrix_stats['validation'] = ConfusionMatrix(
                    model_result['metrics']['validation'])
            except ConfusionMatrixException:
                pass
            self._confusion_matrix['validation'] = self._order_columns(DataFrame.from_dict(
                model_result['metrics']['validation']['ConfusionMatrix']).transpose())
            self._accuracy['validation'] = model_result['metrics']['validation']['ProperClassificationPercent']
        if model_result['metrics']['test']:
            try:
                self.confusion_matrix_stats['test'] = ConfusionMatrix(
                    model_result['metrics']['test'])
            except ConfusionMatrixException:
                pass
            self._confusion_matrix['test'] = self._order_columns(DataFrame.from_dict(
                model_result['metrics']['test']['ConfusionMatrix']).transpose())
            self._accuracy['test'] = model_result['metrics']['test']['ProperClassificationPercent']
        self.train_set = model_result['train_set']
        self.validation_set = model_result['validation_set']
        self.test_set = model_result['test_set']
        self.debug = model_result['debug']
        self.neurons = model_result['parameters']
        self.parameters = model_result['parameters']
        self._knowledgepack = None

    def _get_knowledgepack(self):
        if self._knowledgepack:
            return self._knowledgepack
        elif self._kp_uuid:
            self._knowledgepack = self._sandbox.knowledgepack(self._kp_uuid)
            return self._knowledgepack
        else:
            raise ModelException('This model does not have a knowledgepack.')

    @property
    def knowledgepack(self):
        """The model's KnowledgePack object"""
        return self._get_knowledgepack()

    def summarize(self, metrics_set='validation'):
        """Prints a formatted summary of the model metrics

        Args:
            metrics_set (optional[str]): options are 'validation' (the default), 'test', and 'train'
        """
        if not self._accuracy.get(metrics_set, None):
            print("No results for metric set ", metrics_set)
            return

        formatted_output = ('MODEL INDEX: {}\n'
                            'ACCURACY: {:.2f}\n'
                            'NEURONS: {}\n'
                            ).format(self._index, self._accuracy[metrics_set], self._number_of_neurons)
        print(formatted_output)

    def recognize_vectors(self, vectors):
        """Sends a DataFrame of feature vectors to the model's KnowledgePack for recognition.

        Args:
            vectors (DataFrame): where each row is a feature vector with column headings named the same as
            the features generated by the pipeline (order does not matter, but names do) (optional) metadata
            and label columns may be included

        Returns:
             (DataFrame): contains the results of recognition, including predicted class, neuron ID, and distance
        """
        results = []
        kp = self._get_knowledgepack()
        assert len(
            kp.feature_summary) > 0, "Error: No feature summary was found for this Knowledge Pack"

        feature_list = [feature['Feature'] for feature in kp.feature_summary]
        for i, vector in vectors[feature_list].astype(int).iterrows():
            vector_index = int(i)
            vector_dict = {'Vector': list(
                [int(x) for x in vector.values]), 'DesiredResponses': self._number_of_neurons}
            vector_result = kp.recognize_features(vector_dict)
            result = {'Index': vector_index,
                      'Predicted': vector_result['MappedCategoryVector'],
                      'NeuronID': vector_result['NIDVector'][:len(vector_result['MappedCategoryVector'])],
                      'Distance': vector_result['DistanceVector'][:len(vector_result['MappedCategoryVector'])]}
            for column in vectors.columns.difference(feature_list):
                result[column] = vectors.ix[i, column]
            results.append(result)
        df_result = DataFrame(results).set_index('Index', drop=True)
        df_result.index.name = None

        ordered_columns = ['Distance', 'NeuronID', 'Predicted'] + \
                          [i for i in df_result.columns if i not in [
                              'Distance', 'NeuronID', 'Predicted']]
        df_result = df_result[ordered_columns]

        return df_result

    def recognize_signal(self, capturefile=None, stop_step=False,
                         datafile=None, segmenter=True, lock=True, silent=True,
                         platform='emulator', compare_labels=False, **kwargs):
        """Sends a DataFrame of raw signals to be run through the feature generation pipeline and recognized.

        Args:
            capturefile (str): The name of a captured file uploaded throught the data capture lab
            datafile (str): The name of an uploading datafile
            platform (str): "emulator" or "cloud". The "emulator" will run compiled c code giving device exact results,
                 the cloud runs similary to training providing more flexibility in returning early results by setting the
                 stop step.
            stop_step (int): for debugging, if you want to stop the pipeline at a particular step, set stop_step
              to its index
            compare_labels (bool): If there are labels for the input dataframe, use them to create a confusion matrix
            segmenter (bool or FunctionCall): to suppress or override the segmentation algorithm in the original
              pipeline, set this to False or a function call of type 'segmenter' (defaults to True)
            lock (bool, True): If True, waits for the result to return before releasing the ipython cell.


        Returns:
            (DataFrame, dict): a dataframe containing the results of recognition and a dictionary containing the
            execution summary and the confusion_matrix when labels are provided.

            - execution_summary: a summary of which steps ran in the execution engine
            - confusion_matrix: a confusion matrix, only if the input data has a 'Label' column

        """

        kp = self._get_knowledgepack()

        return kp.recognize_signal(capture=capturefile, datafile=datafile,
                            stop_step=stop_step, segmenter=segmenter, platform=platform, get_result=True, compare_labels=compare_labels)


    def kill_pipeline(self):
        kp = self._get_knowledgepack()
        kp.stop_recognize_signal()

    def __str__(self, metrics_set='validation'):
        output = ('MODEL INDEX: {0}\n'
                  'ACCURACY: {1:.1f}\n'
                  'NEURONS: {2}\n'
                  ).format(self._index, self._accuracy[metrics_set], self._number_of_neurons)
        output += str(self.confusion_matrix_stats[metrics_set])
        return output


class Configuration(object):

    def __init__(self, result_set, sandbox, config_result):
        """Initializes a configuration instance - the container for all models generated by a TVO configuration."""
        self._result_set = result_set
        self._sandbox = sandbox
        self._training_algorithm = config_result['config']['optimizer']
        self._validation_method = config_result['config']['validation_method']
        self._classifier = config_result['config']['classifier']
        self._metrics = config_result['metrics'][0]
        self._parameters = {k: v for (k, v) in config_result['config'].items() if
                            k not in ['optimizer', 'validation_method', 'classifier']}
        self._models = []
        for index, model in config_result['models'].items():
            self._models.append(ModelMetrics(
                self, self._sandbox, index, model))
        self.sort_models()

    @property
    def models(self):
        return self._models

    @property
    def average_accuracy(self, metrics_set='validation'):
        """Returns the average accuracy for a set of model metrics.

        Args:
            metrics_set (optional[str]): options are 'validation' (the default), 'test', and 'train'
        """
        accuracies = [m._accuracy[metrics_set] for m in self._models]
        return sum(accuracies) / float(len(accuracies))

    def sort_models(self, metric='accuracy', metrics_set='validation'):
        """Sorts the configuration's models by a given metric or property.

        Args:
            metric (optional[str]): options are 'accuracy' (the default), 'index', and 'number_of_neurons'
            metrics_set (optional[str]): options are 'validation' (the default), 'test', and 'train'
        """
        if metric == 'accuracy':
            self._models.sort(
                key=lambda x: x._accuracy[metrics_set], reverse=True)
        elif metric == 'number_of_neurons':
            self._models.sort(key=lambda x: x._number_of_neurons)
        elif metric == 'index':
            self._models.sort(key=lambda x: x._index)

    def get_model_by_index(self, index):
        """Returns the model of the given index (name)."""
        return [model for model in self._models if model._index == index].pop()

    def print_models(self):
        """Prints a summary and confusion matrix of each model in the configuration."""
        for model in self._models:
            print(model)

    def summarize(self, metrics_set='validation', report_number=5):
        """Prints a basic summary of the configuration and its models.

        Args:
            metrics_set (optional[str]): options are 'validation' (the default), 'test', and 'train'
            report_number (int):
        """
        print(self)
        self.metrics()
        print("--------------------------------------\n")
        print("{} MODEL RESULTS : SET {}\n".format(
            self._validation_method.upper(), metrics_set.upper()))
        for index, model in enumerate(self._models):
            if index >= report_number:
                break
            model.summarize(metrics_set)

    def metrics(self):
        average_metrics = ['f1_score', 'precision', 'sensitivity',
                           'f1_score_std', 'precision_std', 'sensitivity_std']

        for metric in average_metrics:
            if self._metrics[metric] is None:
                self._metrics[metric] = 0


        if set(self._metrics.keys()).issuperset(set(average_metrics)):
            print("AVERAGE METRICS:")
            print("F1-SCORE:    {:.1f}   sigma {:.2f}\nSENSITIVITY: {:.1f}   sigma {:.2f}\nPRECISION:   {:.1f}   sigma {:.2f}\n".format(self._metrics['f1_score'], self._metrics['f1_score_std'],
                                                                                                                                        self._metrics['precision'], self._metrics[
                                                                                                                                            'precision_std'],
                                                                                                                                        self._metrics['sensitivity'], self._metrics['sensitivity_std'],))

    def __str__(self):
        return ('TRAINING ALGORITHM: {0}\nVALIDATION METHOD:  {1}\nCLASSIFIER:         {2}\n'
                ).format(self._training_algorithm, self._validation_method, self._classifier)


class ModelResultSet(object):
    """Base class for a model result set object."""

    def __init__(self, project, sandbox):
        """Initializes a model result set instance."""
        self._connection = sandbox._connection
        self._project = project
        self._sandbox = sandbox
        self._results_dict = {}
        self._input_data = None
        self._configurations = []

    @property
    def feature_vectors(self):
        return self._input_data

    @property
    def input_data(self):
        return self._input_data

    @property
    def configurations(self):
        return self._configurations

    def _to_dict(self):
        return self._results_dict

    def _format_configuration(self, config):
        return ('Training Algorithm: {optimizer}\n'
                'Validation Method: {validation_method}\n'
                ).format(**config)

    def sort_models(self, metric='accuracy', metrics_set='validation'):
        """Sorts the models within all configurations by a given metric or property.

        Args:
            metric (optional[str]): options are 'accuracy' (the default), 'index', and 'number_of_neurons'
            metrics_set (optional[str]): options are 'validation' (the default), 'test', and 'train'
        """
        for configuration in self._configurations:
            configuration.sort_models(metric, metrics_set)

    def summarize(self, metrics_set='validation', report_number=5):
        """Prints a basic summary of each configuration and its models.

        Args:
            metrics_set (optional[str]): options are 'validation' (the default), 'test', and 'train'
        """
        for config in self._configurations:
            config.summarize(metrics_set, report_number=report_number)

    def get_knowledgepack_by_index(self, config_index, model_index):
        """Returns the KnowledgePack of the given configuration index and model index."""
        knowledgepack = [kp for kp in self._sandbox.knowledgepack() if
                         kp.configuration_index == config_index and kp.model_index == model_index]
        if knowledgepack:
            return knowledgepack.pop()
        else:
            return 'No knowledgepack found for configuration {0}, model {1}.'.format(config_index, model_index)

    def initialize_from_dict(self, init_dict):
        self._results_dict = init_dict
        if init_dict.get('input_data', None):
            self._input_data = DataFrame.from_dict(
                json.loads(init_dict['input_data']))
        for _, config in self._results_dict['configurations'].items():
            self.configurations.append(
                Configuration(self, self._sandbox, config))
