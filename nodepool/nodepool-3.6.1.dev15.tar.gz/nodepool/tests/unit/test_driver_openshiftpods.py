# Copyright (C) 2018 Red Hat
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import fixtures
import logging

from nodepool import tests
from nodepool import zk
from nodepool.driver.openshiftpods import provider


class FakeCoreClient(object):
    def __init__(self):
        self.pods = []

        class FakeApi:
            class configuration:
                host = "http://localhost:8080"
                verify_ssl = False
        self.api_client = FakeApi()

    def list_namespaced_pod(self, project):
        class FakePods:
            items = self.pods
        return FakePods

    def create_namespaced_pod(self, ns, pod_body):
        class FakePod:
            class metadata:
                name = pod_body['metadata']['name']
        self.pods.append(FakePod)
        return FakePod

    def read_namespaced_pod(self, name, ns):
        exist = False
        for pod in self.pods:
            if pod.metadata.name == name:
                exist = True
                break
        if not exist:
            raise RuntimeError("Pod doesn't exists")

        class FakePod:
            class status:
                phase = "Running"
        return FakePod

    def delete_namespaced_pod(self, name, project, delete_body):
        to_delete = None
        for pod in self.pods:
            if pod.metadata.name == name:
                to_delete = pod
                break
        if not to_delete:
            raise RuntimeError("Unknown pod %s" % name)
        self.pods.remove(to_delete)


class TestDriverOpenshiftPods(tests.DBTestCase):
    log = logging.getLogger("nodepool.TestDriverOpenshiftPods")

    def setUp(self):
        super().setUp()
        self.fake_k8s_client = FakeCoreClient()

        def fake_get_client(*args):
            return "fake-token", self.fake_k8s_client

        self.useFixture(fixtures.MockPatchObject(
            provider.OpenshiftPodsProvider, '_get_client',
            fake_get_client
        ))

    def test_openshift_pod(self):
        configfile = self.setup_config('openshiftpods.yaml')
        pool = self.useNodepool(configfile, watermark_sleep=1)
        pool.start()
        req = zk.NodeRequest()
        req.state = zk.REQUESTED
        req.node_types.append('pod-fedora')
        self.zk.storeNodeRequest(req)

        self.log.debug("Waiting for request %s", req.id)
        req = self.waitForNodeRequest(req)
        self.assertEqual(req.state, zk.FULFILLED)

        self.assertNotEqual(req.nodes, [])
        node = self.zk.getNode(req.nodes[0])
        self.assertEqual(node.allocated_to, req.id)
        self.assertEqual(node.state, zk.READY)
        self.assertIsNotNone(node.launcher)
        self.assertEqual(node.connection_type, 'kubectl')
        self.assertEqual(node.connection_port.get('token'), 'fake-token')

        node.state = zk.DELETING
        self.zk.storeNode(node)

        self.waitForNodeDeletion(node)
