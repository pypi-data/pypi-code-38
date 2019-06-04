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
from __future__ import print_function
import os
import sys
import inspect
import json
from logging import debug
import pandas as pd
from pandas import DataFrame
from copy import deepcopy
from numbers import Number
from sensiml.render import BaseRenderer

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


import sensiml.base.utility as utility
from sensiml.datamanager.pipeline import PipelineStep, PipelineError
from sensiml.datamanager.knowledgepack import KnowledgePack
from sensiml.method_calls.functioncalls import FunctionCalls
from sensiml.method_calls.selectorcallset import SelectorCallSet
from sensiml.method_calls.generatorcallset import GeneratorCallSet
from sensiml.method_calls.trainandvalidationcall import TrainAndValidationCall
from sensiml.datamanager.modelresults import ModelResultSet
from sensiml.datamanager.deviceconfig import DeviceConfig


class SandboxPipeline():
    """Base class for a sandbox pipeline consisting of steps"""

    def __init__(self, steps=[]):
        self._steps = steps

    def add(self, item):
        """Appends a PipelineStep object to the pipeline while performing integrity checks.

            Args:
                item: a QueryCall, FunctionCall, GeneratorSet, SelectorSet, or TrainAndValidationCall object

            Returns:
                nothing, or raises an exception if integrity check fails
        """
        assert isinstance(item, PipelineStep)
        self._steps.append(item)

        try:
            self._check_integrity()
        except:
            self._steps.pop()
            raise

    def replace(self, item, index):
        """Replace a pipeline step that has the same name.

        Args:
            item: a QueryCall, FunctionCall, GeneratorSet, SelectorSet, or TrainAndValidationCall object
            index (int): index of pipeline step to replace

            Returns:
                nothing, or raises an exception if integrity check fails
        """
        assert isinstance(item, PipelineStep)
        assert (item.name == self._get_step_name(index))
        backup_item = deepcopy(self._steps[index])

        self._steps[index] = item

        try:
            self._check_integrity()
        except:
            self._steps[index] = backup_item
            raise

    def linear_pipeline(self, item):
        """A linear step will automatically set the previous step's output to the currents step's input.

            Args:
                item (pipeline step): a pipeline step to modify

            Returns:
                pipeline step: pipeline step with updated input_data and outputs attributes
        """

        # if this is the first step
        if len(self._steps) == 0:
            item.outputs = ['temp.raw']
        else:
            item.input_data = self._steps[-1].outputs[0]
            # Count the number of times the name has been used to get unique
            # input/output names
            index = len([
                1 for s in self._steps
                if 'temp.{}'.format(
                    item.name.replace(' ', '_')) in s.outputs[0]
            ])
            item.outputs = [
                'temp.{}{}'.format(item.name.replace(' ', '_'), index)
            ]

            if item._to_dict()['type'] == 'generatorset':
                item.outputs.append('temp.features.{}{}'.format(
                    item.name.replace(' ', '_'), index))
            if len(self._steps[-1].outputs) > 1:
                item.feature_table = self._steps[-1].outputs[-1]
                item.outputs.append('temp.features.{}{}'.format(
                    item.name.replace(' ', '_'), index))

        return item

    def replace_linear_pipeline(self, item, index):
        item.input_data = self._steps[index].input_data
        item.outputs = self._steps[index].outputs
        if len(self._steps[index].outputs) > 1:
            item.feature_table = self._steps[index].feature_table

        return item

    def remove(self, item):
        """Removes the item from the pipeline.

            Args:
                item (pipeline step)
        """
        if item in self._steps:
            self._steps.remove(item)

    def clear(self):
        """Clears all items from the pipeline."""
        self._steps = []

    def to_list(self):
        """Returns a list representation of the pipeline."""
        a = []
        if self._steps:
            for step in self._steps:
                if isinstance(step, FunctionCalls):
                    for o in step._to_list():
                        a.append(o)
                else:
                    if (isinstance(step, dict)):
                        a.append(step)
                    else:
                        a.append(step._to_dict())
        return a

    def describe(self, show_params=True, show_set_params=False):
        """Prints a formatted description of the pipeline"""
        describe_pipeline(self.to_list(), show_params=show_params,
                          show_set_params=show_set_params)

    def _get_pipeline_step_value(self, step, key='type'):
        """Returns the value associated with the specified key from the specified step index.

            Args:
                step (int): step index
                key (str): key to get the value for

            Returns:
                if it exists, the contents associated with the key, otherwise None
        """
        if len(self._steps) == 0:
            print('There are no steps associated with this pipeline.')
            return None

        if len(self._steps) < step:
            print('This pipeline step does not exist.')
            return None

        if isinstance(self._steps[step], dict):
            return self._steps[step].get(key, None)

        return self._steps[step]._to_dict().get(key, None)

    def _get_step_name(self, index):
        if isinstance(self._steps[index], dict):
            return self._steps[index]['name']
        else:
            return self._steps[index].name

    def _check_duplicate_outputs(self, item):
        for i, step in enumerate(self._steps):
            if item.name == self._get_step_name(i):
                return i

        return None

    def _check_integrity(self):
        """Checks the integrity of the pipeline as a whole.

            Returns:
                 True if successful, otherwise raises an exception
        """
        _aggregated_errors = []

        def _aggregate_errors(fmt_string, errors=[], *args):
            # Useful aggregation of error strings
            for error in errors:
                err_string = fmt_string.format(error, *args)
                _aggregated_errors.append(err_string)
                # _aggregated_errors.append(fmt_string.format(args, error))
            return

        output_vars = []
        step_num = 1
        for step in self._steps:
            is_last_step = True if step_num == len(self._steps) else False
            if isinstance(step, PipelineStep):
                errors = step._check_inputs(output_vars)
                if errors:
                    _aggregate_errors(
                        '[{1}] Step "{2}" -- Unmatched input: {0}', errors,
                        step_num, step.name)
                errors = step._check_outputs(output_vars, is_last_step)
                if errors:
                    _aggregate_errors(
                        '[{1}] Step "{2}" -- Duplicate output: {0}', errors,
                        step_num, step.name)
                output_vars.extend(step.outputs)
            else:
                raise PipelineError('Item is not a valid pipeline step.')
            step_num += 1

            # Ensure that the set objects contain the minimum number of call
            # objects
            missing_call_string = "The {0} set does not contain any {1} calls. Please add one or more {1} calls before adding the step to the sandbox."
            if isinstance(step,
                          GeneratorCallSet) and not len(step.generator_calls):
                raise PipelineError(
                    missing_call_string.format('feature generator',
                                               'generator'))
            elif isinstance(step, SelectorCallSet) and not len(step.selectors):
                raise PipelineError(
                    missing_call_string.format('feature selector', 'selector'))
            elif isinstance(step, TrainAndValidationCall):
                if not len(step.classifiers):
                    raise PipelineError(
                        missing_call_string.format('train and validation',
                                                   'classifier'))
                if not len(step.optimizers):
                    raise PipelineError(
                        missing_call_string.format('train and validation',
                                                   'optimizer'))
                if not len(step.validation_methods):
                    raise PipelineError(
                        missing_call_string.format('train and validation',
                                                   'validation method'))

        if not _aggregated_errors:
            return True
        else:
            raise PipelineError('Pipeline failed integrity check: ' +
                                '\n'.join(_aggregated_errors))

    def __str__(self):
        pipeline_string = ''
        pipeline_list = []
        for step in self._steps:
            if isinstance(step, FunctionCalls):
                for o in step._to_list():
                    pipeline_list.append(o)
            else:
                if isinstance(step, dict):
                    pipeline_list.append(step)
                else:
                    pipeline_list.append(step._to_dict())
        for step in pipeline_list:
            if 'name' in step:
                pipeline_string += '{name} ({type})\n'.format(**step)
            else:
                pipeline_string += '{type}\n'.format(**step)
            if 'inputs' in step:
                pipeline_string += '    Inputs: \n'
                for input_ in step['inputs']:
                    pipeline_string += '        {0}\n'.format(input_)
            if 'outputs' in step:
                pipeline_string += '    Outputs: \n'
                for output_ in step['outputs']:
                    pipeline_string += '        {0}\n'.format(output_)
            pipeline_string += '\n'

        return pipeline_string


class Sandbox(object):
    """Base class for a sandbox."""

    def __init__(self, connection, project):
        """Initializes a sandbox instance."""
        self._uuid = ''
        self._name = ''
        self._dirty = False
        self._connection = connection
        self._project = project
        self._pipeline = SandboxPipeline()
        self._cache_enabled = True
        self._results = ModelResultSet(project, self)
        self._execution_summary = None
        self._features = None
        self._device_config = DeviceConfig()
        self._created = None

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._dirty = True
        self._name = value

    @property
    def pipeline(self):
        return self._pipeline

    @property
    def cache(self):
        return self._cache_enabled

    @property
    def results(self):
        return self._results

    @property
    def device_config(self):
        return self._device_config

    @property
    def created(self):
        """Date of the Pipeline creation"""
        return self._created

    @created.setter
    def created(self, value):
        self._created = value

    @property
    def cost_preview(self):
        print('The cost_preview is no longer available. To view device costs look at a KnowledgePack cost_report.\n')

    def _check_sandbox_inserted(self, insert=False):
        """ Checks for a uuid and warns the user if none exists """
        if self.uuid == '':
            if insert:
                print('Sandbox was not on server, attempting to insert now...', end='')
                self.insert()
                print('Success')
            else:
                raise Exception("Sandbox does not exist on the server")
        return True

    def _init_device_config(self, data):
        self._device_config = DeviceConfig(data.get('device_config', None))

    def insert(self):
        """Calls the REST API to insert a new object on to the server."""
        url = 'project/{0}/sandbox/'.format(self._project.uuid)
        sandbox_info = {
            'name': self.name,
            'pipeline': self.pipeline.to_list(),
            'cache_enabled': self.cache,
            'device_config': self.device_config
        }
        response = self._connection.request('post', url, sandbox_info)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.uuid = response_data['uuid']
            self._init_device_config(response_data)
            self._dirty = False

    def update(self):
        """Calls the REST API to update the object on the server."""
        self._pipeline._check_integrity()
        if self._check_sandbox_inserted():
            url = 'project/{0}/sandbox/{1}/'.format(self._project.uuid,
                                                    self.uuid)
            sandbox_info = {
                'name': self.name,
                'pipeline': self.pipeline.to_list(),
                'cache_enabled': self.cache,
                'device_config': self.device_config
            }
            response = self._connection.request('put', url, sandbox_info)
            response_data, err = utility.check_server_response(response)
            if err is False:
                self._init_device_config(response_data)
                self._dirty = False

    def delete(self):
        """Calls the REST API to delete the object from the server."""
        url = 'project/{0}/sandbox/{1}/'.format(self._project.uuid, self.uuid)
        if self._check_sandbox_inserted(insert=False):
            response = self._connection.request(
                'delete',
                url, )
            response_data, err = utility.check_server_response(response)
            self._dirty = False
            self.uuid = ''

    def knowledgepack(self, kp_uuid):
        """Gets the KnowledgePack(s) created by the sandbox.

            Returns:
                a KnowledgePack instance, list of instances, or None
        """
        url = 'project/{0}/sandbox/{1}/knowledgepack/{2}/'.format(
            self._project.uuid, self.uuid, kp_uuid)
        response = self._connection.request(
            'get',
            url, )
        response_data, err = utility.check_server_response(response)
        if err is False:
            kp = KnowledgePack(self._connection, self._project.uuid, self.uuid)
            kp.initialize_from_dict(response_data)
            return kp

    def get_knowledgepacks(self):
        """Gets the KnowledgePack(s) created by the sandbox.

            Returns:
                a KnowledgePack instance, list of instances, or None
        """
        url = 'project/{0}/sandbox/{1}/knowledgepack/'.format(
            self._project.uuid, self.uuid)
        response = self._connection.request(
            'get',
            url, )
        response_data, err = utility.check_server_response(response)
        if err is False:
            return pd.DataFrame(response_data)

    def _handle_result(self, data, pipeline_step=-1):
        """Decides what type of results have been returned and creates a DataFrame or stores model results accordingly."""

        if data.get('status'):
            print(data.get('status'))
            return None, None

        execution_type = data.get('execution_type')

        if data.get('number_of_pages', 0) > 1:
            print('\nRetrieving page {0} of {1}.'.format(
                data.get('page_index', 1), data['number_of_pages']))
            if data['number_of_pages'] > 1:
                print("To get more pages, use: \n" +
                      "next_results, next_stats = dsk.pipeline.get_results(page_index=<desired page number>).")

        summary = pd.DataFrame(data.get('summary', [])).fillna('')
        extra = pd.DataFrame(data.get('extra', []))
        results = data.get('results', [])

        self._execution_summary = summary
        self._features = extra

        if (self.pipeline._get_pipeline_step_value(pipeline_step,
                                                   key='type') == 'tvo' and
                execution_type == 'pipeline') or execution_type == 'auto':
            if isinstance(results, list):
                data = []
                for result in results:
                    temp_results = ModelResultSet(
                        deepcopy(self._project), deepcopy(self))
                    temp_results.initialize_from_dict(result)
                    data.append(temp_results)
            else:
                self._results = ModelResultSet(self._project, self)
                self._results.initialize_from_dict(results)
                data = self._results

        else:
            if isinstance(results, list):
                data = map(lambda x: DataFrame(x), results)
            else:
                data = DataFrame(results)

        if execution_type == 'auto' and 'fitness' in extra.columns:
            return data, {
                'execution_summary': summary,
                'fitness_summary': extra
            }
        else:
            return data, {'execution_summary': summary, 'features': extra}

    def intermediate_data(self, pipeline_step, page_index=0):
        """Retrieves intermediate pipeline step data from a previously executed pipeline.

        Args:
            pipeline_step (int): The pipeline step to retrieve from and executed pipeline.
            page_index (int): the index to pull form the cache

        Returns:
            (DataFrame or ModelResultSet): result of executed pipeline, specified by the sandbox.

        """
        url = 'project/{0}/sandbox/{1}/data/'.format(self._project.uuid,
                                                     self.uuid)
        response = self._connection.request(
            'get', url, data={'pipeline_step': pipeline_step,
                              'page_index': page_index})

        data, err = utility.check_server_response(response)
        if err is False:
            response_data = data
            data, summary = self._handle_result(
                response_data, pipeline_step=pipeline_step)

            return data, summary

    def get_metrics_set(self, data):
        """retrieves metrics set from server

        Args:
            data (dict): dictionary containing
                        - 'y_true' and 'y_pred' keys
                        - y_true and y_pred values must be lists

        Returns:
            (dict): dictionary containing metrics result set from server"""
        url = 'get_metrics_set/'
        response = self._connection.request('get', url, data)
        data, err = utility.check_server_response(response)
        if err is False:
            response_data = data

            return response_data

    def execute(self):
        """Executes the sandbox pipeline and returns results.

            Returns:
                (DataFrame or ModelResultSet): result of executed pipeline, specified by the sandbox
                (dict): execution summary including execution time and whether cache was used for each
                step; also contains a feature cost table if applicable
        """
        self.submit()

        return utility.wait_for_pipeline_result(self,
                                                lock=True,
                                                wait_time=1,
                                                silent=True,
                                                page_index=1,
                                                )

    def async_submit(self, data):
        """Submits the sandbox for asynchronous execution and returns the task status."""
        if self._dirty:
            self.update()

        url = 'project/{0}/sandbox-async/{1}/'.format(self._project.uuid,
                                                      self.uuid)
        response = self._connection.request('post', url, data)
        response_data, err = utility.check_server_response(response)
        if err is False:
            return response_data

    def auto(self, auto_params, seed, renderer=None):
        """Submits the automation job for asynchronous execution and returns the task status."""
        # If the sandbox contains anything except a querycall or featurefilecall, and it
        # is not a custom seed, do not execute the request
        if renderer is None:
            renderer = BaseRenderer()
        if seed.name == 'Custom':
            if self.pipeline.to_list()[-1]['type'] != 'tvo':
                renderer.render(
                    "Only custom pipelines that end with a tvo call can be automated.")
                return 0
            renderer.render("Running Auto Pipeline with Custom Seed:\n")
            describe_pipeline(self.pipeline.to_list())
        elif len(self.pipeline.to_list()) == 0:
            renderer.render(
                "Running Auto Pipeline with {} Seed and Auto Query:\n".format(seed.name))
        elif len(self.pipeline.to_list()) == 1 and self.pipeline.to_list()[0]['type'] in ['query', 'featurefile']:
            renderer.render(
                "Running Auto Pipeline with {} Seed:\n".format(seed.name))
            full_pipeline = deepcopy(self.pipeline.to_list()) + seed.pipeline
        elif len(self.pipeline.to_list()) > 1 and self.pipeline.to_list()[0]['type'] in ['query']:
            renderer.render(
                "Running Auto Pipeline with {} Seed:\n".format(seed.name))
            full_pipeline = deepcopy(self.pipeline.to_list()) + seed.pipeline
        elif len(self.pipeline.to_list()) <= 2 and 'segmenter' in [step['type'] for step in self.pipeline.to_list()] and \
                set([step['type'] for step in self.pipeline.to_list()]).issubset(['query', 'featurefile', 'segmenter']):
            segmenter_name = [step['name'] for step in self.pipeline.to_list(
            ) if step['type'] == 'segmenter'][0]
            renderer.render("Running Auto Pipeline with {} Seed and {} Segmenter:\n".format(
                seed.name, segmenter_name))
            full_pipeline = deepcopy(self.pipeline.to_list()) + seed.pipeline
        else:
            renderer.render("This pipeline contains steps that could be overwritten by the {}\n".format(seed.name) +
                            "seed. Either run this pipeline with the Custom seed or remove steps from the \n" +
                            "pipeline (query, data file, and segmenter steps are okay).")
            return 0

        data = {
            'run_parallel': True,
            'execution_type': 'auto',
            'auto_params': auto_params
        }

        self.async_submit(data)
        return 1

    def retrieve_auto(self):
        result = self.retrieve(execution_type='auto')
        return result

    def autosegment_search(self, params, run_parallel=True):
        """Submits the grid search for asynchronous execution and returns the task status."""
        data = {
            'run_parallel': run_parallel,
            'execution_type': 'autosegment_search',
            'seg_params': params
        }

        return self.async_submit(data)

    def retrieve_autosegment(self):
        result = self.retrieve()
        return result

    def retrieve(self, silent=False, page_index=0, **kwargs):
        """Gets the result of a prior asynchronous execution of the sandbox.

            Returns:
                (DataFrame or ModelResultSet): result of executed pipeline, specified by the sandbox
                (dict): execution summary including execution time and whether cache was used for each
                step; also contains a feature cost table if applicable
        """
        if self._dirty:
            self.update()

        url = 'project/{0}/sandbox-async/{1}/?{2}'.format(
            self._project.uuid, self.uuid,
            urlencode({
                'page_index': page_index
            }))
        response = self._connection.request('get', url)
        data, err = utility.check_server_response(response)
        if err is False:
            response_data = data or {}
            return utility.check_pipeline_status(
                response_data,
                self._handle_result,
                silent=silent,
            )

    def kill_pipeline(self):
        url = 'project/{0}/sandbox-async/{1}/'.format(self._project.uuid,
                                                      self.uuid)
        response = self._connection.request('delete', url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            print(response_data)
            return response_data

    def submit(self):
        """Submits a pipeline for asynchronous execution."""
        data = {'execution_type': 'pipeline'}
        return self.async_submit(data)

    def grid_search(self, grid_params, run_parallel=False):
        """Submits the grid search for asynchronous execution and returns the task status."""
        data = {
            'run_parallel': run_parallel,
            'execution_type': 'grid_search',
            'grid_params': grid_params
        }

        return self.async_submit(data)

    def retrieve_gridsearch(self):
        result = self.retrieve()
        return result

    def refresh(self):
        """Calls the REST API and populates the local sandbox from the server."""
        url = 'project/{0}/sandbox/{1}/'.format(self._project.uuid, self.uuid)
        response = self._connection.request('get', url)
        data, err = utility.check_server_response(response)
        if err is False:
            self.uuid = data['uuid']
            self.name = data['name']
            self.created = data.get('created_at', None)
            if not data.get('cache_enabled', True):
                self.disable_cache()
            self._init_device_config(data)
            self.pipeline._steps = data['pipeline']
            self._dirty = False

    def delete_cache(self):
        """Calls the REST API and deletes the server cache for the sandbox."""
        if self._check_sandbox_inserted(insert=False):
            url = 'project/{0}/sandbox/{1}/cache/'.format(
                self._project.uuid, self.uuid)
            response = self._connection.request('DELETE', url)
            data, err = utility.check_server_response(response)
            if err is False:
                print(data)

    def initialize_from_dict(self, init_dict):
        """Populates a single sandbox from a dictionary of properties.

            Args:
                (dict): contains uuid, name, cache_enabled, and pipeline
        """
        self.uuid = init_dict['uuid']
        self.name = init_dict['name']
        self.created = init_dict.get('created_at', None)

        if not init_dict.get('cache_enabled', True):
            self.disable_cache()

        if len(init_dict['pipeline']) != 0:
            self._pipeline._steps = init_dict['pipeline']
        else:
            self._pipeline._steps = []
            self._init_device_config(init_dict)
        self._dirty = False

    def add_step(self, step):
        """Adds the step to the sandbox pipeline.

            Args:
                step (pipeline step): a QueryCall, FunctionCall, GeneratorSet, SelectorSet, or
                                      TrainAndValidationCall object
        """
        self._pipeline.add(step)
        self._dirty = True

    def update_step(self, step, index):
        """Update a step with new values

            Args:
                step (pipeline step): a QueryCall, FunctionCall, GeneratorSet, SelectorSet, or
                                      TrainAndValidationCall object
                index (int): index of the pipeline step to update

        """
        step = self._pipeline.replace_linear_pipeline(step, index)
        self._pipeline.replace(step, index)
        self._dirty = True

    def add_linear_step(self, step, overwrite=True):
        """Adds a linear step to the pipeline (will automatically use the previous step's output as input).

            Args:
                step (pipeline step): a QueryCall, FunctionCall, GeneratorSet, SelectorSet, or
                    TrainAndValidationCall object
                overwrite (boolean): when adding multiple instances of the same transform, set
                    overwrite to False for the additional steps and the first instance will not
                    be overwritten (default is True)

        """
        if not overwrite or self._pipeline._check_duplicate_outputs(
                step) is None:
            step = self._pipeline.linear_pipeline(step)
            self._pipeline.add(step)
            self._dirty = True
        else:
            self.update_step(step,
                             self._pipeline._check_duplicate_outputs(step))

    def remove_step(self, step):
        """Removes a step from the pipeline.

            Args:
                step (pipeline step): a QueryCall, FunctionCall, GeneratorSet, SelectorSet, or
                                      TrainAndValidationCall object to remove from the pipeline
        """
        self._pipeline.remove(step)
        self._dirty = True

    def clear(self):
        """Clears the sandbox of all steps."""
        self._pipeline.clear()
        self._dirty = True

    def enable_cache(self):
        """Enables the use of caching for the sandbox on the server."""
        self._cache_enabled = True
        self._dirty = True

    def disable_cache(self):
        """Disables the use of caching for the sandbox on the server."""
        self._cache_enabled = False
        self._dirty = True


def describe_pipeline(pipeline, show_params=True, show_set_params=False):
    print("------------------------------------------------------------------------")
    for index, step in enumerate(pipeline):

        if isinstance(step['name'], list):
            name = ', '.join(step['name'])
        else:
            name = step['name']

        print("{0: >2}.     Name: {1: <25} \t\tType: {2: <25}".format(
            index, name, step['type']))
        print("------------------------------------------------------------------------")
        if step.get('set', None) and show_params:
            print_set_items(step, params=show_set_params)
        if step.get('inputs', None) and show_params:
            print(filter_params(step['inputs']))
        if step.get('type') == 'tvo':
            print_tvo(step)
        print("------------------------------------------------------------------------")
    print("")


def filter_params(inputs, num_tabs=1):
    not_params = [
        'input_data', 'group_column',
        'passthrough_columns', 'group_columns', 'remove_columns',
        'label_column', 'feature_table'
    ]
    params = filter(lambda x: x not in not_params, inputs.keys())
    param_values = [
        num_tabs * "\t" + "{0} {1}".format(param + ':',
                                           inputs[param])
        for param in params
    ]
    return '\n'.join(param_values)


def print_set_items(step, params=False):
    for index, set_step in enumerate(step.get('set')):
        print("\t{0: >2}. Name: {1: <25}".format(index,
                                                 set_step['function_name']))
        if params:
            print(filter_params(set_step['inputs'], num_tabs=2))
            print('')


def print_tvo(step):
    map_tvo = {
        'classifiers': 'Classifier:',
        'optimizers': 'Training Algo:',
        'validation_methods': 'Validation Method:'
    }
    for tvo_step in ['classifiers', 'optimizers', 'validation_methods']:
        print("\t{0} {1}".format(map_tvo[tvo_step],
                                 step[tvo_step][0]['name']))
        print(filter_params(step[tvo_step][0]['inputs'], num_tabs=2))
        print('')
