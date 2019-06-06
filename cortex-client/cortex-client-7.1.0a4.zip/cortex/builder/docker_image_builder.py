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
import itertools
import os
from pathlib import Path
import tempfile
from urllib.parse import urljoin

import time
import cuid
import requests
import tenacity

from cortex.utils import log_message
from cortex.logger import getLogger
from cortex.builder.utils.docker_utils import DockerUtils
from cortex.exceptions import BuilderException
from cortex_client.builderclient import BuilderClient

log = getLogger(__name__)

class _DockerImageBuilder:

    def build_and_push(self, temp_dir, name, docker_repo, docker_auth):
        raise NotImplementedError

    @staticmethod
    def create_build_context(
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
        raise NotImplementedError


class DockerDaemonImageBuilder(_DockerImageBuilder):
    """A Docker image builder that uses the Docker socket."""

    @staticmethod
    def create_build_context(
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
        temp_dir = tempfile.mkdtemp()
        return DockerUtils.create_build_context(
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
        )

    def build_and_push(self, temp_dir, name, docker_repo, docker_auth):
        DockerUtils.build_and_push(temp_dir, name, docker_repo, docker_auth)


class BuilderServiceImageBuilder(_DockerImageBuilder):
    """A Docker image builder that uses the Cortex builder service."""

    def __init__(self, builder_url, token):
        # TODO: validate token
        self._client = BuilderClient(builder_url, 1, token)
        self._spinner = itertools.cycle(['-', '/', '|', '\\'])

    @staticmethod
    def create_build_context(
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
        temp_dir = BuilderServiceImageBuilder._generate_abs_build_path()
        return DockerUtils.create_build_context(
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
        )

    def build_and_push(self, build_dir, name, docker_repo, docker_auth=None):
        context_path = BuilderServiceImageBuilder._get_build_context_for_job(build_dir) 
        response = self._build_and_push(context_path, docker_repo)
        print("Build id: {}".format(response.get('jobName')))

        failure_count = 0
        job_id = response.get('jobName')
        while True:
            time.sleep(1)
            print("\b" + next(self._spinner), end="", flush=True)
            job_desc = self._get_job(job_id)
            status = job_desc.get('status', {})
            failed = status.get('failed', 0)
            succeeded = status.get('succeeded', False)
            active = status.get('active', False)
            if succeeded:
                print('\n*** SUCCESS!')
                break
            if not active:
                print('\n*** DONE.')
                break
            if failure_count < failed:
                failure_count = failed
                print('\n*** FAILURE: {}'.format(failed))
                time.sleep(8)
                self._get_job_logs(response.get('jobName'))

    ## private ##

    def _build_and_push(self, build_dir, image_tag):
        return self._client.post_job(build_dir, image_tag)
        
    def _wait_for_status(self, job_id, result_predicate):
        def get_job_print(jobid, spinner):
            print("\b" + next(spinner), end="", flush=True)
            r = self._get_job(jobid)
            print(r)
            return r
        r = tenacity.Retrying(
            wait = tenacity.wait_fixed(2),
            stop = tenacity.stop_after_delay(60),
            retry = tenacity.retry_if_result(result_predicate)
            )
        spinner = itertools.cycle(['-', '/', '|', '\\'])
        return r.wraps(get_job_print)(job_id, spinner)

    
    def _get_job(self, job_id):
        """Get build job"""
        return self._client.get_job(job_id)

    def _get_job_logs(self, job_id):
        """Get build job logs"""
        def get_logs_print(job_id):
            r = self._client.get_job_logs(job_id)
            for l in r.iter_lines(decode_unicode=True):
                if l: print(l)
        return get_logs_print(job_id)

    @staticmethod
    def _generate_abs_build_path():
        """Create a new directory for a Docker build context."""
        # TODO: For now, need to put the build context in `$HOME` so Kaniko can find it.
        context_path = Path('.cortex') / '.builder' / cuid.slug()
        temp_dir = Path.home() / context_path
        temp_dir.mkdir(parents=True, exist_ok=True)
        return str(temp_dir)

    @staticmethod
    def _get_build_context_for_job(path):
        """Get the build context path we need to pass on to the builder service."""
        # TODO: For now, need to put the build context in `$HOME` so Kaniko can find it.
        context_path = str(Path(path).relative_to(Path.home()))
        return context_path
