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
Classes for arranging the input and output for nodes.

Exported classes:

Input -- An input for a node (holding datatype).
Output -- The output of a node (holding datatype and value).
ConstantOutput -- The output of a node (holding datatype and value).

.. warning::
   Don't mess with the Link, Input and Output internals from other places.
   There will be a huge chances of breaking the network functionality!
"""
from abc import abstractmethod, abstractproperty
from collections import OrderedDict
from typing import Union

import sympy

from .. import exceptions
from ..abc.serializable import Serializable
from ..abc.updateable import Updateable
from ..core.cardinality import create_cardinality
from ..core.dimension import HasDimensions, Dimension
from ..core.interface import InputSpec, OutputSpec
from ..datatypes import DataType, types
from ..helpers import log
from ..utils.dicteq import dicteq


class BaseInputOutput(HasDimensions, Updateable, Serializable):

    """
    Base class for Input and Output classes. It mainly implements the
    properties to access the data from the underlying ParameterDescription.
    """
    description_type = None

    def __init__(self, node, description):
        """Instantiate a BaseInputOutput

        :param node: the parent node the input/output belongs to.
        :param description: the :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
               describing the input/output.
        :return: created BaseInputOutput
        :raises FastrTypeError: if description is not of class
                                :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
        :raises FastrDataTypeNotAvailableError: if the DataType requested cannot be found in the ``types``
        """
        super(BaseInputOutput, self).__init__()

        self._node = node

        # Get DataType
        if description.datatype in types:
            self._description = description
            self._datatype = types[description.datatype]

            # Create a validator for the cardinality
            self.cardinality_spec = create_cardinality(description.cardinality, self)
        else:
            raise exceptions.FastrDataTypeNotAvailableError('DataType {} does not exist'.format(description.datatype))

    def __ne__(self, other):
        """
        Check two Node instances for inequality. This is the inverse of __eq__

        :param other: the other instances to compare to
        :type other: BaseInputOutput
        :returns: True if unequal, False otherwise
        """
        if not isinstance(self, type(other)):
            return NotImplemented

        return not self == other

    def __iter__(self):
        """
        This function is blocked to avoid support for iteration using a lecacy __getitem__ method.

        :return: None
        :raises FastrNotImplementedError: always
        """
        raise exceptions.FastrNotImplementedError('Not iterable, this function is to block legacy iteration using getitem')

    def __getstate__(self):
        """
        Retrieve the state of the BaseInputOutput

        :return: the state of the object
        :rtype dict:
        """
        state = super(BaseInputOutput, self).__getstate__()
        state['id'] = self.id
        state['datatype'] = self.datatype.id
        state['description'] = self.description._asdict()
        return state

    def __setstate__(self, state):
        """
        Set the state of the BaseInputOutput by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(BaseInputOutput, self).__setstate__(state)

        if 'description' in state:
            description = state.pop('description')
            if description['datatype'] in types:
                # Reconstruct description object
                description_type = self.description_type
                args = [description[x] for x in description_type._fields]
                self._description = description_type(*args)

                self._datatype = types[description['datatype']]

                # Create a validator for the cardinality
                self.cardinality_spec = create_cardinality(self._description.cardinality, self)
            else:
                raise exceptions.FastrDataTypeNotAvailableError('DataType {} does not exist'.format(description.datatype))

        if 'datatype' in state:
            self._datatype = types[state['datatype']]


    def __repr__(self):
        """
        Get a string representation for the Input/Output

        :return: the string representation
        :rtype: str
        """
        return f'<{type(self).__name__}: {self.fullid}>'

    @property
    def datatype(self):
        """
        The datatype of this Input/Output
        """
        return self._datatype

    @datatype.setter
    def datatype(self, value):
        """
        The datatype of this Input/Output (setter)
        """
        self._datatype = value

    @property
    def description(self):
        """
        The description object of this input/output
        """
        return self._description

    def cardinality(self, key=None, job_data=None):
        """
        Determine the cardinality of this Input/Output. Optionally a key can be
        given to determine for a sample.

        :param key: key for a specific sample
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        """

        # We need to key for the signature in subclasses, shut pylint up
        # pylint: disable=unused-argument,no-self-use

        raise exceptions.FastrNotImplementedError('Purposefully not implemented')

    @property
    def id(self):
        """
        Id of the Input/Output
        """
        return self._description.id

    @property
    def node(self):
        """
        The NodeRun to which this Input/Output belongs
        """
        return self._node

    @property
    def required(self):
        """
        Flag indicating that the Input/Output is required
        """
        return self._description.required

    @abstractproperty
    def fullid(self):
        """
        The fullid of the Input/Output, the fullid should be unnique and
        makes the object retrievable by the network.
        """
        raise exceptions.FastrNotImplementedError('Purposefully not implemented')

    def check_cardinality(self, key=None) -> bool:
        """
        Check if the actual cardinality matches the cardinality specified in
        the ParameterDescription. Optionally you can use a key to test for a
        specific sample.

        :param key: sample_index (tuple of int) or
                    :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
                    for desired sample
        :return: flag indicating that the cardinality is correct
        :rtype: bool
        :raises FastrCardinalityError: if the Input/Output has an incorrect
                cardinality description.
        """
        return self.cardinality_spec.validate(
            payload=None,
            cardinality=self.cardinality(key)
        )


class BaseInput(BaseInputOutput):
    """
    Base class for all inputs.
    """
    description_type = InputSpec

    def __init__(self, node, description):
        """
        Instantiate a BaseInput

        :param node: the parent node the input/output belongs to.
        :param description: the :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
                            describing the input/output.
        :return: the created BaseInput
        :raises FastrTypeError: if description is not of class
                                :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
        :raises FastrDataTypeNotAvailableError: if the DataType requested cannot be found in the ``types``
        """
        if not isinstance(description, InputSpec):
            log.error('Description has type "{}" (must be ParameterDescription)'.format(type(description).__name__))
            raise exceptions.FastrTypeError('An input must be constructed based on an '
                                            'object of a class derived from NodeRun and an '
                                            'object of class InputSpec')

        super(BaseInput, self).__init__(node, description)

    @abstractmethod
    def itersubinputs(self):
        """
        Iterator over the SubInputs

        :return: iterator

        example:

        .. code-block:: python

          >>> for subinput in input_a.itersubinputs():
                  print subinput

        """
        raise exceptions.FastrNotImplementedError('Purposefully not implemented')

    def __lshift__(self, other):
        if not isinstance(other, (BaseOutput, list, tuple, dict, OrderedDict)):
            return NotImplemented

        return self.create_link_from(other)

    def __rrshift__(self, other):
        if not isinstance(other, (BaseOutput, list, tuple, dict, OrderedDict)):
            return NotImplemented

        return self.create_link_from(other)

    @property
    def item_index(self):
        return None

    def constant_id(self) -> str:
        """
        The id that should be used for a constant created to serve this input.
        """
        return f'const__{self.node.id}__{self.id}'

    def create_link_from(self, value):
        if isinstance(value, BaseOutput):
            if self.node.parent is not value.node.parent:
                message = 'Cannot create links between members of different Network'
                log.warning(message)

            network = value.node.parent
            if network is None:
                message = 'Cannot create links between non-network-attached Nodes'
                log.warning(message)
            else:
                log.debug('Linking {} to {}'.format(value.fullid, self.fullid))
                return network.create_link(value, self)
        elif isinstance(value, (list, dict, OrderedDict)) or\
                (isinstance(value, tuple) and all(not isinstance(x, BaseOutput) for x in value)):
            # This is data for a ConstantNode, so create one and set it
            # First make sure the stepid of the new ConstantNode will match the stepid of the current Node
            inp = self
            for k, i in inp.node.parent.stepids.items():
                if inp.node in i:
                    stepid = k
                    break
            else:
                stepid = None
            network = inp.node.parent

            # Create constant node with correct type and id
            const_node = network.create_constant(datatype=inp.datatype,
                                                 data=value,
                                                 id_=self.constant_id,
                                                 stepid=stepid)
            return network.create_link(const_node.output, self)
        elif isinstance(value, tuple) and isinstance(self, Input):
            # First remove all current links
            self.clear()
            new_links = []

            # Create all required links, find all consecutive parts of non-outputs and
            # create ConstantNodes for those, link all outputs separately
            current_part = []
            for element in value:
                if isinstance(element, BaseOutput):
                    # If there were non-outputs found, first combine those
                    # before creating a link from the output
                    if len(current_part) > 0:
                        self.append(tuple(current_part))
                        current_part = []
                    new_links.append(self.append(element))
                else:
                    current_part.append(element)
            if len(current_part) > 0:
                new_links.append(self.append(tuple(current_part)))

            # Return a tuple of all links created
            return tuple(new_links)
        else:
            # We assume that if above tests are all False, a constant is given.
            return self.create_link_from([(value,)])

    def check_cardinality(self, key=None, planning=False) -> bool:
        """
        Check if the actual cardinality matches the cardinality specified in
        the ParameterDescription. Optionally you can use a key to test for a
        specific sample.

        :param key: sample_index (tuple of int) or
                    :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
                    for desired sample
        :return: flag indicating that the cardinality is correct
        :rtype: bool
        :raises FastrCardinalityError: if the Input/Output has an incorrect
                cardinality description.
        """
        cardinality = self.cardinality(key)

        if not isinstance(cardinality, int):
            return planning

        if not self.required and (cardinality, int) and cardinality == 0:
            return True

        return self.cardinality_spec.validate(
            payload=None,
            cardinality=cardinality,
            planning=planning
        )


class Input(BaseInput):
    """
    Class representing an input of a node. Such an input will be connected
    to the output of another node or the output of an constant node to provide
    the input value.
    """

    def __init__(self, node, description):
        """
        Instantiate an input.

        :param node: the parent node of this input.
        :type node: :py:class:`NodeRun <fastr.planning.node.NodeRun>`
        :param ParameterDescription description: the ParameterDescription of the input.
        :return: the created Input
        """
        self._source = {}
        super(Input, self).__init__(node, description)
        self._input_group = 'default'

    def __eq__(self, other):
        """Compare two Input instances with each other. This function ignores
        the parent node and update status, but tests rest of the dict for equality.

        :param other: the other instances to compare to
        :type other: :py:class:`Input <fastr.planning.inputoutput.Input>`
        :returns: True if equal, False otherwise
        :rtype: bool
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        dict_self = dict(vars(self))
        del dict_self['_node']
        del dict_self['_status']

        dict_other = dict(vars(other))
        del dict_other['_node']
        del dict_other['_status']

        return dicteq(dict_self, dict_other)

    def __getstate__(self):
        """
        Retrieve the state of the Input

        :return: the state of the object
        :rtype dict:
        """
        state = super(Input, self).__getstate__()
        state['input_group'] = self.input_group

        return state

    def __setstate__(self, state):
        """
        Set the state of the Input by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(Input, self).__setstate__(state)
        self._input_group = state['input_group']

    def __getitem__(self, key: Union[int, str]) -> 'Union[SubInput, NamedSubInput]':
        """
        Retrieve an item from this Input.

        :param key: the key of the requested item
        :return: The :py:class:`SubInput <fastr.planning.inputoutput.SubInput>`
                 corresponding with the key will be returned.
        :raises FastrTypeError: if key is not of a valid type
        :raises FastrKeyError: if the key is not found
        """
        if not isinstance(key, (int, str)):
            raise exceptions.FastrTypeError('Input indices must a int or str'
                                            ' not {}'.format(type(key).__name__))

        if key not in self.source:
            # This is to allow for linking against inputs['key'][0]
            try:
                key = int(key)
            except ValueError:
                pass  # No problem, just go for the str

            if isinstance(key, int):
                self.source[key] = SubInput(self)
            else:
                self.source[key] = NamedSubInput(self)

        return self.source[key]

    def __setitem__(self, key: Union[int, str], value):
        """
        Create a link between a SubInput of this Inputs and an Output/Constant

        :param key: the key of the SubInput
        :type key: int, str
        :param value: the target to link, can be an output or a value to create a constant for
        :type value: BaseOutput, list, tuple, dict, OrderedDict
        :raises FastrTypeError: if key is not of a valid type
        """
        if not isinstance(key, (int, str)):
            raise exceptions.FastrTypeError('The key of an SubInput to set should be an '
                                            'int or str (found {})'.format(type(key).__name__))

        if key not in self.source:
            if isinstance(key, int):
                subin = SubInput(self)
            else:
                subin = NamedSubInput(self)
            self.source[key] = subin

        self.source[key].create_link_from(value)

    def __str__(self):
        """
        Get a string version for the Input

        :return: the string version
        :rtype: str
        """
        return f'<Input: {self.fullid})>'

    def cardinality(self, key=None, job_data=None):
        """
        Cardinality for an Input is the sum the cardinalities of the SubInputs,
        unless defined otherwise.

        :param key: key for a specific sample, can be sample index or id
        :type key: tuple of int or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        """

        cardinality = 0

        for subinput in self.source.values():
            cardinality += subinput.cardinality(key, job_data)

        return cardinality

    @property
    def datatype(self):
        """
        The datatype of this Input
        """
        return self._datatype

    @datatype.setter
    def datatype(self, value):
        # This does not differ, as it is a property
        # pylint: disable=arguments-differ
        self._datatype = value
        for subinput in self.itersubinputs():
            subinput.datatype = value

    @property
    def dimensions(self):
        """
        The list names of the dimensions in this Input. This will be a list of str.
        """
        subinputs = list(self.itersubinputs())
        sizes = [sub.size for sub in subinputs]

        unique_sizes = set(sizes) - {(0,), (1,), ()}

        if len(unique_sizes) > 1:
            nr_non_symbolic_sizes = sum(all(not isinstance(x, sympy.Symbol) for x in size) for size in unique_sizes)

            if nr_non_symbolic_sizes == 0:
                max_dimensions = max(len(x) for x in unique_sizes)
                for subinput in subinputs:
                    if len(subinput.size) == max_dimensions and subinput.size not in ((0,), (1,), ()):
                        return subinput.dimensions

            raise exceptions.FastrSizeMismatchError('Cannot determine dimensions: sizes of SubInputs do not match!')
        elif len(unique_sizes) == 1:
            return subinputs[sizes.index(unique_sizes.pop())].dimensions
        elif (1,) in sizes:
            return subinputs[sizes.index((1,))].dimensions
        elif (0,) in sizes:
            return subinputs[sizes.index((0,))].dimensions
        else:
            return []

    @property
    def id(self):
        """
        Id of the Input/Output
        """
        return self._description.id

    @property
    def fullid(self) -> str:
        """
        The full defining ID for the Input
        """
        if self.node is not None:
            return '{}/inputs/{}'.format(self.node.fullid, self.id)
        else:
            return 'fastr://ORPHANED/inputs/{}'.format(self.id)

    @property
    def constant_id(self) -> str:
        """
        The id for a constant node that is attached to this input.
        """
        return f'const__{self.node.id}__{self.id}'

    @property
    def input_group(self) -> str:
        """
        The id of the :py:class:`InputGroup <fastr.planning.node.InputGroup>` this
        Input belongs to.
        """
        return self._input_group

    @input_group.setter
    def input_group(self, value: str):
        """
        The id of the :py:class:`InputGroup <fastr.planning.node.InputGroup>` this
        Input belongs to. (setter)
        """
        self._input_group = value
        self.node.update()

    @property
    def source(self):
        """
        The mapping of :py:class:`SubInputs <fastr.planning.inputoutput.SubInput>`
        that are connected and have more than 0 elements.
        """
        return self._source

    @source.setter
    def source(self, value):
        """
        The list of :py:class:`SubInputs <fastr.planning.inputoutput.SubInput>`
        that are connected and have more than 0 elements. (setter)
        """
        self.clear()

        self._source = {0: SubInput(self)}
        self._source[0].source = value

    def get_sourced_nodes(self):
        """
        Get a list of all :py:class:`Nodes <fastr.planning.node.Node>` connected as sources to this Input

        :return: list of all connected :py:class:`Nodes <fastr.planning.node.Node>`
        :rtype: list
        """
        sourced_nodes = []
        for subinput in self.itersubinputs():
            for node in subinput.get_sourced_nodes():
                if node not in sourced_nodes:
                    sourced_nodes.append(node)
        return sourced_nodes

    def get_sourced_outputs(self):
        """
        Get a list of all :py:class:`Outputs <fastr.planning.inputoutput.Output>` connected as sources to this Input

        :return: tuple of all connected :py:class:`Outputs <fastr.planning.inputoutput.Output>`
        :rtype: tuple
        """
        sourced_outputs = []
        for subinput in self.itersubinputs():
            for output in subinput.get_sourced_outputs():
                if output not in sourced_outputs:
                    sourced_outputs.append(output)
        return tuple(sourced_outputs)

    def index(self, value):
        """
        Find index of a SubInput

        :param value: the :py:class:`SubInput <fastr.planning.inputoutput.SubInput>`
                      to find the index of
        :type value: :py:class:`SubInput <fastr.planning.inputoutput.SubInput>`
        :return: key
        :rtype: int, str
        """
        for key, val in self.source.items():
            if val is value:
                return key
        else:
            return None

    def remove(self, value: 'Union[SubInput, NamedSubInput, Link]'):
        """
        Remove a SubInput from the SubInputs list based on the connected Link.

        :param value: the :py:class:`SubInput <fastr.planning.inputoutput.SubInput>`
                      or :py:class:`Link <fastr.planning.link.Link>`
                      to removed from this Input
        :type value: :py:class:`SubInput <fastr.planning.link.Link>`, <fastr.planning.inputoutput.SubInput>`
        """
        to_remove = []
        # Find keys to remove
        for key, subinput in self.source.items():
            if subinput is value or (len(subinput.source) == 1 and subinput.source[0] is value):
                to_remove.append(key)

        # Remove actual data
        for key in to_remove:
            target = self.source.pop(key)

            if target.source is not None:
                for link in target.source:
                    link.destroy()

    def clear(self):
        for key in self.source.keys():
            subinput = self.source.pop(key)
            if subinput.source is not None:
                subinput.source[0].destroy()

    def insert(self, index):
        """
        Insert a new SubInput at index in the sources list

        :param int key: positive integer for position in _source list to insert to
        :return: newly inserted :py:class:`SubInput <fastr.planning.inputoutput.SubInput>`
        :rtype: :py:class:`SubInput <fastr.planning.inputoutput.SubInput>`
        """
        newsub = SubInput(self)
        self.source[index] = newsub
        return newsub

    def append(self, value):
        """
        When you want to append a link to an Input, you can use the append
        property. This will automatically create a new SubInput to link to.

        example:

        .. code-block:: python

          >>> link = node2['input'].append(node1['output'])

        will create a new SubInput in node2['input'] and link to that.
        """
        new_sub = SubInput(self)
        # Get the next index-like key to use
        new_key = max([-1] + [x for x in self.source.keys() if isinstance(x, int)]) + 1
        self.source[new_key] = new_sub
        return new_sub.create_link_from(value)

    def itersubinputs(self):
        """
        Iterate over the :py:class:`SubInputs <fastr.planning.inputoutput.SubInput>`
        in this Input.

        :return: iterator yielding  :py:class:`SubInput <fastr.planning.inputoutput.SubInput>`


        example:

        .. code-block:: python

          >>> for subinput in input_a.itersubinputs():
                  print subinput

        """
        for subinput in self.source.values():
            yield subinput

    def _update(self, key, forward=True, backward=False):
        """Update the validity of the Input and propagate the update downstream.
        An Input is valid if:

        * All SubInputs are valid (see :py:meth:`SubInput.update <fastr.planning.inputoutput.SubInput.update>`)
        * Cardinality is correct
        * If Input is required, it must have a size larger than (0,)

        """
        # log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.fullid))
        for subinput in self.itersubinputs():
            subinput.update(key, forward, backward)

        valid = True
        messages = []
        for subinput in self.itersubinputs():
            if not subinput.valid:
                valid = False
                for message in subinput.messages:
                    messages.append('SubInput {} is not valid: {}'.format(subinput.fullid, message))

        if not self.check_cardinality(planning=True):
            cardinality = self.cardinality()

            # If the cardinality is 0 and Input is not required, this is fine,
            # all other cases where the cardinality check fails are not allowed
            valid = False

            messages.append(('Input "{}" cardinality ({}) is not valid (must'
                             ' be {}, required is {})').format(self.id,
                                                               cardinality,
                                                               self._description.cardinality,
                                                               self.required))
            if isinstance(self._description.cardinality, str) and self._description.cardinality.startswith('as:'):
                target = self._description.cardinality[3:]
                if target in self.node.inputs:
                    target_cardinality = self.node.inputs[target].cardinality()
                    messages.append('Target input {} has cardinality {}'.format(target, target_cardinality))

        if self.size is None:
            valid = False
            messages.append('Cannot determine size of Input "{}"'.format(self.id))

        log.debug('Size: {}'.format(self.size))
        if self.required and (len([x for x in self.size if x != 0]) == 0):
            valid = False
            nodes = ', '.join([x.id for x in self.get_sourced_nodes()])
            messages.append(('Required Input "{}" cannot have size 0. Input obtained'
                             ' from nodes: {}').format(self.id, nodes))

        self._status['valid'] = valid
        self._status['messages'] = messages

        # Update downstream
        self.node.update(key, forward, backward)


class NamedSubInput(Input):
    """
    A named subinput for cases where the value of an input is mapping.
    """
    def __init__(self, parent):
        super().__init__(parent.node, parent.description)
        self.parent = parent

    def __getitem__(self, key: int) -> 'SubInput':
        """
        Retrieve an item (a SubInput) from this NamedSubInput.

        :param key: the key of the requested item
        :return: The :py:class:`SubInput <fastr.planning.inputoutput.SubInput>`
                 corresponding with the key will be returned.
        :raises FastrTypeError: if key is not of a valid type
        :raises FastrKeyError: if the key is not found
        """
        if not isinstance(key, int):
            raise exceptions.FastrTypeError('NamedSubInput indices must a int'
                                            ' not {}'.format(type(key).__name__))

        if key not in self.source:
            self.source[key] = SubInput(self)

        return self.source[key]

    def __str__(self):
        """
        Get a string version for the NamedSubInput

        :return: the string version
        :rtype: str
        """
        return f'<NamedSubInput: {self.fullid})>'

    @property
    def fullid(self):
        """
        The full defining ID for the SubInput
        """
        return '{}/{}'.format(self.parent.fullid, self.parent.index(self))

    @property
    def constant_id(self) -> str:
        """
        The id for a constant node that is attached to this input.
        """
        return f'{self.parent.constant_id}__{self.item_index}'

    @property
    def item_index(self):
        return self.parent.index(self)


class SubInput(BaseInput):
    """
    This class is used by :py:class:`Input <fastr.planning.inputoutput.Input>` to
    allow for multiple links to an :py:class:`Input <fastr.planning.inputoutput.Input>`.
    The SubInput class can hold only a single Link to a (Sub)Output, but behaves
    very similar to an :py:class:`Input <fastr.planning.inputoutput.Input>` otherwise.
    """

    def __init__(self, input_):
        """
        Instantiate an SubInput.

        :param input_: the parent of this SubInput.
        :type input_: :py:class:`Input <fastr.planning.inputoutput.Input>`
        :return: the created SubInput
        """
        self._source = None

        if not isinstance(input_, Input):
            raise exceptions.FastrTypeError('First argument for a SubInput constructor should be an Input')

        self.parent = input_
        super(SubInput, self).__init__(self.node, self.description)

        self.datatype = input_.datatype
        if self.parent.valid:
            self.update()

    def __getitem__(self, key):
        """
        Retrieve an item from this SubInput.

        :param key: the index of the requested item
        :type key: int
        :return: the corresponding :py:class:`SubInput <fastr.planning.inputoutput.SubInput>`
        :rtype: :py:class:`SubInput <fastr.planning.inputoutput.SubInput>`
        :raises FastrTypeError: if key is not of a valid type

        .. note:: As a SubInput has only one SubInput, only requesting int key
                  0 or -1 is allowed, and it will return self
        """

        if not isinstance(key, int):
            raise exceptions.FastrTypeError('SubInput indices must be an int, not {}'.format(type(key).__name__))

        if not -1 <= key < 1:
            raise exceptions.FastrIndexError('SubInput index out of range (key: {})'.format(key))

        return self

    def __eq__(self, other):
        """Compare two SubInput instances with each other. This function ignores
        the parent, node, source and update status, but tests rest of the dict
        for equality.

        :param other: the other instances to compare to
        :type other: SubInput
        :returns: True if equal, False otherwise
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        dict_self = dict(vars(self))
        del dict_self['_node']
        del dict_self['parent']
        del dict_self['_source']
        del dict_self['_status']

        dict_other = dict(vars(other))
        del dict_other['_node']
        del dict_other['parent']
        del dict_other['_source']
        del dict_other['_status']

        return dicteq(dict_self, dict_other)

    def __getstate__(self):
        """
        Retrieve the state of the SubInput

        :return: the state of the object
        :rtype dict:
        """
        state = super(SubInput, self).__getstate__()
        return state

    def __setstate__(self, state):
        """
        Set the state of the SubInput by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(SubInput, self).__setstate__(state)

        if not hasattr(self, '_source'):
            self._source = None

    def __str__(self):
        """
        Get a string version for the SubInput

        :return: the string version
        :rtype: str
        """
        return f'<SubInput: {self.fullid}'

    def cardinality(self, key=None, job_data=None):
        """
        Get the cardinality for this SubInput. The cardinality for a SubInputs
        is defined by the incoming link.

        :param key: key for a specific sample, can be sample index or id
        :type key: :py:class:`SampleIndex <fastr.core.sampleidlist.SampleIndex>` or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        """
        if self.source is not None:
            return self.source[0].cardinality(index=key)
        else:
            return 0

    @property
    def description(self):
        return self.parent.description

    @property
    def dimensions(self):
        """
        List of dimension for this SubInput
        """
        return self.source[0].dimensions

    @property
    def fullid(self):
        """
        The full defining ID for the SubInput
        """
        return '{}/{}'.format(self.parent.fullid, self.parent.index(self))

    @property
    def constant_id(self) -> str:
        """
        The id for a constant node that is attached to this input.
        """
        return f'{self.parent.constant_id}__{self.item_index}'

    @property
    def item_index(self):
        index = self.parent.index(self)
        return index

    @property
    def input_group(self):
        """
        The id of the :py:class:`InputGroup <fastr.planning.node.InputGroup>` this
        SubInputs parent belongs to.
        """
        return self.parent.input_group

    @property
    def node(self):
        """
        The Node to which this SubInputs parent belongs
        """
        return self.parent.node

    @property
    def source_output(self):
        """
        The :py:class:`Output <fastr.planning.inputoutput.Output>`
        linked to this SubInput
        """
        if self.source is not None and len(self.source) > 0:
            return self.source[0].source
        else:
            return None

    @property
    def source(self):
        """
        A list with the source :py:class:`Link <fastr.planning.link.Link>`.
        The list is to be compatible with :py:class:`Input <fastr.planning.inputoutput.Input>`
        """
        if self._source is None:
            self.parent.remove(self)
            return []

        return [self._source]

    @source.setter
    def source(self, value):
        """
        Set new source, make sure previous link to source is released
        """
        if value is self._source:
            return

        if self._source is not None:
            self._source.destroy()

        if value is None:
            self.parent.remove(self)

        self._source = value

    def get_sourced_nodes(self):
        """
        Get a list of all :py:class:`Nodes <fastr.planning.node.Node>` connected as sources to this SubInput

        :return: list of all connected :py:class:`Nodes <fastr.planning.node.Node>`
        :rtype: list
        """
        return [x.source.node for x in self.source]

    def get_sourced_outputs(self):
        """
        Get a list of all :py:class:`Outputs <fastr.planning.inputoutput.Output>` connected as sources to this SubInput

        :return: list of all connected :py:class:`Outputs <fastr.planning.inputoutput.Output>`
        :rtype: list
        """
        return [x.source for x in self.source]

    def remove(self, value):
        """
        Remove a SubInput from parent Input.

        :param value: the :py:class:`SubInput <fastr.planning.inputoutput.SubInput>`
                      to removed from this Input
        :type value: :py:class:`SubInput <fastr.planning.inputoutput.SubInput>`
        """
        # Pass on to the parent Input
        self.parent.remove(value)

    def _update(self, key, forward=True, backward=False):
        """Update the validity of the SubInput and propagate the update downstream.
        A SubInput is valid if:

        * the source Link is set and valid (see :py:meth:`Link.update <fastr.planning.link.Link.update>`)

        """
        # log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.fullid))
        valid = True
        messages = []
        if len(self.source) == 0:
            self.parent.remove(self)
            valid = False
            messages.append('No source in this SubInput, removing!')
        elif not self.source[0].valid:
            valid = False
            messages.append('SubInput source ({}) is not valid'.format(self.source[0].id))
            messages.extend(self.source[0].messages)

        self._status['valid'] = valid
        self._status['messages'] = messages

        # Update downstream
        self.parent.update(key, forward, backward)

    def iteritems(self):
        """
        Iterate over the :py:class:`SampleItems <fastr.core.sampleidlist.SampleItem>`
        that are in the SubInput.

        :return: iterator yielding :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>` objects
        """
        for item in self.source.items():
            yield item

    def itersubinputs(self):
        """Iterate over SubInputs (for a SubInput it will yield self and stop iterating after that)

        :return: iterator yielding  :py:class:`SubInput <fastr.planning.inputoutput.SubInput>`

        example:

        .. code-block:: python

          >>> for subinput in input_a.itersubinputs():
                  print subinput

        """
        yield self


class MacroInput(Input):
    @property
    def input_group(self):
        return self._input_group

    @input_group.setter
    def input_group(self, value):
        raise exceptions.FastrNotImplementedError("Input groups are not settable for MacroNodes"
                                                  " (all inputs have to be in the default group)")


class BaseOutput(BaseInputOutput):
    """
    Base class for all outputs.
    """
    description_type = OutputSpec

    def __init__(self, node, description):
        """Instantiate a BaseOutput

        :param node: the parent node the output belongs to.
        :param description: the :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
               describing the output.
        :return: created BaseOutput
        :raises FastrTypeError: if description is not of class
                                :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
        :raises FastrDataTypeNotAvailableError: if the DataType requested cannot be found in the ``types``
        """
        if not isinstance(description, self.description_type):
            log.error('Description has type "{}" (must be ParameterDescription)'.format(type(description).__name__))
            raise exceptions.FastrTypeError('An output must be constructed based on an '
                                            'object of a class derived from Node and an '
                                            'object of class OutputSpec')
        super().__init__(node, description)

    @property
    def blocking(self):
        """
        Flag indicating that this Output will cause blocking in the execution
        """
        return not self.cardinality_spec.predefined

    @property
    def automatic(self):
        """
        Flag indicating that the Output is generated automatically
        without being specified on the command line
        """
        return self._description.automatic


class Output(BaseOutput):
    """
    Class representing an output of a node. It holds the output values of
    the tool ran. Output fields can be connected to inputs of other nodes.
    """

    def __init__(self, node, description):
        """Instantiate an Output

        :param node: the parent node the output belongs to.
        :param description: the :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
               describing the output.
        :return: created Output
        :raises FastrTypeError: if description is not of class
                                :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
        :raises FastrDataTypeNotAvailableError: if the DataType requested cannot be found in the ``types``
        """
        self._suboutputlist = {}
        self._samples = None
        super(Output, self).__init__(node, description)
        self._listeners = []
        self._preferred_types = []

    def __str__(self):
        """
        Get a string version for the Output

        :return: the string version
        :rtype: str
        """
        return '<Output: {}>'.format(self.fullid)

    def __eq__(self, other):
        """
        Compare two Output instances with each other. This function ignores
        the parent node, listeners and update status, but tests rest of the
        dict for equality.

        :param other: the other instances to compare to
        :type other: fastr.planning.inputoutput.Output
        :returns: True if equal, False otherwise
        :rtype: bool
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        dict_self = dict(vars(self))
        del dict_self['_node']
        del dict_self['_listeners']
        del dict_self['_status']

        dict_other = dict(vars(other))
        del dict_other['_node']
        del dict_other['_listeners']
        del dict_other['_status']

        return dicteq(dict_self, dict_other)

    def __getitem__(self, key: Union[int, slice]) -> 'SubOutput':
        """
        Retrieve an item from this Output. The returned value depends on what type of key used:

        * Retrieving data using index tuple: [index_tuple]
        * Retrieving data sample_id str: [SampleId]
        * Retrieving a list of data using SampleId list: [sample_id1, ..., sample_idN]
        * Retrieving a :py:class:`SubOutput <fastr.planning.inputoutput.SubOutput>` using an int or slice: [n] or [n:m]

        :param key: the key of the requested suboutput, can be a numberor slice
        :return: the :py:class:`SubOutput <fastr.planning.inputoutput.SubOutput>`
                 for the corresponding index
        :raises FastrTypeError: if key is not of a valid type
        """

        if isinstance(key, (int, slice)):
            return self._get_suboutput(key)
        else:
            raise exceptions.FastrTypeError(
                'Index of SubOutput should be int/slice, found {}'.format(type(key).__name__)
            )

    def __getstate__(self):
        """
        Retrieve the state of the Output

        :return: the state of the object
        :rtype dict:
        """
        state = super(Output, self).__getstate__()

        # Add specific fields to the state
        state['suboutputs'] = [x.__getstate__() for x in self._suboutputlist.values()]
        if self._preferred_types is not None:
            state['preferred_types'] = [x.id for x in self._preferred_types]
        else:
            state['preferred_types'] = None

        return state

    def __setstate__(self, state):
        """
        Set the state of the Output by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        super(Output, self).__setstate__(state)

        if state['preferred_types'] is not None:
            self._preferred_types = [types[x] for x in state['preferred_types']]
        else:
            self._preferred_types = None

        suboutputlist = []
        for substate in state['suboutputs']:
            suboutput = SubOutput(self, slice(None))
            suboutput.__setstate__(substate)
            suboutputlist.append((suboutput.indexrep, suboutput))

        # Re-create the dict from the array
        self._suboutputlist = dict(suboutputlist)
        self._listeners = []

    def _cast_to_storetype(self, value):
        """
        Cast a given value to a DataType that matches this Outputs datatype.

        :param value: value to cast
        :return: cast value
        :rtype: DataType matching self.datatype
        """
        if isinstance(value, self.datatype):
            return value

        log.info('CAST VALUE: [{}] {!r} / {}'.format(type(value).__name__,
                                                           value,
                                                           value))

        storetype = types.match_types(self.datatype, type(value))

        if storetype is None:
            storetype = types.match_types(self.datatype)

        if not isinstance(value, storetype):
            if isinstance(value, DataType):
                log.warning('Changing value type from {} to {}'.format(type(value), storetype))
            value = storetype(str(value))

        return value

    def _get_suboutput(self, key):
        """
        Get a suboutput based on the key

        :param int, slice key: The key of the suboutput
        :return: the suboutput
        """
        # Get a string representation of the key
        if isinstance(key, slice):
            keystr = '{}:{}'.format(key.start, key.stop)
            keystr = keystr.replace('None', '')

            if key.step is not None and key.step != 1:
                keystr = '{}:{}'.format(keystr, key.step)
        else:
            keystr = str(key)

        if keystr in self._suboutputlist:
            # Re-use the same SubOutput
            subout = self._suboutputlist[keystr]
        else:
            # Create the desired SubOutput object
            subout = SubOutput(self, key)
            self._suboutputlist[keystr] = subout

        return subout

    def cardinality(self):
        """
        Cardinality of this Output, may depend on the inputs of the parent Node.

        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        :raises FastrCardinalityError: if cardinality references an invalid :py:class:`Input <fastr.planning.inputoutput.Input>`
        :raises FastrTypeError: if the referenced cardinality values type cannot be case to int
        :raises FastrValueError: if the referenced cardinality value cannot be case to int
        """
        return self.cardinality_spec.calculate_planning_cardinality()

    @property
    def datatype(self):
        """
        The datatype of this Output
        """
        return self._datatype

    @datatype.setter
    def datatype(self, value):
        # This does not differ, as it is a property
        # pylint: disable=arguments-differ
        self._datatype = value

    @property
    def dimensions(self):
        """
        The list of the dimensions in this Output. This will be a tuple of Dimension.
        """
        return self.node.dimensions

    @property
    def fullid(self):
        """
        The full defining ID for the Output
        """
        if self.node is not None:
            return '{}/outputs/{}'.format(self.node.fullid, self.id)
        else:
            return 'fastr://ORPHANED/outputs/{}'.format(self.id)

    @property
    def listeners(self):
        """
        The list of :py:class:`Links <fastr.planning.link.Link>` connected to this Output.
        """
        return self._listeners

    @property
    def preferred_types(self):
        """
        The list of preferred :py:class:`DataTypes <fastr.plugins.managers.datatypemanager.DataType>`
        for this Output.
        """
        if self._preferred_types is not None and len(self._preferred_types) > 0:
            return self._preferred_types
        elif self.node.parent is not None and self.node.parent.preferred_types is not None and len(self.node.parent.preferred_types) > 0:
            return self.node.parent.preferred_types
        else:
            return types.preferred_types

    @preferred_types.setter
    def preferred_types(self, value):
        """
        The list of preferred :py:class:`DataTypes <fastr.plugins.managers.datatypemanager.DataType>`
        for this Output. (setter)
        """
        if isinstance(value, type) and issubclass(value, DataType):
            self._preferred_types = [value]
        elif isinstance(value, list) and all([isinstance(x, type) and issubclass(x, DataType) for x in value]):
            self._preferred_types = value
        else:
            log.warning('Invalid definition of preferred DataTypes, must be a DataType or list of DataTypes! Ignoring!')

    @property
    def valid(self):
        """
        Check if the output is valid, i.e. has a valid cardinality
        """
        return self.check_cardinality()

    @property
    def resulting_datatype(self):
        """
        The :py:class:`DataType <fastr.plugins.managers.datatypemanager.DataType>` that
        will the results of this Output will have.
        """
        requested_types = [l.target.datatype for l in self.listeners if l.target is not None]
        requested_types.append(self.datatype)

        if self.preferred_types is not None and len(self.preferred_types) > 0:
            return types.match_types(requested_types,
                                        preferred=self.preferred_types)
        else:
            return types.match_types(requested_types)

    def _update(self, key, forward=True, backward=False):
        """Update the status and validity of the Output and propagate the update the NodeRun.
        An Output is valid if:

        * the parent NodeRun is valid (see :py:meth:`NodeRun.update <fastr.planning.node.NodeRun.update>`)
        """
        # log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.fullid))

        self.node.update(key, forward, backward)

        if self.node.valid:
            self._status['valid'] = True
        else:
            self._status['valid'] = False
            self._status['messages'] = ['Parent NodeRun is not valid']


class SubOutput(Output):
    """
    The SubOutput is an Output that represents a slice of another Output.
    """

    def __init__(self, output, index):
        """Instantiate a SubOutput

        :param output: the parent output the suboutput slices.
        :param index: the way to slice the parent output
        :type index: int or slice
        :return: created SubOutput
        :raises FastrTypeError: if the output argument is not an instance of :py:class:`Output <fastr.planning.inputoutput.Output>`
        :raises FastrTypeError: if the index argument is not an ``int`` or ``slice``
        """
        if not isinstance(output, Output):
            raise exceptions.FastrTypeError('Second argument for a SubOutput init should be an Output')

        if not isinstance(index, (int, slice)):
            raise exceptions.FastrTypeError('SubOutput index should be an integer or a slice, found ({}, type {})'.format(index, type(index).__name__))

        super(SubOutput, self).__init__(output.node, output.description)
        self.parent = output
        self.index = index

    def __str__(self):
        """
        Get a string version for the SubOutput

        :return: the string version
        :rtype: str
        """
        return '<SubOutput {}>'.format(self.fullid)

    def __getstate__(self):
        """
        Retrieve the state of the SubOutput

        :return: the state of the object
        :rtype dict:
        """
        state = super(SubOutput, self).__getstate__()
        state['index'] = self.indexrep
        return state

    def __setstate__(self, state):
        """
        Set the state of the SubOutput by the given state.

        :param dict state: The state to populate the object with
        :return: None
        """
        if isinstance(state['index'], str):
            index = [int(x) if len(x) > 0 else None for x in state['index'].split(':')]
            state['index'] = slice(*index)

        state['_preferred_types'] = []
        super(SubOutput, self).__setstate__(state)
        self._preferred_types = None

    def __eq__(self, other):
        """Compare two SubOutput instances with each other. This function ignores
        the parent, node and update status, but tests rest of the dict for equality.
        equality

        :param other: the other instances to compare to
        :type other: SubOutput
        :returns: True if equal, False otherwise
        :rtype: bool
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        dict_self = dict(vars(self))
        del dict_self['_node']
        del dict_self['parent']
        del dict_self['_status']

        dict_other = dict(vars(other))
        del dict_other['_node']
        del dict_other['parent']
        del dict_other['_status']

        return dicteq(dict_self, dict_other)

    def __len__(self):
        """Return the length of the Output.

        .. note::

            In a SubOutput this is always 1.
        """
        return 1

    @property
    def indexrep(self):
        """
        Simple representation of the index.
        """
        if isinstance(self.index, slice):
            index = '{}:{}'.format(self.index.start, self.index.stop)
            index = index.replace('None', '')

            if self.index.step is not None and self.index.step != 1:
                index = '{}:{}'.format(index, self.index.step)
        else:
            index = self.index

        return index

    def cardinality(self):
        """
        Cardinality of this SubOutput depends on the parent Output and ``self.index``

        :param key: key for a specific sample, can be sample index or id
        :type key: tuple of int or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        :raises FastrCardinalityError: if cardinality references an invalid :py:class:`Input <fastr.planning.inputoutput.Input>`
        :raises FastrTypeError: if the referenced cardinality values type cannot be case to int
        :raises FastrValueError: if the referenced cardinality value cannot be case to int
        """
        parent_cardinality = self.parent.cardinality()

        if parent_cardinality is not None:
            if isinstance(parent_cardinality, int):
                if isinstance(self.index, int):
                    if parent_cardinality >= 1:
                        return 1
                    else:
                        return 0
                else:
                    # Calculate the slice effect on a list of length parent cardinality
                    ind_range = self.index.indices(parent_cardinality)
                    return (ind_range[1] - ind_range[0]) // ind_range[2]
            else:
                return parent_cardinality
        else:
            return None

    @property
    def datatype(self):
        """
        The datatype of this SubOutput
        """
        return self.parent.datatype

    @property
    def fullid(self):
        """
        The full defining ID for the SubOutput
        """
        return '{}/{}'.format(self.parent.fullid, self.indexrep)

    @property
    def listeners(self):
        """
        The list of :py:class:`Links <fastr.planning.link.Link>` connected to this Output.
        """
        return self.parent.listeners

    @property
    def node(self):
        """
        The NodeRun to which this SubOutput belongs
        """
        return self.parent.node

    @property
    def preferred_types(self):
        """
        The list of preferred :py:class:`DataTypes <fastr.plugins.managers.datatypemanager.DataType>`
        for this SubOutput.
        """
        return self.parent.preferred_types

    @preferred_types.setter
    def preferred_types(self, value):
        # We need to key for the signature in subclasses, shut pylint up
        # pylint: disable=unused-argument,no-self-use,arguments-differ
        raise exceptions.FastrNotImplementedError('Cannot set DataType of SubOutput, use the parent Output instead')

    @property
    def samples(self):
        """
        The :py:class:`SampleCollection <fastr.core.sampleidlist.SampleCollection>`
        for this SubOutput
        """
        return self.parent.samples

    @property
    def resulting_datatype(self):
        """
        The :py:class:`DataType <fastr.plugins.managers.datatypemanager.DataType>` that
        will the results of this SubOutput will have.
        """
        return self.parent.resulting_datatype

    def _update(self, key, forward=True, backward=False):
        """Update the status and validity of the SubOutput and propagate the update downstream.
        An SubOutput is valid if:

        * the parent NodeRun is valid (see :py:meth:`NodeRun.update <fastr.planning.node.NodeRun.update>`)

        """
        # log.debug('Update {} passing {} {}'.format(key, type(self).__name__, self.fullid))
        self.parent.update(key, forward, backward)

        if self.node.valid:
            self._status['valid'] = True
        else:
            self._status['valid'] = False
            self._status['messages'] = ['Parent NodeRun is not valid']


class AdvancedFlowOutput(Output):
    """
    Output for nodes that have an advanced flow. This means that the output
    sample id and index is not the same as the input sample id and index.
    The AdvancedFlowOutput has one extra dimensions that is created by the
    Node.
    """
    @property
    def dimensions(self):
        parent_dimensions = super(AdvancedFlowOutput, self).dimensions

        return tuple(Dimension('{}_{}'.format(d.name, self.id), d.size) for d in parent_dimensions[:-1]) + (parent_dimensions[-1],)


class MacroOutput(Output):
    @property
    def dimensions(self):
        return self.node.get_output_info(self)


class SourceOutput(Output):
    """
    Output for a SourceNodeRun, this type of Output determines the cardinality in
    a different way than a normal NodeRun.
    """
    def __init__(self, node, description):
        """Instantiate a FlowOutput

        :param node: the parent node the output belongs to.
        :param description: the :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
               describing the output.
        :return: created FlowOutput
        :raises FastrTypeError: if description is not of class
                                :py:class:`ParameterDescription <fastr.core.tool.ParameterDescription>`
        :raises FastrDataTypeNotAvailableError: if the DataType requested cannot be found in the ``types``
        """
        super(SourceOutput, self).__init__(node, description)

        self._linearized = None

    @property
    def linearized(self):
        """
        A linearized version of the sample data, this is lazily cached
        linearized version of the underlying SampleCollection.
        """
        if self._linearized is None:
            self._linearized = tuple(self.samples[x] for x in self.samples)

        return self._linearized

    def cardinality(self):
        """
        Cardinality of this SourceOutput, may depend on the inputs of the parent NodeRun.

        :param key: key for a specific sample, can be sample index or id
        :type key: tuple of int or :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :return: the cardinality
        :rtype: int, sympy.Symbol, or None
        """
        return sympy.symbols('N_{}'.format(self.node.id.replace(' ', '_')))
