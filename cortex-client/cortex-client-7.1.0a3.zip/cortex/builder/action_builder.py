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

import cuid
import dill
import jinja2
import jwt
import logging
import os
import pkg_resources
import shutil
import tempfile
import urllib3
from typing import Optional
from setuptools import sandbox

from cortex.action import Action
from cortex_client import ActionClient, ConnectionClient
from cortex.utils import md5sum, log_message, is_notebook, decode_JWT
from cortex.timer import Timer
from cortex.logger import getLogger
from cortex.exceptions import BuilderException
from cortex.builder.docker_image_builder import DockerDaemonImageBuilder
from cortex.builder.docker_image_builder import BuilderServiceImageBuilder
from cortex.builder.utils.template_utils import TemplateUtils
from cortex.builder.utils.python_utils import PythonUtils

log = getLogger(__name__)

# Configure dill to 'recurse' dependencies when dumping objects
dill.settings['recurse'] = True

_action_daemon = 'daemon'
_action_function = 'function'
_action_job = 'job'

_base_image = 'c12e/cortex-python36:7552534'

_predict_globals = """
_model_key = "{model_key}"
_model = False
"""

_sklearn_predict_shim = 'predict_function_sklearn.py.j2'
_docker_daemon_port = 5000
_daemon_main = 'daemon.py.j2'
_function_main = 'func.py.j2'
_job_main = 'job.py.j2'
_cortex_sdk_version = pkg_resources.get_distribution("cortex-client").version
_private_registry_prefix = 'private-registry'


class ActionBuilder:
    """
    Builds an action, the computional part of a skill.
    """

    def __init__(self, name: str, client: ActionClient, camel='1.0.0'):
        self._camel = camel
        self._name = name
        self._image = None
        self._image_prefix = None
        self._base_image = _base_image
        self._tag = cuid.slug()
        self._registry = None
        self._client = client
        self._token = client._serviceconnector.token
        decoded = decode_JWT(self._token, verify=False)
        self._username = decoded['sub']
        self._tenant_id = decoded['tenant']
        self._kind = 'blackbox'
        self._action_type = _action_function
        self._code_s = None
        self._code_archive = None
        self._fn_name = None
        self._model = None
        self._requirements = []
        self._conda_requirements = []
        self._docker_builder = ActionBuilder._get_docker_builder()

    @staticmethod
    def _get_docker_builder():
        builder_url = os.environ.get('CORTEX_BUILDER_URL')
        if builder_url:
            return BuilderServiceImageBuilder(builder_url, os.environ.get('CORTEX_TOKEN'))
        return DockerDaemonImageBuilder()

    def from_image(self, image: str):
        """
        Sets the Docker image name.

        :param name: name of the docker image
        """
        self._image = image
        return self

    def image_prefix(self, prefix):
        """
        Adds a path definition prefix to the Docker image name; ignored when the 'registry' property is set.

        :param prefix: prefix to use with the Docker image
        """
        self._image_prefix = prefix
        return self

    def registry(self, registry_uri: str):
        """
        Sets the Docker registry URI.
        """
        self._registry = registry_uri
        return self

    def kind(self, kind: str):
        """
        Sets the kind of action, either "python:3" or "python:2".
        """
        self._kind = kind
        return self

    def daemon(self):
        """
        Sets the action to type: daemon.
        """
        self._action_type = _action_daemon
        return self

    def job(self):
        """
        Sets the action to type: job.
        """
        self._action_type = _action_job
        return self

    @property
    def name(self):
        """
        Gets the name for the ActionBuilder
        """
        return self._name

    def from_source(self, source_str: str, function_name: str = 'main'):
        """
        Builds an action from source code. NOTE: The Python source code must contain a function with the specified name.

        :param source_str: Python source code string
        :param function_name: name of the function to invoke, default is 'main'
        :return: the builder instance
        """
        self._code_s = source_str
        self._fn_name = function_name
        return self

    def from_source_file(self, file_path: str, function_name: str = 'main'):
        """
        Builds an action from a source file.  NOTE: The Python source code must contain a function with the specified name.

        :param file_path: path to a file containing Python source code
        :param function_name: name of the function to invoke, default is 'main'
        :return: the builder instance
        """
        with open(file_path) as f:
            self._code_s = f.read()

        self._fn_name = function_name

        return self

    def from_setup(self, setup_script: str, action_module: str, function_name: str = 'main'):
        """
        Builds an action from a source archive built using Python Setuptools; builds the source distribution
        using the Setuptools sandbox.

        :param setup_script: path to setup.py script
        :param action_module: full path to the Python module containing the action: function
        :param function_name: name of the function to import and invoke, default is 'main'
        :return: the builder instance
        """
        setup_dir = os.path.abspath(os.path.dirname(setup_script))
        dist_dir = '{}/dist'.format(setup_dir)
        log_message('Running setup using script {} in directory {}'.format(setup_script, setup_dir), log, logging.INFO)

        # clean up dist directory from previous builds
        shutil.rmtree(dist_dir, ignore_errors=True)

        sandbox.run_setup(setup_script, ['sdist', '--format=tar'])

        for fname in os.listdir(dist_dir):
            if fname.endswith('tar'):
                self._code_archive = '{}/dist/{}'.format(setup_dir, fname)
                log_message('Using source archive: {}'.format(self._code_archive), log, logging.INFO)
                break

        if not self._code_archive:
            raise BuilderException('Error building source archive, source archive not found under dist directory: {}'.format(dist_dir))

        self._fn_name = function_name
        self._code_s = 'from {} import {}'.format(action_module, function_name)

        return self

    def from_model(self, model, model_type="sklearn", x_pipeline=None, y_pipeline=None, target='y'):
        """
        Associates a model with this ActionBuilder.
        """
        self._model = {'model': model, 'type': model_type, 'x_pipe': x_pipeline, 'y_pipe': y_pipeline, 'target': target}

        return self

    def with_pip_freeze(self):
        """
        Sets the requirements for this ActionBuilder with `pip freeze`.
        """
        self._requirements = list(self._pip_freeze())
        return self

    def with_requirements(self, requirements: list):
        """
        Sets requirements for this ActionBuilder to the given list.

        :param requirements: a list of requirements
        """
        self._requirements = [str(r) for r in requirements]
        return self

    def with_conda_requirements(self, requirements: list):
        """
        Sets conda requirements for this ActionBuilder to the given list.

        :param requirements: a list of requirements
        """
        self._conda_requirements = [str(r) for r in requirements]
        return self

    def with_base_image(self, base_image):
        """
        Sets the base image to use for the Action container.

        :param base_image: a valid image name for an image that is accessible on the machine this builder is run.
        """
        self._base_image = base_image
        return self

    def build(self, **kwargs) -> Optional[Action]:
        """
        Builds an action.

        :return: An action, or `none`, if the dry-run flag is set
        """
        _dry_run = kwargs.get('dry_run', False)
        sdk_version = kwargs.get('cortex_sdk_version', _cortex_sdk_version) 
        kwargs.pop('cortex_sdk_version', None)

        log_message('Building Cortex Action ({}): {}'.format(self._action_type, self._name), log, logging.INFO)

        if self._action_type == _action_daemon:
            self._build_daemon(sdk_version, _dry_run)
        elif self._action_type == _action_job:
            self._build_job(sdk_version, _dry_run, **kwargs)
        else:
            self._build_function(sdk_version, _dry_run)

        if _dry_run:
            return None

        return Action.get_action(self._name, self._client._serviceconnector)

    ## private ##

    def _get_docker_repository(self, use_prefix=False):
        # 1. If the image name is explicitly set, we ignore the registry and prefix settings and also override our
        # default image naming scheme
        if self._image is not None:
            if self._image_prefix and use_prefix:
                return '{}/{}'.format(self._image_prefix, self._image)
            return self._image

        # 2. Use the image prefix in front of our default image name
        if self._image_prefix and use_prefix:
            return '{}/{}:{}'.format(self._image_prefix, self._name, self._tag)

        # 3. Use registry explicitly set by the user
        if self._registry is not None:
            # Prepend registry URI to default image name/tag.  Ignore image prefix.
            return '{}/{}:{}'.format(self._registry, self._name, self._tag)

        # 4. Use built-in private registry in Cortex 5
        api_endpoint = urllib3.util.parse_url(self._client._serviceconnector.url)
        registry_uri = '{}.{}'.format(_private_registry_prefix, '.'.join(api_endpoint.host.split('.')[1:]))

        return '{}/{}/{}:{}'.format(registry_uri, self._tenant_id, self._name.replace('/', '_'), self._tag)

    def _get_docker_auth(self):
        if self._image is None and self._registry is None and self._image_prefix is None:
            # Using the built-in private registry in Cortex 5.  Use the current JWT token for auth.
            return {'username': 'cogscale', 'password': self._client._serviceconnector.token}
        return None

    def _build_function(self, cortex_sdk_version, dry_run=False):
        if self._code_s:
            self._kind = 'python:3'
            if not dry_run:
                # Build new docker image with the given action source code
                self._deploy_function_image(self._code_s, self._fn_name or 'main', '', cortex_sdk_version, self._code_archive)
        elif self._model:
            self._kind = 'python:3'
            # Deploy from ML model object
            self._deploy_model(cortex_sdk_version, dry_run)
        else:
            # Deploy existing docker image
            if not dry_run:
                self._client.deploy_action(self._name, self._kind, self._get_docker_repository())

    def _build_daemon(self, cortex_sdk_version, dry_run=False):
        if self._code_s:
            if not dry_run:
                # Build a new docker image with the given action source code
                self._deploy_daemon_image(self._code_s, self._fn_name or 'main', '', cortex_sdk_version, self._code_archive)
        elif self._model:
            # Deploy from ML model object
            self._deploy_model(cortex_sdk_version, dry_run)
        else:
            # Deploy existing docker image
            if not dry_run:
                self._client.deploy_action(self._name, self._kind, self._get_docker_repository(),
                                           action_type=_action_daemon)

    def _build_job(self, cortex_sdk_version, dry_run=False, **kwargs):
        if self._code_s:
            if not dry_run:
                # Build new docker image with the given action source code
                self._deploy_job_image(self._code_s, self._fn_name or 'main', '', cortex_sdk_version, self._code_archive, **kwargs)
        elif self._model:
            # Deploy from ML model object
            self._deploy_model(cortex_sdk_version, dry_run, **kwargs)
        else:
            # Deploy existing docker image
            if not dry_run:
                vcpus = int(kwargs.get('vcpus', 1))
                memory = int(kwargs.get('memory', 256))
                backend_type = kwargs.get('backend_type', None)
                self._client.deploy_action(self._name, self._kind, self._get_docker_repository(),
                                           action_type=_action_job, backend_type=backend_type, vcpus=vcpus,
                                           memory=memory)


    def _deploy_daemon_image(self, source, func_name, global_code, cortex_sdk_version, source_archive=None):
        temp_dir = self._docker_builder.create_build_context('daemon', source, func_name, global_code, cortex_sdk_version, source_archive, self._base_image, self._requirements, self._conda_requirements)
        self._docker_builder.build_and_push(temp_dir, self._name, self._get_docker_repository(), self._get_docker_auth())
        # Deploy the Cortex Action
        self._client.deploy_action(self._name, self._kind, self._get_docker_repository(use_prefix=True),
                                   action_type=_action_daemon,
                                   port=str(_docker_daemon_port))

    def _deploy_function_image(self, source, func_name, global_code, cortex_sdk_version, source_archive=None):
        temp_dir = self._docker_builder.create_build_context('function', source, func_name, global_code, cortex_sdk_version, source_archive, self._base_image, self._requirements, self._conda_requirements)
        self._docker_builder.build_and_push(temp_dir, self._name, self._get_docker_repository(), self._get_docker_auth())
        self._client.deploy_action(self._name, self._kind, self._get_docker_repository(use_prefix=True))

    def _deploy_job_image(self, source, func_name, global_code, cortex_sdk_version, source_archive=None, **kwargs):
        temp_dir = self._docker_builder.create_build_context('job', source, func_name, global_code, cortex_sdk_version, source_archive, self._base_image, self._requirements, self._conda_requirements)
        self._docker_builder.build_and_push(temp_dir, self._name, self._get_docker_repository(), self._get_docker_auth())
        # Deploy the Cortex Action
        vcpus = int(kwargs.get('vcpus', 1))
        memory = int(kwargs.get('memory', 256))
        backend_type = kwargs.get('backend_type', None)
        self._client.deploy_action(self._name, self._kind, self._get_docker_repository(use_prefix=True),
                                   action_type=_action_job, backend_type=backend_type, vcpus=vcpus,
                                   memory=memory)


    def _dump_source(self, action_source):
        print('--- action.py ---')
        print(action_source)
        print('--- requirements.txt ---')
        print(PythonUtils._build_requirements(self._requirements))
        print('--- conda_requirements.txt ---')
        print(PythonUtils._build_requirements(self._conda_requirements))
        print('-' * 30)

    def _deploy_model(self, cortex_sdk_version, dry_run=False):
        content_client = ConnectionClient(
            self._client._serviceconnector.url,
            2,
            self._client._serviceconnector.token
        )

        temp_path = None
        try:
            # Upload model version to managed content
            with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as temp:
                temp_path = temp.name
                dill.dump(self._model, temp)

            md5 = md5sum(temp.name)
            model_key = '/cortex/models/%s/%s.pk' % (self._name, md5)

            if not content_client.exists(model_key):
                log_message('model version not found, pushing to remote storage: ' + model_key, log)
                with open(temp.name, 'rb') as f:
                    content_client.uploadStreaming(key=model_key, content_type='application/octet-stream', stream=f)
        finally:
            shutil.rmtree(temp_path, ignore_errors=True)

        # Deploy predict action
        _predict_source = TemplateUtils.render_template(_sklearn_predict_shim)
        _globals = _predict_globals.format(model_key=model_key[1:])

        if self._action_type == _action_daemon:
            if dry_run:
                source = TemplateUtils.render_template(_daemon_main, action_globals=_globals, action_code=_predict_source,
                                               func_name='predict')
                self._dump_source(source)
                return

            self._deploy_daemon_image(_predict_source, 'predict', _globals, cortex_sdk_version)
        elif self._action_type == _action_job:
            if dry_run:
                source = TemplateUtils.render_template(_job_main, action_globals=_globals, action_code=_predict_source,
                                               func_name='predict')
                self._dump_source(source)
                return

            self._deploy_job_image(_predict_source, 'predict', _globals, cortex_sdk_version)
        else:
            if dry_run:
                source = TemplateUtils.render_template(_function_main, action_globals=_globals, action_code=_predict_source,
                                               func_name='predict')
                self._dump_source(source)
                return

            self._deploy_function_image(_predict_source, 'predict', _globals, cortex_sdk_version)

    @staticmethod
    def _pip_freeze():
        try:
            from pip._internal.operations import freeze
        except ImportError:  # pip < 10.0
            from pip.operations import freeze

        return freeze.freeze()
