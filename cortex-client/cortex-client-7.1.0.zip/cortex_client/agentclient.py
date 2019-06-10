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
from typing import Dict

from .types import InputMessage
from .client import _Client
from .client import build_client

class AgentClient(_Client):
    """
    A client for the Cortex agent REST API.
    """

    URIs = {'snapshots':'agents/snapshots',
            'targets':  'agents/targets',
            'instances':'agents/instances',
            'services': 'agents/services/{instance_id}/{service_path}',
           }

    def create_snapshot(self, agent_name, tags=None, version=None):
        """
        Creates an agent snapshot.

        :param agent_name: The name of the agent to take a snapshot of.
        :param tags: A list of tags associated with the agent.
        :param version: The version of the agent from which the snapshot is created.
        """
        body = {"agentName": agent_name,
                "tags": tags or []}
        if version:
            body["version"] = version
        return self._post_json(self.URIs['snapshots'], body)

    def get_deploy_targets(self):
        """
        Gets targets for the agent.
        """
        return self._get_json(self.URIs['targets'])

    def create_instance(self, agent_id, snapshot_id, environment_id):
        """
        Creates an agent instance.

        :param agent_id: The unique ID of the agent.
        :param snapshot_id: The ID of the agent snapshot
        :param environment_id: The ID of the environment in which to create the instance.

        """
        body = {"agentId":      agent_id,
                "snapshotId":   snapshot_id,
                "environmentId":environment_id}
        return self._post_json(self.URIs['instances'], body)

    def invoke_agent_service(self,
                             instance_id,
                             service_path,
                             typeName,
                             body: Dict[str, object]):
        """
        Invokes an service defined for the agent.

        :param instance_id: The agent instance ID.
        :param service_path: The URI path of the service.
        :param typeName: The name of the type of the request.
        :param body: The payload of the request.
        """
        uri = self.URIs['services'].format(instance_id=instance_id,
                                           service_path=service_path)
        payload = {"typeName": typeName, "body": body}
        return self._post_json(uri, payload)

    def get_agent_service_response(self,
                                   instance_id,
                                   service_path,
                                   session_id):
        """
        Gets the response to a previously made request to an agent service.

        :param instance_id: The agent instance ID.
        :param service_path: The URI path of the service.
        :param session_id: The ID of the session on which the service invocation was made.
        """
        uri = self.URIs['services'].format(instance_id=instance_id,
                                           service_path=service_path)
        uri = uri + "?sessionId={}".format(session_id)
        return self._get_json(uri)


def build_agentclient(input_message: InputMessage, version) -> AgentClient:
    """
    Builds an agent client.
    """
    return build_client(AgentClient, input_message, version)
