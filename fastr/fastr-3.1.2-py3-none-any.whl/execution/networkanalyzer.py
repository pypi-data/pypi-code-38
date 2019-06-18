# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
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
Module that defines the NetworkAnalyzer and holds the reference implementation.
"""
from abc import abstractmethod


class NetworkAnalyzer(object):
    """
    Base class for NetworkAnalyzers
    """
    @abstractmethod
    def analyze_network(self, network, chunk):
        """
        Analyze a chunk of a Network.

        :param network: Network corresponding with the chunk
        :param chunk: The chunk of the network to analyze
        """
        pass


class DefaultNetworkAnalyzer(NetworkAnalyzer):
    """
    Default implementation of the NetworkAnalyzer.
    """
    def analyze_network(self, network, chunk):
        """
        Analyze a chunk of a Network. Simply process the Nodes in the chunk
        sequentially.

        :param network: Network corresponding with the chunk
        :param chunk: The chunk of the network to analyze
        """
        _, nodes = chunk

        # Start should be able to execute as is
        executionlist = []

        # All the unassigned nodes
        candidates = [x for x in nodes]

        while len(candidates) > 0:
            processed = []
            for node in candidates:
                prerequisites = node.get_sourced_nodes()

                for required in prerequisites:
                    if required in candidates:
                        break
                else:
                    # All required nodes are handled, move the candidate to the back of the execution list
                    executionlist.append(node)
                    processed.append(node)

            for node in processed:
                candidates.remove(node)

        return executionlist
