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


import itertools
import weakref
from abc import ABCMeta, abstractmethod
from collections import OrderedDict

import fastr
from fastr.core.dimension import HasDimensions
from fastr.core.samples import SampleId, SampleIndex
from fastr import exceptions


class BaseInputGroupCombiner(HasDimensions, metaclass=ABCMeta):
    """
    An object that takes the different input groups and combines them in the
    correct way.
    """

    def __init__(self, parent):
        self.parent = weakref.ref(parent)
        self.update()

    @property
    def fullid(self):
        """
        The full id of the InputGroupCombiner
        """
        return '{}/input_group_combiner'.format(self.parent.fullid)

    @property
    def input_groups(self):
        return self.parent().input_groups

    @abstractmethod
    def merge(self, list_of_items):
        """
        Given a list of items for each input group, it returns the combined
        list of items.

        :param list list_of_items: items to combine
        :return: combined list
        """

    @abstractmethod
    def unmerge(self, item):
        """
        Given a item it will recreate the seperate items, basically this is the
        inverse operation of merge. However, this create an OrderedDict so that
        specific input groups can be easily retrieved. To get a round trip, the
        values of the OrderedDict should be taken::

            >>> odict_of_items = combiner.unmerge(item)
            >>> item = combiner.merge(odict_of_items.values())

        :param list item: the item to unmerge
        :return: items
        :rtype: OrderedDict
        """

    @abstractmethod
    def iter_input_groups(self):
        """
        Iterate over all the merged samples
        :return:
        """

    @property
    def dimensions(self):
        dimensions = tuple(self.merge([ig.dimensions for ig in self.input_groups.values()]))
        return dimensions

    def merge_sample_id(self, list_of_sample_ids):
        return SampleId(self.merge(list_of_sample_ids))

    def merge_sample_index(self, list_of_sample_indexes):
        return SampleIndex(self.merge(list_of_sample_indexes))

    def merge_sample_data(self, list_of_sample_data):
        return {k: v if v is not None and len(v) > 0 else None for data in list_of_sample_data for k, v in data.items()}

    def merge_sample_jobs(self, list_of_sample_jobs):
        return set.union(*list_of_sample_jobs)

    def merge_failed_annotations(self, list_of_failed_annotations):
        return set.union(*list_of_failed_annotations)

    def merge_payloads(self, sample_payloads):
        # Determine the sample index
        sample_index = self.merge_sample_index([x.index for x in sample_payloads])

        # Create sampleid
        sample_id = self.merge_sample_id([x.id for x in sample_payloads])

        # Extract jobdata and combine in single dict
        job_data = self.merge_sample_data(x.data for x in sample_payloads)

        # Create superset of all job dependencies
        job_depends = self.merge_sample_jobs(x.jobs for x in sample_payloads)

        # Create superset of all failed annotations
        failed_annotations = self.merge_sample_jobs(x.failed_annotations for x in sample_payloads)

        return sample_index, sample_id, job_data, job_depends, failed_annotations

    def __iter__(self):
        return self.iter_input_groups()

    def update(self):
        pass


class DefaultInputGroupCombiner(BaseInputGroupCombiner):
    """
    The default input group combiner combines the input group in a cross
    product version, taking each combinations of samples between the input
    groups. So if there are two input groups with one with size N and the
    other with size M x P the result would be N x M x P samples, with all
    possible combinations of the samples in each input group.
    """
    def merge(self, list_of_items):
        """
        Given a list of items for each input group, it returns the combined
        list of items.

        :param list list_of_items: items to combine
        :return: combined list
        """
        return [x for item in list_of_items for x in item]

    def unmerge(self, item):
        """
        Given a item it will recreate the seperate items, basically this is the
        inverse operation of merge. However, this create an OrderedDict so that
        specific input groups can be easily retrieved. To get a round trip, the
        values of the OrderedDict should be taken::

            >>> odict_of_items = combiner.unmerge(item)
            >>> item = combiner.merge(odict_of_items.values())

        :param list item: the item to unmerge
        :return: items
        :rtype: OrderedDict
        """
        result = OrderedDict()
        for target in list(self.input_groups.values()):
            mask = [True if ig.id == target.id else False for ig in self.input_groups.values() for _ in ig.size]
            result[target.id] = tuple(k for k, m in zip(item, mask) if m)

        return result

    def iter_input_groups(self):
        for sample_payloads in itertools.product(*[ig.iterinputvalues for ig in self.input_groups.values()]):
            fastr.log.debug('sample_payload: {}'.format(sample_payloads))
            fastr.log.debug('sample payload data: {}'.format([x.data for x in sample_payloads]))
            yield self.merge_payloads(sample_payloads)


class MergingInputGroupCombiner(BaseInputGroupCombiner):
    """
    The merging input group combiner takes a similar approach as the default
    combiner but merges dimensions that are the same. If input group A has
    N(3) x M(2) samples and B has M(2) x P(4) it wil not result in N(3) x M(2)
    x M(2) x P(4), but merge the dimensions M leading to N(3) x M(2) x P(4) in
    resulting size.
    """
    def __init__(self, input_groups, merge_dimension):
        self.merge_dimensions = merge_dimension
        self._merges = None
        self._merge_sizes = None
        self._masks = None
        super(MergingInputGroupCombiner, self).__init__(input_groups)

    def update(self):
        dimnames = [x.dimnames for x in self.input_groups.values()]
        sizes = [x.size for x in self.input_groups.values()]

        # Validate the sample dimensions and sizes are consistent
        unique_dimnames = tuple(set(x for dimname in dimnames for x in dimname))
        unique_sizes = {x: set() for x in unique_dimnames}

        for size, dimname in zip(sizes, dimnames):
            for size_element, dimname_element in zip(size, dimname):
                unique_sizes[dimname_element].add(size_element)
        if not all(len(x) == 1 for x in unique_sizes.values()):
            raise exceptions.FastrValueError('The dimension have incosistent sizes: {}'.format(unique_sizes))
        unique_sizes = {k: v.pop() for k, v in unique_sizes.items()}

        # Check how many merges to perform
        if self.merge_dimensions == 'all':
            counts = {name: [sum(x == name for x in dimname) for dimname in dimnames] for name in unique_dimnames}
            merges = {name: min(value) for name, value in counts.items()}
            merges = tuple(key for key, value in merges.items() for x in range(value))
        else:
            merges = tuple(self.merge_dimensions)

        self._merges = merges

        # Make a merge mask for the dimnames
        masks = []
        for dimname in dimnames:
            temp = []
            temp_merges = list(merges)
            for name in dimname:
                if name in temp_merges:
                    index = temp_merges.index(name)
                    temp.append(index)
                    temp_merges[index] = None
                else:
                    temp.append(slice(unique_sizes[name]))
            masks.append(temp)

        self._masks = masks

        # Do the actual merging
        self._merge_sizes = tuple(unique_sizes[x] for x in merges)

    def merge(self, list_of_items):
        new_item = [x for mask, item in zip(self._masks, list_of_items) for m, x in zip(mask, item) if isinstance(m, slice)]
        new_item.extend(x for x, m in zip(list_of_items[0], self._masks[0]) if not isinstance(m, slice))
        return new_item

    def unmerge(self, item):
        index = 0
        result = OrderedDict()
        nr_slices = sum(isinstance(x, slice) for y in self._masks for x in y)
        for input_group, mask in zip(self.input_groups, self._masks):
            original_item = []
            for m in mask:
                if isinstance(m, slice):
                    original_item.append(item[index])
                    index += 1
                else:
                    original_item.append(item[m + nr_slices])
            result[input_group] = tuple(original_item)

        return result

    def iter_input_groups(self):
        # Create iterator for the merged part of the iteration
        if len(self._merges) > 0:
            fixed_indexes = itertools.product(*[range(x) for x in self._merge_sizes])
        else:
            fixed_indexes = [()]

        # Loop over the fixed (merged) indices and then over the remainder
        for fixed_index in fixed_indexes:
            iterators = [itertools.product(*[range(m.stop) if isinstance(m, slice) else [fixed_index[m]] for m in mask]) for mask in self._masks]

            for indexes in itertools.product(*iterators):
                # Retrieve the samples from all input groups
                samples = []

                for index, input_group in zip(indexes, self.input_groups.values()):
                    try:
                        samples.append(input_group[SampleIndex(index)])
                    except exceptions.FastrIndexNonexistent:
                        samples.append(None)

                # Merge all sample payloads
                if all(x is not None for x in samples):
                    yield self.merge_payloads(samples)
                else:
                    fastr.log.info('Skipping {} because it is non-existent due to sparsity!'.format(indexes))

