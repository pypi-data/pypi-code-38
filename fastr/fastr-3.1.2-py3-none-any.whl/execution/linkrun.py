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
The link module contain the Link class. This class represents the links
in a network. These links lead from an output (BaseOutput) to an input
(BaseInput) and indicate the desired data flow. Links are smart objects, in the
sense that when you set their start or end point, they register themselves with
the Input and Output. They do all the book keeping, so as long as you only set
the source and target of the Link, the link should be valid.

.. warning::
   Don't mess with the Link, Input and Output internals from other places.
   There will be a huge chances of breaking the network functionality!
"""

import itertools
import weakref

import sympy

from .. import exceptions
from ..abc.serializable import Serializable
from ..abc.updateable import Updateable
from ..core.dimension import Dimension
from ..core.samples import SampleId, SampleIndex, SampleItem
from ..datatypes import types
from ..helpers import log
from ..planning.inputoutput import BaseInput
from ..planning.inputoutput import BaseOutput
from ..planning.inputoutput import Input

__all__ = ['LinkRun']


class LinkRun(Updateable, Serializable):
    """
    Class for linking outputs (:py:class:`BaseOutput <fastr.planning.inputoutput.BaseOutput>`) to
    inputs (:py:class:`BaseInput <fastr.planning.inputoutput.BaseOutput>`)

    Examples:

    .. code-block:: python

       >>> import fastr
       >>> network = fastr.Network()
       >>> link1 = network.create_link( n1.ouputs['out1'], n2.inputs['in2'] )

       link2 = Link()
       link2.source = n1.ouputs['out1']
       link2.target = n2.inputs['in2']
    """

    __dataschemafile__ = 'Link.schema.json'

    def __init__(self, link, parent=None):
        """
        Create a new Link in a Network.

        :param link: the base link
        :type link: :py:class:`Link <fastr.planning.link.Link>`
        :param parent: the parent network, if None is given the fastr.current_network is assumed to be the parent
        :type parent: :py:class:`Network <fastr.planning.network.Network>` or None
        :return: newly created LinkRun
        :raises FastrValueError: if parent is not given and `fastr.current_network` is not set
        :raises FastrValueError: if the source output is not in the same network as the Link
        :raises FastrValueError: if the target input is not in the same network as the Link
        """
        super(LinkRun, self).__init__()

        self.id = link.id
        self._source = link.source
        self._target = link.target

        self._collapse = link.collapse
        self._expand = link.expand

        self.__updating__ = False

        if parent is not None:
            self._parent = parent
        else:
            message = 'parent argument is None, need a parent Network to function!'
            raise exceptions.FastrValueError(message)

        self.__updating__ = True
        self.update()

    def __repr__(self):
        """
        Get a string representation for the Link

        :return: the string representation
        :rtype: str
        """
        if self._source is not None:
            source_str = self.source.fullid
        else:
            source_str = 'None'

        if self.target is not None:
            target_str = self.target.fullid
        else:
            target_str = 'None'

        if len(self._collapse) > 0:
            collapse_str = '\nconverging: {}'.format(', '.join([str(x) for x in self._collapse]))
        else:
            collapse_str = ''

        if self.parent is not None:
            parent_str = self.parent.id
        else:
            parent_str = 'None'

        return 'LinkRun {} (network: {}):\n   {} ==> {}{}'.format(self.id, parent_str, source_str, target_str, collapse_str)

    def __getitem__(self, index):
        """
        Get a an item for this Link. The item will be retrieved from the connected output, but a diverging or converging
        flow can change the number of samples/cardinality.

        :param index: index of the item to retrieve
        :type index: SampleIndex
        :return: the requested item
        :rtype: :py:class:`SampleItem <fastr.core.sampleidlist.SampleItem>`
        :raises FastrIndexError: if the index length does not match the number dimensions
                                  in the source data (after collapsing/expanding)
        """
        sourcesize = self.source.size
        sourceindex = []
        counter = 0

        # Check if index and size have the same number of dimensions
        if self.expand and len(self.size) != len(index):
            raise exceptions.FastrIndexError('The index does not match objects dimensions! (size: {}, index: {}, expand: {}'.format(self.size, index, self.expand))

        # Mix in the converging dimensions
        for dimnr in range(len(sourcesize)):
            if dimnr in self.collapse_indexes or dimnr - len(sourcesize) in self.collapse_indexes:
                sourceindex.append(slice(None))
            else:
                sourceindex.append(index[counter])
                counter += 1
        sourceindex = SampleIndex(sourceindex)

        # Check if the entire index was used
        if (not self.expand and counter != len(index) and index != (0,)) \
                or (self.expand and counter != (len(index) - 1)):
            raise exceptions.FastrIndexError('The index was not used entirely!')

        source_sample_data = self.source[sourceindex]

        if source_sample_data == ():
            if all(isinstance(x, slice) or 0 <= x < s for x, s in zip(sourceindex, self.source.size)):
                raise exceptions.FastrIndexNonexistent('Cannot find index {} (probably due to sparsity)'.format(sourceindex))
            else:
                raise exceptions.FastrIndexError('Cannot find index {}, out of bounds!')

        if isinstance(source_sample_data, SampleItem):
            source_jobs = source_sample_data.jobs
            source_failed_annotations = source_sample_data.failed_annotations
        else:
            source_jobs = set.union(*[x.jobs for x in source_sample_data])
            source_failed_annotations = set.union(*[x.failed_annotations for x in source_sample_data])

        # Get the resulting sample_id
        if self.collapse != ():
            sample_id = source_sample_data[0].id
            sample_id = [s for i, s in enumerate(sample_id) if
                         i not in self.collapse_indexes and i - len(sample_id) not in self.collapse_indexes]
            sample_id = SampleId(sample_id) if len(sample_id) > 0 else SampleId('all')
        else:
            sample_id = source_sample_data.id

        # Return the item in a similar way as Link.iteritems()
        if self.expand:
            # TODO: double check the functioning of this piece of code
            div_index = index[counter]
            log.debug('Divering index {} from data {}'.format(div_index, source_sample_data))
            div_sample_id = sample_id + str(div_index)
            if isinstance(source_sample_data, SampleItem):
                source_sample_data = source_sample_data,  # Also create tuple for simple sample (non-collapsing)

            # See what the cardinality of the sources is
            source_data_sizes = set(len(x.data.sequence_part()) for x in source_sample_data)

            # Make sure sample exists, no sample if none of the parts have the cardinality
            if all(x <= div_index for x in source_data_sizes):
                # There is no sample (cardinality will be 0)
                raise exceptions.FastrIndexNonexistent

            # Select data from the parts that have enough cardinality
            div_sample_data = []
            for item in source_sample_data:
                item_data = item.data.sequence_part()
                if len(item_data) > div_index:
                    div_sample_data.append(item_data[div_index])

            # Wrap in the complete form
            div_sample_data = {0: tuple(div_sample_data)}

            log.debug('Selected data for diverging: {}'.format(div_sample_data))
            return SampleItem(index, div_sample_id, div_sample_data, source_jobs, source_failed_annotations)
        else:
            if isinstance(source_sample_data, SampleItem):
                sample_data = source_sample_data
            else:
                sample_data = SampleItem.combine(source_sample_data)

            return SampleItem(index, sample_id, sample_data.data, source_jobs, source_failed_annotations)

    def __eq__(self, other):
        """
        Test for equality between two Links

        :param LinkRun other: object to test against
        :return: True for equality, False otherwise
        :rtype: bool
        """
        if not isinstance(other, LinkRun):
            return NotImplemented

        self_state = self.__getstate__()
        other_state = other.__getstate__()

        return self_state == other_state

    def __getstate__(self):
        """
        Retrieve the state of the Link

        :return: the state of the object
        :rtype dict:
        """
        state = super(LinkRun, self).__getstate__()

        state['id'] = self.id
        state['source'] = self._source.fullid if self._source is not None else None
        state['target'] = self._target.fullid if self._target is not None else None
        state['collapse'] = self._collapse
        state['expand'] = self._expand

        return state

    def __setstate__(self, state):
        """
        Set the state of the Link by the given state.

        :param dict state: The state to populate the object with
        :return: None
        :raises FastrValueError: if the parent network and `fastr.current_network` are not set
        """
        super(LinkRun, self).__setstate__(state)
        self._source = None
        self._target = None

        self.id = state['id']

        self.__updating__ = False
        if 'parent' in state:
            parent = state['parent']
            del state['parent']
        else:
            message = 'Link creation requires a parent Network!'
            raise exceptions.FastrValueError(message)

        self._collapse = tuple(state['collapse'])
        self._expand = state['expand']

        self._parent = None
        if parent is not None:
            self.parent = parent

        self.source = self.parent[state['source']]
        self.target = self.parent[state['target']]
        self.__updating__ = True
        self.update()

    @classmethod
    def createobj(cls, state, network=None):
        """
        Create object function for Link

        :param cls: The class to create
        :param state: The state to use to create the Link
        :param network: the parent Network
        :return: newly created Link
        """
        log.debug('State for createobj LinkList: {}'.format(state))
        if 'parent' not in state and network is not None:
            state['parent'] = network

        return super(LinkRun, cls).createobj(state, network)

    def cardinality(self, index=None):
        """
        Cardinality for a Link is given by source Output and the collapse/expand settings

        :param key: key for a specific sample (can be only a sample index!)
        :type key: SampleIndex
        :return: the cardinality
        :rtype: int, sympy.Symbol
        :raises FastrIndexError: if the index length does not match the number of dimension in the data
        """
        if self.source is not None:
            if index is None:
                if self.expand:
                    cardinality = 1
                else:
                    cardinality = self.source.cardinality()

                if cardinality is None:
                    return sympy.symbols('N_link_{}'.format(self.id.replace(' ', '_')))

                sourcesize = self.source.size

                for dimnr in range(len(sourcesize)):
                    if dimnr in self.collapse_indexes or dimnr - len(sourcesize) in self.collapse_indexes:
                        if sourcesize[dimnr] is None:
                            log.debug('Dimension {} in source size {} is None!'.format(dimnr, sourcesize))
                            return None
                        cardinality = cardinality * sourcesize[dimnr]
            else:
                sourcesize = self.source.size
                sourceindex = []
                counter = 0

                # Check if index and size have the same number of dimensions
                if self.expand and len(self.size) != len(index):
                    raise exceptions.FastrIndexError('The index does not match objects dimensions! (size: {}, index: {}, expand: {}'.format(self.size, index, self.expand))

                if len(self.collapse) > 0:
                    # Mix in the converging dimensions
                    for dimnr in range(len(sourcesize)):
                        if dimnr in self.collapse_indexes or dimnr - len(sourcesize) in self.collapse_indexes:
                            if not isinstance(sourcesize[dimnr], int):
                                log.debug('Link sources are not (yet) defined, encountered {} ({})'.format(sourcesize[dimnr], type(sourcesize[dimnr]).__name__))
                                return sympy.symbols('N_{}'.format(self.fullid.replace(' ', '_')))

                            sourceindex.append(list(range(sourcesize[dimnr])))
                        else:
                            sourceindex.append([index[counter]])
                            counter += 1
                    sourceindices = [SampleIndex(x) for x in itertools.product(*sourceindex)]
                else:
                    sourceindices = [index]

                # Cardinality per sample is 1 after expand, only collapse adds cardinality
                if self.expand:
                    return len(sourceindices)

                # Get cardinality for each sample
                cardinality = [self.source.cardinality(x) for x in sourceindices]
                if all(x is not None for x in cardinality):
                    cardinality = sum(cardinality)
                else:
                    log.debug(('Link source ({}) cardinality has a None, cardinaly list: {},'
                               ' sourceindex: {!r}, in link {}').format(self.source.fullid,
                                                                        cardinality,
                                                                        sourceindices,
                                                                        self))
                    cardinality = sympy.symbols('N_{}'.format(self.id.replace(' ', '_')))
            return cardinality

    @property
    def collapse(self):
        """
        The converging dimensions of this link. Collapsing changes some dimensions
        of sample lists into cardinality, reshaping the data.

        Collapse can be set to a tuple or an int/str, in which case it will be
        automatically wrapped in a tuple. The int will be seen as indices of
        the dimensions to collapse. The str will be seen as the name of the dimensions
        over which to collapse.

        :raises FastrTypeError: if assigning a collapse value of a wrong type
        """
        return self._collapse

    @collapse.setter
    def collapse(self, value):
        """
        Setter function for collapse property
        """
        if isinstance(value, (int, str)):
            value = (value,)
        elif isinstance(value, list):
            value = tuple(value)

        if not isinstance(value, tuple):
            raise exceptions.FastrTypeError('converging dimensions should be an int, str or a tuple/list of int or str')

        # Check if the type is correct
        if all(isinstance(x, (int, str)) for x in value):
            self._collapse = value
        else:
            raise exceptions.FastrTypeError('converging dimensions should be an int, str or a tuple/list of int or str')

        # Update this link to reflect changes throughout the network
        self.update()

    @property
    def expand(self):
        """
        Flag indicating that the link will expand the cardininality into a new
        sample dimension to be created.
        """
        return self._expand

    @expand.setter
    def expand(self, value):
        """
        Setter for expand
        """
        self._expand = value
        self.update()

    @property
    def collapse_indexes(self):
        """
        The converging dimensions of this link as integers. Dimension names are
        replaces with the corresponding int.

        Collapsing changes some dimensions of sample lists into cardinality,
        reshaping the data
        """
        dimnamemap = dict((y, x) for x, y in enumerate(self.source.dimnames))
        result = tuple(x if isinstance(x, int) or x not in dimnamemap else dimnamemap[x] for x in self._collapse)
        if not all(isinstance(x, int) for x in result):
            raise exceptions.FastrValueError('Collapsing dimension point to non-existing dimension name! ({}), available dimnames: {}'.format(result, list(dimnamemap.keys())))

        return result

    @property
    def status(self):
        return self._status

    @property
    def fullid(self):
        """
        The full defining ID for the Input
        """
        return '{}/linklist/{}'.format(self.parent.fullid, self.id)

    @property
    def parent(self):
        """
        The Network to which this Link belongs.
        """
        return self._parent()

    @parent.setter
    def parent(self, value):
        """
        Setter function for parent property
        """
        if self._parent is not None:
            if self._parent() is value:
                return  # Setting to same value doesn't do anything

            raise exceptions.FastrAttributeError('Cannot assign a new parent if there is already a parent assigned')

        self._parent = weakref.ref(value)

    @property
    def dimensions(self):
        """
        The dimensions of the data delivered by the link. This can be different
        from the source dimensions because the link can make data collapse or expand.
        """
        if self.source is not None:
            dimensions = self.source.dimensions
            if dimensions == () or dimensions is None:
                return dimensions

            # Collapse the dimesions requested
            dimensions = tuple(s for i, s in enumerate(dimensions) if
                               i not in self.collapse_indexes and i - len(dimensions) not in self.collapse_indexes)

            if self.expand:
                # Add a new dimension
                log.debug('Link expand changes dimensions from {} to {}'.format(dimensions, dimensions + (self.source.cardinality(),)))
                new_dimension_name = '{}__{}'.format(self.source.node.id, self.source.id)

                if self.source.cardinality() is not None:
                    new_dimension_size = self.source.cardinality()
                else:
                    # There should be data, try to extract from the data
                    cardinalities = set(self.source.samples[sid].cardinality for sid in self.source.samples)

                    if len(cardinalities) == 1:
                        log.debug('Found unique cardinality {}, using that for expanding'.format(cardinalities))
                        new_dimension_size = cardinalities.pop()
                    elif len(cardinalities) == 0:
                        log.debug('Found no cardinality: {}, using a symbol instead'.format(cardinalities))
                        new_dimension_size = sympy.symbols('N_{}_expand'.format(self.id))
                    else:
                        message = 'Found non-unique cardinality, this will cause a varying size after' \
                                  ' expand! (Found {})'.format(cardinalities)
                        message += ' Using largest cardinality {}'.format(max(cardinalities))
                        new_dimension_size = max(cardinalities)
                        log.debug(message)

                dimensions = dimensions + (Dimension(new_dimension_name, new_dimension_size),)

            # All dimensions were collapse, create a new single sample dimension
            if len(dimensions) == 0 and len(self.source.dimensions) != 0:
                return Dimension(self.target.node.id, 1),

            return dimensions
        else:
            # Return a dummy
            return Dimension(self.id, 0),

    @property
    def size(self):
        """
        The size of the data delivered by the link. This can be different
        from the source size because the link can make data collapse or expand.
        """
        if self.source is not None:
            size = self.source.size
            if size == () or size is None:
                return size

            size = tuple(s for i, s in enumerate(size) if
                         i not in self.collapse_indexes and i - len(size) not in self.collapse_indexes)

            if self.expand:
                log.debug('Link expand changes size from {} to {}'.format(size, size + (self.source.cardinality(),)))

                if self.source.cardinality() is not None:
                    size = size + (self.source.cardinality(),)
                else:
                    if self.source.samples is not None:
                        # There should be data, try to extract from the data
                        cardinalities = set(self.source.samples[sid].cardinality for sid in self.source.samples)

                        if len(cardinalities) == 1:
                            log.debug('Found unique cardinality {}, using that for expanding'.format(cardinalities))
                            size = size + (cardinalities.pop(),)
                        elif len(cardinalities) == 0:
                            log.debug('Found no cardinality: {}, using a symbol instead'.format(cardinalities))
                            size = size + (sympy.symbols('N_{}_expand'.format(self.id)),)
                        else:
                            message = 'Found non-unique cardinality, this will cause a varying size after' \
                                      ' expand! (Found {})'.format(cardinalities)
                            message += ' Using largest cardinality {}'.format(max(cardinalities))
                            size = size + (max(cardinalities),)
                            log.debug(message)

                    else:
                        # No data yet (Node has not been prepared)
                        size = size + (sympy.symbols('N_{}_expand'.format(self.id)),)
                        log.debug('Node has not been prepared, new size {}'.format(size))
            if size == ():
                return 1,

            return size
        else:
            return 0,

    @property
    def source(self):
        """
        The source :py:class:`BaseOutput <fastr.planning.inputoutput.BaseOutput>`
        of the Link. Setting the source will automatically
        register the Link with the source BaseOutput. Updating source will also
        make sure the Link is unregistered with the previous source.

        :raises FastrTypeError: if assigning a non :py:class:`BaseOutput <fastr.planning.inputoutput.BaseOutput>`
        """
        if hasattr(self, '_source'):
            return self._source
        else:
            return None

    @source.setter
    def source(self, value):
        """
        Setter function for source property
        """
        if isinstance(value, BaseOutput):
            # Add to network of new value if no network is known
            if self.parent is None and value.node.parent is not None:
                value.node.parent.add_link(self)

            if self.parent is not value.node.parent:
                raise exceptions.FastrNetworkMismatchError('Network mismatch! ({} vs {})'.format(self.parent.id,
                                                                                                 value.node.parent.id))

            # Remove self from old source
            if (hasattr(self, '_source') and isinstance(self._source, BaseOutput)
                    and any(x is self for x in self._source.listeners)):
                self._source.listeners.remove(self)

            # Test for matching datatypes
            if (hasattr(self, '_target') and isinstance(self.target, BaseInput)
                    and types.match_types(self.target.datatype,
                                             value.datatype,
                                             preffered=value.preferred_types) is None):
                self._source = None
                log.warning('Non-matching datatypes {} and {}! Abort linking!'.format(
                    self.target.datatype,
                    value.datatype))
                return

            # Add self to new source
            if not any(x is self for x in value.listeners):
                value.listeners.append(self)

            self._source = value

            # Update this link to reflect changes throughout the network
            self.update()
        elif value is None:
            # Remove from listeners if present and set to None
            self.destroy()
        else:
            raise exceptions.FastrTypeError('source is not of class BaseOutput')

    @source.deleter
    def source(self):
        """
        Deleter function for source property
        """
        if self in self._source.listeners:
            self._source.listeners.remove(self)

        del self._source

    @property
    def target(self):
        """The target :py:class:`BaseInput <fastr.planning.inputoutput.BaseInput>`
        of the Link. Setting the target will automatically
        register the Link with the target BaseInput. Updating target will also
        make sure the Link is unregistered with the previous target.

        :raises FastrTypeError: if assigning a non :py:class:`BaseInput <fastr.planning.inputoutput.BaseInput>`
        """
        if hasattr(self, '_target'):
            return self._target
        else:
            return None

    @target.setter
    def target(self, value):
        """
        Setter function for target property
        """
        if isinstance(value, BaseInput):
            # Add to network of new value if no network is known
            if self.parent is None and value.node.parent is not None:
                value.node.parent.add_link(self)

            if self.parent is not value.node.parent:
                ValueError('Network mismatch!')

            # Remove self from old target
            if (hasattr(self, '_target') and isinstance(self._target, BaseInput)
                    and self is self._target.source):
                self._target.source.remove(self)

            # Test for matching datatypes
            if (hasattr(self, '_source') and isinstance(self._source, BaseOutput)
                    and types.match_types(self._source.datatype,
                                             value.datatype,
                                             preferred=self.source.preferred_types) is None):
                self._target = None
                log.warning('Cannot match datatypes {} and {} or not preferred datatype is set! Abort linking {} to {}!'.format(
                    self._source.datatype,
                    value.datatype,
                    self.source.fullid,
                    value.fullid
                ))

            # Add self to new target
            value.source = self

            # Always have link SubInput as link target
            if isinstance(value, Input):
                value = value._source[0]

            self._target = value

            # Update this link to reflect changes throughout the network
            self.update()
        elif value is None:
            self.destroy()
        else:
            raise exceptions.FastrTypeError('target is not of class BaseInput')

    @target.deleter
    def target(self):
        """
        Deleter function for target property
        """
        if self is self._target.source:
            self._target.source.remove(self)

        del self._target

    def destroy(self):
        """
        The destroy function of a link removes all default references to a
        link. This means the references in the network, input and output
        connected to this link. If there is no references in other places in
        the code, it will destroy the link (reference count dropping to zero).

        This function is called when a source for an input is set to another
        value and the links becomes disconnected. This makes sure there is no
        dangling links.
        """
        if self.target is not None:
            self._target.remove(self)
            self._target.update()
            self._target = None

        if self.source is not None:
            self._source.listeners.remove(self)
            self._source.update()
            self._source = None

        if self.parent is not None:
            self.parent.remove(self)

    def _update(self, key, forward=True, backward=False):
        """Update the validity of the Link and propagate the update downstream.
        A Link is valid if:

        * Source is set
        * Target is set
        * Source and target datatypes are matching
        * All dimensions to collapse exist in the source size
        """
        messages = []
        valid = True

        # Check if source and target are set
        if self.source is None:
            messages.append('[{}] no source set'.format(self.fullid))
            valid = False

        if self.target is None:
            messages.append('[{}] no target set'.format(self.fullid))
            valid = False

        # Check if source and target datatypes are matching
        preferred_types = self.source.preferred_types if self.source and self.source.preferred_types else None
        if valid and types.match_types(self.source.datatype, self.target.datatype, preferred=preferred_types) is None:
            messages.append('[{}] source and target have non-matching datatypes: source {} and {}'.format(self.id, self.source.datatype.name, self.target.datatype.name))
            valid = False

        # Check if all collapse dimension exist
        if self.source is not None:
            size = self.source.size

            try:
                for convdim in self.collapse_indexes:
                    if convdim < -len(size) or convdim >= len(size):
                        messages.append('[{}] collapse dimension {} invalid index for size {} (sourced output: {})'.format(self.id, convdim, size, self.source.fullid))
                        valid = False
            except exceptions.FastrValueError as exception:
                messages.append(exception.message)
                valid = False

        self._status['valid'] = valid
        self._status['messages'] = messages

        # Propagate update downstream
        if forward and self.target is not None:
            self.target.node.update(key, forward, backward)
