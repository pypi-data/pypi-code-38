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
This module contains the NetworkChunker class and its default implementation
the DefaultNetworkChunker
"""

from abc import abstractmethod
from collections import deque

from .. import exceptions
from ..helpers import log

class NetworkChunker(object):
    """
    The base class for NetworkChunkers. A Network chunker is a class that takes
    a Network and produces a list of chunks that can each be analyzed and
    executed in one go.
    """

    @abstractmethod
    def chunck_network(self, network):
        """ Create a list of Network chunks that can be pre-analyzed completely.
        Each chunk needs to be executed before the next can be analyzed and
        executed.

        :param network: Network to split into chunks
        :return: list containing chunks
        """
        pass


class DefaultNetworkChunker(NetworkChunker):
    """
    The default implementation of the NetworkChunker. It tries to create as
    large as possible chunks so the execution blocks as little as possible.
    """

    def __init__(self):
        self.chunks = []
        self.node_status = {}
        self.pool = set()
        self.processed_nodes = set()
        self.used_nodes = set()

    def chunck_network(self, network):
        """ Create a list of Network chunks that can be pre-analyzed completely.
        Each chunk needs to be executed before the next can be analyzed and
        executed.

        The returned chunks are (at the moment) in the format of a tuple (start, nodes)
        which are both tuples. The tuple contain the nodes where to start execution (should
        ready if previous chunks are done) and all nodes of the chunk respectively.

        :param network: Network to split into chunks
        :return: tuple containing chunks
        """
        self._set_network_used_nodes(network)

        log.debug('START Pool: {}'.format(self.used_nodes))
        log.debug('SOURCELIST: {}'.format(network.sourcelist))
        log.debug('CONSTANTLIST: {}'.format(network.constantlist))
        candidates = deque()

        for source in network.sourcelist.values():
            if source.id in self.used_nodes:
                candidates.append(source.id)

        for constant in network.constantlist.values():
            if constant.id in self.used_nodes:
                candidates.append(constant.id)

        log.debug('START candidates: {}'.format(candidates))

        chunks = []
        self.pool = set(self.used_nodes)
        while len(self.used_nodes) > 0:
            chunk_start = [x for x in candidates]
            new_chunk = []
            new_candidates = deque()

            while len(candidates) > 0:
                node = network.nodelist[candidates.popleft()]
                log.debug('Considering Node {}'.format(node.id))

                if node in candidates:
                    log.error('NODE HAS ENTERED CANDIDATES TWICE! {}'.format(node))

                if node.id not in self.pool:
                    log.debug(('Used nodes: {}\nPool: {}\nCandidates: {}'
                                     '\nNew candidates: {}').format(self.used_nodes,
                                                                    self.pool,
                                                                    candidates,
                                                                    new_candidates))
                    message = 'Encountered previously visited Node {}!'.format(node.id)
                    log.error(message)
                    raise exceptions.FastrStateError(message)

                # If this NodeRun definitely cannot be executed, move to pool for next chunks
                if not self._node_is_candidate(node):
                    log.debug('Moving {} to next chunk (not a candidate)'.format(node.id))
                    if node.id not in new_candidates:
                        new_candidates.append(node.id)
                    continue

                # If this NodeRun is blocked by earlier nodes in the Chunk, move it to pool for next chunks
                if self._node_is_blocked(node):
                    log.debug('Moving {} to next chunk (is blocked)'.format(node.id))
                    if node.id not in new_candidates:
                        new_candidates.append(node.id)
                    continue

                # Change node status and append to working chunk
                log.debug('Adding {} to chunk'.format(node.id))
                self.used_nodes.remove(node.id)
                self.node_status[node.id] = 'visited'
                new_chunk.append(node.id)

                log.debug('Processing listeners for {}'.format(node.id))
                # Recurse into following Nodes
                for listener in node.listeners:
                    lnode = listener.target.node
                    log.debug('Considering listener {}'.format(lnode.id))

                    if lnode.id not in self.used_nodes:
                        log.debug('Ignoring {}'.format(lnode.id))
                        continue

                    if not self._node_is_blocked(lnode):
                        if lnode.id not in candidates:
                            log.info('Adding {} to candidates'
                                            ' (blocking {})'.format(lnode.id,
                                                                    self._node_is_blocked(lnode)))
                            candidates.append(lnode.id)
                        else:
                            log.debug('Listener {} already in candidates'.format(lnode.id))
                    else:
                        if lnode.id not in new_candidates:
                            log.debug('Queueing {} ({})'.format(lnode.id, self._node_is_blocked(lnode)))
                            if lnode in candidates:
                                candidates.remove(lnode.id)
                            if node.id not in new_candidates:
                                new_candidates.append(lnode.id)

            # Add the newly created chunk to the list
            chunk_start = tuple(x for x in chunk_start if x in new_chunk)
            log.debug('Adding chunk {} with start {}'.format(new_chunk,
                                                                   chunk_start))

            if len(new_chunk) == 0 and candidates == new_candidates:
                raise exceptions.FastrStateError('Network chunker does not converge! It appears there is a bug!')

            chunks.append((chunk_start, tuple(new_chunk)))

            candidates = new_candidates
            self.processed_nodes.update(new_chunk)
            self.pool = self.pool - self.processed_nodes  # Remove processed nodes from pool
            log.debug('Start new chuck with candidates {} and pool {}'.format(candidates,
                                                                                    self.pool))

        # After chunking return a tuple of tuples, to avoid tempering later on
        chunks = tuple(tuple(tuple(network.nodelist[x] for x in item) for item in chunk) for chunk in chunks)
        return tuple(chunks)

    def _node_is_candidate(self, node):
        """
        Check if the NodeRun is considered a candidate

        :param node: NodeRun to check
        :return: flag indicating the NodeRun is a candidate
        """
        for node in node.get_sourced_nodes():
            if node.id not in self.processed_nodes and node.id not in self.pool:
                return False

        return True

    @staticmethod
    def _node_is_analyzable(node):
        """
        Check if it is possible to analyze a NodeRun

        :param node: NodeRun to check
        :return: flag indicating the NodeRun is analyzable
        """
        for snode in node.get_sourced_nodes():
            if snode.blocking:
                return False

        return True

    def _node_is_blocked(self, target):
        """
        Check if a NodeRun is blocked

        :param target: NodeRun to check
        :return:flag indicating the NodeRun is blocked by a blocking NodeRun
        """
        for node in target.get_sourced_nodes():
            if node.id in self.pool and (node.blocking or self._node_is_blocked(node)):
                log.debug('NodeRun {} is the cause of the blocked node {} (pool: {})'.format(node.id,
                                                                                                   target.id,
                                                                                                   self.pool))
                return True

        return False

    def _set_network_used_nodes(self, network):
        """ Create a list of used Nodes from the network

        :param network: Network to analyze
        """
        self.used_nodes.clear()
        self.node_status.clear()
        for sink in network.sinklist.values():
            self.used_nodes.add(sink.id)
            if not self._node_is_analyzable(sink):
                self.node_status[sink.id] = 'blocked'
            else:
                self.node_status[sink.id] = 'unvisited'

            self._network_walker(sink)

    def _network_walker(self, node):
        """
        Recursive backwards search through the network to find all Nodes required for the Sinks.

        :param node: NodeRun to start search from
        """
        # loop over inputs of the node
        for input_ in node.inputs.values():
            # loop over the subinputs of every input
            for parentnode in input_.get_sourced_nodes():
                # if the node connected to the input is not the source node then add to execute list and walk further.
                #print('Adding parent {}'.format(parentnode.fullid))
                self.used_nodes.add(parentnode.id)
                if parentnode.blocking:
                    self.node_status[parentnode.id] = 'blocking'
                elif not self._node_is_analyzable(parentnode):
                    self.node_status[parentnode.id] = 'blocked'
                else:
                    self.node_status[parentnode.id] = 'unvisited'

                # Recurse down into the network
                self._network_walker(parentnode)

