# Copyright 2019 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import textwrap

import yaml

from tests.base import AnsibleZuulTestCase


class TestZuulHostVars(AnsibleZuulTestCase):
    tenant_config_file = 'config/remote-zuul-json/main.yaml'

    def setUp(self):
        super().setUp()
        self.fake_nodepool.remote_ansible = True

        ansible_remote = os.environ.get('ZUUL_REMOTE_IPV4')
        self.assertIsNotNone(ansible_remote)

    def _run_job(self, job_name):
        # Keep the jobdir around so we can inspect contents if an
        # assert fails. It will be cleaned up anyway as it is contained
        # in a tmp dir which gets cleaned up after the test.
        self.executor_server.keep_jobdir = True

        # Output extra ansible info so we might see errors.
        self.executor_server.verbose = True
        conf = textwrap.dedent(
            """
            - job:
                name: {job_name}
                run: playbooks/{job_name}.yaml
                roles:
                  - zuul: org/common-config
                nodeset:
                  nodes:
                    - name: controller
                      label: whatever
                host-vars:
                  controller:
                    ansible_python_interpreter: python2

            - project:
                check:
                  jobs:
                    - {job_name}
            """.format(job_name=job_name))

        file_dict = {'zuul.yaml': conf}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        job = self.getJobFromHistory(job_name)
        return job

    def test_hostvars(self):
        job = self._run_job('no-log')
        with self.jobLog(job):
            build = self.history[-1]
            inventory = yaml.safe_load(open(os.path.join(
                self.test_root, build.uuid, 'ansible', 'inventory.yaml')))
            self.assertEqual(
                "python2",
                inventory["all"]["hosts"]["controller"][
                    "ansible_python_interpreter"])
