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

from .client import _Client

class BuilderClient(_Client):
    """
    A client for the Cortex Docker builder service REST API.
    """

    URIs = {'action':'builder/action'}

    def post_job(self, build_dir, image_tag):
        """
        Submit a build job request
        """
        body = {
            'imageTag' : image_tag,
            'buildContext': build_dir
        }
        return self._post_json(self.URIs['action'], body)

    def get_job(self, jobid):
        """
        Gets targets for the agent.
        """
        return self._get_json(self.URIs['action'] + '/{}'.format(jobid))

    def get_job_logs(self, jobid):
        """
        Gets job logs.
        """
        url = '/'.join([self.URIs['action'], jobid, 'logs'])
        return self._get(url, stream=True)
