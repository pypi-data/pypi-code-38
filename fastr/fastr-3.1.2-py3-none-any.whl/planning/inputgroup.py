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


import weakref
from collections import OrderedDict

from sympy.core.symbol import Symbol

from ..abc.updateable import UpdateableMeta
from .. import exceptions
from ..core.dimension import HasDimensions, Dimension
from ..core.samples import SampleIndex, SampleItem, SamplePayload
from ..helpers import log
from ..planning.inputoutput import BaseInput


class InputGroup(OrderedDict, HasDimensions, metaclass=UpdateableMeta):
    """
    A class representing a group of inputs. Input groups allow the
    """
    __updatetriggers__ = ['__init__',
                          '__setitem__',
                          '__delitem__',
                          'clear',
                          'pop',
                          'popitem',
                          'setdefault',
                          'update']

    def __init__(self, parent, id_=None):
        """
        Create a new InputGroup representation

        :param parent: the parent node
        :type parent: :py:class:`NodeRun <fastr.planning.node.NodeRun>`
        :param str id_: the id of the input group
        :raises FastrTypeError: if parent is not a NodeRun
        """
        super(InputGroup, self).__init__()
        self._parent = weakref.ref(parent)
        self.id = id_
        self._dimensions = ()
        self._primary = None
        self.__updating__ = True

    def __getitem__(self, key):
        if isinstance(key, SampleIndex):
            index = key

            # Determine which input sample to use for Input
            indexmap = dict(zip(self.dimnames, index))
            data = {}

            nodegroups = self.parent.parent.nodegroups

            # Match dimensions if possible
            lookup = {v: dimname for dimname in self.dimnames for value in nodegroups.values() if dimname in value for v in value}
            lookup.update({x: x for x in self.dimnames})

            for key, value in lookup.items():
                lookup[key] = indexmap[value]

            for id_, input_ in self.items():
                source_index = self.find_source_index(target_size=self.size,
                                                      target_dimnames=self.dimnames,
                                                      source_size=input_.size,
                                                      source_dimnames=input_.dimnames,
                                                      target_index=index)

                # Get data from Input
                if source_index is not None:
                    data[id_] = input_[source_index]
                else:
                    data[id_] = SampleItem(index, '__EMPTY__', [], set())

            # Aggregate data for input group
            sample_id = data[self.primary.id].id
            hold_jobs = set.union(*[val.jobs for val in data.values()])

            return SamplePayload(index, sample_id, data, hold_jobs)
        else:
            return super(InputGroup, self).__getitem__(key)

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        """
        Assign an input to this input group.

        :param str key: id of the input
        :param value: the input to assign
        :type value: :py:class:`Input <fastr.planning.inputoutput.Input>`
        :raises FastrTypeError: if value of valid type
        """
        if not isinstance(value, BaseInput):
            message = 'Cannot assign a non-Input to an InputGroup'
            log.error(message)
            raise exceptions.FastrTypeError(message)

        if self.parent is not None and value.node is not self.parent:
            message = 'Input has a different parent NodeRun than the InputGroup, this is not a valid assignment!'
            log.error(message)
            raise exceptions.FastrParentMismatchError(message)

        super(InputGroup, self).__setitem__(key, value)

    @property
    def fullid(self):
        return '{}/input_groups/{}'.format(self.parent.fullid, self.id)

    @property
    def parent(self):
        """
        The parent node of this InputGroup
        """
        if self._parent is not None:
            return self._parent()
        else:
            return None

    @property
    def dimensions(self):
        """
        The dimensions of this InputGroup
        """
        return self._dimensions

    @property
    def primary(self):
        """
        The primary Input in this InputGroup. The primary Input is the Input
        that defines the size of this InputGroup. In case of ties it will be
        the first in the tool definition.
        """
        return self._primary

    @property
    def empty(self):
        """
        Bool indicating that this InputGroup is empty (has no data connected)
        """
        return self.size is None or len([x for x in self.size if x != 0]) == 0

    def find_source_index(self, target_size, target_dimnames, source_size, source_dimnames, target_index):
        # Determine which input sample to use for Input

        if source_size == target_size:
            source_index = target_index
        elif source_size == (1,):
            source_index = SampleIndex(0)
        elif all(x == 0 for x in source_size):
            source_index = None
        else:
            source_index = self.solve_broadcast(target_size=target_size,
                                                target_dimnames=target_dimnames,
                                                source_size=source_size,
                                                source_dimnames=source_dimnames,
                                                target_index=target_index,
                                                nodegroups=self.parent.parent.nodegroups)

        return source_index

    @staticmethod
    def _get_lookup(target_dimnames, nodegroups):
        lookup = {v: dimname for dimname in target_dimnames for value in nodegroups.values() if dimname in value for v in value}
        lookup.update({x: x for x in target_dimnames})

        return lookup

    @classmethod
    def solve_broadcast(cls, target_size, target_dimnames, source_size, source_dimnames, target_index, nodegroups=None):
        indexmap = dict(zip(target_dimnames, target_index))
        sizemap = dict(zip(target_dimnames, target_size))
        lookup = cls._get_lookup(target_dimnames, nodegroups)

        if all(x in lookup for x in source_dimnames):
            matched_dims = [lookup[x] for x in source_dimnames]
            source_index = SampleIndex(indexmap[x] for x in matched_dims)
            estimated_source_size = tuple(sizemap[x] for x in matched_dims)
        else:
            raise exceptions.FastrSizeMismatchError('Cannot broadcast, not all dimnames can be matched! (source dimnames {}, lookup {}'.format(source_dimnames, lookup))

        if source_size != estimated_source_size:
            raise exceptions.FastrSizeMismatchError('The estimated size after broadcast matching is incorrect! (estimated {}, actual {})'.format(estimated_source_size, source_size))

        return source_index

    @property
    def iterinputvalues(self):
        """
        Iterate over the item in this InputGroup

        :returns: iterator yielding :py:class:`SampleItems <fastr.core.sampeidlist.SampleItem>`
        """
        for index, _, _, _, _ in self.primary.items():
            yield self[index]

    def __updatefunc__(self):
        """
        Update the InputGroup. Triggers when a change is made to the content
        of the InputGroup. Automatically recalculates the size, primary Input
        etc.
        """
        sizes = [x.size for x in self.values()]
        dimnames = [x.dimnames for x in self.values()]

        unique_sizes = set(sizes) - {(0,), (1,), (), None}

        if len(unique_sizes) > 1:
            if not any(all(not isinstance(x, Symbol) for x in size) for size in unique_sizes):
                # All entries in unique sizes are symbols, we cannot really
                # know what will be the size. Assume for now that the first
                # Input with symbolic input will be the primary
                max_dims = max(x.ndims for x in self.values())
                for input_ in self.values():
                    if input_.size in unique_sizes and input_.ndims == max_dims:
                        self._primary = input_
                        self._dimensions = input_.dimensions
                        break

            # Check if we can match via dimnames
            elif all(len(x) == len(set(x)) for x in dimnames):
                longest_dimname, longest_size = max(zip(dimnames, sizes), key=lambda x: len(x[1]))
                longest_dimensions = tuple(Dimension(name, size) for name, size in zip(longest_dimname, longest_size))

                if all(all(x in longest_dimname for x in y) for y in dimnames):
                    self._dimensions = longest_dimensions
                    self._primary = list(self.values())[sizes.index(self.size)]
                else:
                    nodegroups = self.parent.parent.nodegroups
                    lookup = {v: dimname for dimname in longest_dimname for value in nodegroups.values() if dimname in value for v in value}
                    lookup.update({x: x for x in longest_dimname})

                    if all(x in lookup for y in dimnames for x in y):
                        self._dimensions = longest_dimensions
                        self._primary = list(self.values())[sizes.index(self.size)]
                    else:
                        message = '[{}] Not all dimnames ({}) are present in the highest-dimensional input ({})'.format(
                            self.fullid,
                            [x for y in dimnames for x in y],
                            list(lookup.keys()),
                        )
                        log.warning(message)

                        self._dimensions = longest_dimensions
                        self._primary = list(self.values())[sizes.index(self.size)]
            else:
                message = 'One or more inputs have non-unique dimnames ({})'.format(dimnames)
                log.error(message)
                raise exceptions.FastrValueError(message)

        elif len(unique_sizes) == 1:
            self._primary = list(self.values())[sizes.index(unique_sizes.pop())]
            self._dimensions = self._primary.dimensions
        elif (1,) in sizes:
            self._primary = list(self.values())[sizes.index((1,))]
            self._dimensions = self._primary.dimensions
        else:
            self._primary = None
            self._dimensions = ()


