# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
import os

from azureml._model_management._util import image_payload_template
from azureml._model_management._util import upload_dependency


class ContainerImageRequestBuilder(object):

    def __init__(self, workspace, image_flavor, name, tags, properties, description):
        json_payload = copy.deepcopy(image_payload_template)

        if image_flavor is None:
            raise ValueError("image_flavor is required")
        json_payload['imageFlavor'] = image_flavor

        if name is None:
            raise ValueError("name is required")
        json_payload['name'] = name

        if tags is None:
            tags = []
        json_payload['tags'] = tags

        # for now setting kv tags to empty!!!!
        json_payload['kvTags'] = {}

        if properties is None:
            properties = {}
        json_payload['properties'] = properties

        if description is None:
            description = ""
        json_payload['description'] = description

        self.workspace = workspace
        self.json_payload = json_payload

    def set_dockerfile(self, docker_file):
        if docker_file is not None:
            docker_file = docker_file.rstrip(os.sep)
            (self.json_payload['dockerFileUri'], _) = upload_dependency(self.workspace, docker_file)
        else:
            self.json_payload['dockerFileUri'] = ""

    def set_python_properties(self, runtime, architecture, driver_file, requirements, conda_file):
        self.json_payload['targetRuntime']['runtimeType'] = runtime
        self.json_payload['targetRuntime']['targetArchitecture'] = architecture

        if requirements:
            (self.json_payload['targetRuntime']['properties']['pipRequirements'], _) = \
                upload_dependency(self.workspace, requirements)

        if conda_file:
            conda_file = conda_file.rstrip(os.sep)
            (self.json_payload['targetRuntime']['properties']['condaEnvFile'], _) = \
                upload_dependency(self.workspace, conda_file)

        if driver_file:
            driver_mime_type = 'application/x-python'
            (driver_package_location, _) = upload_dependency(self.workspace, driver_file)
            self.json_payload['assets'].append({'id': 'driver', 'url': driver_package_location,
                                                'mimeType': driver_mime_type})

    def set_model_ids(self, model_ids):
        if model_ids:
            self.json_payload['modelIds'] = model_ids

    def set_dependencies(self, dependencies):
        if dependencies is not None:
            for dependency in dependencies:
                (artifact_url, artifact_id) = upload_dependency(self.workspace, dependency, create_tar=True)

                new_asset = {'mimeType': 'application/octet-stream',
                             'id': artifact_id,
                             'url': artifact_url,
                             'unpack': True}
                self.json_payload['assets'].append(new_asset)

    def set_cuda(self, enable_cuda):
        self.json_payload['targetRuntime']['properties']['installCuda'] = enable_cuda

    def get_payload(self):
        return self.json_payload
