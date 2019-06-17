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

# Patch asyncio to allow nested loop.run_to_completion() calls, necessary
# when the BuilderServiceImageBuilder runs inside a JupyterLab kernel,
# which is already running syncronous code in an asyncio event loop.
import asyncio
import nest_asyncio
nest_asyncio.apply()

import itertools
import os
from pathlib import Path
import tempfile
from urllib.parse import urljoin

from asgiref.sync import sync_to_async
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
        requirements=[],
        conda_requirements=[],
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
        requirements=[],
        conda_requirements=[],
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

    # One hour wait limit for build job completion, query every 2 seconds
    CONST_JOB_COMPLETION_LIMIT_SEC = 60 * 60
    CONST_JOB_STATUS_INTERVAL_SEC = 2

    def __init__(self, builder_url, token):
        # TODO: validate token
        self._client = BuilderClient(builder_url, 1, token)

    @staticmethod
    def create_build_context(
        action_type,
        source,
        func_name,
        global_code,
        cortex_sdk_version,
        source_archive,
        base_image,
        requirements=[],
        conda_requirements=[],
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
        job_id = response.get('jobName')
        print("Build id: {}".format(job_id))

        # Concurrently wait for job completion and log exhaustion.
        loop = asyncio.get_event_loop()
        futures = asyncio.gather(
            self._wait_for_job_completion(job_id),
            self._wait_for_job_logs(job_id)
        )
        [status, ignored] = loop.run_until_complete(futures)

        succeeded = status.get('succeeded', False)
        if succeeded:
            print('\n*** SUCCESS!')
        else:
            print('\n*** FAILURE')

    ## private ##

    def _build_and_push(self, build_dir, image_tag):
        return self._client.post_job(build_dir, image_tag)

    async def _wait_for_job_completion(self, job_id):
        """ async wait until build job succeeds or fails """
        def is_job_pending(status):
            if status:
                succeeded = status.get('succeeded', False)
                failed = status.get('failed', 0)
                return not (succeeded or failed)
            return True

        @tenacity.retry(
            retry=tenacity.retry_if_result(is_job_pending),
            stop=tenacity.stop_after_delay(CONST_JOB_COMPLETION_LIMIT_SEC),
            wait=tenacity.wait_fixed(CONST_JOB_STATUS_INTERVAL_SEC)
        )
        async def retry_job_status(job_id):
            status = await sync_to_async(self._get_job_status)(job_id)
            return status

        return await retry_job_status(job_id)

    async def _wait_for_job_logs(self, job_id):
        """ async wait until job logs have been exhasuted, with print side-effect """
        def print_log_stream(job_id):
            with self._client.get_job_logs(job_id) as response:
                for line in response.iter_lines(decode_unicode=True):
                   if line: print(line)

        # HACK - job logs aren't immediately available, as the containers inside
        # the job's pod must be started.  Until I've accounted for that in the
        # builder service log request handler, poll job status here...
        def is_available(status):
            if status:
                active = status.get('active', 0)
                succeeded = status.get('succeeded', False)
                failed = status.get('failed', 0)
                return active or succeeded or failed
            return False

        @tenacity.retry(
            retry=tenacity.retry_if_result(is_job_pending),
            stop=tenacity.stop_after_delay(CONST_JOB_COMPLETION_LIMIT_SEC),
            wait=tenacity.wait_fixed(CONST_JOB_STATUS_INTERVAL_SEC)
        )
        async def retry_job_status(job_id):
            status = await sync_to_async(self._get_job_status)(job_id)
            return status
        await retry_job_status(job_id)
        # End HACK

        await sync_to_async(print_log_stream)(job_id)

    def _get_job(self, job_id):
        """Get build job"""
        return self._client.get_job(job_id)

    def _get_job_status(self, job_id):
        job_desc = self._get_job(job_id)
        status = job_desc.get('status', {})
        return status

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