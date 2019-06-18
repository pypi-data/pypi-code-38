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
Network module containing Network facilitators and analysers.
"""
import inspect
import itertools
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import traceback
import urllib.parse

from collections import OrderedDict, defaultdict

from graphviz import Digraph

from .. import exceptions
from .. import resources as fastr_resources
from ..abc.serializable import Serializable
from ..core import vfs_plugin
from ..core.resourcelimit import ResourceLimit
from ..core.version import Version
from ..datatypes import types
from ..execution.networkrun import NetworkRun
from ..helpers import iohelpers, config, log
from ..planning import node
from ..planning.link import Link
from ..planning.node import Node, ConstantNode, SourceNode, SinkNode, MacroNode
from ..planning.inputoutput import Output

__all__ = ['Network']


class Network(Serializable):
    """
    The NetworkRun contains the entire Run state for a Network execution. It
    has a working copy of the network, but also includes all temporary data
    required for the execution. These objects are meant to be single use.
    """

    __dataschemafile__ = 'Network.schema.json'

    NETWORK_DUMP_FILE_NAME = '__fastr_network__.json'
    SOURCE_DUMP_FILE_NAME = '__source_data__.pickle.gz'
    SINK_DUMP_FILE_NAME = '__sink_data__.json'

    def __init__(self, id_='unnamed_network', version=None, filename=None):
        """
        Create a new, empty Network

        :param str name: name of the Network
        :return: newly created Network
        :raises OSError: if the tmp mount in the config is not a writable directory
        """

        regex = r'^\w[\w\d_]*$'
        if re.match(regex, id_) is None:
            raise exceptions.FastrValueError('An id in Fastr should follow'
                                             ' the following pattern {}'
                                             ' (found {})'.format(regex, id_))

        if version is None:
            version = '0.0'

        #: The namespace this network lives in, this will be set by the NetworkManager on load
        self.namespace = None

        self._id = id_
        self.parent = None
        self.version = Version(version)
        self.description = ''
        self.toolnodelist = {}
        self.nodelist = {}
        self.sinklist = {}
        self.constantlist = {}
        self.sourcelist = {}
        self.macrolist = {}
        self.linklist = {}
        self.preferred_types = []
        self.stepids = {}
        self.link_number = 0
        self.node_number = 0

        # If the filename is not given, estimate it from the call stack
        if filename is None:
            frame = inspect.currentframe().f_back
            filename = frame.f_globals.get('__file__', None)
            if filename is not None:
                filename = os.path.abspath(filename)
            else:
                filename = 'python-shell'

        self.filename = filename

        # Check if temp dir exists, if not try to create it
        if not os.path.exists(config.mounts['tmp']):
            log.info("fast temporary directory does not exists, creating it...")
            try:
                os.mkdir(config.mounts['tmp'])
            except OSError:
                message = "Could not create fastr temporary directory ({})".format(config.mounts['tmp'])
                log.critical(message)
                raise exceptions.FastrOSError(message)

    def __repr__(self):
        return '<Network {} (v{})>'.format(self.id, self.version)

    def __eq__(self, other):
        """
        Compare two Networks and see if they are equal.

        :param other:
        :type other: :py:class:`Network <fastr.planning.network.Network>`
        :return: flag indicating that the Networks are the same
        :rtype: bool
        """
        if not isinstance(other, Network):
            return NotImplemented

        dict_self = dict(vars(self))
        del dict_self['nodelist']
        del dict_self['filename']

        dict_other = dict(vars(other))
        del dict_other['nodelist']
        del dict_other['filename']

        return dict_self == dict_other

    def __ne__(self, other):
        """
        Tests for non-equality, this is the negated version __eq__
        """
        return not (self.__eq__(other))

    # Retrieve a Node/Link/Input/Output in the network based on the fullid
    def __getitem__(self, item):
        """
        Get an item by its fullid. The fullid can point to a link, node, input, output or even subinput/suboutput.

        :param str,unicode item: fullid of the item to retrieve
        :return: the requested item
        """
        if not isinstance(item, str):
            raise exceptions.FastrTypeError('Key should be a fullid string, found a {}'.format(type(item).__name__))

        if isinstance(item, str):
            item = str(item)

        parsed = urllib.parse.urlparse(item)
        if parsed.scheme != 'fastr':
            raise exceptions.FastrValueError('Item should be an URL with the fastr:// scheme (Found {} in {})'.format(parsed.scheme, item))

        path = parsed.path.split('/')[1:]

        if len(path) < 2 or path[0] != 'networks' or path[1] != self.id:
            raise exceptions.FastrValueError('URL {} does not point to anything in this network, {}'.format(item, path))

        no_version = 0
        if path[2] != str(self.version):
            no_version = 1

        value = self

        for part in path[3 - no_version:]:
            if hasattr(value, '__getitem__'):
                try:
                    if isinstance(value, (list, tuple, Output)):
                        value = value[int(part)]
                    else:
                        value = value[part]
                except (KeyError, IndexError, TypeError, ValueError):
                    pass
                else:
                    continue

            if hasattr(value, part):
                value = getattr(value, part)
            else:
                raise exceptions.FastrLookupError('Could not find {} in {}'.format(part, value))

        return value

    def __getstate__(self):
        """
        Retrieve the state of the Network

        :return: the state of the object
        :rtype dict:
        """
        state = {
            'id': self.id,
            'version': str(self.version),
            'filename': self.filename,
            'description': self.description,
            'link_number': self.link_number,
            'node_number': self.node_number,
            'nodelist': [x.__getstate__() for x in self.nodelist.values()],
            'linklist': [x.__getstate__() for x in self.linklist.values()],
            'preferred_types': [x.id for x in self.preferred_types],
            'stepids': {k: [x.id for x in v] for k, v in self.stepids.items()},
            'namespace': self.namespace
        }

        return state

    def __setstate__(self, state):
        """
        Set the state of the Network by the given state. This completely
        overwrites the old state!

        :param dict state: The state to populate the object with
        :return: None
        """
        # Initialize empty to avoid errors further on
        self._id = state['id']
        self.parent = None
        self.version = Version(state['version'])
        self.nodelist = {}
        self.linklist = {}
        self.macrolist = {}
        self.sourcelist = {}
        self.constantlist = {}
        self.sinklist = {}
        self.toolnodelist = {}
        self.preferred_types = []
        self.stepids = {}
        self.description = state['description']

        # Make proper version
        state['version'] = Version(state['version'])

        # Set ID, we need this for messages later on
        self._id = state['id']
        del state['id']

        # Recreate nodes
        if 'nodelist' in state:
            for node_state in state['nodelist']:
                # Get the node class
                node_class = node_state.get('class', 'Node')
                node_class = getattr(node, node_class)

                node_obj = node_class.createobj(node_state, self)
                log.debug('Adding node: {}'.format(node_obj))
                self.add_node(node_obj)
            del state['nodelist']

        if 'nodegroups' in state:
            for group, nodes in state['nodegroups'].items():
                for node_name in nodes:
                    self.nodelist[node_name].nodegroup = group

        # Add preferred types
        state['preferred_types'] = [types[x] for x in state['preferred_types']]

        # Insert empty link_list
        statelinklist = state['linklist']
        state['linklist'] = {}

        # Update the objects dict
        self.__dict__.update(state)

        # Create the link list, make sure all Nodes are in place first
        for link in statelinklist:
            self.linklist[link['id']] = Link.createobj(link, self)

        # Make the stepids reference the Node instead of using ids
        if self.stepids is None:
            self.stepids = {}
        self.stepids = {k: [self.nodelist[x] for x in v] for k, v in list(self.stepids.items())}

        self.node_number = state['node_number']
        self.link_number = state['link_number']

    @property
    def id(self):
        """
        The id of the Network. This is a read only property.
        """
        return self._id

    @property
    def ns_id(self):
        """
        The namespace and id of the Tool
        """
        if self.namespace is None:
            return self.id
        else:
            return '{}/{}'.format(self.namespace, self.id)

    @property
    def fullid(self):
        """
        The fullid of the Network, within the network scope
        """
        return 'fastr:///networks/{}/{}'.format(self.id, self.version)

    @property
    def global_id(self):
        """
        The global id of the Network, this is different for networks used in
        macronodes, as they still have parents.
        """
        if self.parent is None:
            return self.fullid
        else:
            return '{}/network'.format(self.parent.global_id)

    @property
    def nodegroups(self):
        """
        Give an overview of the nodegroups in the network
        """
        nodegroups = defaultdict(list)
        for node in self.nodelist.values():
            if node.nodegroup is not None:
                nodegroups[node.nodegroup].append(node)
        return nodegroups

    def add_node(self, node):
        """
        Add a Node to the Network. Make sure the node is in the node list and
        the node parent is set to this Network

        :param node: node to add
        :type node: :py:class:`Node <fastr.planning.node.Node>`
        :raises FastrTypeError: if node is incorrectly typed
        """
        if node.id not in self.nodelist and isinstance(node, Node):
            self.nodelist[node.id] = node

            # Automatically sort Nodes in the right dict
            if isinstance(node, ConstantNode):
                self.constantlist[node.id] = node
            elif isinstance(node, SourceNode):
                self.sourcelist[node.id] = node
            elif isinstance(node, SinkNode):
                self.sinklist[node.id] = node
            elif isinstance(node, MacroNode):
                self.macrolist[node.id] = node
            elif isinstance(node, Node):
                self.toolnodelist[node.id] = node
            else:
                raise exceptions.FastrTypeError('Unknown Node type encountered! (type {})'.format(type(node).__name__))

            node.parent = self

    def add_link(self, link):
        """
        Add a Link to the Network. Make sure the link is in the link list and
        the link parent is set to this Network

        :param link: link to add
        :type link: :py:class:`Link <fastr.planning.link.Link>`
        :raises FastrTypeError: if link is incorrectly typed
        :raises FastrNetworkMismatchError: if the link already belongs to another Network
        """

        if not isinstance(link, Link):
            raise exceptions.FastrTypeError('Link argument is not of Link class! (type {})'.format(type(link).__name__))

        if link.id not in self.linklist:
            if link.parent is None:
                # Make sure parent and network have mutual understanding of the arrangement
                link.parent = self
            elif link.parent is not self:
                raise exceptions.FastrNetworkMismatchError('Cannot add a Link that already belongs to another Network!')

            self.linklist[link.id] = link

    def remove(self, value):
        """
        Remove an item from the Network.

        :param value: the item to remove
        :type value: :py:class:`Node <fastr.planning.node.Node>` or
                      :py:class:`Link <fastr.planning.link.Link>`
        """
        if isinstance(value, Link):
            self.linklist.pop(value.id)

        if isinstance(value, Node):
            self.nodelist.pop(value.id)

    def add_stepid(self, stepid, node):
        """
        Add a Node to a specific step id

        :param str stepid: the stepid that the node will be added to
        :param node: the node to add to the stepid
        :type node: :py:class:`Node <fastr.planning.node.Node>`
        """
        if stepid is not None:
            if stepid in self.stepids:
                self.stepids[stepid] += [node]
            else:
                self.stepids[stepid] = [node]

    def check_id(self, id_):
        """
        Check if an id for an object is valid and unused in the Network. The
        method will always returns True if it does not raise an exception.

        :param str id_: the id to check
        :return: True
        :raises FastrValueError: if the id is not correctly formatted
        :raises FastrValueError: if the id is already in use
        """

        regex = r'^\w[\w\d_]*$'
        if re.match(regex, id_) is None:
            raise exceptions.FastrValueError('An id in Fastr should follow'
                                             ' the following pattern {}'
                                             ' (found {})'.format(regex, id_))

        if id_ in self.nodelist or id_ in self.linklist:
            raise exceptions.FastrValueError('The id {} is already in use in {}!'.format(id_, self.id))

        return True

    def create_node(self, tool, tool_version, id_=None, stepid=None, resources=None, nodegroup=None):
        """
        Create a Node in this Network. The Node will be automatically added to
        the Network.

        :param tool: The Tool to base the Node on
        :type tool: :py:class:`Tool <fastr.core.tool.Tool>`
        :param str id_: The id of the node to be created
        :param str stepid: The stepid to add the created node to
        :param resources: The resources required to run this node
        :param str nodegroup: The group the node belongs to, this can be
                              important for FlowNodes and such, as they
                              will have matching dimension names.
        :return: the newly created node
        :rtype: :py:class:`Node <fastr.planning.node.Node>`
        """
        # Create a node in the network
        resources = resources or ResourceLimit()
        if isinstance(tool, str):
            tool = fastr_resources.tools[tool, tool_version]

        if isinstance(tool, tuple):
            raise TypeError('Tool argument must be either of class Tool or str, older tuple notations are deprecated!')

        try:
            NodeType = getattr(node, tool.node_class)
        except AttributeError:
            raise exceptions.FastrValueError('The indicated node class {} cannot be found for Tool {}/{}'.format(tool.node_class, tool.id, tool.version))

        node_obj = NodeType(tool, id_, parent=self,
                            resource_limits=resources, nodegroup=nodegroup)

        if node_obj.tool:
            if str(node_obj.tool.version) != tool_version:
                message = 'tool version incorrect, network needs: {}, installed: {}'.format(tool_version, node_obj.tool.version)
                log.critical(message)
                raise exceptions.FastrToolVersionError(message)

        self.add_node(node_obj)
        self.add_stepid(stepid, node_obj)

        return node_obj

    def create_macro(self, network, resources=None, id_=None):
        node = MacroNode(network, id_, parent=self, resource_limits=resources)

        self.add_node(node)
        return node

    def create_constant(self, datatype, data, id_=None, stepid=None, resources=None, nodegroup=None):
        """
        Create a ConstantNode in this Network. The Node will be automatically added to
        the Network.

        :param datatype: The DataType of the constant node
        :type datatype: :py:class:`BaseDataType <fastr.plugins.managers.datatypemanager.BaseDataType>`
        :param data: The data to hold in the constant node
        :type data: datatype or list of datatype
        :param str id_: The id of the constant node to be created
        :param str stepid: The stepid to add the created constant node to
        :param resources: The resources required to run this node
        :param str nodegroup: The group the node belongs to, this can be
                              important for FlowNodes and such, as they
                              will have matching dimension names.
        :return: the newly created constant node
        :rtype: :py:class:`ConstantNode <fastr.planning.node.ConstantNode>`
        """
        resources = resources or ResourceLimit()
        if not isinstance(data, (list, dict, OrderedDict)):
            data = [data]

        const_node = ConstantNode(datatype, data, id_, parent=self, resource_limits=resources, nodegroup=nodegroup)
        self.add_node(const_node)
        self.add_stepid(stepid, const_node)

        return const_node

    def create_link(self, source, target, id_=None, collapse=None, expand=None):
        """
        Create a link between two Nodes and add it to the current Network.

        :param source: the output that is the source of the link
        :type source: :py:class:`BaseOutput <fastr.planning.inputoutput.BaseOutput>`
        :param target: the input that is the target of the link
        :type target: :py:class:`BaseInput <fastr.planning.inputoutput.BaseInput>`
        :param str id_: the id of the link
        :return: the created link
        :type: :py:class:`Link <fastr.planning.link.Link>`
        """
        link = Link(source, target, id_=id_, parent=self, collapse=collapse, expand=expand)
        self.add_link(link)

        return link

    def create_source(self, datatype, id_=None, stepid=None, resources=None, nodegroup=None):
        """
        Create a SourceNode in this Network. The Node will be automatically added to
        the Network.

        :param datatype: The DataType of the source source_node
        :type datatype: :py:class:`BaseDataType <fastr.plugins.managers.datatypemanager.BaseDataType>`
        :param str id_: The id of the source source_node to be created
        :param str stepid: The stepid to add the created source source_node to
        :param resources: The resources required to run this node
        :param str nodegroup: The group the node belongs to, this can be
                              important for FlowNodes and such, as they
                              will have matching dimension names.
        :return: the newly created source source_node
        :rtype: :py:class:`SourceNode <fastr.core.source_node.SourceNode>`
        """

        # Set a source for the network.
        resources = resources or ResourceLimit()
        source_node = SourceNode(datatype=datatype, id_=id_, parent=self, resource_limits=resources, nodegroup=nodegroup)
        self.add_node(source_node)
        self.add_stepid(stepid, source_node)

        return source_node

    def create_sink(self, datatype, id_=None, stepid=None, resources=None, nodegroup=None):
        """
        Create a SinkNode in this Network. The Node will be automatically added to
        the Network.

        :param datatype: The DataType of the sink node
        :type datatype: :py:class:`BaseDataType <fastr.plugins.managers.datatypemanager.BaseDataType>`
        :param str id_: The id of the sink node to be created
        :param str stepid: The stepid to add the created sink node to
        :param resources: The resources required to run this node
        :return: the newly created sink node
        :rtype: :py:class:`SinkNode <fastr.planning.node.SinkNode>`
        """

        # Set a sink for the network
        resources = resources or ResourceLimit()
        node = SinkNode(datatype=datatype, id_=id_, parent=self, resource_limits=resources, nodegroup=nodegroup)
        self.add_node(node)
        self.add_stepid(stepid, node)

        return node

    def is_valid(self):
        def check_object(obj):
            status = obj.status
            if not status['valid']:
                if status['messages']:
                    for message in status['messages']:
                        log.error(message)
                else:
                    log.error("{} {} is not valid, no message available!".format(type(obj).__name__, obj.id))
            return status['valid']

        valid = (
            all(check_object(x) for x in self.nodelist.values()) and
            all(check_object(x) for x in self.linklist.values())
        )

        return valid

    def create_reference(self, source_data, output_directory):
        # Create output directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        output_url = vfs_plugin.path_to_url(output_directory, scheme='ref')
        log.info('Created temp result directory {}'.format(output_directory))
        network_temp_dir = os.path.join(output_directory, '__fastr_run_tmp__')

        # Save source data to reference dir
        iohelpers.save_gpickle(os.path.join(output_directory, self.SOURCE_DUMP_FILE_NAME), source_data)

        # Save a dump of the network
        with open(os.path.join(output_directory, self.NETWORK_DUMP_FILE_NAME), 'w') as fh_out:
            self.dump(fh_out, method='json', indent=2)

        # Set the output sink data to temporary directory
        sink_data = {}
        for sink in self.sinklist.values():
            sink_data[sink.id] = '{}/{}/{{sample_id}}/{{cardinality}}/result.json'.format(
                output_url,
                sink.id
            )
        log.info('Set sink data to: {}'.format(sink_data))

        # Execute the network
        self.execute(sourcedata=source_data, sinkdata=sink_data, tmpdir=network_temp_dir)

    @classmethod
    def test(cls, reference_data_dir, network=None, source_data=None, force_remove_temp=False, tmp_results_dir=None):
        """
        Execute the network with the source data specified and test the results
        against the refence data. This effectively tests the network execution.

        :param str reference_data_dir: The path or vfs url of reference data to compare with
        :param dict source_data: The source data to use
        :param force_remove_temp: Make sure the tmp results directory is cleaned at end of test
        :param tmp_results_dir: Path to results directory
        """
        if not isinstance(reference_data_dir, str):
            raise exceptions.FastrTypeError('reference_data_dir should be a string!')

        if reference_data_dir.startswith('vfs://'):
            reference_data_dir = vfs_plugin.url_to_path(reference_data_dir)

        if not os.path.isdir(reference_data_dir):
            raise exceptions.FastrTypeError('The reference_data_dir should be pointing to an existing directory!')

        if network is None:
            network = cls.loadf(os.path.join(reference_data_dir, cls.NETWORK_DUMP_FILE_NAME))

        if source_data is None:
            source_data = iohelpers.load_gpickle(os.path.join(reference_data_dir, cls.SOURCE_DUMP_FILE_NAME))

        temp_results_dir = None
        validation_result = []
        try:
            # Create temporary output directory
            if tmp_results_dir is None:
                temp_results_dir = os.path.normpath(tempfile.mkdtemp(
                    prefix='fastr_network_test_{}_'.format(network.id), dir=config.mounts['tmp']
                ))

            try:
                network.create_reference(source_data=source_data, output_directory=temp_results_dir)
            except Exception as exception:
                exc_info = traceback.format_exc()
                log.warning('Encountered exception during Network execution: {}\n{}'.format(exception, exc_info))
                validation_result.append(
                    'Encountered uncaught {} exception when running network:\n{}'.format(
                        type(exception).__name__,
                        exception,
                    )
                )

            # Check all sinks results
            for sink in network.sinklist.values():
                sink_output_dir = os.path.join(temp_results_dir, sink.id)

                if not os.path.isdir(sink_output_dir):
                    validation_result.append(
                        'Output directory for sink {} not found (expected to find {})'.format(
                            sink.id,
                            sink_output_dir
                        )
                    )
                    continue

                sink_reference_dir = os.path.join(reference_data_dir, sink.id)

                output_samples = sorted(os.listdir(sink_output_dir))
                reference_samples = sorted(os.listdir(sink_reference_dir))

                if output_samples != reference_samples:
                    validation_result.append('\n'.join((
                        'Different samples found in sink "{}"'.format(sink.id),
                        'Output samples: {}'.format(output_samples),
                        'Reference samples: {}'.format(reference_samples),
                    )))
                    continue

                for sample in output_samples:
                    sample_output_dir = os.path.join(sink_output_dir, sample)
                    sample_reference_dir = os.path.join(sink_reference_dir, sample)

                    output_values = sorted(os.listdir(sample_output_dir))
                    reference_values = sorted(os.listdir(sample_reference_dir))

                    if output_values != reference_values:
                        validation_result.append('\n'.join((
                            'Difference number of cardinality entries for {}/{}'.format(sink.id, sample),
                            'Output cardinality entries: {}'.format(output_values),
                            'Reference cardinality entries: {}'.format(reference_values),
                        )))
                        continue

                    for value in output_values:
                        with open(os.path.join(sample_output_dir, value, 'result.json')) as fh_in:
                            output_data = json.load(fh_in)
                        with open(os.path.join(sample_reference_dir, value, 'result.json')) as fh_in:
                            reference_data = json.load(fh_in)

                        output_item = types[output_data['datatype']](output_data['value'])
                        reference_item = types[reference_data['datatype']](reference_data['value'])

                        if output_item != reference_item:
                            validation_result.append('\n'.join((
                                'Value for {}/{}/{} was not equal! (found "{}", expected "{}")'.format(
                                    sink.id,
                                    sample,
                                    value,
                                    output_item,
                                    reference_item,
                                ),
                                'Output: [{}] {!r}'.format(type(output_item.value).__name__,
                                                           output_item.value),
                                'Reference: [{}] {!r}'.format(type(reference_item.value).__name__,
                                                              reference_item.value),
                            )))

            if len(validation_result) == 0:
                log.info('Run and reference were equal! Test passed!')
            else:
                log.info('Found difference with reference data! Test failed!')
                for line in validation_result:
                    log.info(line)
            return validation_result
        finally:
            # Clean up
            if temp_results_dir is not None and os.path.isdir(temp_results_dir):
                if validation_result == 0 or force_remove_temp:
                    log.info('Removing temp result directory {}'.format(temp_results_dir))
                    shutil.rmtree(temp_results_dir, ignore_errors=True)
                else:
                    log.info(
                        'Keeping temp directory {} on disk for inspection, do not forget to remove it yourself!'.format(
                            temp_results_dir
                        )
                    )

    def execute(self, sourcedata, sinkdata, blocking=True, **kwargs):
        if not self.is_valid():
            log.critical('Cannot run Network {} ({}), it is not valid!'.format(self.id, self.version))
            return

        # Setup the Run and prepare arguments in dict
        run = NetworkRun(self)
        kwargs['sourcedata'] = sourcedata
        kwargs['sinkdata'] = sinkdata

        if blocking:
            # Run execution in blocking mode
            run.execute(**kwargs)
        else:
            # Create and start the execution in a background thread
            run.thread = threading.Thread(group=None,
                                          target=run.execute,
                                          name='run_thread_{}'.format(run.id),
                                          kwargs=kwargs)
            run.thread.start()

        return run

    @staticmethod
    def _dim_name_generator(max_level=3):
        base_name = 'NMOPQRSTUVWXYZABCDEFGHIJKL'

        for level in range(1, max_level + 1):
            for name in itertools.product(base_name, repeat=level):
                yield ''.join(name)

    def draw(self, name=None, draw_dimensions=True, hide_unconnected=True,
             context=None, graph=None, expand_macro=False, font_size=14):
        # If not working on an existing graph, create one
        if graph is None:
            graph = Digraph(
                'structs',
                filename='{name}.gv'.format(name=name),
                graph_attr={'rankdir': 'LR', 'splines': 'true'},
                node_attr={'shape': 'record', 'fontsize': str(font_size), 'margin': '0.55,0.055'}
            )

        # If not given, create the drawing context to pass along
        if context is None:
            dimension_name_generator = self._dim_name_generator()
            context = {
                'network_stack': [self],
                'dimensions': defaultdict(lambda: next(dimension_name_generator)),
                'draw_dimensions': draw_dimensions,
                'hide_unconnected': hide_unconnected,
                'expand_macro': expand_macro,
                'colors': {
                    'source_node': 'darkolivegreen1',
                    'node': 'gray90',
                    'sink_node': 'lightskyblue1',
                    'constant_node': 'plum1',
                    'macro_node': 'goldenrod1',
                    'macro_link': 'lightgoldenrod1'
                }
            }

        # Add all nodes
        nodes_in_cluster = set()

        for step_id, node_list in self.stepids.items():
            full_step_id = '_'.join(x.id for x in context['network_stack']) + '__' + step_id
            with graph.subgraph(name='cluster_' + full_step_id) as sub_graph:
                sub_graph.attr(label=step_id)
                sub_graph.attr(color='gray60')

                for node in node_list:
                    nodes_in_cluster.add(node.id)
                    node.draw(context=context, graph=sub_graph)

        for node in self.nodelist.values():
            if node.id not in nodes_in_cluster:
                node.draw(context=context, graph=graph)

        # All the links
        for link in self.linklist.values():
            link.draw(context=context, graph=graph)

        return graph

    def draw_network(self, name="network_layout", img_format='svg', draw_dimension=True, hide_unconnected=True, expand_macro=False, font_size=14):
        """
        Output a dot file and try to convert it to an image file.

        :param str img_format: extension of the image format to convert to
        :return: path of the image created or None if failed
        :rtype: str or None
        """
        image_file_path = '{}.{}'.format(name, img_format)
        if os.path.exists(image_file_path):
            os.remove(image_file_path)

        graph = self.draw(draw_dimensions=draw_dimension, hide_unconnected=hide_unconnected,
                          expand_macro=expand_macro, font_size=font_size)

        with open(image_file_path, 'wb') as fh_out:
            fh_out.write(graph.pipe(format=img_format))

        return image_file_path
