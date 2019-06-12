# Copyright 2018 Red Hat
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
#
# See the License for the specific language governing permissions and
# limitations under the License.

import math
import voluptuous as v

from nodepool.driver.openshift.config import OpenshiftPool
from nodepool.driver.openshift.config import OpenshiftProviderConfig


class OpenshiftPodsProviderConfig(OpenshiftProviderConfig):
    def __eq__(self, other):
        if isinstance(other, OpenshiftPodsProviderConfig):
            return (super().__eq__(other) and
                    other.context == self.context and
                    other.pools == self.pools)
        return False

    def load(self, config):
        self.launch_retries = int(self.provider.get('launch-retries', 3))
        self.context = self.provider['context']
        self.max_pods = self.provider.get('max-pods', math.inf)
        for pool in self.provider.get('pools', []):
            # Force label type to be pod
            for label in pool.get('labels', []):
                label['type'] = 'pod'
            pp = OpenshiftPool()
            pp.load(pool, config)
            pp.provider = self
            self.pools[pp.name] = pp

    def getSchema(self):
        openshift_label = {
            v.Required('name'): str,
            v.Required('image'): str,
            'image-pull': str,
            'cpu': int,
            'memory': int,
            'python-path': str,
        }

        pool = {
            v.Required('name'): str,
            v.Required('labels'): [openshift_label],
        }

        schema = OpenshiftProviderConfig.getCommonSchemaDict()
        schema.update({
            v.Required('pools'): [pool],
            v.Required('context'): str,
            'launch-retries': int,
            'max-pods': int,
        })
        return v.Schema(schema)
