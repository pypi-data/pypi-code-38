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
import deprecation

from .client import _Client
from .client import build_client
from .types import JSONType


@deprecation.deprecated(deprecated_in="5.4.4", details="Use the ActionClient instead.")
class JobsClient(_Client):
    """
    A client for the Cortex jobs REST API.
    """

    URIs = {'jobs':         'jobs',
            'tasks':        'jobs/{}/tasks',
            'registries':   'registries',
           }

    ## Jobs ##

    def get_jobs(self) -> JSONType:
        """
        Lists jobs.

        :return: A list of jobs.
        """
        return self._get_json(self.URIs['jobs'])

    def post_job(self, job: JSONType) -> JSONType:
        """
        Deploys a job.

        :param job: A job definition
        :return: JSONType.
        """
        return self._post_json(self.URIs['jobs'], job)

    def get_job(self, job_id: str):
        """
        Gets job definition details.

        :param job_id: the identifier of the job.
        :return: JSONType
        """
        uri = self._serviceconnector.urljoin([self.URIs['jobs'], job_id])
        return self._get_json(uri)

    def get_job_stats(self, job_id: str):
        """
        Gets stats for a given job.

        :param job_id: The identifier of the job.
        :return: JSONType
        """
        uri = self._serviceconnector.urljoin([self.URIs['jobs'], job_id, 'stats'])
        return self._get_json(uri)

    ## Tasks ##

    def get_tasks(self, job_id: str):
        """
        Lists tasks for a given job.

        :param job_id: The identifier of the job.
        :return: JSONType
        """
        uri = self.URIs['tasks'].format(job_id)
        return self._get_json(uri)

    def post_task(self, job_id, task: JSONType):
        """
        Submits a task for execution.

        :param job_id: The identifier of the job.
        :param task: The task definition.
        :return: JSONType
        """
        uri = self.URIs['tasks'].format(job_id)
        return self._post_json(uri, task)

    def get_task(self, job_id, task_id):
        """
        Returns details for a single job task.

        :param job_id: The identifier of the job.
        :param task_id: The identifier of the task to return.
        :return: JSONType
        """
        uri = self._serviceconnector.urljoin([self.URIs['tasks'].format(job_id), task_id])
        return self._get_json(uri)

    def cancel_task(self, job_id, task_id):
        """
        Cancels a task that has been queued

        :param job_id: The job identifier.
        :param task_id: The identifier of the task to cancel.
        :return: JSONType
        """
        uri = self._serviceconnector.urljoin([self.URIs['tasks'].format(job_id), task_id, 'cancel'])
        return self._post_json(uri, {})

    def get_task_logs(self, job_id, task_id):
        """
        Returns logs for a job task.

        :param job_id: The job identifier.
        :param task_id: The identifier of the task to cancel.
        :return: JSONType
        """
        uri = self._serviceconnector.urljoin([self.URIs['tasks'].format(job_id), task_id, 'logs'])
        return self._post_json(uri, {})

    ## Registries ##

    def get_registries(self):
        """
        Returns a list of configured container registries.

        :return: JSONType
        """
        return self._get_json(self.URIs['registries'])

    def post_registry(self, registry_info: JSONType):
        """
        Registers a private Docker registry account for job containers.

        :param registry_info: the Docker registry information
        :return: JSONType
        """
        return self._post_json(self.URIs['registries'], registry_info)
