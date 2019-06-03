"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from requests_toolbelt.multipart.encoder import MultipartEncoder
import json
import dill
from .client import _Client


class ExperimentClient(_Client):

    """
    A client for the Cortex experiment and model management API.
    """

    URIs = {
        'experiments': 'experiments',
        'experiment': 'experiments/{experiment_name}',
        'runs': 'experiments/{experiment_name}/runs',
        'run': 'experiments/{experiment_name}/runs/{run_id}',
        'artifact': 'experiments/{experiment_name}/runs/{run_id}/artifacts/{artifact}',
        'meta': 'experiments/{experiment_name}/runs/{run_id}/meta/{meta}',
        'param': 'experiments/{experiment_name}/runs/{run_id}/params/{param}',
        'metric': 'experiments/{experiment_name}/runs/{run_id}/metrics/{metric}'
    }

    def list_experiments(self):
        r = self._serviceconnector.request(method='GET', uri=self.URIs['experiments'])
        r.raise_for_status()
        rs = r.json()

        return rs.get('experiments', [])

    def save_experiment(self, experiment_name, **kwargs):
        body_obj = {'name': experiment_name}

        if kwargs:
            body_obj.update(kwargs)

        body = json.dumps(body_obj)
        headers = {'Content-Type': 'application/json'}
        uri = self.URIs['experiments']
        r = self._serviceconnector.request(method='POST', uri=uri, body=body, headers=headers)
        r.raise_for_status()
        return r.json()

    def delete_experiment(self, experiment_name):
        uri = self.URIs['experiment'].format(experiment_name=experiment_name)
        r = self._serviceconnector.request(method='DELETE', uri=uri)
        r.raise_for_status()
        rs = r.json()

        return rs.get('success', False)

    def get_experiment(self, experiment_name):
        uri = self.URIs['experiment'].format(experiment_name=experiment_name)
        r = self._serviceconnector.request(method='GET', uri=uri)
        r.raise_for_status()

        return r.json()

    def list_runs(self, experiment_name):
        uri = self.URIs['runs'].format(experiment_name=experiment_name)
        r = self._serviceconnector.request(method='GET', uri=uri)
        r.raise_for_status()
        rs = r.json()

        return rs.get('runs', [])

    def find_runs(self, experiment_name, filter, sort=None, limit=25):
        uri = self.URIs['runs'].format(experiment_name=experiment_name)

        # filter and limit are required query params
        params = {
            'filter': json.dumps(filter),
            'limit': limit
        }

        # Add sorting
        if sort:
            params['sort'] = json.dumps(sort)

        r = self._serviceconnector.request(method='GET', uri=uri, params=params)
        r.raise_for_status()
        rs = r.json()

        return rs.get('runs', [])

    def delete_runs(self, experiment_name, filter=None, sort=None, limit=None):
        uri = self.URIs['runs'].format(experiment_name=experiment_name)

        params = {}

        # Add query filter
        if filter:
            params['filter'] = json.dumps(filter)

        # Add sorting
        if sort:
            params['sort'] = json.dumps(sort)

        # Add limit
        if limit:
            params['limit'] = limit

        r = self._serviceconnector.request(method='DELETE', uri=uri, params=params)
        r.raise_for_status()
        rs = r.json()

        return rs.get('message')

    def create_run(self, experiment_name, **kwargs):
        body_obj = {}

        if kwargs:
            body_obj.update(kwargs)

        body = json.dumps(body_obj)
        headers = {'Content-Type': 'application/json'}
        uri = self.URIs['runs'].format(experiment_name=experiment_name)
        r = self._serviceconnector.request(method='POST', uri=uri, body=body, headers=headers)
        r.raise_for_status()
        return r.json()

    def get_run(self, experiment_name, run_id):
        uri = self.URIs['run'].format(experiment_name=experiment_name, run_id=run_id)
        r = self._serviceconnector.request(method='GET', uri=uri)
        r.raise_for_status()

        return r.json()

    def update_run(self, experiment_name, run_id, **kwargs):
        body_obj = {}

        if kwargs:
            body_obj.update(kwargs)

        body = json.dumps(body_obj)
        headers = {'Content-Type': 'application/json'}
        uri = self.URIs['run'].format(experiment_name=experiment_name, run_id=run_id)
        r = self._serviceconnector.request(method='PUT', uri=uri, body=body, headers=headers)
        r.raise_for_status()
        rs = r.json()

        success = rs.get('success', False)
        if not success:
            raise Exception('Error updating run {}: {}'.format(run_id, rs.get('error')))
        return success

    def delete_run(self, experiment_name, run_id):
        uri = self.URIs['run'].format(experiment_name=experiment_name, run_id=run_id)
        r = self._serviceconnector.request(method='DELETE', uri=uri)
        r.raise_for_status()
        rs = r.json()

        success = rs.get('success', False)
        if not success:
            raise Exception('Error deleting run {}: {}'.format(run_id, rs.get('error')))
        return success

    def update_meta(self, experiment_name, run_id, meta, val):
        uri = self.URIs['meta'].format(experiment_name=experiment_name, run_id=run_id, meta=meta)
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request(method='PUT', uri=uri, body=json.dumps({'value': val}), headers=headers)
        r.raise_for_status()
        rs = r.json()

        success = rs.get('success', False)
        if not success:
            raise Exception('Error updating run {} meta property {}: {}'.format(run_id, meta, rs.get('error')))
        return success

    def update_param(self, experiment_name, run_id, param, val):
        uri = self.URIs['param'].format(experiment_name=experiment_name, run_id=run_id, param=param)
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request(method='PUT', uri=uri, body=json.dumps({'value': val}), headers=headers)
        r.raise_for_status()
        rs = r.json()

        success = rs.get('success', False)
        if not success:
            raise Exception('Error updating run {} param {}: {}'.format(run_id, param, rs.get('error')))
        return success

    def update_metric(self, experiment_name, run_id, metric, val):
        uri = self.URIs['metric'].format(experiment_name=experiment_name, run_id=run_id, metric=metric)
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request(method='PUT', uri=uri, body=json.dumps({'value': val}), headers=headers)
        r.raise_for_status()
        rs = r.json()

        success = rs.get('success', False)
        if not success:
            raise Exception('Error updating run {} metric {}: {}'.format(run_id, metric, rs.get('error')))
        return success

    def update_artifact(self, experiment_name, run_id, artifact, stream):
        uri = self.URIs['artifact'].format(experiment_name=experiment_name, run_id=run_id, artifact=artifact)
        r = self._serviceconnector.request(method='PUT', uri=uri, body=stream)
        r.raise_for_status()
        rs = r.json()

        success = rs.get('success', False)
        if not success:
            raise Exception('Error updating run {} artifact {}: {}'.format(run_id, artifact, rs.get('error')))
        return success

    def get_artifact(self, experiment_name, run_id, artifact):
        uri = self.URIs['artifact'].format(experiment_name=experiment_name, run_id=run_id, artifact=artifact)
        r = self._serviceconnector.request(method='GET', uri=uri, stream=True)
        r.raise_for_status()

        return r.content
