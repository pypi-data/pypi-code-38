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
from typing import Dict
from .client import _Client


class ActionClient(_Client):
    """
    A client for the Cortex Actions API.
    """

    URIs = {
        'deploy':       'actions',
        'invoke':       'actions/{action_name}/invoke',
        'delete':       'actions/{action_name}',
        'logs':         'actions/{action_name}/logs',
        'job_stats':    'jobs/{action_name}/stats',
        'tasks':        'jobs/{action_name}/tasks',
        'task_logs':    'jobs/{action_name}/tasks/{task_id}/logs',
        'task_status':  'jobs/{action_name}/tasks/{task_id}/status',
        'task_delete':  'jobs/{action_name}/tasks/{task_id}',
        'send_message': 'actions/send-message',
    }

    def deploy_action(self, name, kind: str, docker: str, code = '', action_type = None, **kwargs):
        """
        Deploys an action.

        :param name: The resource name of the action.
        :param kind: The action kind (only for functions) - python:2 or python:3
        :param docker: The Docker image to use (optional for functions, required for **jobs** and **daemons**)
        :param code: The action code to deploy; expects a file-like object and zip compressed contents.
        :param action_type: The type of action workload: function, daemon, job (default: function).
        :return: The action deployment result.
        """
        action = {'name': name}

        if docker:
            action['docker'] = docker

        if kind:
            action['kind'] = kind

        if code:
            try:
                code_file = open(code, 'rb')
            except TypeError:
                code_file = code

            action['code'] = ('code.zip', code_file, 'application/zip')

        if kwargs.get('command'):
            action['command'] = kwargs.get('command')

        if kwargs.get('port'):
            action['port'] = kwargs.get('port')

        if kwargs.get('environment'):
            action['environment'] = kwargs.get('environment')

        if kwargs.get('vcpus'):
            action['vcpus'] = str(kwargs.get('vcpus'))

        if kwargs.get('memory'):
            action['memory'] = str(kwargs.get('memory'))

        if kwargs.get('backend_type'):
            action['backend_type'] = kwargs.get('backend_type')

        uri = self.URIs['deploy']
        if action_type is not None:
            uri = '{}?actionType={}'.format(uri, action_type)

        m = MultipartEncoder(action)
        r = self._serviceconnector.request(method='POST', uri=uri, body=m, headers={'Content-type': m.content_type})
        r.raise_for_status()
        return r.json()

    def invoke_action(self, action_name, params: Dict[str, object]) -> Dict[str, object]:
        """
        Invokes an action.

        :param action_name: The name of the action to invoke.
        :param params: The body params to send the action.

        :return: The result of calling the action.
        """
        uri = self.URIs['invoke'].format(action_name=action_name)
        return self._post_json(uri, params)

    def get_logs(self, action_name) -> Dict[str, object]:
        """
        Gets the most recent logs for an action.

        :param action_name: The action name to retrieve logs from.
        :return: The most recent logs for the requested action.
        """
        uri = self.URIs['logs'].format(action_name=action_name)
        return self._get_json(uri) or {}

    def delete_action(self, action_name, action_type=None):
        """
        Deletes an action.

        :param action_name: The name of the action to delete.
        :return: The status of the deletion.
        """
        uri = self.URIs['delete'].format(action_name=action_name)
        if action_type:
            uri = '{}?actionType={}'.format(uri, action_type)

        r = self._serviceconnector.request(method='DELETE', uri=uri)
        r.raise_for_status()

        return r.json()

    def get_task_status(self, action_name, task_id):
        """
        Gets the status for an action task (for job type actions only).

        :param action_name: The name of the job action for the task.
        :param task_id: The task id to get status for.
        :return: Task status.
        """
        uri = self.URIs['task_status'].format(action_name=action_name, task_id=task_id)
        r = self._serviceconnector.request(method='GET', uri=uri)
        r.raise_for_status()
        return r.text


    def get_task_logs(self, action_name, task_id):
        """
        Gets the logs for an action task (for job type actions only).

        :param action_name: The name of the job action for the task.
        :param task_id: The task id to get logs for.
        :return: Task logs.
        """
        uri = self.URIs['task_logs'].format(action_name=action_name, task_id=task_id)
        return self._get_json(uri)

    def get_job_stats(self, action_name):
        """
        Gets execution stats for tasks associated with action `action_name` of type job.

        :param action_name: The name of the job action.
        :return: A `dict` with stats information.
        """
        uri = self.URIs['job_stats'].format(action_name=action_name)
        return self._get_json(uri)

    def get_tasks(self, action_name):
        """
        Gets list of tasks associated with the give job `action_name`.

        :param action_name: The name of the job action.
        :return: A `dict` with tasks.
        """
        uri = self.URIs['tasks'].format(action_name=action_name)
        return self._get_json(uri)

    def delete_task(self, action_name, task_id):
        """
        Deletes a task associated with a job action.

        :param action_name: The name of the job action.
        :param task_id: The ID of the task to delete.
        :return: Deletion status.
        """
        uri = self.URIs['task_delete'].format(action_name=action_name, task_id=task_id)
        r = self._serviceconnector.request(method='DELETE', uri=uri)
        r.raise_for_status()
        return r.json()

    def send_message(self, message):
        """
        Send Synapse Message

        :param message: Input message
        :return: status of message
        """
        uri = self.URIs['send_message']
        return self._post_json(uri, message)
