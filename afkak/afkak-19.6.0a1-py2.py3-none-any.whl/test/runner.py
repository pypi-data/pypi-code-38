# -*- encoding: utf-8 -*-
# Copyright 2019 Ciena Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Afkak integration test runner


"""

import attr


@attr.s(frozen=True)
class KafkaClusterSpec(object):
    """
    :ivar int replicas: Number of Kafka brokers in the cluster.
    """
    replicas = attr.ib()


@attr.s(frozen=True)
class KafkaTopicSpec(object):
    """
    :ivar str name: Name of the topic.
    :ivar int partitions: Number of partitions in the topic.
    """
    name = attr.ib()
    partitions = attr.ib()


def _main():
    pass


if __name__ == '__main__':
    _main()
