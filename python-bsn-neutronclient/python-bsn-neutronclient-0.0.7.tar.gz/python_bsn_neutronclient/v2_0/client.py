# -*- coding: utf-8 -*-

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

from neutronclient.v2_0.client import Client as NeutronClientV2


class Client(NeutronClientV2):
    force_bcf_sync_path = "/forcesynctopologies/%s"
    force_bcf_sync_path_plural = "/forcesynctopologies"

    def force_bcf_sync(self, topo_sync_id=None):
        if not topo_sync_id:
            topo_sync_id = 1

        body = {'forcesynctopology': {'timestamp_ms': 'now'}}
        return self.put(self.force_bcf_sync_path % topo_sync_id, body=body)
