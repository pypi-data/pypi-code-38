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


import uuid
import itertools
import copy
import json
from tempfile import NamedTemporaryFile
from os import remove
import time
import logging
from pandas import DataFrame, Series
from requests.exceptions import HTTPError
from six import string_types

from sensiml.base.exceptions import DuplicateValueError
import sensiml.base.utility as utility
from sensiml.base.snippets import generate_pipeline
from sensiml.base.exceptions import *
try:
    from sensiml.visualize import Visualize
except:
    print("skipping visualization library")
    pass


logger = logging.getLogger(__name__)


class InvalidParameterException(Exception):
    pass


class InvalidModelException(Exception):
    pass


class PlatformNotSpecifiedException(Exception):
    pass


class Pipeline(object):
    """Base class of a pipeline object"""

    def __init__(self, kb, name=None):
        self._kb = kb
        self._project = kb.project
        self._results = None
        self._stats = None
        self._dataset = None
        self._async = None
        self._save = False
        self._tvo_call = None
        self._generator_index = 0
        self._selector_index = 0
        self._classifier_call = None
        self._training_algorithm_call = None
        self._validation_call = None
        self._group_columns = None
        self._label_column = None
        self._data_columns = None

        if name:
            self._id = "{}".format(name)
        else:
            self._id = "{}_sandbox".format(time.time())

        self._sandbox = self._project.sandboxes.get_or_create_sandbox(self._id)

        logger.debug('kb_dsk_pipeline_instance:' + self._id)

    @property
    def name(self): return self._id

    @property
    def data_columns(self):
        if self._data_columns:
            return sorted(list(self._data_columns))
        return self._data_columns

    @data_columns.setter
    def data_columns(self, value):
        if isinstance(value, list):
            if len(set(value)) is not len(value):
                raise DuplicateValueError()
            self._data_columns = set(map(lambda x: str(x), value))
        else:
            print("Error: data_columns must be a list.")
            return

        upper_case_data_columns = set(
            map(lambda x: x.upper(), self.data_columns))

    @property
    def label_column(self):
        return self._label_column

    @label_column.setter
    def label_column(self, value):
        if isinstance(value, str) or isinstance(value, string_types):
            self._label_column = str(value)
        else:
            print("Error: label_column must be a string.")

    @property
    def group_columns(self):
        if self._group_columns:
            return sorted(list(self._group_columns))
        return self._group_columns

    @group_columns.setter
    def group_columns(self, value):
        if isinstance(value, list):
            if len(set(value)) is not len(value):
                raise DuplicateValueError()
            self._group_columns = set(map(lambda x: str(x), value))
        else:
            print("Error: group_columns must be a list.")

    def get_knowledgepack(self, uuid):
        """retrieve knowledgepack by uuid from the server

        Args:
            uuid (str): unique identifier for knowledgepack

        Returns:
            TYPE: a knowledgepack object
        """
        return self._sandbox.knowledgepack(uuid)

    def list_knowledgepacks(self):
        """Lists all of the projects on kb cloud associated with current pipeline

        Returns:
            DataFrame: projects on kb cloud
        """

        knowledgepacks = self._sandbox.get_knowledgepacks().rename(
            columns={'name': 'Name', 'project_name': 'Project', 'sandbox_name': 'Pipeline', 'uuid': 'kp_uuid', 'created_at':'Created'})
        if len(knowledgepacks) < 1:
            print("No Knowledgepacks stored for this pipeline on the cloud.")
            return None

        return knowledgepacks[['Name', 'Created', 'Project', 'Pipeline', 'kp_uuid']]

    def set_columns(self, data_columns=None, group_columns=None, label_column=None):
        """Sets the columns for group_columns, data_columns and the label column
         to be used in the pipeline. This will automatically handle label column, ignore columns, group columns
         and passthrough columns for the majority of pipelines. For pipelines that need individually specified
         column attributes, set them in the step command.

        Args:
            data_columns (None, list): List of sensor data streams to use.
            group_columns (None, list): List of columns to use when applying aggregate functions
                and defining unique subsets on which to operate.
            label_column (None, str): The column name containing the ground truth label.

        """
        if data_columns:
            self.data_columns = data_columns

        if label_column:
            self.label_column = label_column

        if group_columns:
            self.group_columns = group_columns

    def get_pipeline_length(self):
        """
        Returns:
            int: The current length of the pipeline.
        """
        return len(self._sandbox._pipeline._steps)

    def get_function_type(self, name):
        """
        Returns:
            str: The type of a function.
        """
        return self._kb.functions.get_function_by_name(name).type

    def describe(self, show_params=True, show_set_params=False):
        """Prints out a description of the pipeline steps and parameters

        Args:
            show_params (bool, True): Include the parameters in the pipeline description

        """
        self._sandbox.pipeline.describe(
            show_params=show_params, show_set_params=show_set_params)

    def rehydrate_knowledgepack(self, model=None, uuid=None, replace=True):
        """Replace the executing cell with pipeline code for a knowledge Pack

        Args:
            model (model, knowledgepack, None): pass in a model to build a pipeline from that
        """

        return self.rehydrate(model=model, replace=replace, kp_summary=True, uuid=uuid)

    def rehydrate_pipeline(self, model=None, uuid=None, replace=True):
        """Replace the executing cell with pipeline code for the current pipeline or
        pipeline that generated the model

        Args:
            model (model, knowledgepack, None): pass in a model to build a pipeline from that
        """

        return self.rehydrate(model=model, replace=replace, kp_summary=False, uuid=uuid)

    def rehydrate(self, model=None, replace=True, kp_summary=False, uuid=None):
        """Replace the executing cell with pipeline code for either a model or
        pipeline.

        Args:
            model (model, knowledgepack, None): pass in a model to build a pipeline from that
            replace (boolean, True): replace the executing cell with pipeline code
        """
        if isinstance(uuid, str):
            knowledgepack = self._kb.get_knowledgepack(uuid)

        if hasattr(model, "knowledgepack"):
            knowledgepack = model.knowledgepack
        else:
            knowledgepack = model

        steps = None

        if knowledgepack:
            try:
                if kp_summary:
                    if not knowledgepack.knowledgepack_summary:
                        print("Knowledpack doesn't have a summary.")
                        return
                    steps = [knowledgepack.pipeline_summary[0]] +\
                        knowledgepack.knowledgepack_summary['recognition_pipeline'] +\
                        [knowledgepack.pipeline_summary[-1]]
                else:
                    steps = knowledgepack.pipeline_summary
            except:
                raise InvalidModelException(
                    "Model Pipeline was not able to be generated.")

        else:
            steps = self._sandbox.pipeline.to_list()

        # reindex min max scale
        if knowledgepack and kp_summary:
            min_max_step = None
            for index in range(len(steps)-1, 0,-1):
                if steps[index]['name'] == "Min Max Scale":
                    min_max_step = index

            # Set the Min Max Scale features correctly

            feature_min_max = steps[min_max_step]['inputs']['feature_min_max_parameters']
            rescaled_features_min_max = {'maximums': {}, 'minimums':{}}

            for factor in ['maximums', 'minimums']:
                generator_index = 0
                last_index = None
                for _, key in enumerate(sorted(feature_min_max['maximums'].keys())):
                    if last_index != key.split('_')[1]:
                        last_index = key.split('_')[1]
                        generator_index += 1

                    rescaled_features_min_max[factor]['gen_' +\
                                                    '{0:04}'.format(generator_index) +\
                                                      '_{}'.format('_'.join(key.split('_')[2:]))] =   feature_min_max[factor][key]

            steps[min_max_step]['inputs']['feature_min_max_parameters'] = rescaled_features_min_max

            # Add a custom feature selector to handle family generators such as histogram

            fs_dict = generate_custom_feature_selector(
                knowledgepack.feature_summary)

            fs_step = {'type': 'selectorset',
                       'name': 'selector_set',
                        'set': [
                                {'inputs': {"custom_feature_selection": fs_dict},
                                 'function_name': 'Custom Feature Selection By Index'},
                            ],
                        'inputs': {'remove_columns': [],
                                   'passthrough_columns': steps[min_max_step]['inputs']['passthrough_columns'],
                                   'input_data': steps[min_max_step]['inputs']['input_data'],
                                   'label_column': steps[-1]['label_column'],
                                   'number_of_features': len(knowledgepack.feature_summary),
                                   'feature_table': steps[min_max_step]['outputs'][1],
                                   'cost_function': 'sum'},
                        'outputs': ['temp.selector_set0', 'temp.features.selector_set0'],
                        'refinement': {}
                       }

            steps.insert(min_max_step, fs_step)

        return generate_pipeline(self._kb.functions.function_list,
                          steps, replace=replace)

    def submit(self, lock=False):
        """Submit a pipeline asynchronously to SensiML Cloud for execution."""
        try:
            self._sandbox.submit()

        except HTTPError:
            return False

        return True

    def execute(self, wait_time=15, silent= True, describe=True, **kwargs):
        """Execute pipeline asynchronously and check for results.

        Args:
            wait_time (int, 10): Time to wait in between status checks.
            silent (bool, True): Silence status updates.
        """
        if describe:
            print("Executing Pipeline with Steps:\n")
            self.describe(show_params=False)

        status = self.submit()

        time.sleep(5)
        return self.get_results(lock=True, wait_time=wait_time, silent=silent, **kwargs)

    def auto(self, auto_params, run_parallel=True, lock=True, silent=True, renderer=None):
        """Execute automated pipeline asynchronously. 

        The automated pipeline is used to find optimal parameters with a genetic algorithm. The genetic algorithm starts with a user-defined 
        randomized population (pipelines) and generates models from them and tests them, keeps a subset of high-performing combinations, and 
        then recombines those "survivors" and repeats the process over again. The offspring of good parameter combinations are usually also 
        good and sometimes are significantly better than their parents. As the algorithm iterates each successive generation, it often finds a 
        near-optimal model without trying as many configurations. The algorithm terminates when the desired number of iteration is completed.

        The created pipelines are run in parallel in SensiML servers and results are ranked by the fitness score which takes into account the 
        model's F1 score, precision, sensitivity, and other metrics. The automation options and definition of the performance metrics are 
        given below.

        Args:
            seed (str): Pipeline templates that focus on different feature libraries. Options and definitions are given below.
                Basic Features: Generates a set of all-purpose, high-performance features using statistical, energy, and rate of change feature 
                    generators. The seed then performs feature selection and model generation algorithms with a genetic algorithm to optimize 
                    pipeline parameters.
                Advanced Features: Generates a comprehensive set of features using statistical, energy, amplitude, shape, time, and rate of 
                    change feature generators. The seed then performs feature selection and model generation algorithms with a genetic algorithm 
                    to optimize pipeline parameters.
                Histogram_Features: Generates a set of histogram features and then performs feature selection and model generation algorithms 
                    with a genetic algorithm to optimize pipeline parameters.
                Downsampled_Features: Generates a set of downsampled features and then performs feature selection and model generation algorithms 
                    with a genetic algorithm to optimize pipeline parameters.
                Custom: Uses the user-defined pipeline to extract features and then searches for optimal parameters for the feature selection step, 
                    if defined, and the model generation step (required) using a genetic algorithm.
                No Feature Generation: Takes a given set of features and finds the best feature selection and model generation parameters.

            params (dict) : Parameters of the genetic algorithm to optimize the pipelines. Definition and options of the parameters are given below.
                sample_rate, (int, 100): Sample rate of sensor data
                smoothing_factor, (int, 9): Smoothing factor that will be used in the feature generator algorithms.
                search_steps, (list, ['selectorset', 'tvo']): it is used to define which libraries in the pipelines will be optimized.
                population_size, (int, 10): Initial number of randomly created pipelines.
                iterations, (int, 1): Repetition number of optimization process
                mutation_rate, (float, 0.1): Random changes from the previous population.
                recreation_rate, (float, 0.1): Rate of randomly created pipelines for next generation.
                survivor_rate, (float, 0.5): Ratio of the population that will be transferred to next generation.
                number_of_models_to_return, (int, 5): Number of pipeline that will return to user.
                run_parallel, (bool, True): Run in parallel in KB cloud.
                allow_unknown, (bool, False): Allows creating unknown prediction results for the vectors. A vector is classified as an unknown if it 
                    cannot be recognized by any neurons.
                validation_method, (Stratified Shuffle Split): Validation method that will be used in optimization
                fitness (dict): Fitness parameters are combination of statistical and cost variables. It is used to evaluate the performance of 
                    the models found by the algorithm. The user will define the coefficient scores for the parameters to define the priority of 
                    the parameters in the fitness score. Definition and options of the parameters are given below.

                    statistical variables:
                        accuracy: The degree of correctness of all vectors 
                        f1_score: Measures of the test's accuracy
                        precision: Proportion of positive identifications that is actually correct 
                        sensitivity: Measures of the proportion of actual positives that are correctly identified
                        specificity: Measures of the proportion of actual negatives that are correctly identified 
                        positive_predictive_rate: Ratio of "true positive" is the event that the test makes a positive prediction
                    cost variables:
                        neurons: Number of neurons that used in the model 
                        features: Number of features that used in the model,

            lock (bool, False): Ping for results every 30 seconds until the process finishes.
            silent (bool, True): Silence status updates.

        Example:

            activity_data = dsk.datasets.load_activity_raw()
            dsk.upload_dataframe('activity_data.csv', activity_data, force=True)

            dsk.pipeline.reset()
            dsk.pipeline.set_input_data('activity_data.csv', 
                                data_columns = ['accelx', 'accely', 'accelz', 'gyrox', 'gyroy', 'gyroz'],
                                group_columns = ['Subject','Class', 'Rep'],
                                label_column = 'Class')

            dsk.pipeline.add_transform("Windowing", params={"window_size": 100, "delta": 100 })

            results, summary = dsk.pipeline.auto({'seed': 'Basic Features', 
                                                  'params':{"search_steps": ['selectorset', 'tvo'],
                                                            "population_size": 10,
                                                            "iterations": 1,
                                                            "mutation_rate": 0.1,
                                                            "recreation_rate": 0.1,
                                                            "survivor_rate": 0.5,
                                                            "number_of_models_to_return": 5,
                                                            "run_parallel": True,
                                                            "allow_unknown": False,
                                                            "validation_method": "'Stratified Shuffle Split'",
                                                            "fitness": {'neurons': 0.5, 
                                                                        'accuracy': 1.0, 
                                                                        'f1_score': 0.0, 
                                                                        'features': 0.3, 
                                                                        'precision': 0.0, 
                                                                        'sensitivity': 0.7, 
                                                                        'specificity': 0.0, 
                                                                        'positive_predictive_rate': 0.0},

                                                              }})

            results.summarize()



        """
        if self._group_columns:
            auto_params['group_columns'] = list(self._group_columns)
        if self._data_columns:
            auto_params['data_columns'] = list(self._data_columns)
        if self._label_column:
            auto_params['label_column'] = self._label_column

        seed = self._kb.seeds.get_seed_by_name(auto_params['seed'])
        success = self._sandbox.auto(
            auto_params=auto_params, seed=seed, renderer=renderer)
        if success:
            return self.get_results(lock=lock, silent=silent, renderer=renderer)
        return (None, None)

    def grid_search(self, grid_params, run_parallel= True, lock=True, silent=True):
        """Grid search is a parameter optimization method that exhaustivley searches over a gridded parameter space.
        Grid search returns will return the score each parameter combination for f1, precision and sensitivity so that
        you can choose the best performing combination to build a knowledge pack with.

        Args:
            grid_params (dict): Grid search parameters.
            run_parallel (bool, True): Run grid search in parallel in KB cloud.
            lock (bool, False): Ping for results every 30 seconds until the process finishes.


        grid_params is a nested python dictionary object.

            grid_params = {"Name Of Function":{"Name of Parameter":[ A, B, C]}}

        Where A, B and C are the parameters to search over. Additionally, for each step you may want to search over more than
        one of a functions configurable parameters. To do this simply add another element to the functions dictionary.

            grid_params = {"Name Of Function":{"Name of Parameter 1":[ A, B, C],
                                            "Name of Parameter 2":[ D, E]}}

        This will tell grid search to search over 6 different parameter spaces.

        You can also specify more than one step to search over in grid params. This is done by adding another element to
        the function level of the grid_params dictionary.

            grid_params = {"Name Of Function":{"Name of Parameter 1":[ A, B, C],
                                            "Name of Parameter 2":[ D, E]},
                          "Name of Function 2":{"Name of Paramter":[1, 2, 3, 4, 5, 6]}}

        Example:

            grid_params = {'Windowing':{"window_size": [100,200],'delta':[100]},
                        'selector_set': {"Recursive Feature Elimination":{'number_of_features':[10, 20]}},
                        'Hierarchical Clustering with Neuron Optimization': {'number_of_neurons':[10,20]}
                        }

            results, stats = dsk.pipeline.grid_search(grid_params)

        """

        print("Executing Pipeline with Steps:\n")
        self.describe(show_params=False)

        self._sandbox.grid_search(grid_params= grid_params, run_parallel= run_parallel)

        time.sleep(5)
        return self.get_results(lock=lock, silent=silent)

    def autosegment_search(self, params, run_parallel=True, lock=True, silent=True):
        """Execute auto segment search pipeline asynchronously.

        Args:
            params (dict): Automation parameters for segment search.
            run_parallel (bool, True): Run in parallel in KB cloud.
            lock (bool, False): Ping for results every 30 seconds until the process finishes.
            silent (bool, True): Silence status updates.
        """
        print("Running AutoSegment Pipeline\n")

        # check that the pipeline is correct for autosegmentation.
        for step_index, step in enumerate(self._sandbox.pipeline.to_list()):
            if step_index == 0:
                if step['type'] != 'featurefile':
                    print("First step in pipeline must be a featurefile")
                    return None, None
            else:
                if step['type'] != 'transform':
                    print("Pipeline can only contain sensor transforms.")
                    return None, None

        self._sandbox.autosegment_search(params, run_parallel=run_parallel)

        return self.get_results(lock=lock, silent=silent)

    def get_results(self,  lock=False, wait_time=15, silent=False, page_index=0, renderer=None, **kwargs):
        """Retrieve status, results from the kb cloud for the current pipeline.

        Args:
            results to retrieve. The default is the last type that was run.
            lock (bool, False): This will lock the process and continuously ping the KB cloud
            for the status of the pipeline process.
            wait_time (int, 30): The time to wait between individual status checks.
            silent (bool,  False): This will silence updates to every 4th update check.
            page_index (int, 0): The page desired if the result is multi-paged (1-based)

        Returns:
            results (DataFrame or model result): This is the result of the last executed pipeline step.
            stats (dictionary): A dictionary containing the execution summary, features and other
            summary statistics
        """

        self._results = utility.wait_for_pipeline_result(self._sandbox,
                                                         lock=lock,
                                                         wait_time=wait_time,
                                                         silent=silent,
                                                         page_index=page_index,
                                                         renderer=renderer,
                                                         **kwargs)

        return self._results[0], self._results[1]

    def data(self, pipeline_step, page_index=0):
        """Retrieves results from a specific pipeline step in the pipeline from stored values in kbcloud
        after execution has been performed.

        Args:
            pipeline_step (int): Pipeline step to retrieve results from.
            page_index (int): Index of data to get.

        Returns:
            A ModelResultSet if the selected pipeline step is TVO step, otherwise the output of the pipeline
            step is returned as a DataFrame.
        """
        try:
            return self._sandbox.intermediate_data(pipeline_step=pipeline_step, page_index=page_index)[0]
        except HTTPError:
            return None

    def visualize_features(self, feature_vector, label_column=None):
        """Makes a plot of feature vectors by class to aid in understanding your model

        Args:
            feature_vector (DataFrame): Dataframe containing feature vectors and label column
        """
        if label_column is None:
            label_column = self.label_column

        return Visualize(feature_vector=feature_vector,
                  label=label_column).plot_features()

    def visualize_neuron_array(self, model, feature_vector, featureX, featureY, neuron_alpha=.2):
        """Makes a plot of feature vectors by class to aid in understanding your model

        Args:
            model (model/knowledpack): The model or knowledpack to use for plotting the neurons
            feature_vector (DataFrame): Dataframe containing feature vectors and label column
            featureX (str): The name of the feature for the x axis
            featureY (str): The name of the feature for the y axis

        """

        if hasattr(model, "knowledgepack"):
            if model.knowledgepack.device_configuration.get("classifier", None) != 'PME':
                print(
                    "Visualize neuron array is only supported for models using the PME classifier.")
                return

        Visualize(model=model, feature_vector=feature_vector,
                  label=self.label_column).neuron_feature_map(featureX, featureY, neuron_alpha=neuron_alpha)

    def clear_cache(self):
        """Deletes the cache on KB cloud for this pipeline."""
        if self._sandbox is not None:
            self._sandbox.delete_cache()

    def reset(self, delete_cache=False):
        """ Reset the current pipeline steps.

        Args:
            delete_cache (bool, False): Delete the cache from KB cloud.
        """
        self._sandbox.clear()
        self._sandbox.update()
        self._generator_index = 0
        self._selector_index = 0
        self._data_columns = ''
        self._tvo_call = None
        self._classifier_call = None
        self._training_algorithm_call = None
        self._validation_call = None
        if self.group_columns:
            self._group_columns.discard('SegmentID')

        if delete_cache:
            print(
                "\n\nWarning:: You have cache set to delete, this will cause your pipelines to run slower!\n\n")
            self.clear_cache()

    def set_knowledgepack_platform(self, *args, **kwargs):
        """Backwards compatible call to set_device_configuration"""
        logger.warning(
            'Deprecated: Please use set_device_configuration instead.')
        self.set_device_configuration(*args, **kwargs)

    def stop_pipeline(self):
        """Kills a pipeline that is running on KB cloud."""
        self._sandbox.kill_pipeline()

    def delete_sandbox(self):
        """Clears the local pipeline steps, and delete the sandbox from the KB cloud."""
        self.reset(delete_cache=True)

        if self._sandbox is not None:
            self._sandbox.delete()

    def _preprocess(self, segmenterid):
        """ adds the segmenter preprocess steps to the pipeline """

        try:
            segmenter = self._project.get_segmenters().loc[segmenterid]
        except TypeError:
            print("Error. Segmenter associated with this query does not exist.")
            return

        if segmenter.preprocess is None:
            return

        preprocess = json.loads(segmenter.preprocess)

        for i in range(len(preprocess.keys())):
            transform = preprocess[str(i)]
            self._add_transform({'name': transform['params']['name'], 'params': transform['params']['inputs']}, False)
            self._data_columns.add(transform['actual_name'])
            print("Adding Preprocess Transform {}".format(
                transform['params']['name']))

    def set_input_query(self, name):
        """Set the input data to be a stored query.

        Args:
            name (str): The name of the saved query.
        """

        query_call = self._kb.functions.create_query_call(name)
        query_call.query = self._project.queries.get_query_by_name(name)

        self._dataset = query_call

        label_column = query_call.query.label_column

        self.set_columns(query_call.query.columns._columns,
                         query_call.query.metadata_columns._columns+ \
                             [label_column, 'SegmentID'],
                         label_column)

        self._add_initial_data()

        self._preprocess(query_call.query.segmenter)


    def set_input_data(self, name, data_columns=None,
                       group_columns=None,
                       label_column=None):
        """Use a data file that has been uploaded as your data source.

        Args:
            name (str, list): The name of the data file or list of datafiles in SensiML cloud.
            data_columns (list, required): Array of data streams to use in model building.
            group_columns (list, required): The List of columns to use when applying aggregate functions
                and defining unique subsets on which to operate.
            label_column (str, required): The column with the true classification.

        """

        self.set_columns(data_columns, group_columns, label_column)

        if isinstance(name, list):
            for index, csv_name in enumerate(name):
                if csv_name[-4:] != '.csv':
                    name[index] = "{}.csv".format(csv_name)
        else:
            if name[-4:] != '.csv':
                name = "{}.csv".format(name)

        call = self._kb.functions.create_featurefile_call(name)
        self._dataset = call
        self._dataset.data_columns = self.data_columns
        self._dataset.group_columns = self.group_columns
        self._dataset.label_column = self.label_column

        self._add_initial_data()

    def set_input_capture(self, names):
        """Use a data file that has been uploaded as your data source.

        Args:
            name (str,list): single capture or list of captures file names to use in SensiML cloud.

        """

        self.set_columns(list(self._project.columns()), ['Subject'], None)

        call = self._kb.functions.create_capturefile_call(names)
        self._dataset = call
        self._dataset.data_columns = self.data_columns

        self._add_initial_data()

    def add_linear_step(self, func):
        """Add a step to the pipeline. Automatically tie the previous step and current step.

        Args:
            func (function): A sensiml function method call
        """
        self._sandbox.add_linear_step(func)

    def add_segmenter(self, name, params={}):
        """Add a Segmenter to the pipeline.

        Args:
            name (str): Name of the segmenter method to add.
            params (dict, optional): Dictionary containing the parameters of the transform.

        """

        self._add_transform({'name': name, 'params': params })

    def add_transform(self, name, params={}, overwrite=True):
        """Add a Transform to the pipeline.

        Args:
            name (str): Name of the transform method to add.
            params (dict, optional): Dictionary containing the parameters of the transform.
            overwrite (boolean): when adding multiple instances of the same transform, set
                overwrite to False for the additional steps and the first instance will not
                be overwritten (default is True)

        """

        self._add_transform({'name': name, 'params': params }, overwrite)

    def add_feature_generator(self, feature_generators, params={}, function_defaults={}):
        """Add a feature generator set to the pipeline.

        Args:
            feature_generators (list): List of feature generators. As names or dictionaries.
            params (dict, {}}): Parameters to apply to the feature generator set.
            function_defaults (dict,{}}): Parameters to apply to all individual feature generators.

        Examples:
            >>> # Add a single feature generator
            >>> dsk.pipeline.add_feature_generator([{'name': 'Downsample', 'params': {'new_length': 5}}, {'name': 'Mean'}],
                                                   function_defaults = {'columns': sensor_columns})

            >>> # Call multiple functions by name when they use the same same function defaults
            >>> dsk.pipeline.add_feature_generator(['Mean', 'Standard Deviation', 'Skewness', 'Kurtosis', '25th Percentile',
                                                   '75th Percentile', '100th Percentile', 'Zero Crossing Rate'],
                                                   function_defaults = {'columns': sensor_columns})

            >>> # Call multiple functions using function defaults
            >>> dsk.pipeline.add_feature_generator([{'name': 'Downsample', 'params': {'new_length': 5}}, {'name': 'Mean'}],
                                                    function_defaults = {'columns': sensor_columns})

            >>> # Call multiple functions by subtype which use different parameters; note all subtypes will take the same inputs
            >>> dsk.pipeline.add_feature_generator([{'subtype_call': 'Area', 'params': {'sample_rate': 100, 'smoothing_factor': 9}},
                                                    {'subtype_call': 'Time', 'params': {'sample_rate': 100}},
                                                    {'subtype_call': 'Rate of Change'},
                                                    {'subtype_call': 'Statistical'},
                                                    {'subtype_call': 'Energy'},
                                                    {'subtype_call': 'Amplitude', 'params': {'smoothing_factor': 9}},
                                                    {'subtype_call': 'Physical', 'params': {'sample_rate': 100}}
                                                    ],
                                                    function_defaults={'columns': sensor_columns},
                                                   )

            >>> # Mix subtype and specify additional feature generators
            >>> dsk.pipeline.add_feature_generator([{'subtype_call': 'Statistical'},
                                                    {'name': 'Downsample', 'params': {'new_length': 5}},
                                                    ],
                                                    function_defaults={'columns': sensor_columns},
                                                    )

            >>> # Call the same feature generators multiple times with different parameters
            >>> dsk.pipeline.add_feature_generator([{'name': 'Downsample', 'params': {'new_length': 5, 'columns': sensor_columns[0]}},
                                                    {'name': 'Downsample', 'params': {'new_length': 12}},
                                                    ],
                                                    function_defaults={'columns': sensor_columns},
                                                    )

        """
        # if we get a list of strings
        feature_generators = copy.deepcopy(feature_generators)
        if isinstance(feature_generators[0], str):
            feature_generators = list(map(lambda x: {"name": x,"params":{}}, feature_generators))
            for fg in feature_generators:
                for default_param in list(function_defaults.keys()):
                    if default_param not in list(fg['params'].keys()):
                        fg['params'].update(
                            {default_param: function_defaults.get(default_param)})

        # if we get a list of dicts
        elif isinstance(feature_generators[0], dict):
            for fg in feature_generators:
                if fg.get('params', None) is None:
                    fg['params'] = {}
                for default_param in list(function_defaults.keys()):
                    if default_param not in list(fg['params'].keys()):
                        fg['params'].update(
                            {default_param: function_defaults.get(default_param)})

        else:
            print("Feature Generator was improperly specified. See Documentation (dsk.pipeline.add_feature_generator?) for examples.")
            raise InvalidParameterException(
                "Feature Generator was improperly specified. See Documentation (dsk.pipeline.add_feature_generator?) for examples.")

        self._add_feature_generator(feature_generators, params)

    def add_feature_selector(self, feature_selectors, params={}):
        """Add a feature selection set to the pipeline.

        Args:
            feature_selectors (List): List of dictionaries containing feature selectors
            params (dict, {}): Parameters of the feature selector set.

        Examples:
            >>> dsk.pipeline.add_feature_selector([{"name":"Recursive Feature Elimination", "params":{"method":"Log R"}}],
            >>>                                    params = {"number_of_features":20})
        """

        self._add_feature_selector(feature_selectors, params)

    def set_validation_method(self, name, params={}):
        """Set the validation method for the tvo step.

        Args:
            name (str): Name of the validation method to use.
            params (dict, optional): Parameters for the validation method.

        """
        self._validation_call = call = self._kb.functions.create_validation_method_call(
            name)
        for k, v in params.items():
            setattr(call, k, v)

    def set_classifier(self, name, params={}):
        """Classification method for the TVO step to use.

        Args:
            name (str): Name of the classification method.
            params (dict, optional): Parameters of the classification method.
        """
        self._classifier_call = call = self._kb.functions.create_classifier_call(
            name)
        for k, v in params.items():
            setattr(call, k, v)

    def set_training_algorithm(self, name, params={}):
        """Training algorithm for the TVO step to use.

        Args:
            name (str): Name of the training algorithm.
            params (dict, optional): Parameters of the training algorithm.
        """
        self._training_algorithm_call = call = self._kb.functions.create_training_algorithm_call(
            name)
        for k, v in params.items():
            setattr(call, k, v)

    def set_tvo(self, params={}):
        """Description of the train, validate optimize step, which consists of a training algorithm,
        validation method and classifier.

        Args:
            params (dict, optional): Parameters of the TVO step.

        Example:
            >>> dsk.pipeline.set_validation_method('Stratified K-Fold Cross-Validation', params={'number_of_folds':3})
            >>> dsk.pipeline.set_classifier('PME', params={"classification_mode":'RBF','distance_mode':'L1'})
            >>> dsk.pipeline.set_training_algorithm('Hierarchical Clustering with Neuron Optimization', params = {'number_of_neurons':10})
            >>> dsk.pipeline.set_tvo({'label_column':'Label', 'ignore_columns': ['Subject', 'Rep']})
        """
        self._tvo_call = call = self._kb.functions.create_train_and_validation_call(
            'tvo')
        for k, v in params.items():
            setattr(call, k, v)
        if(self._classifier_call and self._training_algorithm_call and self._validation_call):
            call.add_classifier(self._classifier_call)
            call.add_validation_method(self._validation_call)
            call.add_optimizer(self._training_algorithm_call)
        else:
            raise PipelineOrderException(
                'Set classifier, validation, and training_algorithm methods before calling.')

        self._add_tvo(self._tvo_call)

    def iterate_columns(self, fg, n_columns=None, columns= None):
        """ Builds Multiple Feature generators by iterating over the input columns

        Args:
            fg (dict): Single input feature generator folowing the standard format
            n_columns (int): The number of columns to return as a combination.
            columns (list): if None, will use the columns in the input feature generator, otherwise will use this list provided

        fg =  {'name':'Downsample with Min Max Scaling', 'params':{"columns": ['gyrZ','gyrX'] , "new_length": 15}}

        fg_new = dsk.pipeline.iterate_columns(fg, n_columns=1)

        >> print(fg_new)
        >> [{'name': 'Downsample with Min Max Scaling', 'params': {'columns': ['gyrX'], 'new_length': 15}},
            {'name': 'Downsample with Min Max Scaling', 'params': {'columns': ['gyrX'], 'new_length': 15}}]

        """


        if n_columns is None:
            function = self._kb.functions.get_function_by_name(fg['name'])
            n_columns = get_contract_column_type(function.input_contract)

            if n_columns is None or n_columns < 0:
                return [fg]

        if columns is None:
            columns = fg['params']['columns']

        column_list = itertools.combinations(columns, n_columns)

        fg_list = []
        tmp_fg = copy.deepcopy(fg)

        for column_combo in column_list:
            tmp_fg['params']['columns'] = list(column_combo)
            fg_list.append(copy.deepcopy(tmp_fg))

        return fg_list

    def _check_for_input_data(self):
        if len(self._sandbox._pipeline.to_list()) == 0:
            raise PipelineOrderException(
                "You must specify the input data before specifying additional steps")

    def _add_tvo(self, call):
        self._add_label_column(call)
        self._add_ignore_columns(call)

        self.tvo_index = self.get_pipeline_length()
        self._sandbox.add_linear_step(call)

    def _add_transform(self, transform, overwrite=True):

        self._check_for_input_data()

        logger.debug('transform:' + str(transform['name']))

        if self.get_function_type(transform['name']) == 'Segmenter' and self.group_columns:
            if 'Cascade' not in transform['name']:
                self._group_columns.discard('SegmentID')
            self._group_columns.discard('CascadeID')

        call = self._kb.functions.create_function_call(transform['name'])
        # Add params to function call object
        for k, v in transform['params'].items():
            setattr(call, k, v)

        self._set_call_columns(call)
        self._sandbox.add_linear_step(call, overwrite)

        if self.get_function_type(transform['name']) == 'Segmenter' and self.group_columns:
            self._group_columns.add('SegmentID')
            if 'Cascade' in transform['name']:
                self._group_columns.add('CascadeID')

    def _add_feature_generator(self, feature_generators, feature_generator_params= {}):

        self._check_for_input_data()

        generator_set = self._kb.functions.create_generator_call_set(
            'generator_set')

        logger.debug('feature_generator_set')

        # set any generator set params given
        for k, v in feature_generator_params.items():
            setattr(generator_set, k, v)

        subtype_functions = []
        for fg in feature_generators:
            if fg.get('subtype_call', None):
                logger.debug('generator_subtype_call:' + \
                             str(fg['subtype_call']))
                for name in self._kb.list_functions('Feature Generator',  str(fg['subtype_call']),  kp_functions=True, qgrid=False).NAME:
                    subtype_functions.append({'name': name, 'params':fg['params']})

        feature_generators.extend(subtype_functions)

        feature_generator_list = []
        for fg in feature_generators:
            if fg.get('name', None):
                feature_generator_list.extend(self.iterate_columns(fg))

        for fg in feature_generator_list:
            logger.debug('generator_name:' + str(fg['name']))
            call = self._kb.functions.create_function_call(fg['name'])

            for k, v in fg['params'].items():
                setattr(call, k , v)

            generator_set.add_generator_call(call)

        self._add_group_columns(generator_set)

        self._generator_index = self.get_pipeline_length()

        self._sandbox.add_linear_step(generator_set)

    def _add_feature_selector(self, feature_selectors, selector_set_params= {}):

        self._check_for_input_data()

        selector_set = self._kb.functions.create_selector_call_set(
            'selector_set')

        logger.debug('feature_selector_set')

        for k, v in selector_set_params.items():
            setattr(selector_set, k, v)

        for fs in feature_selectors:
            logger.debug('feature_selector:' + fs['name'])
            call = self._kb.functions.create_function_call(fs['name'])
            for k, v in fs['params'].items():
                setattr(call, k, v)
            selector_set.add_selector_call(call)

        self._add_passthrough_columns(selector_set)
        self._add_label_column(selector_set)

        self._selector_index = self.get_pipeline_length()
        self._sandbox.add_linear_step(selector_set)

    def _add_initial_data(self):
        """Add the raw data call to the pipeline """
        if self.get_pipeline_length() != 0:
            raise PipelineOrderException(
                "Input data must be the first step in the pipeline")

        self._sandbox.add_linear_step(self._dataset)

    def _add_label_column(self, call):
        if self.label_column and hasattr(call, 'label_column'):
            if call.label_column is None:
                call.label_column = self.label_column

    def _add_group_columns(self, call):
        if self.group_columns and hasattr(call, 'group_columns'):
            if call.group_columns is None:
                call.group_columns = self.group_columns

    def _add_passthrough_columns(self, call):
        if self.group_columns and hasattr(call, 'passthrough_columns'):
            if call.passthrough_columns is None:
                call.passthrough_columns = self.group_columns

    def _add_ignore_columns(self, call):
        if (self.label_column and self.group_columns) and hasattr(call, 'ignore_columns'):
            if call.ignore_columns is None:
                call.ignore_columns = list(
                    set(self.group_columns) - set([self.label_column]))
        elif hasattr(call, 'ignore_columns') and call.ignore_columns is None:
            call.ignore_columns = []

    def _set_call_columns(self, call):
        self._add_label_column(call)
        self._add_group_columns(call)
        self._add_passthrough_columns(call)
        self._add_ignore_columns(call)


def get_contract_column_type(input_contract):

    column_contract = None

    for elem in input_contract:
        if elem.get('name', None) == 'columns':
            column_contract = elem
            break

    if isinstance(column_contract, dict):
        return column_contract.get('num_columns', None)

    return None


def generate_custom_feature_selector(feature_summary):
    """
    takes a feature summary and resturns the Custom Feature Selection by Index feature selection dictionary
    """
    current_gen_index = 1
    last_gen_index = feature_summary[0]['Feature'].split('_')[1]
    feature_selection = {1: []}
    for feature in feature_summary:
        if last_gen_index != feature['Feature'].split('_')[1]:
            current_gen_index += 1
            last_gen_index = feature['Feature'].split('_')[1]
            feature_selection[current_gen_index] = []
        feature_selection[current_gen_index].append(
            feature['GeneratorFamilyIndex'])

    return feature_selection
