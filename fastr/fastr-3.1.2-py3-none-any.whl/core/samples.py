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
This package holds the classes for working with samples.
"""

from abc import ABCMeta, abstractmethod, abstractproperty
import itertools
from collections import MutableMapping, OrderedDict
from .. import datatypes
from .. import exceptions
from .. import resources

from .dimension import Dimension, HasDimensions


class SampleItemBase(tuple):
    """
    This class represents a sample item, a combination of a SampleIndex,
    SampleID, value and required jobs. The SampleItem based on a named
    tuple and has some extra methods to combine SampleItems easily.
    """

    def __new__(cls, index, id_, data, jobs=None, failed_annotations=None):
        """
        Create a SampleItem. Data should be an OrderedDict of tuples.

        :param index: the sample index
        :type index: tuple, slice
        :param id_: the sample id
        :type id_: :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :param data: the data values
        :type data: SampleValue, Mapping
        :param set jobs: set, tuple or list of jobs on which this SampleItems data depends.
        :param set failed_annotations: set of tuples. The tuple is contructed like follows: (job_id, reason).
        """

        if not isinstance(index, SampleIndex):
            index = SampleIndex(index)

        if not isinstance(id_, SampleId):
            id_ = SampleId(id_)

        if jobs is None:
            jobs = set()

        if not isinstance(jobs, (set, tuple, list)):
            raise exceptions.FastrTypeError(
                "Jobs should be a set, tuple or list of jobs or job ids, found {}".format(type(jobs).__name__)
            )

        jobs = {job if isinstance(job, str) else job.id for job in jobs}

        if failed_annotations is None:
            failed_annotations = set()

        if not isinstance(failed_annotations, set):
            raise exceptions.FastrTypeError(
                "failed_annotations should be a set, found {}".format(type(failed_annotations).__name__)
            )

        return super(SampleItemBase, cls).__new__(cls, [index, id_, data, jobs, failed_annotations])

    def __repr__(self):
        """
        Get a string representation for the SampleItem

        :return: the string representation
        :rtype: str
        """
        return '<{cls} index={s.index}, id={s.id}>'.format(cls=type(self).__name__, s=self)

    def __getnewargs__(self):
        """
        Get new args gives the arguments to use to re-create this object, This
        is used for serialization.
        """
        return tuple(self)

    def __add__(self, other):
        """
        The addition operator combines two SampleItems into a single
        SampleItems. It merges the data and jobs and takes the index
        and id of the left-hand item.

        :param other: The other item to add to this one
        :type other: SampleItem
        :return: the combined SampleItem
        :rtype: SampleItem
        """
        if not isinstance(other, SampleItemBase):
            return NotImplemented

        return type(self)(self.index,
                          self.id,
                          self.data + other.data,
                          self.jobs | other.jobs,
                          self.failed_annotations | other.failed_annotations)

    @staticmethod
    def combine(*args):
        """
        Combine a number of SampleItems into a new one.

        :param args: the SampleItems to combine
        :type args: iterable of SampleItems
        :return: the combined SampleItem
        :rtype: SampleItem

        It is possible to both give multiple arguments, where each argument is
        a SampleItem, or a single argument which is an iterable yielding
        SampleItems.

        .. code-block:: python

          # variables a, b, c, d are SampleItems to combine
          # These are all valid ways of combining the SampleItems
          comb1 = SampleItem.combine(a, b, c, d)  # Using multiple arguments
          l = [a, b, c, d]
          comb2 = SampleItem.combine(l)  # Using a list of arguments
          comb3 = SampleItem.combine(l.__iter__())  # Using an iterator
        """
        if len(args) == 1 and not isinstance(args[0], SampleItemBase):
            args = args[0]

        args = [x for x in args]

        if not all(isinstance(x, SampleItemBase) for x in args):
            raise exceptions.FastrTypeError("All arguments should be SampleItems! Found {}".format(args))

        if len(args) == 0:
            raise exceptions.FastrValueError("Cannot combine empty list")
        elif len(args) == 1:
            return args[0]
        else:
            result = args[0]
            for item in args[1:]:
                result = result + item
            return result

    @property
    def index(self):
        """
        The index of the SampleItem

        :return: The index of this SampleItem
        :rtype: SampleIndex
        """
        return self[0]

    @property
    def id(self):
        """
        The sample id of the SampleItem

        :return: The id of this SampleItem
        :rtype: SampleId
        """
        return self[1]

    @property
    def data(self):
        """
        The data SampleValue of the SampleItem

        :return: The value of this SampleItem
        :rtype: SampleValue
        """
        return self[2]

    @property
    def jobs(self):
        """
        The set of the jobs on which this SampleItem depends

        :return: The jobs that generated the data for this SampleItem
        :rtype: set
        """
        return self[3]

    @property
    def failed_annotations(self):
        return self[4]

    @property
    def cardinality(self):
        """
        The cardinality of this Sample
        """
        return len(self.data)

    @property
    def dimensionality(self):
        """
        The dimensionality of this Sample
        """
        return len(self.index)


class SampleItem(SampleItemBase):
    def __new__(cls, index, id_, data, jobs=None, failed_annotations=None):
        """
        Create a SampleItem. Data should be an OrderedDict of tuples.

        :param index: the sample index
        :type index: tuple, slice
        :param id_: the sample id
        :type id_: :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :param data: the data values
        :type data: SampleValue, Mapping
        :param set jobs: set of jobs on which this SampleItems data depends.
        :param set failed_annotations: set of tuples. The tuple is contructed like follows: (job_id, reason).
        """

        if not isinstance(data, SampleValue):
            data = SampleValue(data)

        if not all(isinstance(x, (int, str)) for x in data.keys()):
            types = set(type(x).__name__ for x in data.keys())
            raise exceptions.FastrTypeError("All keys in data should be tuples, found {}".format(types))

        if not all(isinstance(x, tuple) for x in data.values()):
            types = set(type(x).__name__ for x in data.values())
            raise exceptions.FastrTypeError("All values in data should be tuples, found {}".format(types))

        return super(SampleItem, cls).__new__(cls, index, id_, data, jobs, failed_annotations)


class SamplePayload(SampleItemBase):
    def __new__(cls, index, id_, data, jobs=None, failed_annotations=None):
        """
        Create a SampleItem. Data should be an OrderedDict of tuples.

        :param index: the sample index
        :type index: tuple, slice
        :param id_: the sample id
        :type id_: :py:class:`SampleId <fastr.core.sampleidlist.SampleId>`
        :param data: the data values
        :type data: SampleValue, Mapping
        :param set jobs: set of jobs on which this SampleItems data depends.
        :param set failed_annotations: set of tuples. The tuple is contructed like follows: (job_id, reason).
        """

        if not isinstance(data, MutableMapping):
            raise exceptions.FastrTypeError('SamplePayload should have a MutableMapping as data')

        if not all(isinstance(x, str) for x in data.keys()):
            types = set(type(x).__name__ for x in data.keys())
            raise exceptions.FastrTypeError("All keys in data should be str, found {}".format(types))

        if not all(isinstance(x, SampleItem) for x in data.values()):
            types = set(type(x).__name__ for x in data.values())
            raise exceptions.FastrTypeError("All values in data should be SampleItems, found {}".format(types))

        return super(SamplePayload, cls).__new__(cls, index, id_, data, jobs, failed_annotations)

    def __add__(self, other):
        """
        The addition operator combines two SampleItems into a single
        SampleItems. It merges the data and jobs and takes the index
        and id of the left-hand item.

        :param other: The other item to add to this one
        :type other: SampleItem
        :return: the combined SamplePayload
        :rtype: SamplePayload
        """
        if not isinstance(other, SamplePayload):
            return NotImplemented

        common_keys = set(self.data.keys()) & set(other.data.keys())

        if len(common_keys) > 0:
            raise exceptions.FastrValueError(
                'Cannot combine SamplePayloads, they both contain definitions for {}'.format(common_keys)
            )

        new_data = OrderedDict(self.data)
        new_data.update(other.data)
        return SamplePayload(self.index,
                             self.id,
                             new_data,
                             self.jobs | other.jobs,
                             self.failed_annotations | other.failed_annotations)


class HasSamples(HasDimensions, metaclass=ABCMeta):
    """
    Base class for all classes that supply samples. This base class allows
    to only define __getitem__ and size and get all other basic functions mixed
    in so that the object behaves similar to a Mapping.
    """

    @abstractmethod
    def __getitem__(self, item):
        raise NotImplementedError()

    def __contains__(self, item):
        try:
            self[item]
        except (KeyError, IndexError):
            return False
        else:
            return True

    def iteritems(self):
        if len(self.size) > 0:
            if None in self.size:
                raise exceptions.FastrValueError('The size {} contains None, cannot continue!')
            for index in itertools.product(*[list(range(x)) for x in self.size]):
                try:
                    yield self[SampleIndex(index)]
                except exceptions.FastrIndexNonexistent:
                    pass

    def __iter__(self):
        for item in self.items():
            yield item.index

    def items(self):
        return list(self.iteritems())

    def indexes(self):
        return list(self)

    def ids(self):
        return [self[x].id for x in self.items()]


class ContainsSamples(HasSamples):
    @abstractproperty
    def samples(self):
        pass

    def __getitem__(self, item):
        return self.samples[item]

    def __setitem__(self, key, value):
        self.samples[key] = value

    @property
    def dimensions(self):
        return self.samples.dimensions


class SampleBaseId(tuple):
    """
    This class represents a sample id. A sample id is a multi-dimensional
    id that has a simple, consistent string representation.
    """
    _element_type = type(None)

    def __new__(cls, *args):
        """
        Create a new SampleId

        :param args: the strings to make sample id for
        :type args: iterator/iterable of element type or element type
        """
        # Probably an iterable or str, so only use first element
        if len(args) == 1:
            args = args[0]

        # Make sure we won't iterate over character in a str
        if isinstance(args, cls._element_type):
            args = (args,)

        # Use the generator to create values and store as tuple for later use
        try:
            args = [x for x in args]
        except TypeError:
            if isinstance(cls._element_type, tuple):
                etype = '/'.join(x.__name__ for x in cls._element_type)
            else:
                etype = cls._element_type.__name__
            raise exceptions.FastrTypeError(
                'The arguments for {} should be a iterable of {} elements, found non-iterable {}'.format(cls.__name__,
                                                                                                         etype, args)
            )

        # Make sure the ID is not empty (which would make a terrible identifier)
        if len(args) == 0:
            raise exceptions.FastrValueError('A {} must have at least one dimension to be valid!'.format(cls.__name__))

        if not all(isinstance(x, cls._element_type) for x in args):
            raise exceptions.FastrTypeError(
                'The arguments for {} should be a iterable of {} elements, found iterable {}'.format(cls.__name__,
                                                                                                     cls._element_type,
                                                                                                     args)
            )

        return super(SampleBaseId, cls).__new__(cls, args)

    def __repr__(self):
        """
        Get a string representation for the SampleBaseId

        :return: the string representation
        :rtype: str
        """
        return '<{} {}>'.format(type(self).__name__, super(SampleBaseId, self).__repr__())

    def __str__(self):
        """
        Get a string version for the SampleId, joins the SampleId with __ to
        create a single string version.

        :return: the string version
        :rtype: str
        """
        return '__'.join(str(x) for x in self)

    def __add__(self, other):
        """
        Add another SampleId, this allows to add parts to the SampleId in a
        convenient way.
        """
        if isinstance(other, self._element_type):
            other = (other,)

        if not isinstance(other, tuple):
            return NotImplemented

        return type(self)(super(SampleBaseId, self).__add__(other))

    def __radd__(self, other):
        """
        Add another SampleId, this allows to add parts to the SampleId in a
        convenient way. This is the right-hand version of the operator.
        """

        if isinstance(other, self._element_type):
            other = (other,)

        if not isinstance(other, tuple):
            return NotImplemented

        return type(self)(tuple(other) + tuple(self))


class SampleId(SampleBaseId):
    """
    SampleId is an identifier for data using human readable strings
    """
    _element_type = str


class SampleIndex(SampleBaseId):
    """
    SampleId is an identifier for data using the location in the N-d data structure.
    """
    _element_type = (int, slice)

    def __str__(self):
        """
        Get a string version for the SampleId, joins the SampleId with __ to
        create a single string version.

        :return: the string version
        :rtype: str
        """
        # This horrible one-liner returns the str representation of the elements
        # For an int is just calls str, but for a slice it will create a str like
        # start:stop[:step] with the None as empty
        plot_elem = [('{x[0]}:{x[1]}' if s.step is None else '{x[0]}:{x[1]}:{x[2]}').format(
            x=[str(n) if n is not None else '' for n in (s.start, s.stop, s.step)])
            if isinstance(s, slice) else str(s) for s in self]
        return '({})'.format(', '.join(plot_elem))

    def __repr__(self):
        """
        Get a string representation for the SampleIndex

        :return: the string representation
        :rtype: str
        """
        return '<{} {}>'.format(type(self).__name__, str(self))

    @property
    def isslice(self):
        """
        Flag indicating that the SampleIndex is a slice (as opposed to a
        simple single index).
        """
        return any(isinstance(x, slice) for x in self)

    def expand(self, size):
        """
        Function expanding a slice SampleIndex into a list of non-slice
        SampleIndex objects

        :param size: the size of the collection to slice
        """
        if len(size) != len(self):
            raise exceptions.FastrValueError('Number of dimensions of the index and size do not'
                                             ' match ({} vs {})'.format(len(self), len(size)))

        if not self.isslice:
            return self

        # For each dimension get the range arguments
        index_range = (x.indices(s) if isinstance(x, slice) else (x, x+1) for x, s in zip(self, size))

        # Create an xrange iterator for each dimension
        index_range = [range(*x) if len(x) > 0 else [] for x in index_range]

        # Create all combinations of indices
        return tuple(SampleIndex(x) for x in itertools.product(*index_range))


class SampleValue(MutableMapping):
    """
    A collection containing the content of a sample
    """
    _key_type = (int, str)

    def __init__(self, *args, **kwargs):
        try:
            self._data = dict(*args, **kwargs)
        except (TypeError, ValueError) as err:
            raise exceptions.FastrTypeError(
                'Cannot create dict based on: args "{}" kwargs and "{}" (reason: {})'.format(args, kwargs, err)
            )

    def __repr__(self):
        return '<SampleValue {}>'.format(self._data)

    def __getitem__(self, item):
        if not isinstance(item, self._key_type):
            raise exceptions.FastrTypeError('Keys in a SampleValue should be of {}'.format(self._key_type))

        try:
            return self._data[item]
        except KeyError:
            raise exceptions.FastrKeyError('Key {} not found in {}'.format(item, self._data))

    def __setitem__(self, key, value):
        if not isinstance(key, self._key_type):
            raise exceptions.FastrTypeError('Keys in a SampleValue should be of {}'.format(self._key_type))

        if not isinstance(value, tuple):
            raise exceptions.FastrTypeError('Values in a SampleValue should be of type tuple')

        self._data[key] = value

    def __getstate__(self):
        state = {}
        for key, value in self._data.items():
            state[key] = tuple(x.__getstate__() for x in value)

        return ('SampleValue', state)

    def __setstate__(self, state):
        if state[0] != 'SampleValue':
            raise exceptions.FastrValueError('Cannot unpickle incorrectly formatted SampleValue data!')
        self._data = {}
        for key, value in state[1].items():
            new_value = []
            for item in value:
                if item[0] not in datatypes.types:
                    resources.tools.data  # Trigger tools population
                new_item = datatypes.types[item[0]]()
                new_item.__setstate__(item)
                new_value.append(new_item)

            self._data[key] = tuple(new_value)

    def __delitem__(self, key):
        if not isinstance(key, self._key_type):
            raise exceptions.FastrTypeError('Keys in a SampleValue should be of {}'.format(self._key_type))

        del self._data[key]

    def __len__(self):
        return sum(len(x) for x in self.values())

    def __iter__(self):
        for key in sorted(self._data.keys()):
            yield key

    @property
    def is_sequence(self):
        return all(isinstance(x, int) for x in self.keys())

    @property
    def is_mapping(self):
        return not self.is_sequence

    def sequence_part(self):
        return tuple(x for k, v in self.items() if isinstance(k, int) for x in v)

    def mapping_part(self):
        return OrderedDict([(k, v) for k, v in self.items() if isinstance(k, str)])

    def cast(self, datatype):
        new_data = {}
        for key, value in self.items():
            new_data[key] = tuple(x if datatype.isinstance(x) else datatype(x) for x in value)
        return SampleValue(new_data)

    def iterelements(self):
        for value in self.values():
            for element in value:
                yield element

    def __radd__(self, other):
        # Allow for sum
        if not isinstance(other, int):
            return NotImplemented

        if other != 0:
            return NotImplemented

        return self

    def __add__(self, other):
        if not isinstance(other, SampleValue):
            return NotImplemented

        # Create result with the tuple parts if they exist
        result = {}
        sequence_part_self = self.sequence_part()
        sequence_part_other = other.sequence_part()

        if len(sequence_part_self) > 0:
            result[0] = sequence_part_self

        if len(sequence_part_other) > 0:
            result[1] = sequence_part_other

        # Add keys known in self, merge with other if needed
        mapping_part_self = self.mapping_part()
        mapping_part_other = other.mapping_part()
        for key, value in mapping_part_self.items():
            if key in mapping_part_other:
                result[key] = value + mapping_part_other[key]
            else:
                result[key] = value

        # Add the keys of other not yet merged
        for key, value in mapping_part_other.items():
            if key not in result:
                result[key] = value

        return SampleValue(result)


class SampleCollection(MutableMapping, HasDimensions):
    """
    The SampleCollections is a class that contains the data including a form
    of ordering. Each sample is reachable both by its SampleId and a
    SampleIndex. The object is sparse, so not all SampleId have to be defined
    allowing for non-rectangular data shapes.

    .. note::

        This object is meant to replace both the SampleIdList and the
        ValueStorage.
    """

    def __init__(self, dimnames, parent):
        """
        Createa a new SampleCollection
        """
        self._dimensions = tuple(Dimension(name, 0) for name in dimnames)
        self._parent = parent
        self._id_lookup = dict()
        self._index_lookup = dict()

    def __repr__(self):
        return '<SampleCollection containing {} samples>'.format(self.size)

    def __contains__(self, item):
        """
        Check if an item is in the SampleCollection. The item can be a SampleId
        or SampleIndex. If the item is a slicing SampleIndex, then check if it
        would return any data (True) or no data (False)

        :param item: the item to check for
        :type item: SampleId, SampleIndex
        :return: flag indicating item is in the collections
        :rtype: bool
        """
        if not isinstance(item, (SampleIndex, SampleId)):
            try:
                item = SampleIndex(item)
            except (exceptions.FastrValueError, exceptions.FastrTypeError):
                try:
                    item = SampleId(item)
                except (exceptions.FastrValueError, exceptions.FastrTypeError):
                    pass

        if isinstance(item, SampleId):
            return item in self._id_lookup
        elif isinstance(item, SampleIndex):
            if not item.isslice:
                return item in self._index_lookup
            else:
                return any(x in self._index_lookup for x in item.expand(self.size))
        else:
            return False

    def __getitem__(self, item):
        """
        Retrieve (a) SampleItem(s) from the SampleCollection using the SampleId
        or SampleIndex. If the item is a tuple, it should be valid tuple for
        constructing either a SampleId or SampleIndex.

        :param item: the identifier of the item to retrieve
        :type item: SampleId, SampleIndex, or tuple
        :returns: the requested item
        :rtype: SampleItem
        :raises FastrTypeError: if the item parameter is of incorrect type
        :raises KeyError: if the item is not found
        """

        # If the item is not a SampleId or SampleIndex, try to salvage by
        # turning the item into a proper format
        if not isinstance(item, (SampleIndex, SampleId)):
            try:
                item = SampleIndex(item)
            except (exceptions.FastrValueError, exceptions.FastrTypeError):
                try:
                    item = SampleId(item)
                except (exceptions.FastrValueError, exceptions.FastrTypeError):
                    pass

        if isinstance(item, SampleId):
            try:
                return self._id_lookup[item]
            except KeyError:
                raise exceptions.FastrKeyError('Cannot find key {!r} in {}'.format(item,
                                                                                   sorted(self._id_lookup.keys())))
        elif isinstance(item, SampleIndex):
            if not item.isslice:
                try:
                    return self._index_lookup[item]
                except KeyError:
                    if all(0 <= x < s for x, s in zip(item, self.size)):
                        raise exceptions.FastrIndexNonexistent(
                            'Could not find index {} in sparse array {}'.format(item, self)
                        )
                    else:
                        raise exceptions.FastrKeyError(
                            'Cannot find index {!r} in {}'.format(item, sorted(self._index_lookup.keys()))
                        )
            else:
                # Unpack slice
                try:
                    return tuple(self._index_lookup[x] for x in item.expand(self.size) if x in self._index_lookup)
                except KeyError:
                    raise exceptions.FastrKeyError('Cannot find key {!r}'.format(item))
        else:
            raise exceptions.FastrTypeError('The key of a SampleCollection has'
                                            'to be a SampleId or SampleIndex'
                                            ' (found {})'.format(item))

    def __setitem__(self, key, value):
        """
        Set an item to the SampleCollection. The key can be a SampleId,
        SampleIndex or a tuple containing a SampleId and SampleIndex.
        The value can be a SampleItem (with the SampleId and SampleIndex
        matching), a tuple with values (assuming no depending jobs), or a
        with a list of values and a set of depending jobs.

        :param key: the key of the item to store
        :type key: SampleId, SampleIndex, tuple of both, or SampleItem
        :param value: the value of the SampleItem to store
        :type value: SampleItem, tuple of values, or tuple of tuple of values and set of depending jobs
        :raises FastrTypeError: if the key or value types are incorrect
        :raises FastrValueError: if the id or values are incorrectly formed
        """

        # Parse the key to set
        if isinstance(key, SampleId):
            sample_id = key
            sample_index = None
        elif isinstance(key, SampleIndex):
            sample_id = None
            sample_index = key
        elif isinstance(key, SampleItem):
            sample_id = key.id
            sample_index = key.index
        elif isinstance(key, tuple):
            if len(key) == 2 and isinstance(key[0], SampleId) and isinstance(key[1], SampleIndex):
                sample_id = key[0]
                sample_index = key[1]
            elif len(key) == 2 and isinstance(key[0], SampleIndex) and isinstance(key[1], SampleId):
                sample_id = key[1]
                sample_index = key[0]
            else:
                raise exceptions.FastrValueError('If the key to set is a tuple, it must '
                                                 'contain exactly one SampleId and one SampleItem')
        else:
            raise exceptions.FastrTypeError('The key to set must be a SampleId, SampleIndex,'
                                            ' or tuple (found {})'.format(type(key).__name__))

        # Parse the value to set
        if isinstance(value, SampleItem):
            if sample_id is not None and value.id != sample_id:
                raise ValueError('The SampleId of the key and the value do not'
                                 ' correspond! ({} vs {})'.format(value.id, sample_id))

            if sample_index is not None and value.index != sample_index:
                raise ValueError('The SampleIndex of the key and the value do'
                                 ' not correspond! ({} vs {})'.format(value.index, sample_index))

            value = SampleItem(value.index, value.id, value.data, value.jobs, value.failed_annotations)
        elif isinstance(value, SamplePayload):
            if sample_id is not None and value.id != sample_id:
                raise ValueError('The SampleId of the key and the value do not'
                                 ' correspond! ({} vs {})'.format(value.id, sample_id))

            if sample_index is not None and value.index != sample_index:
                raise ValueError('The SampleIndex of the key and the value do'
                                 ' not correspond! ({} vs {})'.format(value.index, sample_index))
        elif isinstance(value, tuple):
            # Assume the (values, depending_jobs) value format
            if sample_index is None:
                raise exceptions.FastrValueError('Could not find a proper SampleIndex for item to store')

            if sample_id is None:
                raise exceptions.FastrValueError('Could not find a proper SampleId for item to store')

            if len(value) == 2 and isinstance(value[0], SampleValue) and isinstance(value[1], set):
                # Create the SampleItem
                value = SampleItem(sample_index, sample_id, value[0], value[1], set())
            if len(value) == 3 and isinstance(value[0], SampleValue) and \
                    isinstance(value[1], set) and isinstance(value[2], set):
                # Create the SampleItem
                value = SampleItem(sample_index, sample_id, value[0], value[1], set())
            else:
                raise exceptions.FastrValueError('The tuple value is not a (values, depending) or'
                                                 ' (values, depending, failed_annotations)'
                                                 ' jobs tuple or a tuple of values!')
        else:
            # Try to cast it SampleValue
            if not isinstance(value, SampleValue):
                value = SampleValue(value)

            # Assume a iterable of values
            # We know that datatype is callable
            # pylint: disable=not-callable
            value = SampleItem(sample_index, sample_id, value, set(), set())

        # Make sure we know both sample_index and sample_id
        if sample_index is None:
            sample_index = value.index
        if sample_id is None:
            sample_id = value.id

        # Check if items already exists and that both point to the same item
        if sample_index in self._index_lookup or sample_id in self._id_lookup \
                and self._index_lookup.get(sample_index) is not self._id_lookup.get(sample_id):
            raise exceptions.FastrValueError(
                'The index and id of the item to set point to different items!' +
                ' Using index {} and id {}'.format(sample_index, sample_id) +
                ' {} points to {} '.format(sample_index, self._index_lookup.get(sample_index).id) +
                ' and {} points to {} '.format(sample_id, self._id_lookup.get(sample_id).index)
            )

        # Adapt the size
        for dimension, index in zip(self.dimensions, sample_index):
            dimension.update_size(index + 1)

        # Store in both lookups
        self._index_lookup[sample_index] = value
        self._id_lookup[sample_id] = value

    def __delitem__(self, key):
        """
        Remove an item from the SampleCollection

        :param key: the key of the item to remove
        :type key: SampleId, SampleIndex, tuple of both, or SampleItem
        """
        if isinstance(key, SampleId):
            sample_id = key
            sample_index = self._id_lookup[sample_id].index
        elif isinstance(key, SampleIndex):
            sample_index = key
            sample_id = self._index_lookup[sample_index].id
        elif isinstance(key, SampleItem):
            sample_id = key.id
            sample_index = key.index
        elif isinstance(key, tuple):
            if len(key) == 2 and isinstance(key[0], SampleId) and isinstance(key[1], SampleIndex):
                sample_id = key[0]
                sample_index = key[1]
            elif len(key) == 2 and isinstance(key[0], SampleIndex) and isinstance(key[1], SampleId):
                sample_id = key[1]
                sample_index = key[2]
            else:
                raise exceptions.FastrValueError('If the key to set is a tuple, it must '
                                                 'contain exactly one SampleId and one SampleItem')
        else:
            raise exceptions.FastrTypeError('The key to remove must be a SampleId, SampleIndex,'
                                            ' or tuple (found {})'.format(type(key).__name__))

        # Check if items already exists and that both point to the same item
        if sample_index not in self._index_lookup or sample_id not in self._id_lookup:
            raise exceptions.FastrValueError('Either the SampleId or SampleIndex to remove was not found!'
                                             ' This indicates a data corruption int he SampleCollection!')

        if self._index_lookup.get(sample_index) is not self._id_lookup.get(sample_id):
            raise exceptions.FastrValueError('The index and id of the item to remove point to different items!')

        del self._index_lookup[sample_index]
        del self._index_lookup[sample_id]

    def __iter__(self):
        """
        Iterate over the indices
        """
        for index in sorted(self._index_lookup):
            yield index

    def __len__(self):
        """
        Get the number of samples in the SampleCollections.
        """
        return len(self._id_lookup)

    @property
    def dimensions(self):
        return self._dimensions

    @property
    def ndims(self):
        """
        The number of dimensions in this SampleCollection
        """
        return len(self.dimensions)

    @property
    def parent(self):
        """
        The parent object holding the SampleCollection
        """
        return self._parent

    @property
    def fullid(self):
        """
        The full defining ID for the SampleIdList
        """
        if self.parent is not None:
            return '{}/SampleCollection'.format(self.parent.fullid)
        else:
            return 'UNKNOWN/SampleCollection'
