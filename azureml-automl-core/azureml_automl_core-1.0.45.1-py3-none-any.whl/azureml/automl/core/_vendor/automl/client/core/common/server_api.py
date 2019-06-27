# Copyright (c) 2017 Microsoft Corporation.  All rights reserved.
"""Objects for communicating with the miro server."""
import copy
import json

import requests

from automl.client.core.common import (client_state, constants, pipeline_spec,
                                       problem_info, resource_limits)


class RecommendationResponse(object):
    """The recommendation response object."""

    def __init__(self,
                 p_spec,
                 predicted_cost=None,
                 predicted_status=None,
                 training_percent=None,
                 predicted_metrics=None,
                 pipeline_id=None):
        """
        Initialize a recommendation response object.

        Args:
            p_spec (PipelineSpec): pipeline specification
            predicted_cost (float): predicted cost
            predicted_status (string): predicted status code,
                see constants.ServerStatus
            training_percent (int): percentage of dataset to use for training
            predicted_metrics (dict of string and float):
                predicted metrics for the pipeline
            pipeline_id (PipelineID): id representing the pipeline,
                optional if pipeline_spec is specified
        """
        self.p_spec = p_spec
        self.predicted_cost = predicted_cost
        self.predicted_status = predicted_status
        self.training_percent = training_percent
        self.predicted_metrics = predicted_metrics
        self.pipeline_id = pipeline_id

    @staticmethod
    def from_pid(pipeline_id,
                 predicted_cost=None,
                 predicted_status=None,
                 training_percent=100,
                 predicted_metrics=None):
        """
        Create a recommendation response with pid.

        Args:
            pipeline_id (PipelineID): id representing the pipeline
            predicted_cost (float): predicted cost
            predicted_status (string): predicted status code,
                see constants.ServerStatus
            training_percent (int): percentage of dataset to use for training
            predicted_metrics (dict of string and float):
                predicted metrics for the pipeline
        """
        res = RecommendationResponse(
            None,
            predicted_cost=float(predicted_cost) if predicted_cost else None,
            predicted_status=predicted_status,
            training_percent=training_percent,
            predicted_metrics=predicted_metrics,
            pipeline_id=pipeline_id)
        return res

    @staticmethod
    def from_dict(d):
        """Create a recommendation response from a dicationary."""
        ret = RecommendationResponse(None)
        ret.__dict__ = copy.deepcopy(d)
        ret.p_spec = pipeline_spec.PipelineSpec.from_dict(ret.p_spec)
        return ret

    def to_dict(self):
        """Create a dictionary from a recommendation response."""
        d = copy.deepcopy(self.__dict__)
        d['p_spec'] = self.p_spec.to_dict()
        return d


class MiroServerAPI(object):
    """Miro Server API object."""

    def __init__(self,
                 endpoint,
                 model_name="default",
                 api_key=None,
                 settings_file=None,
                 logger=None):
        """
        Initialize the class for talking with the Miro server.

        :param endpoint:
        :param model_name:
        :param api_key:
        :param settings_file:
        :param logger:
        """
        self._log = logger

        self._endpoint = endpoint
        self._model_name = model_name
        self._api_key = api_key

    def _handle_response(self, url, req_data, r):
        if r.status_code != 200:
            request_dump = ("\n\r" + url + "\n\r" +
                            json.dumps(req_data, indent=4))
            error_str = "server responded with status %s" % r.status_code
            error_str += request_dump
            self._log and self._log.error(error_str)
            raise Exception(error_str)

        try:
            data = r.json()
        except Exception:
            data = None
        if data is None:
            request_dump = ("\n\r" + url + "\n\r" +
                            json.dumps(req_data, indent=4))
            error_str = "failed to parse server response"
            error_str += request_dump
            self._log and self._log.error(error_str)
            raise Exception(error_str)

        if 'error' in data:
            self._log and self._log.error(data['error'])
            raise Exception(data['error'])

        return data

    def _get_pipeline_request(self, problem_info, state):
        r = self._get_request()
        r.update({'state': state.to_dict()})
        r.update({'problem_info': problem_info.to_dict()})
        return r

    def _get_request(self):
        return {
            'api_key': self._api_key,
        }

    def next_pipeline(self, problem_info, state):
        """
        Get the next pipeline.

        TODO: describe this function.
        :param acquisition_function:
        :param acquisition_param:
        :param state: A ClientState object.
        :param problem_info: A ProblemInfo object.
        :return:
        """
        url = self._endpoint + "/models/%s/next" % self._model_name
        data = self._get_pipeline_request(problem_info, state)
        # TODO: generate real certs (and remove verify=False)
        r = requests.post(url, json=data, headers={
                          'content-type': 'application/json'}, verify=False)
        responses = self._handle_response(url, data, r)
        return [RecommendationResponse.from_dict(resp) for resp in responses]

    def fetch_api_version(self):
        """
        Get the api version.

        TODO: describe this function.
        :return:
        """
        url = self._endpoint + "/version"
        data = self._get_request()
        r = requests.post(url, json=data, headers={
                          'content-type': 'application/json'}, verify=False)
        return self._handle_response(url, data, r)

    def fetch_model_info(self):
        """
        Get the model info.

        TODO: describe this function.
        :return:
        """
        url = self._endpoint + "/models/%s/info" % self._model_name
        data = self._get_request()
        r = requests.post(url, json=data, headers={
                          'content-type': 'application/json'}, verify=False)
        return self._handle_response(url, data, r)


class InMemoryServerAPI(MiroServerAPI):
    """Implements the API to a server object in memory instead of REST."""

    def __init__(self, server, api_version=None, package_version=None):
        """Initialize the class for talking with the Miro server."""
        super(InMemoryServerAPI, self).__init__(None, api_key=1234)
        self._server = server
        self._api_version = api_version
        self._package_version = package_version

    def next_pipeline(self, problem_info, state):
        """Get the next pipeline."""
        data = self._get_pipeline_request(problem_info, state)

        response_json = self._server.model_next(data)
        responses = json.loads(response_json)
        return [RecommendationResponse.from_dict(resp) for resp in responses]

    def fetch_api_version(self):
        """Get the api version."""
        return {'api_version': self._api_version,
                'package_version': self._package_version}

    def fetch_model_info(self):
        """Get the model info."""
        return json.loads(self._server.model_info())

    def fetch_predict_times(self):
        """Get average predict time."""
        return json.loads('{0}'.format(self._server.get_average_predict_time()))


class O16nServerAPI(MiroServerAPI):
    """O16N Server api object."""

    def __init__(self,
                 endpoint,
                 api_key=None,
                 settings_file=None):
        """Create an O16N api object."""
        super(O16nServerAPI, self).__init__(
            endpoint, model_name=None, api_key=api_key,
            settings_file=settings_file)

    @staticmethod
    def input_df_to_state(input_df):
        """Create input objects for miro."""
        metric = input_df.get('metric')
        if metric is None:
            metric = 'default'

        task = input_df.get('task')

        # Construct input objects for miro brain from input df
        cl_state = client_state.ClientState(metric, task)
        ids = input_df.get('pipeline_ids')
        scores = input_df.get('scores')
        pred_times = input_df.get('predicted_times', []) or []
        act_times = input_df.get('actual_times', []) or []
        act_times = O16nServerAPI.convert_nan_string_to_numpy(act_times)
        training_percents = input_df.get('training_percents', []) or []
        whitelisted_model_names = O16nServerAPI.get_model_names(
            input_df, 'model_names_whitelisted', task)
        blacklisted_model_names = O16nServerAPI.get_model_names(
            input_df, 'model_names_blacklisted', task)
        for i in range(len(ids)):
            cl_state.update(ids[i], {metric: scores[i]},
                            pred_times[i] if i < len(pred_times) else float('nan'),
                            act_times[i] if i < len(act_times) else float('nan'),
                            predicted_metrics=input_df.get('predicted_metrics',
                                                           None),
                            training_percent=training_percents[i] if
                            i < len(training_percents) else 100)

        problem_info_var = problem_info.ProblemInfo(
            dataset_samples=input_df.get('num_samples'),
            dataset_features=input_df.get('num_features'),
            dataset_classes=input_df.get('num_classes'),
            dataset_num_categorical=input_df.get('num_categorical'),
            num_recommendations=input_df.get('num_recommendations'),
            runtime_constraints={
                resource_limits.TIME_CONSTRAINT:
                input_df.get('time_constraint')},
            task=task, metric=metric,
            cost_mode=input_df.get(
                'cost_mode', constants.PipelineCost.COST_NONE),
            is_sparse=input_df.get('is_sparse_data', False),
            subsampling=input_df.get('subsampling', False),
            model_names_whitelisted=whitelisted_model_names,
            model_names_blacklisted=blacklisted_model_names)

        problem_info_var.set_cost_mode()

        return problem_info_var, cl_state

    @staticmethod
    def get_model_names(input_df, parameter_name, task):
        """Get model names."""
        legacy_model_names = O16nServerAPI.map_customer_name_to_legacy_model_name(
            input_df.get(parameter_name, None), task)
        if legacy_model_names is None or len(legacy_model_names) == 0:
            model_names = None
        else:
            model_names = \
                [legacy_model_name for legacy_model_name in
                 legacy_model_names if legacy_model_name]
        return model_names

    @staticmethod
    def convert_nan_string_to_numpy(list_of_value):
        """Convert NaN string getting from json and convert to numpy value."""
        new_list_of_value = [
            float('nan') if item == 'NaN' else item for item in list_of_value]
        return new_list_of_value

    @staticmethod
    def map_customer_name_to_legacy_model_name(whitelist_model_names, task):
        """Mao customer model name to legacy model name."""
        if whitelist_model_names is None:
            return None
        if task == constants.Tasks.CLASSIFICATION:
            return [
                constants.ModelNameMappings.
                CustomerFacingModelToLegacyModelMapClassification.get(
                    whitelist_model_name, None) for whitelist_model_name
                in whitelist_model_names]
        elif task == constants.Tasks.REGRESSION:
            return [
                constants.ModelNameMappings.
                CustomerFacingModelToLegacyModelMapRegression.get(
                    whitelist_model_name, None) for whitelist_model_name
                in whitelist_model_names]
        else:
            raise ValueError(
                "task is {0}, which is not supported".format(task))
        return

    # Need this to follow the schema.json in O16N image
    @staticmethod
    def state_to_input_df_json(pinfo, cl_state):
        """Convert state to input dataframe in JSON."""
        return {"input_df": O16nServerAPI.state_to_input_df_dic(
            pinfo, cl_state)}

    @staticmethod
    def state_to_input_df_dic(pinfo, cl_state):
        """Convert state to input dataframe in dictionary."""
        return {
            'metric': pinfo.metric,
            'task': pinfo.task,
            'pipeline_ids': cl_state.pipeline_hashes(),
            'scores': cl_state.optimization_scores(),
            'predicted_times': cl_state.predicted_times(),
            'actual_times': cl_state.actual_times(),
            'num_recommendations': pinfo.num_recommendations,
            'cost_mode': pinfo.cost_mode,
            'num_samples': pinfo.dataset_samples,
            'num_features': pinfo.dataset_features,
            'num_classes': pinfo.dataset_classes,
            'num_categorical': pinfo.dataset_num_categorical,
            'time_constraint': pinfo.runtime_constraints[
                resource_limits.TIME_CONSTRAINT],
            'model_names_whitelisted': pinfo.model_names_whitelisted,
            'model_names_blacklisted': pinfo.model_names_blacklisted}

    def next_pipeline(self, pinfo, cl_state):
        """Get the next pipeline."""
        # add the bearer token header for O16N Communication
        headers = {'Authorization': 'Bearer ' +
                   str(self._api_key), 'content-type': 'application/json'}
        data = O16nServerAPI.state_to_input_df_json(pinfo, cl_state)

        url = self._endpoint

        r = requests.post(url, data=json.dumps(data), headers=headers)
        response = self._handle_response(url, data, r)

        # response from o16n server is already a dic without p_spec.
        return response

    def fetch_api_version(self):
        """Get the api version."""
        raise NotImplementedError()

    def fetch_model_info(self):
        """Get the model info."""
        raise NotImplementedError()
