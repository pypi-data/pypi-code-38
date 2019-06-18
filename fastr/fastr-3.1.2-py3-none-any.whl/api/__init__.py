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
This module provides the API for fastr that users should use. This API will be
considered stable between major versions. If users only interact via this API
(and refrain from operating on ``parent`` attributes), their code should be
compatible within major version of fastr.
"""

import datetime
from typing import Any, Dict, Generic, Iterator, List, Mapping, Optional, Tuple, TypeVar, Union
import os

from .. import exceptions
from ..planning.network import Network as CoreNetwork
from ..planning.inputoutput import BaseInput, BaseOutput
from ..core.resourcelimit import ResourceLimit
from ..core.tool import Tool
from ..core.version import Version
from ..datatypes import BaseDataType
from ..execution.networkrun import NetworkRun


# Expose only the main functions to users, rest will follow from there
__all__ = [
    'create_network',
    'create_network_copy',
    'ResourceLimit',
]


CollapseType = Tuple[Union[int, str], ...]

VersionType = Union[Version, str]

DataTypeType = Union[BaseDataType, str]
ToolType = Union[
    Tool,
    str,
]

# The data structure used for source data, base structure can be dict of list or dict
SourceDataType = Dict[str, Union[
    # List of values (str or tuple)
    List[Union[str, Tuple[str, ...]]],

    # Dict of str (id) -> value (str or tuple)
    Dict[str, Union[str, Tuple[str, ...]]]
]]

# The data structure used for sink data
SinkDataType = Union[str, Dict[str, str]]

# Different data structures that describe a state
NetworkStateType = Union['Network', CoreNetwork, dict]


T = TypeVar("T")


class SubObjectMap(Mapping[str, T], Generic[T]):
    """
    Generic object to retrieve wrapped objects from a collection
    """
    __slots__ = ('_parent', '_attribute', '_type')

    def __init__(self, parent: Any, attribute: str, type_: type):
        self._parent = parent
        self._attribute = attribute
        self._type = type_

    def __repr__(self) -> str:
        return '<{} map, items: {}>'.format(
            self._type.__name__,
            list(self.collection.keys())
        )

    def __iter__(self) -> Iterator[T]:
        for key in self.collection.__iter__():
            yield key

    def __len__(self) -> int:
        return len(self.collection)

    def __getitem__(self, item) -> T:
        return self._type(self.collection[item])

    @property
    def collection(self) -> Mapping[str, T]:
        return getattr(self._parent.parent, self._attribute)


class BaseWrapper:
    """
    Generic base class for wrapping fastr internal objects in a user-exposed
    API objects.
    """
    __slots__ = ('_parent',)

    def __init__(self, parent: Any):
        self._parent = parent

    def __repr__(self) -> str:
        return repr(self.parent)

    def __str__(self) -> str:
        return str(self.parent)

    @property
    def id(self) -> str:
        """
        The unique id describing this resource
        """
        return self.parent.id

    @property
    def parent(self) -> Any:
        """
        The parent object for this wrapper. This point to a non-api object
        in the internals of fastr and should not be used by normal users.
        """
        return self._parent


def cast_basewrapper(value):
    """
    Cast a value to non have BaseWrappers. BaseWrappers will be replaced by their parent.
    In Tuples each element is cast if needed.
    """
    if isinstance(value, BaseWrapper):
        value = value.parent
    elif isinstance(value, tuple):
        value = tuple(x.parent if isinstance(x, BaseWrapper) else x for x in value)
    return value


class Output(BaseWrapper):
    """
    Representation of an Output of a Node
    """
    def __getitem__(self, item: Union[int, slice]) -> 'Output':
        """
        Get a SubOuput of this Ouput. The SubOutput selects some data from the
        parent Output based on an index or slice of the cardinalty.

        :param key: the key of the requested item, can be an index or slice
        :return: the requested SubOutput with a view of the data in this Output
        """
        return Output(self.parent.__getitem__(item))


# The data structure that can be used for the source of linking
LinkSourceType = Union[Output, BaseOutput, list, dict, tuple]


class Link(BaseWrapper):
    """
    Representation of a link for editing the Network
    """
    @property
    def collapse(self) -> CollapseType:
        """
        The dimensions which the link will collapse into the cardinality
        """
        return self.parent.collapse

    @collapse.setter
    def collapse(self, value: CollapseType):
        self.parent.collapse = value

    @property
    def expand(self) -> bool:
        """
        Flag that indicates if the Link will expand the cardinality into a new
        dimension.
        """
        return self.parent.expand

    @expand.setter
    def expand(self, value: bool):
        self.parent.expand = value


class Input(BaseWrapper):
    """
    Representation of an Input of a Node
    """

    def __getitem__(self, key: str) -> 'NamedSubInput':
        if not isinstance(key, str):
            raise ValueError('Can only manipulate named sub inputs directly')

        return NamedSubInput(self.parent[key])

    def __setitem__(self, key: str, value):
        if not isinstance(key, str):
            raise ValueError('Can only manipulate named sub inputs directly')

        self.parent[key] = cast_basewrapper(value)

    def append(self, value: LinkSourceType) -> Link:
        """
        Create a link from give resource to a new SubInput.

        :param value: The source for the link to be created
        :return: The newly created link
        """
        return self.parent.append(cast_basewrapper(value))

    @property
    def input_group(self) -> str:
        """
        The input group of this Input. This property can be read and changed.
        Changing the input group of an Input will influence the data flow in
        a Node (see :ref:`advanced-flow-node` for details).
        """
        return self.parent.input_group

    @input_group.setter
    def input_group(self, value: str):
        self.parent.input_group = value

    def __lshift__(self, other: LinkSourceType) -> Union[Link, Tuple[Link, ...]]:
        """
        This operator allows the easy creation of Links to this Input using the ``<<`` operator.
        Creating links can be done by:

        .. code-block:: python

            # Generic form
            >> link = input << output
            >> link = input << ['some', 'data']  # Create a constant node

            # Examples
            >> link1 = addint.inputs['left_hand'] << source1.input
            >> link2 = addint.inputs['right_hand'] << [1, 2, 3]

            # Mutliple links
            >> links = addints.inputs['left_hand'] << (source1.output, source2.output, source3.output)

        The last example would return a tuple with three links.

        :param other: the target to create the link from, this can be an Output, a tuple of Outputs, or a data
                      structure that can be used as the data for a ConstantNode
        :return: Newly created link(s)
        """
        # Make sure wrappers are cast to non-wrappers
        other = cast_basewrapper(other)

        return self.parent << other

    def __rrshift__(self, other: LinkSourceType) -> Union[Link, Tuple[Link, ...]]:
        """
        This operator allows to use the ``>>`` operator as alternative to using the ``<<`` operator.
        See the :py:meth:`__lshift__ operator <fastr.api.Input.__lshift__>` for details.

        :param other: the target to create the link from
        :return: Newly created link(s)
        """
        # Make sure wrappers are cast to non-wrappers
        other = cast_basewrapper(other)

        return other >> self.parent


class NamedSubInput(BaseWrapper):
    """
    A named sub-input. This is only used in cases where a tool accepts a mapping
    as an input. For example, if a command-line tool would accept::

        --set key1=value1 key2=value2

    Or something similar, where key1 and key2 are arbitrary strings. This can
    be translated in fastr to::

        tool.inputs['set']['key1'] << value1
        tool.inputs['set']['key2'] << value2

    """
    def __lshift__(self, other: LinkSourceType) -> Union[Link, Tuple[Link, ...]]:
        """
        This operator allows the easy creation of Links to this Input using the ``<<`` operator.
        Creating links can be done by:

        .. code-block:: python

            # Generic form
            >> link = input << output
            >> link = input << ['some', 'data']  # Create a constant node

            # Examples
            >> link1 = addint.inputs['left_hand'] << source1.input
            >> link2 = addint.inputs['right_hand'] << [1, 2, 3]

            # Mutliple links
            >> links = addints.inputs['left_hand'] << (source1.output, source2.output, source3.output)

        The last example would return a tuple with three links.

        :param other: the target to create the link from, this can be an Output, a tuple of Outputs, or a data
                      structure that can be used as the data for a ConstantNode
        :return: Newly created link(s)
        """
        # Make sure wrappers are cast to non-wrappers
        other = cast_basewrapper(other)

        return self.parent << other

    def __rrshift__(self, other: LinkSourceType) -> Union[Link, Tuple[Link, ...]]:
        """
        This operator allows to use the ``>>`` operator as alternative to using the ``<<`` operator.
        See the :py:meth:`__lshift__ operator <fastr.api.Input.__lshift__>` for details.

        :param other: the target to create the link from
        :return: Newly created link(s)
        """
        # Make sure wrappers are cast to non-wrappers
        other = cast_basewrapper(other)

        return other >> self.parent

    def append(self, value: LinkSourceType) -> Link:
        """
        Create a link from give resource to a new SubInput.

        :param value: The source for the link to be created
        :return: The newly created link
        """
        return self.parent.append(cast_basewrapper(value))



class Node(BaseWrapper):
    """
    Representation of Node for editing the Network
    """
    __slots__ = ('_inputs', '_outputs')

    def __init__(self, parent):
        super().__init__(parent)
        self._inputs = InputMap(self, 'inputs', Input)
        self._outputs = SubObjectMap(self, 'outputs', Output)

    @property
    def inputs(self) -> 'InputMap':
        """
        Mapping object containing all Inputs of a Node
        """
        return self._inputs

    @property
    def outputs(self) -> SubObjectMap[Output]:
        """
        Mapping object containing all Outputs of a Node
        """
        return self._outputs

    @property
    def input(self) -> Input:
        """
        In case there is only a single Inputs in a Node, this can be used as a short hand.
        In that case it is basically the same as ``list(node.inputs.values()[0])``.
        """
        if len(self.inputs) == 1:
            return next(iter(self.inputs.values()))
        else:
            raise KeyError('There is not 1 unique input, cannot use short-cut!')

    @input.setter
    def input(self, value):
        if len(self.inputs) == 1:
            input = next(iter(self.inputs.values()))
            input << value
        else:
            raise KeyError('There is not 1 unique input, cannot use short-cut!')

    @property
    def output(self) -> Output:
        """
        In case there is only a single Outputs in a Node, this can be used as a short hand.
        In that case it is basically the same as ``list(node.outputs.values()[0])``.
        """
        if len(self.outputs) == 1:
            return next(iter(self.outputs.values()))
        else:
            raise KeyError('There is not 1 unique outputs, cannot use short-cut!')

    @property
    def merge_dimensions(self) -> Union[str, Tuple[str, ...]]:
        return self._parent.merge_dimensions

    @merge_dimensions.setter
    def merge_dimensions(self, value: Union[str, Tuple[str, ...]]):
        self._parent.merge_dimensions = value


class InputMap(SubObjectMap[Input]):
    def __setitem__(self, key, value):
        # Make sure wrappers are cast to non-wrappers
        value = cast_basewrapper(value)
        self.collection[key] = value


class Network(BaseWrapper):
    """
    Representation of a Network for the creating and adapting Networks
    """
    __slots__ = ('_node_map',)

    def __init__(self, id, version=None):
        self._parent = CoreNetwork(id_=id, version=version)
        self._node_map = SubObjectMap(self, 'nodelist', Node)

    @property
    def nodes(self) -> SubObjectMap[Node]:
        return self._node_map

    @property
    def version(self) -> Version:
        """
        Version of the Network (so users can keep track of their version)
        """
        return self.parent.version

    def create_node(self,
                    tool: ToolType,
                    tool_version: str,
                    id: str = None,
                    step_id: str = None,
                    resources: ResourceLimit = None,
                    node_group: str = None) -> Node:
        """
        Create a Node in this Network. The Node will be automatically added to
        the Network.

        :param tool: The Tool to base the Node on in the form: ``name/space/toolname:version``
        :param tool_version: The version of the tool wrapper to use
        :param id: The id of the node to be created
        :param step_id: The step to add the created node to
        :param resources: The resources required to run this node
        :param node_group: The group the node belongs to, this can be
                           important for FlowNodes and such, as they
                           will have matching dimension names.
        :return: the newly created node
        """

        if not isinstance(tool, (str, Tool)):
            raise exceptions.FastrTypeError('The tool argument should be either a Tool or a str')

        resources = resources or ResourceLimit()
        return Node(self.parent.create_node(
            tool=tool,
            tool_version=tool_version,
            id_=id,
            stepid=step_id,
            resources=resources.copy(),
            nodegroup=node_group
        ))

    def create_macro(self,
                     network: Union[NetworkStateType, Tool, str],
                     id: str = None) -> Node:
        """
        Create macro node (a node which actually contains a network used as node
        inside another network).

        :param network: The network to use, this can be a network (state), a
                        macro tool, or the path to a python file that contains
                        a function create_network which returns the desired
                        network.
        :param id: The id of the node to be created
        :return: the newly created node
        """
        return Node(self.parent.create_macro(network=network, id_=id))

    def create_constant(self,
                        datatype: DataTypeType,
                        data: SourceDataType,
                        id: str = None,
                        step_id: str = None,
                        resources: ResourceLimit = None,
                        node_group: str = None) -> Node:
        """
        Create a ConstantNode in this Network. The Node will be automatically added to
        the Network.

        :param datatype: The DataType of the constant node
        :param data: The data to hold in the constant node
        :param id: The id of the constant node to be created
        :param step_id: The step to add the created constant node to
        :param resources: The resources required to run this node
        :param node_group: The group the node belongs to, this can be
                              important for FlowNodes and such, as they
                              will have matching dimension names.
        :return: the newly created constant node
        """
        resources = resources or ResourceLimit()
        return Node(self.parent.create_constant(
            datatype=datatype,
            data=data,
            id_=id,
            stepid=step_id,
            resources=resources.copy(),
            nodegroup=node_group
        ))

    def create_link(self,
                    source: Union[Input, BaseInput],
                    target: Union[Output, BaseOutput],
                    id: str = None,
                    collapse: CollapseType = None,
                    expand: bool = False) -> Link:
        """
        Create a link between two Nodes and add it to the current Network.

        :param source: the output that is the source of the link
        :param target: the input that is the target of the link
        :param id: the id of the link
        :param collapse: The dimensions to collapse in this link.
        :param expand: Flag to expand cardinality into a new dimension
        :return: the created link
        """
        if isinstance(source, Output):
            source = source.parent

        if isinstance(target, Input):
            target = target.parent

        return Link(self.parent.create_link(
            source=source,
            target=target,
            id_=id,
            collapse=collapse,
            expand=expand
        ))

    def create_source(self,
                      datatype: DataTypeType,
                      id: str = None,
                      step_id: str = None,
                      resources: ResourceLimit = None,
                      node_group: str = None) -> Node:
        """
        Create a SourceNode in this Network. The Node will be automatically added to
        the Network.

        :param datatype: The DataType of the source source_node
        :type datatype: :py:class:`BaseDataType <fastr.plugins.managers.datatypemanager.BaseDataType>`
        :param str id: The id of the source source_node to be created
        :param str step_id: The step to add the created source source_node to
        :param resources: The resources required to run this node
        :param str node_group: The group the node belongs to, this can be
                              important for FlowNodes and such, as they
                              will have matching dimension names.
        :return: the newly created source source_node
        :rtype: :py:class:`SourceNode <fastr.core.source_node.SourceNode>`
        """
        resources = resources or ResourceLimit()
        return Node(self.parent.create_source(
            datatype=datatype,
            id_=id,
            stepid=step_id,
            resources=resources.copy(),
            nodegroup=node_group
        ))

    def create_sink(self,
                    datatype: DataTypeType,
                    id: str = None,
                    step_id: str = None,
                    resources: ResourceLimit = None,
                    node_group: str = None) -> Node:
        """
        Create a SinkNode in this Network. The Node will be automatically added to
        the Network.

        :param datatype: The DataType of the sink node
        :param id: The id of the sink node to be created
        :param step_id: The step to add the created sink node to
        :param resources: The resources required to run this node
        :param str node_group: The group the node belongs to, this can be
                              important for FlowNodes and such, as they
                              will have matching dimension names.
        :return: the newly created sink node
        """
        resources = resources or ResourceLimit()
        return Node(self.parent.create_sink(
            datatype=datatype,
            id_=id,
            stepid=step_id,
            resources=resources.copy(),
            nodegroup=node_group,
        ))

    def create_reference(self,
                         source_data: SourceDataType,
                         output_directory: str,
                         ):
        """
        Create reference data to test a Network against

        :param source_data: The source data to use for the reference
        :param output_directory: The directory to store the reference
        """
        self._parent.create_reference(source_data=source_data,
                                      output_directory=output_directory)

    def draw(self,
             file_path: str = None,
             draw_dimensions: bool = True,
             hide_unconnected: bool = True,
             expand_macros: Union[bool, int] = 1,
             font_size: int = 14) -> Optional[str]:
        """
        Draw a graphical representation of the Network

        :param str file_path: The path of the file to create, the extension will control the image type
        :param bool draw_dimensions: Flag to control if the dimension sizes should be drawn
                                     in the figure, default is true
        :param bool expand_macros: Flag to control if and how macro nodes should be expanded,
                                   by default 1 level is expanded
        :return: path of the image created or None if failed
        """
        if file_path is not None:
            file_path, ext = os.path.splitext(file_path)
        else:
            file_path = self.id
            ext = 'svg'

        if not ext:
            ext = 'svg'

        return self.parent.draw_network(name=file_path,
                                        img_format=ext.lstrip('.'),
                                        draw_dimension=draw_dimensions,
                                        hide_unconnected=hide_unconnected,
                                        expand_macro=expand_macros,
                                        font_size=font_size)

    def execute(self,
                source_data: SourceDataType,
                sink_data: SinkDataType,
                tmpdir: str = None,
                timestamp: Union[datetime.datetime, str] = None,
                blocking: bool = True,
                execution_plugin: Optional[str] = None) -> NetworkRun:
        """
        Execute the network with the given source and sink data.

        :param source_data: Source data to use as an input
        :param sink_data: Sink rules to use for determining the outputs
        :param tmpdir: The scratch directory to use for this network run, if
                       an existing directory is given, fastr will try to resume
                       a network run (see :ref:`continuing-network`)
        :param timestamp: The timestamp of the network run (useful for retrying
                          or continuing previous runs)
        :param blocking: Flag to indicate if the execution should be blocking
                         or launched in a background thread
        :param execution_plugin: The execution plugin to use for this run
        :return: The network run object for the started execution
        """
        return self.parent.execute(
            sourcedata=source_data,
            sinkdata=sink_data,
            tmpdir=tmpdir,
            timestamp=timestamp,
            blocking=blocking,
            execution_plugin=execution_plugin,
        )

    @classmethod
    def load(cls, filename: str) -> 'Network':
        """
        Load Network froma  file

        :param str filename:
        :return: loaded network
        :rtype: Network
        """
        result = BaseWrapper.__new__(Network)

        # Load Network and create correct node map
        result._parent = CoreNetwork.loadf(filename)
        result._node_map = SubObjectMap(result.parent, 'nodelist', Node)

        return result

    def save(self,
             filename: str,
             indent: int = 2):
        """
        Save the Network to a JSON file

        :param filename: Path of the file to save to
        :param indent: Indentation to use (None for no indentation)
        """
        self.parent.dumpf(filename, method='json', indent=indent)

    def is_valid(self):
        return self._parent.is_valid()


def create_network(id: str,
                   version: VersionType = None) -> Network:
    """
    Create a new Network object

    :param id: id of the network
    :param version: version of the network
    :return:
    """
    return Network(id=id, version=version)


def create_network_copy(network_state: NetworkStateType) -> Network:
    """
    Create a network based on another Network state. The network state can be a Network
    or the state gotten from a Network with __getstate__.

    :param network_state: Network (state) to create a copy of
    :return: The rebuilt network
    """
    if isinstance(network_state, Network):
        network_state = network_state.parent

    if isinstance(network_state, CoreNetwork):
        network_state = network_state.__getstate__()

    # Create the copy of the Network
    result = BaseWrapper.__new__(Network)
    result._parent = CoreNetwork.createobj(network_state)
    result._node_map = SubObjectMap(result.parent, 'nodelist', Node)

    return result
