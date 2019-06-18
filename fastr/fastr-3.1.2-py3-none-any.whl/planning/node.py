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
A module to maintain a network node.

Exported classes:

Node -- A class encapsulating a tool.
ConstantNode -- A node encapsulating an Output to set scalar values.
SourceNode -- A class providing a handle to a file.
"""
import itertools
import os
import pprint
import weakref
from abc import ABCMeta
from collections import OrderedDict, defaultdict

import sympy

from .. import api
from .. import exceptions
from ..abc.serializable import Serializable
from ..abc.updateable import Updateable
from ..core.dimension import HasDimensions, Dimension
from ..core.resourcelimit import ResourceLimit
from ..core.interface import InputSpec, OutputSpec
from ..core.samples import SampleId
from ..core.tool import Tool
from ..datatypes import DataType, types
from ..helpers import log
from ..planning.inputoutput import BaseInput, Input, MacroInput, Output, AdvancedFlowOutput, SourceOutput, MacroOutput
from ..planning.inputgroup import InputGroup
from ..planning.inputgroupcombiner import DefaultInputGroupCombiner, MergingInputGroupCombiner
from .. import resources


class InputDict(OrderedDict):
    """
    The container containing the Inputs of Node. Implements helper functions
    for the easy linking syntax.
    """

    # We know this class is not really for public interaction, however it has
    # an important function linking of nodes.
    # pylint: disable=too-few-public-methods

    def __setitem__(self, key, value):
        """
        Set an item in the input dictionary. The behaviour depends on the
        type of the value. For a
        :py:class:`BaseInput <fastr.planning.inputoutput.BaseInput>`,
        the input will simply be added to the list of inputs. For a
        :py:class:`BaseOutput <fastr.planning.inputoutput.BaseOutput>`,
        a link between the output and input will be created.

        :param str key: id of the input to assign/link
        :param value: either the input to add or the output to link
        :type value: :py:class:`BaseInput <fastr.planning.inputoutput.BaseInput>`
                      or
                      :py:class:`BaseOutput <fastr.planning.inputoutput.BaseOutput>`
        :param dict_setitem: the setitem function to use for the underlying
                              OrderedDict insert
        """
        if isinstance(value, Input):
            super(InputDict, self).__setitem__(key, value)
        else:
            self[key].create_link_from(value)


class OutputDict(OrderedDict):
    """
    The container containing the Inputs of Node. Only checks if the inserted
    values are actually outputs.
    """

    # We know this class is not really for public interaction, however it we
    # have it to do type checking and consistency with the InputDict
    # pylint: disable=too-few-public-methods

    def __setitem__(self, key, value):
        """
        Set an output.

        :param str key: the of the item to set
        :param value: the output to set
        :type value: :py:class:`BaseOutput <fastr.planning.inputoutput.BaseOutput>`
        :param dict_setitem: the setitem function to use for the underlying
                              OrderedDict insert
        """
        if isinstance(value, Output):
            super(OutputDict, self).__setitem__(key, value)
        else:
            message = 'Cannot add object of type {} to OutputDict'.format(type(value).__name__)
            log.warning(message)


class BaseNode(HasDimensions, Updateable, Serializable, metaclass=ABCMeta):
    NODE_TYPES = {}

    def __init_subclass__(cls, **kwargs):
        """
        Register nodes in class for easly location
        """
        cls.NODE_TYPES[cls.__name__] = cls


class Node(BaseNode):
    """
    The class encapsulating a node in the network. The node is responsible
    for setting and checking inputs and outputs based on the description
    provided by a tool instance.
    """
    __dataschemafile__ = 'Node.schema.json'

    _InputType = Input
    _OutputType = Output

    def __init__(self, tool, id_=None, node_class=None, parent=None, resource_limits=None, nodegroup=None):
        """
        Instantiate a node.

        :param tool: The tool to base the node on
        :type tool: :py:class:`Tool <fastr.core.tool.Tool>`
        :param str id_: the id of the node
        :param str node_class: The class of the NodeRun to create (e.g. SourceNodeRun, NodeRun)
        :param parent: the parent network of the node
        :param int cores: number of cores required for executing this Node
        :param str memory: amount of memory required in the form \\d+[mMgG]
                           where M is for megabyte and G for gigabyte
        :param str walltime: amount of time required in second or in the form
                             HOURS:MINUTES:SECOND
        :type parent: :py:class:`Network <fastr.planning.network.Network>`
        :return: the newly created Node
        """
        super(Node, self).__init__()

        if isinstance(tool, Tool):
            self._tool = tool
        elif isinstance(tool, (str, tuple)):
            if tool in resources.tools:
                self._tool = resources.tools[tool]
            else:
                message = ('Specified tool ({}) is not in the tools: {}. '
                           'Check the config (fastr/resources/fastr.config)').format(tool,
                                                                                     list(resources.tools.todict().keys()))
                log.critical(message)
                raise exceptions.FastrToolUnknownError(message)
        elif tool is None:
            self._tool = None
        else:
            message = 'tool should either be a string or a Tool.'
            log.critical(message)
            raise exceptions.FastrTypeError(message)

        # Don't set parent here, as not info needed for registration is there yet
        self._parent = None
        if parent is None:
            message = 'parent argument is None, need a parent Network to function!'
            raise exceptions.FastrValueError(message)

        node_number = parent.node_number
        parent.node_number += 1

        if id_ is None:
            # Node ID is a simple $name_$counter format, making sure nodes can
            # not be named the same

            #: The Node id s a unique string identifying the Node
            id_ = 'node_{}_{}'.format(self.name, node_number)

        parent.check_id(id_)
        self._id = id_
        self._nodegroup = nodegroup

        #: The parent is the Network this Node is part of
        self.parent = parent

        #: A list of inputs of this Node
        self.inputs = InputDict()

        #: A list of outputs of this Node
        self.outputs = OutputDict()

        # Create all inputs and outputs, if the class is set in the Tool file,
        # respect that, otherwise use the class default.
        if self._tool is not None:
            for name, input_ in self._tool.inputs.items():
                self.inputs[name] = self._InputType(self, input_)
            for name, output in self._tool.outputs.items():
                self.outputs[name] = self._OutputType(self, output)

        # Set the job requirements
        self.resources = resource_limits

        # Cache dimensions for speed
        self._dimensions = None

        # Set the flow control
        self._input_groups = OrderedDict()
        self._merge_dimensions = None
        self.input_group_combiner = None
        self.merge_dimensions = 'none'

        # Update Inputs and self (which calls Outputs)
        self.update()

    def __repr__(self):
        """
        Get a string representation for the Node

        :return: the string representation
        :rtype: str
        """
        if self._tool is not None:
            toolinfo = '(tool: {tool.id} v{tool.version!s})'.format(tool=self._tool)
        else:
            toolinfo = ''
        return_list = ['{} {} {}'.format(type(self).__name__, self.id, toolinfo)]

        # The "+ [8]" guarantees a minimum of 8 width and avoids empty lists
        width_input_keys = max([len(x) for x in self.inputs.keys()] + [8])
        width_input_types = max([len(x.datatype.id) for x in self.inputs.values()] + [8]) + 2
        width_output_keys = max([len(x) for x in self.outputs.keys()] + [8])
        width_output_types = max([len(x.datatype.id) for x in self.outputs.values()] + [8]) + 2

        return_list.append('{:^{}}  | {:^{}}'.format('Inputs', width_input_types + width_input_keys + 1,
                                                     'Outputs', width_output_types + width_output_keys + 1))
        return_list.append('-' * (width_input_keys + width_input_types + width_output_keys + width_output_types + 7))
        for (input_key, input_, output_key, output) in itertools.zip_longest(self.inputs.keys(), 
                                                                             self.inputs.values(),
                                                                             self.outputs.keys(),
                                                                             self.outputs.values()):
            if input_ is None:
                input_id = ''
                input_type = ''
            else:
                input_id = input_key
                input_type = '({})'.format(input_.datatype.id)

            if output is None:
                output_id = ''
                output_type = ''
            else:
                output_id = output_key
                output_type = '({})'.format(output.datatype.id)

            return_list.append('{:{}} {:{}}  |  {:{}} {:{}}'.format(input_id, width_input_keys,
                                                                    input_type, width_input_types,
                                                                    output_id, width_output_keys,
                                                                    output_type, width_output_types))

        return '\n'.join(return_list)

    def __str__(self):
        """
        Get a string version for the Node

        :return: the string version
        :rtype: str
        """
        return "<{}: {}>".format(type(self).__name__, self.id)

    def __eq__(self, other):
        """
        Check two Node instances for equality.

        :param other: the other instances to compare to
        :type other: fastr.planning.node.Node
        :returns: True if equal, False otherwise
        """
        if not isinstance(other, Node):
            return NotImplemented

        if self._id != other.id:
            return False

        if self.resources != other.resources:
            return False

        if self.nodegroup != other.nodegroup:
            return False

        if self._merge_dimensions != other._merge_dimensions:
            return False

        if self.tool != other.tool:
            return False

        if self.inputs != other.inputs:
            return False

        if self.outputs != other.outputs:
            return False

        return True

    def __ne__(self, other):
        """
        Check two Node instances for inequality. This is the inverse of __eq__

        :param other: the other instances to compare to
        :type other: fastr.planning.node.Node
        :returns: True if unequal, False otherwise
        """
        if not isinstance(self, type(other)):
            return NotImplemented

        return not self == other

    def __getstate__(self):
        """
        Retrieve the state of the Node

        :return: the state of the object
        :rtype dict:
        """
        state = super(Node, self).__getstate__()

        # Make id prettier in the result
        state['id'] = self.id
        state['nodegroup'] = self.nodegroup

        # Add the class of the Node in question
        state['class'] = type(self).__name__

        # Get all input and output
        state['inputs'] = [x.__getstate__() for x in self.inputs.values()]
        state['outputs'] = [x.__getstate__() for x in self.outputs.values()]

        if self._tool is not None:
            state['tool'] = [self._tool.ns_id, str(self._tool.version)]

        # Add resource requirements
        state['resources'] = self.resources.__getstate__() if self.resources else self.resources
        state['merge_dimensions'] = self._merge_dimensions

        return state

    def __setstate__(self, state):
        """
        Set the state of the Node by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        # Make sure the Node classes are aligned (and warn if not so)
        if 'class' in state and state['class'] != type(self).__name__:
            log.warning('Attempting to set the state of a {} to {}'.format(
                state['class'],
                type(self).__name__
            ))

        if not hasattr(self, '_input_groups'):
            self._input_groups = OrderedDict()

        if 'id' in state:
            self._id = state['id']

        if 'nodegroup' in state:
            self.nodegroup = state['nodegroup']
        else:
            self.nodegroup = None

        if 'parent' in state:
            parent = state['parent']
            del state['parent']
        else:
            parent = None

        if 'tool' in state and state['tool'] is not None:
            self._tool = resources.tools[tuple(state['tool'])]
        else:
            self._tool = None

        # Create Input/Output objects
        inputlist = []
        for input_ in state['inputs']:
            if 'node' in input_:
                # Check if the expected Node id matches our current id
                if input_['node'] != state['id']:
                    raise exceptions.FastrParentMismatchError('This Input has different parent node!')
                del input_['node']

            # It can happen that this has been done by a subclass, check first
            if not isinstance(input_, BaseInput):
                description = self.tool.inputs[input_['id']]
                inputobj = self._InputType(self, description)
                inputobj._node = self
                inputobj.__setstate__(input_)
            else:
                inputobj = input_
            inputlist.append((inputobj.id, inputobj))

        outputlist = []
        for output in state['outputs']:
            if '_node' in output:
                # Check if the expected Node id matches our current id
                if output['_node'] != state['_id']:
                    raise exceptions.FastrParentMismatchError('This Input has different parent node!')
                del output['_node']

            # It can happen that this has been done by a subclass, check first
            if not isinstance(output, Output):
                description = self.tool.outputs[output['id']]
                outputobj = self._OutputType(self, description)
                outputobj.__setstate__(output)
            else:
                outputobj = output
            outputlist.append((outputobj.id, outputobj))

        self.inputs = InputDict(inputlist)
        self.outputs = OutputDict(outputlist)

        super(Node, self).__setstate__(state)

        if parent is not None:
            self.parent = parent
        else:
            message = 'parent argument is None, need a parent Network to function!'
            raise exceptions.FastrValueError(message)

        self._dimensions = None
        self.resources = ResourceLimit()
        if state.get('resources'):
            self.resources.__setstate__(state['resources'])

        self.merge_dimensions = state['merge_dimensions']

        self.update()

    @property
    def merge_dimensions(self):
        return self._merge_dimensions

    @merge_dimensions.setter
    def merge_dimensions(self, value):
        if isinstance(value, str):
            options = ['all', 'none']
            if value not in options:
                raise exceptions.FastrValueError('Invalid option {} given (valid options: {})'.format(value, options))
            self._merge_dimensions = value
            if value == 'none':
                self.input_group_combiner = DefaultInputGroupCombiner(self)
            elif value == 'all':
                self.input_group_combiner = MergingInputGroupCombiner(self, value)
        else:
            self._merge_dimensions = value
            self.input_group_combiner = MergingInputGroupCombiner(self, tuple(value))

    @classmethod
    def createobj(cls, state, network=None):
        if 'parent' not in state:
            if network is not None:
                log.debug('Setting network to: {}'.format(network))
                state['parent'] = network
            else:
                log.debug('No network given for de-serialization')
        else:
            log.debug('Parent is already defined as: {}'.format(network))

        state = dict(state)

        return super(Node, cls).createobj(state, network)

    @property
    def blocking(self):
        """
        Indicate that the results of this Node cannot be determined without first executing the Node, causing a
        blockage in the creation of jobs. A blocking Nodes causes the Chunk borders.
        """
        for output in self.outputs.values():
            if output.blocking:
                log.debug('Blocking because Output {} has cardinality {}'.format(output.fullid,
                                                                                       output.cardinality()))
                return True
        return False

    @property
    def dimnames(self):
        """
        Names of the dimensions in the Node output. These will be reflected
        in the SampleIdList of this Node.
        """
        if hasattr(self, '_dimnames') and self._dimnames is not None:
            return self._dimnames
        else:
            return super(Node, self).dimnames

    @dimnames.setter
    def dimnames(self, value):
        if isinstance(value, str):
            value = value,

        if not isinstance(value, tuple) or not all(isinstance(x, str) for x in value):
            raise exceptions.FastrTypeError('Dimnames has to be a tuple of str!')

        log.warning('You are overriding the dimnames of a Node, beware this is possible but not encouraged and can lead to strange results!')
        self._dimnames = value

    @dimnames.deleter
    def dimnames(self):
        del self._dimnames

    @property
    def fullid(self):
        """
        The full defining ID for the Node inside the network
        """
        return '{}/nodelist/{}'.format(self.parent.fullid, self.id)

    @property
    def global_id(self):
        """
        The global defining ID for the Node from the main network (goes out
        of macro nodes to root network)
        """
        return '{}/nodelist/{}'.format(self.parent.global_id, self.id)

    @property
    def input_groups(self):
        """
        A list of input groups for this Node. An input group is InputGroup
         object filled according to the Node

        """
        return self._input_groups

    @property
    def dimensions(self):
        if self._dimensions is None:
            self._dimensions = self.input_group_combiner.dimensions
        return self._dimensions

    @property
    def outputsize(self):
        """
        The size of output of this SourceNode
        """
        return self.size

    @property
    def nodegroup(self):
        return self._nodegroup

    @nodegroup.setter
    def nodegroup(self, value):
        self._nodegroup = value

    @property
    def id(self):
        """
        The id of the Node
        """
        return self._id

    @property
    def listeners(self):
        """
        All the listeners requesting output of this node, this means the
        listeners of all Outputs and SubOutputs
        """
        listeners = []
        for output in self.outputs.values():
            for listener in output.listeners:
                if listener not in listeners:
                    listeners.append(listener)
        return listeners

    @property
    def name(self):
        """
        Name of the Tool the Node was based on. In case a Toolless Node was
        used the class name is given.
        """
        if hasattr(self, '_tool') and isinstance(self._tool, Tool):
            return self._tool.id
        else:
            return self.__class__.__name__

    @property
    def parent(self):
        """
        The parent network of this node.
        """
        return self._parent()

    @parent.setter
    def parent(self, value):
        """
        The parent network of this node. (setter)
        """
        if hasattr(self, '_parent') and self._parent is not None:
            if self._parent() is value:
                return  # Setting to same value doesn't do anything
            raise exceptions.FastrAttributeError('Cannot reset attribute once set')

        self._parent = weakref.ref(value)
        self._parent().add_node(self)

    @property
    def status(self):
        return self._status

    @property
    def tool(self):
        return self._tool

    def draw_id(self, context):
        return '{}__{}'.format('_'.join(x.id for x in context['network_stack']), self.id)

    def draw_link_target(self, context, port_name, input=True):
        if input:
            port_spec = 'i_{}'.format(port_name)
        else:
            port_spec = 'o_{}'.format(port_name)

        return '{}:{}'.format(self.draw_id(context), port_spec)

    def draw(self, context, graph, color=None):
        if color is None:
            color = context['colors']['node']

        inputs = []
        dimensions = ''
        for input_ in self.inputs.values():
            # Skip rendering unconnected inputs
            if context['hide_unconnected']:
                if len(input_.get_sourced_nodes()) == 0:
                    continue

            # Draw dimensions in the graph
            if context['draw_dimensions']:
                dimensions = '[' + 'x'.join(context['dimensions'][x] for x in input_.dimnames) + ']'

            inputs.append('<i_{id}>{dim} {id}'.format(id=input_.id, dim=dimensions))
        inputs = '|'.join(inputs)

        outputs = []
        for output in self.outputs.values():
            # Skip rendering unconnected outputs
            if context['hide_unconnected']:
                if len(output.listeners) == 0:
                    continue
            
            # Draw dimensions in the graph
            if context['draw_dimensions']:
                dimensions = '[' + 'x'.join(context['dimensions'][x] for x in output.dimnames) + ']'

            outputs.append('<o_{id}>{id} {dim}'.format(id=output.id, dim=dimensions))
        outputs = '|'.join(outputs)

        graph.node(self.draw_id(context=context),
                   label="<id>{id}|{{{{{inputs}}}|{{{outputs}}}}}".format(id=self.id, inputs=inputs, outputs=outputs),
                   fillcolor=color,
                   style="filled")

    def get_sourced_nodes(self):
        """
        A list of all Nodes connected as sources to this Node

        :return: list of all nodes that are connected to an input of this node
        """
        sourced_node = []
        for input_ in self.inputs.values():
            for node in input_.get_sourced_nodes():
                if node not in sourced_node:
                    sourced_node.append(node)
        return sourced_node

    def find_source_index(self, target_index, target, source):
        # If there are multiple input groups, select only part of index from
        # the inputgroup which source belongs to
        if len(self.input_groups) > 1:
            input_groups = self.input_groups
            mask = [True if ig.id == source.input_group else False for ig in input_groups.values() for _ in ig.size]
            target_index = tuple(k for k, m in zip(target_index, mask) if m)

        # Delegate to InputGroup to check mixing within InputGroup
        return self.input_groups[source.input_group].find_source_index(target_size=target.size,
                                                                       target_dimnames=target.dimnames,
                                                                       source_size=source.size,
                                                                       source_dimnames=source.dimnames,
                                                                       target_index=target_index)

    def _update(self, key, forward=True, backward=False):
        """
        Update the Node information and validity of the Node and propagate
         the update downstream. Updates inputs, input groups, outputsize and outputs.

        A Node is valid if:

        * All Inputs are valid (see :py:meth:`Input.update <fastr.planning.inputoutput.Input.update>`)
        * All InputGroups are non-zero sized

        """
        # Make sure the Inputs and input groups are up to date
        # log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.id))

        if backward:
            for sourced_node in self.get_sourced_nodes():
                sourced_node.update(key, False, backward)

        for input_ in self.inputs.values():
            input_.update(key, forward, backward)

        # Reset dimensions cache
        self._dimensions = None

        self.update_input_groups()
        self.input_group_combiner.update()

        # Update own status
        valid = True
        messages = []

        if len(self.get_sourced_nodes()) == 0:
            valid = False
            messages.append('[{}] No nodes are linked to any input of this Node'.format(self.id))

        if len(self.listeners) == 0:
            valid = False
            messages.append('[{}] No nodes are linked to any output of this Node'.format(self.id))

        for id_, input_ in self.inputs.items():
            if not input_.valid:
                valid = False
                for message in input_.messages:
                    messages.append('[{}] Input {} is not valid: {}'.format(self.id, input_.id, message))

        for input_group in self.input_groups.values():
            if input_group.empty:
                valid = False
                messages.append('[{}] InputGroup {} is empty'.format(self.id, input_group.id))

        for id_, output in self.outputs.items():
            if output.resulting_datatype is not None and not issubclass(output.resulting_datatype, DataType):
                valid = False
                messages.append('[{}] Output {} cannot determine the Output DataType (got {}), please specify a '
                                'valid DataType or add casts to the Links'.format(self.id,
                                                                                  id_,
                                                                                  output.resulting_datatype))

        self._status['valid'] = valid
        self._status['messages'] = messages

        # Update all outputs
        for output in self.outputs.values():
            output.update(key, forward, backward)

        # Update all downstream listeners
        if forward:
            for listener in self.listeners:
                listener.update(key, forward, False)

    def update_input_groups(self):
        """
        Update all input groups in this node
        """
        input_groups = OrderedDict()

        for input_ in self.inputs.values():
            if input_.input_group not in input_groups:
                input_groups[input_.input_group] = InputGroup(self, input_.input_group)
            input_groups[input_.input_group][input_.id] = input_

        self._input_groups = input_groups


class MacroNode(Node):
    """
    MacroNode encapsulates an entire network in a single node.
    """
    _OutputType = MacroOutput
    _InputType = MacroInput

    def __init__(self, value, id_=None, parent=None, resource_limits=None, nodegroup=None):
        """
        :param network: network to create macronode for
        :type network: fastr.planning.network.Network
        """
        # If MacroNode is loaded as a tool retrieve macro definition file(.py .xml .pickle .json) location
        if isinstance(value, Tool):
            if value.node_class != 'MacroNode':
                raise exceptions.FastrValueError('Tool {} is node_class is not MacroNode but {}'.format(
                    value.ns_id, value.node_class
                ))

            if not isinstance(value.target, resources.targets['MacroTarget']):
                raise exceptions.FastrTypeError('Can only use a Tool that has a Macro target to create a MacroNode')

            self._network = value.target.network
        elif isinstance(value, str) and os.path.isfile(value):
            # xml pickle, json, etc
            self._network = api.Network.load(value).parent
        # Else it is a Network class that we can use, make a copy
        else:
            try:
                # Make sure to make a copy of the network
                self._network = api.create_network_copy(value).parent
            except (ValueError, AttributeError):
                message = 'Macro node should either be a Network, a MacroTool or a FileName'
                log.critical(message)
                raise

        # This must be set before the update is called from the superclass __init__
        self._source_dimensions = {}
        self._source_sizes = {}
        self._output_info = {sink_id: None for sink_id in self._network.sinklist.keys()}

        # Now we can safely call the super
        super(MacroNode, self).__init__(None, id_, parent=parent, resource_limits=resource_limits, nodegroup=nodegroup)

        # Cache this to avoid costly recalculations
        self._create_inputs()
        self._create_outputs()

        try:
            if not self._network.is_valid():
                raise exceptions.FastrValueError('[{}] internal Network is not valid'.format(self.id))
        except exceptions.FastrError as exception:
            message = 'Macro Node: {} is not a valid network ({})'.format(id_, exception)
            log.critical(message)
            raise exceptions.FastrValueError(message)

    @property
    def network(self):
        return self._network

    def _create_inputs(self):
        for _, source in sorted(self._network.sourcelist.items()):
            spec = InputSpec(source.id, '1-*', source.datatype, required=True)
            self.inputs[spec.id] = self._InputType(self, spec)

    def _create_outputs(self):
        for _, sink in sorted(self._network.sinklist.items()):
            spec = OutputSpec(sink.id, "unknown", sink.datatype)
            self.outputs[spec.id] = self._OutputType(self, spec)

    def __eq__(self, other):
        """Compare two MacroNode instances with each other. This function ignores
        the parent and update status, but tests rest of the dict for equality.
        equality

        :param other: the other instances to compare to
        :type other: MacroNode
        :returns: True if equal, False otherwise
        """
        if not isinstance(other, MacroNode):
            return NotImplemented

        if self.id != other.id:
            return False

        if self.nodegroup != other.nodegroup:
            return False

        if self.inputs != other.inputs:
            return False

        if self.outputs != other.outputs:
            return False

        if self.network != other.network:
            return False

        return True

    def __getstate__(self):
        """
        Retrieve the state of the MacroNode

        :return: the state of the object
        :rtype dict:
        """
        state = super(MacroNode, self).__getstate__()
        state['inputs'] = []
        state['outputs'] = []
        state['network'] = self.network.__getstate__()
        return state

    def __setstate__(self, state):
        self._network = api.create_network_copy(state.pop('network')).parent
        super(MacroNode, self).__setstate__(state)
        self._create_inputs()
        self._create_outputs()
        self._output_info = {sink_id: None for sink_id in self._network.sinklist.keys()}

    def _update_input_mappings(self):
        """
        Update the mapping of the dimensions of source node to those
        of inputs. This is needed because the internal network has
        other dimensions than the macro node externally.
        """
        self._source_dimensions = {}
        self._source_sizes = {}
        for input_ in self.inputs.values():
            source_node = self.network.sourcelist[input_.id]

            if source_node.dimnames[0] not in self._source_dimensions:
                self._source_dimensions[source_node.dimnames[0]] = input_.dimnames
            if source_node.dimnames[0] not in self._source_sizes:
                self._source_sizes[source_node.dimnames[0]] = input_.size

    def get_output_info(self, output):
        """
        This functions maps the output dimensions based on the input dimensions
        of the macro. This is cached for speed as this can become rather costly
        otherwise

        :param output: output to get info for
        :return: tuple of Dimensions
        """
        if self._output_info[output.id] is None:

            # Translate back result index and id
            sink = self.network.sinklist[output.id]
            new_dimname = []
            new_size = []

            for dimname, size in zip(sink.dimnames, sink.outputsize):
                # If they were translated, replace them back
                if dimname in self._source_dimensions:
                    dimension_part = self._source_dimensions[dimname]
                    size_part = self._source_sizes[dimname]

                    new_dimname.extend(dimension_part)
                    new_size.extend(size_part)
                else:
                    new_dimname.append(dimname)
                    new_size.append(size)

            self._output_info[output.id] = tuple(Dimension(name, size) for name, size in zip(new_dimname, new_size))

        return self._output_info[output.id]

    def draw_link_target(self, context, port_name, input=True):
        if input:
            port_spec = 'i_{}'.format(port_name)
            if context['expand_macro'] is True or context['expand_macro'] >= len(context['network_stack']):
                return '{}_inputs:{}'.format(self.draw_id(context), port_spec)
        else:
            port_spec = 'o_{}'.format(port_name)
            if context['expand_macro'] is True or context['expand_macro'] >= len(context['network_stack']):
                return '{}_outputs:{}'.format(self.draw_id(context), port_spec)

        return '{}:{}'.format(self.draw_id(context), port_spec)

    def draw(self, context, graph, color=None):
        if color is None:
            color = context['colors']['macro_node']

        if context['expand_macro'] is True or context['expand_macro'] >= len(context['network_stack']):
            node_id = self.draw_id(context)

            context['network_stack'].append(self)
            old_dimensions = context['dimensions']
            context['dimensions'] = defaultdict(old_dimensions.default_factory)

            # Draw network
            with graph.subgraph(name='cluster_' + '_'.join(x.id for x in context['network_stack'])) as sub_graph:
                sub_graph.attr(label='{} ({} v{})'.format(self.id, self.network.id, self.network.version)),

                dimensions_in = ''
                dimensions_out = ''

                # Create connection node for inputs
                inputs = []
                outputs = []

                for input_ in self.inputs.values():
                    source_node = self.network.nodelist[input_.id]
                    if context['draw_dimensions']:
                        dimensions_in = '[' + 'x'.join(old_dimensions[x] for x in input_.dimnames) + ']'
                        dimensions_out = '[' + 'x'.join(context['dimensions'][x] for x in source_node.dimnames) + ']'

                    inputs.append('<i_{id}>{dim} {id}'.format(id=input_.id, dim=dimensions_in))
                    outputs.append('<dummy_{id}>{id} {dim}'.format(id=input_.id, dim=dimensions_out))
                inputs = '|'.join(inputs)
                outputs = '|'.join(outputs)

                sub_graph.node(
                    node_id + '_inputs',
                    label="<id>{id} inputs|{{{{{inputs}}}|{{{outputs}}}}}".format(id=self.id, inputs=inputs, outputs=outputs),
                    fillcolor=context['colors']['macro_link'],
                    style="filled"
                )

                # Create connection node for outputs
                inputs = []
                outputs = []

                for output in self.outputs.values():
                    sink_node = self.network.nodelist[output.id]
                    if context['draw_dimensions']:
                        dimensions_in = '[' + 'x'.join(context['dimensions'][x] for x in sink_node.dimnames) + ']'
                        dimensions_out = '[' + 'x'.join(old_dimensions[x] for x in output.dimnames) + ']'

                    inputs.append('<dummy_{id}>{dim} {id}'.format(id=output.id, dim=dimensions_in))
                    outputs.append('<o_{id}>{id} {dim}'.format(id=output.id, dim=dimensions_out))
                inputs = '|'.join(inputs)
                outputs = '|'.join(outputs)

                sub_graph.node(
                    node_id + '_outputs',
                    label="<id>{id} outputs|{{{{{inputs}}}|{{{outputs}}}}}".format(id=self.id, inputs=inputs, outputs=outputs),
                    fillcolor=context['colors']['macro_link'],
                    style="filled"
                )

                # Draw the macro network inside the sub_graph
                self.network.draw(context=context, graph=sub_graph)

                # Generate extra links to connect parent network to internal macro network
                for input_ in self.inputs.values():
                    source = '{}_inputs:dummy_{}'.format(node_id, input_.id)
                    target = self.network.nodelist[input_.id].draw_id(context)
                    graph.edge(source, target)

                for output in self.outputs.values():
                    source = self.network.nodelist[output.id].draw_id(context)
                    target = '{}_outputs:dummy_{}'.format(node_id, output.id)
                    graph.edge(source, target)

            # Reset context
            context['network_stack'].pop()
            context['dimensions'] = old_dimensions
        else:
            super(MacroNode, self).draw(context=context,
                                        graph=graph,
                                        color=color)

    def _update(self, key, forward=True, backward=False):
        """
        Update the Node information and validity of the Node and propagate
         the update downstream. Updates inputs, input groups, outputsize and outputs.

        A Node is valid if:

        * All Inputs are valid (see :py:meth:`Input.update <fastr.planning.inputoutput.Input.update>`)
        * All InputGroups are non-zero sized

        """
        super(MacroNode, self)._update(key, forward=False, backward=backward)
        self._update_input_mappings()
        self._output_info = {sink_id: None for sink_id in self._network.sinklist.keys()}

        # Update all downstream listeners
        if forward:
            for listener in self.listeners:
                listener.update(key, forward, False)


class FlowNode(Node):
    """
    A Flow Node is a special subclass of Nodes in which the amount of samples
    can vary per Output. This allows non-default data flows.
    """
    _OutputType = Output

    def __init__(self, tool, id_=None, parent=None, resource_limits=None, nodegroup=None):
        """
        Instantiate a flow node.

        :param tool: The tool to base the node on
        :type tool: :py:class:`Tool <fastr.core.tool.Tool>`
        :param str id_: the id of the node
        :param parent: the parent network of the node
        :type parent: :py:class:`Network <fastr.planning.network.Network>`
        :return: the newly created FlowNode
        """
        super(FlowNode, self).__init__(tool, id_, parent=parent, resource_limits=resource_limits, nodegroup=nodegroup)

        self._input_groups = OrderedDict()

        # Update Inputs and self (which calls Outputs)
        self.update()

    @property
    def blocking(self):
        """
        A FlowNode is (for the moment) always considered blocking.

        :return: True
        """
        return True

    @property
    def outputsize(self):
        """
        Size of the outputs in this Node
        """
        # Get sizes of all input groups
        output_size = []
        for input_group in self.input_groups.values():
            if input_group.size is not None:
                output_size.extend(input_group.size)
            else:
                return None

        output_size.append(sympy.symbols('N_{}'.format(self.id)))
        return tuple(output_size)

    @property
    def dimensions(self):
        """
        Names of the dimensions in the Node output. These will be reflected
        in the SampleIdList of this Node.
        """
        if self.nodegroup is not None:
            extra_dim = self.nodegroup
        else:
            extra_dim = self.id

        extra_dim = Dimension(extra_dim, sympy.symbols('N_{}'.format(self.id)))

        return super(FlowNode, self).dimensions + (extra_dim,)


class AdvancedFlowNode(FlowNode):
    _OutputType = AdvancedFlowOutput


class SourceNode(FlowNode):
    """
    Class providing a connection to data resources. This can be any kind of
    file, stream, database, etc from which data can be received.
    """

    __dataschemafile__ = 'SourceNode.schema.json'
    _OutputType = SourceOutput

    def __init__(self, datatype, id_=None, parent=None, resource_limits=None, nodegroup=None):
        """
        Instantiation of the SourceNode.

        :param datatype: The (id of) the datatype of the output.
        :param id_: The url pattern.

        This class should never be instantiated directly (unless you know what
        you are doing). Instead create a source using the network class like
        shown in the usage example below.

        usage example:

        .. code-block:: python

          >>> import fastr
          >>> network = fastr.create_network()
          >>> source = network.create_source(datatype=types['ITKImageFile'], id_='sourceN')
        """
        tool = resources.tools['fastr/Source:1.0', '1.0']

        super(SourceNode, self).__init__(tool, id_, parent=parent, resource_limits=resource_limits, nodegroup=nodegroup)

        self._input_groups = []

        # Set the DataType
        if datatype in types:
            if isinstance(datatype, str):
                datatype = types[datatype]
        else:
            message = 'Unknown DataType for SourceNode {} (found {}, which is not found in the types)!'.format(self.fullid, datatype)
            log.critical(message)
            raise exceptions.FastrValueError(message)

        self.datatype = datatype
        self._input_data = None

    def __getstate__(self):
        """
        Retrieve the state of the SourceNode

        :return: the state of the object
        :rtype dict:
        """
        state = super(SourceNode, self).__getstate__()

        return state

    def __setstate__(self, state):
        """
        Set the state of the SourceNode by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(SourceNode, self).__setstate__(state)

        self._input_data = None

    @property
    def datatype(self):
        """
        The datatype of the data this source supplies.
        """
        return self.outputs['output'].datatype

    @datatype.setter
    def datatype(self, value):
        """
        The datatype of the data this source supplies. (setter)
        """
        self.outputs['output'].datatype = value

    @property
    def sourcegroup(self):
        log.warning('[DEPRECATED] The sourcegroup property of the'
                          ' SourceNode is deprecated and replaced by the'
                          ' nodegroup property of the Node. Please use that'
                          ' property instead, it will have the same'
                          ' functionality')
        return self.nodegroup

    @property
    def nodegroup(self):
        return self._nodegroup

    @nodegroup.setter
    def nodegroup(self, value):
        self._nodegroup = value
        self._dimensions = None

    @property
    def dimensions(self):
        """
        The dimensions in the SourceNode output. These will be reflected
        in the SampleIdLists.
        """
        if self._dimensions is None:
            if self.nodegroup is not None:
                name = self.nodegroup
            else:
                name = self.id

            self._dimensions = Dimension(name, sympy.Symbol('N_{}'.format(name))),

        return self._dimensions

    @property
    def output(self):
        """
        Shorthand for ``self.outputs['output']``
        """
        return self.outputs['output']

    @property
    def valid(self):
        """
        This does nothing. It only overloads the valid method of Node().
        The original is intended to check if the inputs are connected to
        some output. Since this class does not implement inputs, it is skipped.
        """
        return True

    def draw(self, context, graph, color=None):
        if color is None:
            color = context['colors']['source_node']

        super(SourceNode, self).draw(context=context,
                                     graph=graph,
                                     color=color)

    def set_data(self, data, ids=None):
        """
        Set the data of this source node.

        :param data: the data to use
        :type data: dict, OrderedDict or list of urls
        :param ids: if data is a list, a list of accompanying ids
        """
        self._input_data = OrderedDict()

        # Check if data has key or generate keys
        log.debug('Storing {} (ids {}) in {}'.format(data, ids, self.fullid))
        if isinstance(data, OrderedDict):
            data = list(data.values())
            ids = [SampleId(x) for x in data.keys()]
        elif isinstance(data, dict):
            # Have data sorted on ids
            ids, data = list(zip(*sorted(data.items())))
            ids = [SampleId(x) for x in ids]
        elif isinstance(data, list):
            if ids is None:
                ids = [SampleId('id_{}'.format(k)) for k in range(len(data))]
            elif not isinstance(ids, list):
                raise exceptions.FastrTypeError('Invalid type! The ids argument should be a list that matches the data samples!')
        elif isinstance(data, tuple):
            # A single sample with cardinality
            ids = [SampleId('id_0')]
            data = [data]
        else:
            if isinstance(data, set):
                log.warning('Source data for {} is given as a set,'.format(self.fullid) +
                                  ' this is most probably a mistake and a list or dict should'
                                  ' be used instead')
            ids = [SampleId('id_0')]
            data = [data]

        for key, value in zip(ids, data):
            if isinstance(value, tuple):
                self._input_data[key] = tuple(x if self.datatype.isinstance(x) else str(x) for x in value)
            else:
                self._input_data[key] = (value if self.datatype.isinstance(value) else str(value)),
            log.debug('Result {}: {} (Type {})'.format(key, self._input_data[key], type(self._input_data[key]).__name__))

    def _update(self, key, forward=True, backward=False):
        """
        Update the Node information and validity of the Node and propagate
         the update downstream. Updates inputs, input_groups, outputsize and outputs.

        A Node is valid if:

        * All Inputs are valid (see :py:meth:`Input.update <fastr.planning.inputoutput.Input.update>`)
        * All InputGroups are non-zero sized

        """
        # Make sure the Inputs and input groups are up to date
        # log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.id))

        for input_ in self.inputs.values():
            input_.update(key)

        self.update_input_groups()

        # Update own status
        valid = True
        messages = []

        if len(self.listeners) == 0:
            valid = False
            messages.append('[{}] No nodes are linked to any output of this SourceNode'.format(self.id))

        for id_, input_ in self.inputs.items():
            if not input_.valid:
                valid = False
                for message in input_.messages:
                    messages.append('Input {} is not valid: {}'.format(id_, message))

        for input_group in self.input_groups.values():
            if input_group.empty:
                valid = False
                messages.append('InputGroup {} is empty'.format(input_group.id))

        for id_, output in self.outputs.items():
            if output.resulting_datatype is not None and not issubclass(output.resulting_datatype, DataType):
                    valid = False
                    messages.append(
                        'Output {} cannot determine the Output DataType (got {}), '
                        'please specify a valid DataType or add casts to the Links'.format(
                            id_, output.resulting_datatype))

        self._status['valid'] = valid
        self._status['messages'] = messages

        # Update all outputs
        for output in self.outputs.values():
            output.update(key)

        # Update all downstream listeners
        if forward:
            for listener in self.listeners:
                listener.update(key, forward, backward)


class SinkNode(Node):
    """
    Class which handles where the output goes. This can be any kind of file, e.g.
    image files, textfiles, config files, etc.
    """

    __dataschemafile__ = 'SinkNode.schema.json'

    def __init__(self, datatype, id_=None, parent=None, resource_limits=None, nodegroup=None):
        """ Instantiation of the SourceNode.

        :param datatype: The datatype of the output.
        :param id_: the id of the node to create
        :return: newly created sink node

        usage example:

        .. code-block:: python

          >>> import fastr
          >>> network = fastr.create_network()
          >>> sink = network.create_sink(datatype=types['ITKImageFile'], id_='SinkN')

        """
        Node.__init__(self, resources.tools['fastr/Sink:1.0', '1.0'], id_, parent=parent, resource_limits=resource_limits, nodegroup=nodegroup)
        # Set the DataType
        if datatype in types:
            if isinstance(datatype, str):
                datatype = types[datatype]
        else:
            message = 'Invalid DataType for SinkNode {} (found {})!'.format(self.fullid, datatype)
            log.critical(message)
            raise exceptions.FastrValueError(message)

        self.datatype = datatype
        self.url = None

    def __getstate__(self):
        state = super(SinkNode, self).__getstate__()
        state['url'] = self.url
        return state

    def __setstate__(self, state):
        super(SinkNode, self).__setstate__(state)
        self.url = state['url']

    @property
    def datatype(self):
        """
        The datatype of the data this sink can store.
        """
        return self.inputs['input'].datatype

    @datatype.setter
    def datatype(self, value):
        """
        The datatype of the data this sink can store (setter).
        """
        self.inputs['input'].datatype = value

    @property
    def input(self):
        """
        The default input of the sink Node
        """
        return self.inputs['input']

    @input.setter
    def input(self, value):
        """
        The default input of the sink Node (setter)
        """
        self.inputs['input'] = value

    def draw(self, context, graph, color=None):
        if color is None:
            color = context['colors']['sink_node']

        super(SinkNode, self).draw(context=context,
                                     graph=graph,
                                     color=color)

    def _update(self, key, forward=True, backward=False):
        """
        Update the Node information and validity of the Node and propagate
         the update downstream. Updates inputs, input groups, outputsize and outputs.

        A Node is valid if:

        * All Inputs are valid (see :py:meth:`Input.update <fastr.planning.inputoutput.Input.update>`)
        * All InputGroups are non-zero sized

        """
        # Make sure the Inputs and input groups are up to date
        # log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.id))

        if backward:
            for sourced_node in self.get_sourced_nodes():
                sourced_node.update(key, False, backward)

        for input_ in self.inputs.values():
            input_.update(key, forward, backward)

        # Reset dimensions cache
        self._dimensions = None

        self.update_input_groups()
        self.input_group_combiner.update()

        # Update own status
        valid = True
        messages = []

        if len(self.get_sourced_nodes()) == 0:
            valid = False
            messages.append('[{}] No nodes are linked to any input of this Node'.format(self.id))

        for id_, input_ in self.inputs.items():
            if not input_.valid:
                valid = False
                for message in input_.messages:
                    messages.append('[{}] Input {} is not valid: {}'.format(self.id, input_.id, message))

        for input_group in self.input_groups.values():
            if input_group.empty:
                valid = False
                messages.append('[{}] InputGroup {} is empty'.format(self.id, input_group.id))

        self._status['valid'] = valid
        self._status['messages'] = messages


class ConstantNode(SourceNode):
    """
    Class encapsulating one output for which a value can be set. For example
    used to set a scalar value to the input of a node.
    """

    __dataschemafile__ = 'ConstantNode.schema.json'

    def __init__(self, datatype, data, id_=None, parent=None, resource_limits=None, nodegroup=None):
        """
        Instantiation of the ConstantNode.

        :param datatype: The datatype of the output.
        :param data: the prefilled data to use.
        :param id_: The url pattern.

        This class should never be instantiated directly (unless you know what
        you are doing). Instead create a constant using the network class like
        shown in the usage example below.

        usage example:

        .. code-block:: python

          >>> import fastr
          >>> network = fastr.create_network()
          >>> source = network.create_source(datatype=types['ITKImageFile'], id_='sourceN')

        or alternatively create a constant node by assigning data to an item in an InputDict:

        .. code-block:: python

          >>> node_a.inputs['in'] = ['some', 'data']

        which automatically creates and links a ConstantNode to the specified Input
        """
        super(ConstantNode, self).__init__(datatype, id_, parent=parent, resource_limits=resource_limits, nodegroup=nodegroup)
        self.set_data(data)
        self._data = self._input_data

    def __getstate__(self):
        """
        Retrieve the state of the ConstantNode

        :return: the state of the object
        :rtype dict:
        """
        state = super(ConstantNode, self).__getstate__()

        state['data'] = list(self._data.items())

        return state

    def __setstate__(self, state):
        """
        Set the state of the ConstantNode by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(ConstantNode, self).__setstate__(state)

        self._data = OrderedDict((SampleId(str(x) for x in key), tuple(str(x) for x in value)) for key, value in state['data'])
        self.set_data()  # Make sure that the output size etc gets set

    def set_data(self, data=None, ids=None):
        """
        Set the data of this constant node in the correct way. This is mainly
        for compatibility with the parent class SourceNode

        :param data: the data to use
        :type data: dict or list of urls
        :param ids: if data is a list, a list of accompanying ids
        """
        # We have to arguments to match the superclas
        # pylint: disable=unused-argument
        if data is None and self.data is not None:
            self._input_data = self.data
        else:
            super(ConstantNode, self).set_data(data, ids)

    @property
    def data(self):
        """
        The data stored in this constant node
        """
        return self._data

    @property
    def print_value(self):
        result = []
        for value in self.data.values():
            value = [str(x) for x in value]
            value = tuple((x[:12] + '...' + x[-18:]) if len(x) > 33 else x for x in value)
            result.append(value)

        return pprint.pformat(result, width=36).replace('\n', r'\n')

    def draw(self, context, graph, color=None):
        if color is None:
            color = context['colors']['constant_node']

        graph.node(self.draw_id(context=context),
                   label="<id>{id}|<o_output>{data}".format(id=self.id, data=self.print_value),
                   fillcolor=color,
                   style="filled")
