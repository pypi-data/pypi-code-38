# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Access EnvironmentClient"""

import requests
import json

from .workspace_client import WorkspaceClient


class EnvironmentClient(WorkspaceClient):
    """Environment client class"""

    def get_rest_client(self, user_agent=None):
        """get service rest client"""
        return self._service_context._get_environment_restclient(user_agent=user_agent)

    def _get_environment_definition(self, name, version=None):
        """
        :param environment_name:
        :type name: str
        :param version:
        :type version: str
        :return Returns the environment definition object:
        """

        cluster_address = self.get_cluster_url()
        headers = self.auth.get_authentication_header()
        workspace_address = self.get_workspace_uri_path()

        environment_url = cluster_address + "/environment/v1.0" + \
            workspace_address + "/environments/" + name

        if version is not None:
            environment_url += "/versions/" + str(version)
        # Else Retrieve the latest version of the environment definition

        response = requests.get(environment_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            message = "Error retrieving the environment definition. Code: {}\n: {}".format(response.status_code,
                                                                                           response.text)
            raise Exception(message)

    def _register_environment_definition(self, environment_dict):
        """
        :return Returns the environment definition dictionary from the response:
        """

        environment_name = environment_dict["name"]
        cluster_address = self.get_cluster_url()
        headers = self.auth.get_authentication_header()
        workspace_address = self.get_workspace_uri_path()
        environment_url = cluster_address + "/environment/v1.0" + \
            workspace_address + "/environments/" + environment_name

        body = {'Name': environment_name,
                'python': environment_dict["python"],
                "EnvironmentVariables": environment_dict["environmentVariables"],
                "Docker": environment_dict["docker"],
                "Spark": environment_dict["spark"]
                }

        response = requests.put(
            environment_url, headers=headers, json=body)

        if response.status_code == 200:
            return response.json()
        else:
            message = "Error registering the environment definition. Code: {}\n: {}".format(response.status_code,
                                                                                            response.text)
            raise Exception(message)

    def _get_image_details(self, name, version=None):
        """
        :param environment_name:
        :type name: str
        :param version:
        :type version: str
        :return Returns the image details:
        """

        cluster_address = self.get_cluster_url()
        headers = self.auth.get_authentication_header()
        workspace_address = self.get_workspace_uri_path()

        environment_url = cluster_address + "/environment/v1.0" + \
            workspace_address + "/environments/" + name

        if version is not None:
            environment_url += "/versions/" + str(version)

        environment_url += "/image"

        response = requests.get(environment_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            message = "Error getting image details. Code: {}\n: {}".format(response.status_code,
                                                                           response.text)
            raise Exception(message)

    def _list_definitions(self):
        """
        :return Returns the list of environment definitions in the workspace:
        """

        cluster_address = self.get_cluster_url()
        headers = self.auth.get_authentication_header()
        workspace_address = self.get_workspace_uri_path()

        environment_url = cluster_address + "/environment/v1.0" + \
            workspace_address + "/environments/"

        response = requests.get(environment_url, headers=headers)

        if response.status_code == 200:
            content = response.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')

            environment_dict = json.loads(content)
            return environment_dict["value"]
        else:
            message = "Error listing environment definitions. Code: {}\n: {}".format(response.status_code,
                                                                                     response.text)
            raise Exception(message)

    def _get_recipe_for_build(self, name, version=None):
        """
        :param environment_name:
        :type name: str
        :param version:
        :type version: str
        :return Returns the recipe details for image build:
        """

        cluster_address = self.get_cluster_url()
        headers = self.auth.get_authentication_header()
        workspace_address = self.get_workspace_uri_path()

        environment_url = cluster_address + "/environment/v1.0" + \
            workspace_address + "/environments/" + name

        if version is not None:
            environment_url += "/versions/" + str(version)

        environment_url += "/recipe"
        response = requests.post(environment_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            message = "Error getting recipe specifications. Code: {}\n: {}".format(response.status_code,
                                                                                   response.text)
            raise Exception(message)

    def _start_cloud_image_build(self, name, version=None):
        """
        :param environment_name:
        :type name: str
        :param version:
        :type version: str
        :return Returns the cloud image build details:
        """

        cluster_address = self.get_cluster_url()
        headers = self.auth.get_authentication_header()
        workspace_address = self.get_workspace_uri_path()

        environment_url = cluster_address + "/environment/v1.0" + \
            workspace_address + "/environments/" + name

        if version is not None:
            environment_url += "/versions/" + str(version)

        environment_url += "/image"

        response = requests.post(environment_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            message = "Error building image. Code: {}\n: {}".format(response.status_code,
                                                                    response.text)
            self._logger.error(message)
            raise Exception(message)

    def _get_cloud_image_build_status(self, build_id):
        """
        :param build_id:
        :type build_id: str
        :return Returns the cloud image build status:
        """

        cluster_address = self.get_cluster_url()
        headers = self.auth.get_authentication_header()
        workspace_address = self.get_workspace_uri_path()

        environment_url = cluster_address + "/environment/v1.0" + \
            workspace_address + "/builds/" + build_id

        response = requests.get(environment_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            message = "Error getting image build status. Code: {}\n: {}".format(response.status_code,
                                                                                response.text)

            raise Exception(message)
