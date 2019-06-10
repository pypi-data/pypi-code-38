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
import logging
import os
import pkg_resources
import re
import shutil

import docker
from docker.utils.json_stream import json_stream

from cortex.builder.utils.template_utils import TemplateUtils
from cortex.builder.utils.python_utils import PythonUtils
from cortex.logger import getLogger
from cortex.timer import Timer
from cortex.utils import log_message

log = getLogger(__name__)

_action_daemon = "daemon"
_action_function = "function"
_action_job = "job"

_base_image = "c12e/cortex-python36:7552534"

_docker_daemon_port = 5000
_dockerfile_daemon = "Dockerfile.daemon.j2"
_dockerfile_func = "Dockerfile.func.j2"
_dockerfile_job = "Dockerfile.job.j2"

_daemon_main = "daemon.py.j2"
_function_main = "func.py.j2"
_job_main = "job.py.j2"

class DockerUtils:
    """Docker related utils."""
    @staticmethod
    def create_docker_file(temp_dir, action_type, cortex_sdk_version, source_archive, base_image):
        """Creates a `Dockerfile`.

        :param temp_dir: Directory where we want to put the build context.
        :param action_type: The type of Action to build the Dockerfile for. Must be `function`, `job` or `daemon`.
        :param cortex_sdk_version: The version of the Python SDK to install in the Docker image. 
        :param source_archive: Optional `action.tar` file with source.
        :param base_image: The base image for the Dockerfile.

        :return: None
        """
        action_type_args = {
            'function': {'template_name': _dockerfile_func},
            'daemon': {'template_name': _dockerfile_daemon, 'port': _docker_daemon_port},
            'job': {'template_name': _dockerfile_job}
        }
        if bool(source_archive):
            shutil.copyfile(source_archive, "{}/action.tar".format(temp_dir))
        # Generate Dockerfile for container
        TemplateUtils.render_and_save(
            temp_dir,
            "Dockerfile",
            base_image=base_image,
            cortex_sdk_version=cortex_sdk_version,
            deploy_archive=bool(source_archive),
            **action_type_args[action_type]
        )

    @staticmethod
    def create_action_source_module(temp_dir, action_type, source, func_name, global_code):
        """Creates an `action.py` Python module with `source` code.

        :param temp_dir: The build context directory.
        :param action_type: The Action type. Must be one of `function`, `job` or `daemon`.
        :param source: The source code to add to the module.
        :param func_name: The name of the function to invoke in the module.
        :param global_code: Any globals to include in the module. 

        :return: None
        """
        action_type_args = {
            'function': _function_main,
            'daemon': _daemon_main,
            'job': _job_main,
        }
        # Generate action.py 
        TemplateUtils.render_and_save(
            temp_dir,
            "action.py",
            action_type_args[action_type],
            action_globals=global_code,
            action_code=DockerUtils.indent_block(source),
            func_name=func_name,
        )

    @staticmethod
    def create_build_context(
        temp_dir,
        action_type,
        source,
        func_name,
        global_code,
        cortex_sdk_version,
        source_archive,
        base_image,
        requirements,
        conda_requirements,
    ):
        # TODO: return what?
        DockerUtils.create_docker_file(temp_dir, action_type, cortex_sdk_version, source_archive, base_image)
        DockerUtils.create_action_source_module(temp_dir, action_type, source, func_name, global_code)
        # Generate pip requirements.txt
        reqs = PythonUtils.build_requirements(requirements)
        TemplateUtils.dump_file(temp_dir, "requirements.txt", reqs)
        # Generate conda requirements
        conda_reqs = PythonUtils.build_requirements(conda_requirements)
        TemplateUtils.dump_file(temp_dir, "conda_requirements.txt", conda_reqs)

        # TODO: cleanup temp. Needs to happend after function deploy
        # shutil.rmtree(temp_dir, ignore_errors=True)
        return temp_dir

    @staticmethod
    def build_and_push(build_dir, name, repository, auth_config=None):
        """Build a Docker image and push it to a Docker registry.

        :param build_dir: The directory where the build context is located.
        :param name: A tag for the built image.
        :param repository: The full image registry+repo+name.
        :param auth_config: Override the credentials that are found in the config for this request. auth_config should contain the username and password keys to be valid.

        :return: None
        """
        d = DockerUtils.get_docker_client()
        cli = d.api
        log_message("Building Docker image {}...".format(repository), log, logging.INFO)
        with Timer() as t:
            buildargs = DockerUtils.get_proxy_env_vars()
            stream = cli.build(
                path=build_dir,
                tag=repository,
                forcerm=True,
                buildargs=buildargs,
                # NOTE: use_config_proxy reads http_proxy from ~/.docker/config.json
                # if proxy config is provided in ~/.docker/config.json, the docker config
                # will overwrite http(s)_proxy values passed in as `buildargs`.
                use_config_proxy=True,
            )
            for obj in json_stream(stream):
                if "stream" in obj:
                    line = obj["stream"].strip()
                    if line and not line.startswith("--->"):
                        log_message(line, log, logging.INFO)
                elif "error" in obj:
                    msg = "Docker ERROR: {}".format(obj["error"])
                    log_message(msg, log, logging.ERROR)
                    raise BuilderException(msg)
        log_message(
            "Image {} built in {:2f} seconds".format(repository, t.interval),
            log,
            logging.INFO,
        )

        ## TODO: is this necessary? get rid of this line?
        cli.tag(image=repository, repository=name)

        log_message("Pushing image to remote repository...", log, logging.INFO)
        with Timer() as t:
            stream = cli.push(repository, auth_config=auth_config, stream=True)
            for obj in json_stream(stream):
                if "status" in obj:
                    match = re.search(
                        r"(^.*:\s+digest:\s+sha256:)([0-9a-f]+).*", obj["status"]
                    )
                    if match:
                        log_message(obj["status"], log, logging.INFO)
                if "errorDetail" in obj:
                    msg = "Docker ERROR: {}".format(obj["errorDetail"])
                    log_message(msg, log, logging.ERROR)
                    raise BuilderException(msg)
        log_message(
            "Image {} pushed in {:2f} seconds".format(repository, t.interval),
            log,
            logging.INFO,
        )

        log_message("Cleaning up...", log, logging.INFO)
        try:
            # Remove old versions of the image
            repo_no_tag = repository[0 : repository.rindex(":")]
            images = d.images.list(name=repo_no_tag, filters={"before": repository})
            if images and len(images) > 0:
                for img in images:
                    log_message(
                        "Removing previous image: " + img.short_id, log, logging.INFO
                    )
                    d.images.remove(img.id, force=True)
        except (Exception) as e:
            log_message(
                "Docker ERROR during cleanup: {}".format(str(e)), log, logging.ERROR
            )

    @staticmethod
    def get_docker_client():
        """Returns a Docker client."""
        try:
            return docker.from_env(version="auto")
        except Exception as e:
            msg = "{}. Is Docker running?".format(str(e))
            log_message("*** ERROR (Docker): {}".format(msg), log, logging.ERROR)
            raise BuilderException(msg)

    @staticmethod
    def get_proxy_env_vars():
        """Returns a dict with http proxy settings found in environment variables."""
        envkeys = ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]
        return dict((k, os.environ[k]) for k in envkeys if k in os.environ)

    @staticmethod
    def indent_block(s: str, spaces=4):
        """Indent a block of code `s`."""
        lines = s.split("\n")
        lines = map(lambda line: (" " * spaces) + line, lines)
        return "\n".join(lines)