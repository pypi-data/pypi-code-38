# Copyright 2018 Red Hat
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

import logging
import urllib3
import time

from kubernetes.config import config_exception as kce
from kubernetes import client as k8s_client
from openshift import config

from nodepool.driver.openshift.provider import OpenshiftProvider
from nodepool.driver.openshiftpods import handler

urllib3.disable_warnings()


class OpenshiftPodsProvider(OpenshiftProvider):
    log = logging.getLogger("nodepool.driver.openshiftpods."
                            "OpenshiftPodsProvider")

    def __init__(self, provider, *args):
        self.provider = provider
        self.ready = False
        try:
            self.token, self.k8s_client = self._get_client(
                provider.context)
        except kce.ConfigException:
            self.log.exception("Couldn't load client from config")
            self.log.info("Get context list using this command: "
                          "python3 -c \"from openshift import config; "
                          "print('\\n'.join([i['name'] for i in "
                          "config.list_kube_config_contexts()[0]]))\"")
            self.token = None
            self.k8s_client = None
        self.pod_names = set()
        for pool in provider.pools.values():
            self.pod_names.update(pool.labels.keys())

    def _get_client(self, context):
        conf = config.new_client_from_config(context=context)
        token = conf.configuration.api_key.get('authorization', '').split()[-1]
        return (token, k8s_client.CoreV1Api(conf))

    def start(self, zk_conn):
        self.log.debug("Starting")
        if self.ready or not self.k8s_client:
            return
        self.ready = True

    def listNodes(self):
        servers = []

        class FakeServer:
            def __init__(self, pool, pod, provider, valid_names):
                self.id = "%s-%s" % (pool, pod.metadata.name)
                self.name = self.id
                self.metadata = {}

                if [True for valid_name in valid_names
                    if pod.metadata.name.startswith("%s-" % valid_name)]:
                    node_id = pod.metadata.name.split('-')[-1]
                    try:
                        # Make sure last component of name is an id
                        int(node_id)
                        self.metadata['nodepool_provider_name'] = provider
                        self.metadata['nodepool_node_id'] = node_id
                    except Exception:
                        # Probably not a managed project, let's skip metadata
                        pass

            def get(self, name, default=None):
                return getattr(self, name, default)

        if self.ready:
            for pool in self.provider.pools.keys():
                for pod in self.k8s_client.list_namespaced_pod(pool).items:
                    servers.append(FakeServer(
                        pool, pod, self.provider.name, self.pod_names))
        return servers

    def getProjectPodName(self, server_id):
        for pool in self.provider.pools.keys():
            if server_id.startswith("%s-" % pool):
                pod_name = server_id[len(pool) + 1:]
                return pool, pod_name
        return None, None

    def cleanupNode(self, server_id):
        if not self.ready:
            return
        # Look for pool name
        project_name, pod_name = self.getProjectPodName(server_id)
        if not project_name:
            self.log.exception("%s: unknown pool" % server_id)
            return
        self.log.debug("%s: removing pod" % pod_name)
        delete_body = {
            "apiVersion": "v1",
            "kind": "DeleteOptions",
            "propagationPolicy": "Background"
        }
        try:
            self.k8s_client.delete_namespaced_pod(
                pod_name, project_name, delete_body)
            self.log.info("%s: pod removed" % server_id)
        except Exception:
            # TODO: implement better exception handling
            self.log.exception("Couldn't remove pod %s" % server_id)

    def waitForNodeCleanup(self, server_id):
        project_name, pod_name = self.getProjectPodName(server_id)
        for retry in range(300):
            try:
                self.k8s_client.read_namespaced_pod(pod_name, project_name)
            except Exception:
                break
            time.sleep(1)

    def getRequestHandler(self, poolworker, request):
        return handler.OpenshiftPodRequestHandler(poolworker, request)
