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

from .message import Message
from .logger import getLogger
from cortex_client import ActionClient
from cortex_client.serviceconnector import ServiceConnector
from .camel import CamelResource

log = getLogger(__name__)


class Action(CamelResource):
    """
    A Cortex Action. Actions are the computional part of a skill.
    """
    def __init__(self, action, connector: ServiceConnector):
        super().__init__(action, True)
        self._connector = connector

    def invoke(self, message: Message, timeout=30):
        """
        Invoke an action.

        :param message: A Message to send as input to the action.
        :return: A response Message.
        """
        action_client = ActionClient(self._connector.url, self._connector.version, self._connector.token)
        return Message(action_client.invoke_action(self.name, message.to_params()))

    def get_deployment_status(self):
        """
        Get the deployment status of an action.
        """
        a = Action.get_action(self.name, self._connector)
        return a.deploymentStatus

    def delete(self):
        """
        Delete an action.
        """
        action_client = ActionClient(self._connector.url, self._connector.version, self._connector.token)
        return action_client.delete_action(self.name, self.type)

    def get_task_status(self, task_id):
        """
        Get the status for a job task (a task is a particular invocation of the action type: job).

        :param task_id: The identifier for the task.
        """
        action_client = ActionClient(self._connector.url, self._connector.version, self._connector.token)
        return action_client.get_task_status(self.name, task_id)

    def get_task_logs(self, task_id):
        """
        Get the logs for a task.

        :param task_id: The identifier for the task.
        """
        action_client = ActionClient(self._connector.url, self._connector.version, self._connector.token)
        return action_client.get_task_logs(self.name, task_id)

    def _repr_(self):
        return "Action(name={name}, version={version}, type={type}, kind={kind})"\
            .format(name=self.name, version=self.version, kind=self.kind, type=self.type)

    def _repr_html_(self):
        template = """
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Version</th>
                    <th>Type</th>
                    <th>Kind</th>
                    <th>Image</th>
                    <th>Deployment Status</th>
                </tr>
            </thead>
            <tbody>
                <td>{name}</td>
                <td>{version}</td>
                <td>{type}</td>
                <td>{kind}</td>
                <td>{image}</td>
                <td>{status}</td>
            </tbody>
        </table>
        """

        return template.format(name=self.name, version=self.version, type=self.type,
                               kind=self.kind, image=self.image, status=self.get_deployment_status())


    @staticmethod
    def get_action(name: str, connector: ServiceConnector):
        """
        Fetches an Action to work with.

        :param name: The name of the Action to retrieve.

        :return: An Action object.
        """
        uri = 'actions/{name}'.format(name=name)
        log.debug('Getting action using URI: %s' % uri)
        r = connector.request('GET', uri)
        r.raise_for_status()
        j = r.json()

        return Action(j.get('function', {}), connector)
