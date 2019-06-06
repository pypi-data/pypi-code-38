from functools import total_ordering
from copy import copy

from lib5c.core.mixins import Picklable, Loggable, Annotatable
from lib5c.parsers.primers import load_primermap
from lib5c.util.primers import natural_sort_key


@total_ordering
class Locus(object, Picklable, Annotatable):
    """
    Basically anything with a chromosome, start, and end. Can also include
    arbitrary metadata.

    Attributes
    ----------
    chrom : str
        The chromosome on which this locus resides (e.g., ``'chr4'``).
    start : int
        The start coordinate for the zero-indexed, half-open interval occupied
        by the locus.
    end : int
        The end coordinate for the zero-indexed, half-open interval occupied by
        the locus.
    data : dict(str -> any)
        Arbitrary additional data about the locus. This attribute is filled in
        with any kwargs passed to the constructor.

    Notes
    -----
    Locus objects support comparison and ordering via the ``total_ordering``
    decorator. See this class's implementations of ``__eq__()`` and ``__lt__()``
    for more details.

    Locus objects support the Annotatable mixin, which is the source of their
    ``data`` attribute and all its related functions.
    """

    def __init__(self, chrom, start, end, **kwargs):
        """
        Constructor.

        Parameters
        ----------
        chrom : str
            The chromosome on which this locus resides (e.g., ``'chr4'``).
        start : int
            The start coordinate for the zero-indexed, half-open interval
            occupied by the locus.
        end : int
            The end coordinate for the zero-indexed, half-open interval occupied
            by the locus.
        kwargs : other keyword arguments
            Any additional kwargs will be stored in the new instance's ``data``
            attribute.
        """
        Annotatable.__init__(self)
        self.chrom = chrom
        self.start = start
        self.end = end
        self.data = kwargs

    def __str__(self):
        """
        Gets a pretty string representation of this Locus.

        Returns
        -------
        str
            String representation of this Locus.

        Examples
        --------
        >>> from lib5c.core.loci import Locus
        >>> locus = Locus('chr3', 34109023, 34113109, strand='+')
        >>> print locus
        Locus chr3:34109023-34113109
            strand: +
        """
        str_repr = 'Locus %s:%i-%i' % (self.chrom, self.start, self.end)
        str_repr += Annotatable.__str__(self)
        return str_repr

    def __eq__(self, other):
        """
        Implementation of equality comparison for Locus objects. Locus objects
        are considered equal if they occupy precisely the same coordinates on
        the genome. The values in ``data`` are not considered when checking for
        equality.

        Parameters
        ----------
        other : Locus
            The other Locus object to compare this one to.

        Returns
        -------
        bool
            True if the two Locus objects are equivalent, False otherwise.

        Examples
        --------
        >>> from lib5c.core.loci import Locus
        >>> locus_a = Locus('chr3', 34109023, 34113109, counts=10)
        >>> locus_b = Locus('chr3', 34109023, 34113109, counts=20)
        >>> locus_c = Locus('chr3', 34113147, 34116141, counts=10)
        >>> locus_d = Locus('chrX', 34109023, 34113109, counts=10)
        >>> locus_a == locus_b  # only chrom, start, and end matter
        True
        >>> locus_a == locus_c  # start and end coordinates are different
        False
        >>> locus_a == locus_d  # chromosome is different
        False
        """
        return (self.chrom == other.chrom and
                self.start == other.start and
                self.end == other.end)

    def __ne__(self, other):
        """
        Inequality comparison for Locus objects.

        Parameters
        ----------
        other : Locus
            The other Locus object to compare this one to.

        Returns
        -------
        bool
            False if the two Locus objects are equivalent, True otherwise.

        Examples
        --------
        >>> from lib5c.core.loci import Locus
        >>> locus_a = Locus('chr3', 34109023, 34113109, counts=10)
        >>> locus_b = Locus('chr3', 34109023, 34113109, counts=20)
        >>> locus_c = Locus('chr3', 34113147, 34116141, counts=10)
        >>> locus_d = Locus('chrX', 34109023, 34113109, counts=10)
        >>> locus_a != locus_b  # only chrom, start, and end matter
        False
        >>> locus_a != locus_c  # start and end coordinates are different
        True
        >>> locus_a != locus_d  # chromosome is different
        True
        """
        return not (self == other)

    def __lt__(self, other):
        """
        Implementation of inequality comparison for Locus objects. Locus objects
        are compared by alphanumeric sort order of ``chrom``, then start
        coordinate, then end coordinate. Values in ``data`` are ignored.

        Parameters
        ----------
        other : Locus
            The other Locus object to compare this one to.

        Returns
        -------
        bool
            True if this Locus object sorts ahead of ``other``, False otherwise.

        Examples
        --------
        >>> from lib5c.core.loci import Locus
        >>> locus_a = Locus('chr3', 34109023, 34113109)
        >>> locus_b = Locus('chr3', 34113147, 34116141)
        >>> locus_c = Locus('chrX', 34109023, 34113109)
        >>> locus_a < locus_b  # same chrom but a starts first
        True
        >>> locus_a < locus_c  # different chrom, '3' comes before 'X'
        True
        """
        return ((natural_sort_key(self.chrom), self.start, self.end) <
                (natural_sort_key(other.chrom), other.start, other.end))

    def __hash__(self):
        """
        Overrides the ``__hash__()`` function for Locus objects. The hash for
        a Locus object is computed only over its ``chrom``, ``start``, and
        ``end`` attributes, so as to guarantee that two Locus objects that are
        equal under the ``__eq__()`` function implementation hash to the same
        value.

        Returns
        -------
        int
            The hash for this Locus object.

        Examples
        --------
        >>> from lib5c.core.loci import Locus
        >>> locus_a = Locus('chr3', 34109023, 34113109, counts=10)
        >>> locus_b = Locus('chr3', 34109023, 34113109, counts=5)
        >>> locus_c = Locus('chr3', 34113147, 34116141, counts=10)
        >>> hash(locus_a) == hash(locus_b)
        True
        >>> hash(locus_a) == hash(locus_c)
        False
        """
        return hash((self.chrom, self.start, self.end))

    def as_dict(self):
        """
        Gets a dict representation of the Locus.

        Returns
        -------
        dict
            This dict is guaranteed to have at least the following keys::

                {
                    'chrom': str,
                    'start': int,
                    'end': int
                }

            Other keys may be present if included in the ``data`` attribute.

        Examples
        --------
        >>> from lib5c.core.loci import Locus
        >>> locus = Locus('chr3', 34109023, 34113109, strand='+')
        >>> locus.as_dict()
        {'start': 34109023, 'end': 34113109, 'chrom': 'chr3', 'strand': '+'}
        """
        dict_repr = self.data
        dict_repr['chrom'] = self.chrom
        dict_repr['start'] = self.start
        dict_repr['end'] = self.end
        return dict_repr

    def get_name(self):
        """
        Gets the name of the locus, if present.

        Returns
        -------
        str or None
            The value of ``data['name']`` if it exists; None otherwise.

        Examples
        --------
        >>> from lib5c.core.loci import Locus
        >>> locus = Locus('chr3', 34109023, 34113109, name='5C_329_Sox2_FOR_2')
        >>> locus.get_name()
        '5C_329_Sox2_FOR_2'
        """
        return self.get_value('name')

    def get_region(self):
        """
        Gets the region of the locus, if present.

        Returns
        -------
        str or None
            The value of ``data['region']`` if it exists; None otherwise.

        Examples
        --------
        >>> from lib5c.core.loci import Locus
        >>> locus = Locus('chr3', 34109023, 34113109, region='Sox2')
        >>> locus.get_region()
        'Sox2'
        """
        return self.get_value('region')

    def get_strand(self):
        """
        Gets the strand of the locus, if present.

        Returns
        -------
        '+' or '-' or None
            The value of ``data['strand']`` if it exists; None otherwise.

        Examples
        --------
        >>> from lib5c.core.loci import Locus
        >>> locus = Locus('chr3', 34109023, 34113109, strand='+')
        >>> locus.get_strand()
        '+'
        """
        return self.get_value('strand')


class LocusMap(object, Picklable, Annotatable, Loggable):
    """
    Representation of an organized group of Locus objects.

    Attributes
    ----------
    locus_list : list of Locus objects
        Ordered list of unique Locus objects in the LocusMap.
    regions : list of str
        Ordered list of region names, as strings, present in the LocusMap. This
        list is filled in only when the Locus objects within the LocusMap have
        a ``'region'`` key in their ``data`` attribute.
    name_dict : dict(str -> Locus)
        Dict mapping Locus names as strings to the Locus object with that name.
        This dict is filled in only when the Locus objects within the LocusMap
        have a ``'name'`` key in their ``data`` attribute.
    region_index_dict : dict(str -> list of Locus objects)
        Maps a region name and an index within the region to a Locus object
        within the specified region. This means that, for example,
        ::

            locus_map.region_index_dict['Sox2'][3]

        resolves to the Locus object that is the 4th Locus object of the Sox2
        region in the LocusMap instance called ``locus_map``.
    hash_to_index_dict : dict(int -> int)
        Maps a Locus object's hash to its index within ``locus_list``.
    name_to_index_dict : dict(str -> int)
        Dict mapping Locus names as strings to their index within the LocusMap.
        This dict is filled in only when the Locus objects within the LocusMap
        have a ``'name'`` key in their ``data`` attribute.

    Notes
    -----
    Locus objects in a LocusMap are ordered by the total ordering implemented by
    the Locus class. See that class's implementation of ``__eq__()`` and
    ``__lt__()`` for more details.

    LocusMap objects support the Loggable and Annotatable mixins. See the
    Examples section for an example.

    Examples
    --------
    >>> from lib5c.core.loci import LocusMap
    >>> locus_map = LocusMap.from_primerfile('test/primers.bed')
    >>> locus_map.size()
    1551
    >>> locus_map.print_log()
    LocusMap created
    source primerfile: test/primers.bed
    >>> locus_map.set_value('test key', 'test value')
    >>> locus_map.get_value('test key')
    'test value'
    """

    def __init__(self, locus_list):
        """
        Constructor.

        Parameters
        ----------
        locus_list : list of Locus objects
            Ordered list of Locus objects in the LocusMap.
        """
        self.locus_list = sorted(locus_list)
        if len(self.locus_list) != len(set(self.locus_list)):
            raise ValueError('Locus objects in LocusMap must be unique')
        self.regions = []
        for locus in self.locus_list:
            if locus.get_region() and locus.get_region() not in self.regions:
                self.regions.append(locus.get_region())
        self.name_dict = {locus.get_name(): locus for locus in self.locus_list}
        self.region_index_dict = {region: [locus for locus in self.locus_list
                                           if locus.get_region() == region]
                                  for region in self.regions}
        self.name_to_index_dict = {self.locus_list[i].get_name(): i
                                   for i in range(len(self.locus_list))}
        self.hash_to_index_dict = {hash(self.locus_list[i]): i
                                   for i in range(len(self.locus_list))}
        Loggable.__init__(self)
        Annotatable.__init__(self)
        self.log_event('LocusMap created')

    @classmethod
    def from_primerfile(cls, primerfile):
        """
        Factory method that creates a LocusMap object from a BED file containing
        primer information.

        Parameters
        ----------
        primerfile : str
            String reference to the primer file.

        Returns
        -------
        LocusMap
            LocusMap object parsed from the primer file.

        Examples
        --------
        >>> from lib5c.core.loci import LocusMap
        >>> locus_map = LocusMap.from_primerfile('test/primers.bed')
        >>> locus_map.size()
        1551
        >>> locus_map.print_log()
        LocusMap created
        source primerfile: test/primers.bed
        """
        parsed_dict = load_primermap(primerfile)
        regions = parsed_dict.keys()
        locus_list = [Locus(**parsed_dict[region][index])
                      for region in regions
                      for index in range(len(parsed_dict[region]))]
        instance = cls(locus_list)
        instance.log_event('source primerfile: %s' % primerfile)
        return instance

    @classmethod
    def from_binfile(cls, binfile):
        """
        Factory method that creates a LocusMap object from a BED file containing
        bin information.

        Parameters
        ----------
        binfile : str
            String reference to the bin file.

        Returns
        -------
        LocusMap
            LocusMap object parsed from the bin file.

        Examples
        --------
        >>> from lib5c.core.loci import LocusMap
        >>> locus_map = LocusMap.from_binfile('test/bins_new.bed')
        >>> locus_map.size()
        1807
        >>> locus_map.print_log()
        LocusMap created
        source binfile: test/bins_new.bed
        """
        parsed_dict = load_primermap(binfile)
        regions = parsed_dict.keys()
        locus_list = [Locus(parsed_dict[region][index]['chrom'],
                            parsed_dict[region][index]['start'],
                            parsed_dict[region][index]['end'],
                            **{key: parsed_dict[region][index][key]
                               for key in parsed_dict[region][index]
                               if key not in ['chrom', 'start', 'end']})
                      for region in regions
                      for index in range(len(parsed_dict[region]))]
        instance = cls(locus_list)
        instance.log_event('source binfile: %s' % binfile)
        return instance

    @classmethod
    def from_list_of_dict(cls, list_of_dict):
        """
        Factory method that creates a LocusMap object from a list of dicts that
        represent the Loci that the LocusMap should be composed of.

        Parameters
        ----------
        list_of_dict : list of dict
            A list of dicts, with each dict representing a Locus that should be
            created and put into the LocusMap.

        Returns
        -------
        LocusMap
            A LocusMap whose Locus objects are equivalent to the dicts passed in
            ``list_of_dict``

        Examples
        --------
        >>> from lib5c.core.loci import LocusMap
        >>> list_of_dict = [{'chrom': 'chr3',
        ...                  'start': 34109023,
        ...                  'end': 34113109,
        ...                  'name': 'Sox2_FOR_2'},
        ...                 {'chrom': 'chr3',
        ...                  'start': 34113147,
        ...                  'end': 34116141,
        ...                  'name': 'Sox2_REV_4'}]
        ...
        >>> locus_map = LocusMap.from_list_of_dict(list_of_dict)
        >>> locus_map.print_log()
        LocusMap created
        created from list of dict
        >>> for locus in locus_map:
        ...     print locus
        ...
        Locus chr3:34109023-34113109
            name: Sox2_FOR_2
        Locus chr3:34113147-34116141
            name: Sox2_REV_4
        >>> list_of_dict_dup = [{'chrom': 'chr3',
        ...                      'start': 34109023,
        ...                      'end': 34113109,
        ...                      'name': 'Sox2_FOR_2'},
        ...                     {'chrom': 'chr3',
        ...                      'start': 34113147,
        ...                      'end': 34116141,
        ...                      'name': 'Sox2_REV_4'},
        ...                     {'chrom': 'chr3',
        ...                      'start': 34113147,
        ...                      'end': 34116141,
        ...                      'name': 'duplicate Locus!'}]
        ...
        >>> locus_map_dup = LocusMap.from_list_of_dict(list_of_dict_dup)
        Traceback (most recent call last):
            ...
        ValueError: Locus objects in LocusMap must be unique
        """
        locus_list = [Locus(list_of_dict[index]['chrom'],
                            list_of_dict[index]['start'],
                            list_of_dict[index]['end'],
                            **{key: list_of_dict[index][key]
                               for key in list_of_dict[index]
                               if key not in ['chrom', 'start', 'end']})
                      for index in range(len(list_of_dict))]
        instance = cls(locus_list)
        instance.log_event('created from list of dict')
        return instance

    @classmethod
    def from_list(cls, list_of_locusmaps):
        r"""
        Factory method that creates a new LocusMap object from a list of
        existing LocusMap objects by concatenation.

        Parameters
        ----------
        list_of_locusmaps : list of LocusMap
            A list of LocusMap objects to be concatenated.

        Returns
        -------
        LocusMap
            The concatenated LocusMap.

        Notes
        -----
        This function should be slightly more efficient than iterative addition.
        Therefore, it is preferred to use
        ::

            summed_locus_map = LocusMap.from_list(list_of_locus_maps)

        over
        ::

            summed_locus_map = sum(list_of_locus_maps, LocusMap([]))

        as evidenced by
        ::

            > python -mtimeit `
              -s'from lib5c.core.loci import LocusMap' `
              -s'lm = LocusMap.from_primerfile(\"test/primers.bed\")' `
              -s'lm_list = [lm.extract_region(r) for r in lm.regions]' `
              's = LocusMap.from_list(lm_list)'
            10 loops, best of 3: 48.2 msec per loop

        versus
        ::

            > python -mtimeit `
              -s'from lib5c.core.loci import LocusMap' `
              -s'lm = LocusMap.from_primerfile(\"test/primers.bed\")' `
              -s'lm_list = [lm.extract_region(r) for r in lm.regions]' `
              's = sum(lm_list, LocusMap([]))'
            10 loops, best of 3: 174 msec per loop

        Examples
        --------
        >>> from lib5c.core.loci import LocusMap
        >>> locus_map = LocusMap.from_primerfile('test/primers.bed')
        >>> sox2_locus_map = locus_map.extract_region('Sox2')
        >>> sox2_locus_map.size()
        265
        >>> sox2_locus_map.get_regions()
        ['Sox2']
        >>> klf4_locus_map = locus_map.extract_region('Klf4')
        >>> klf4_locus_map.size()
        251
        >>> klf4_locus_map.get_regions()
        ['Klf4']
        >>> summed_locus_map = LocusMap.from_list([sox2_locus_map,
        ...                                        klf4_locus_map])
        ...
        >>> summed_locus_map.print_log()
        LocusMap created
        created from list
        >>> summed_locus_map.size()
        516
        >>> summed_locus_map.get_regions()
        ['Sox2', 'Klf4']
        >>> builtin_sum_result = sum([sox2_locus_map, klf4_locus_map],
        ...                          LocusMap([]))
        ...
        >>> builtin_sum_result.size()
        516
        >>> builtin_sum_result.get_regions()
        ['Sox2', 'Klf4']
        """
        instance = cls([locus for locusmap in list_of_locusmaps
                        for locus in locusmap])
        instance.log_event('created from list')
        for existing_locusmap in list_of_locusmaps:
            instance.data.update(existing_locusmap.data)
        return instance

    def __str__(self):
        """
        Gets a pretty string representation of this LocusMap.

        Returns
        -------
        str
            String representation of this LocusMap.

        Examples
        --------
        >>> from lib5c.core.loci import LocusMap
        >>> locus_map = LocusMap.from_primerfile('test/primers.bed')
        >>> locus_map.set_value('primerset', '314_ES-NPC')
        >>> print locus_map
        LocusMap comprising 1551 loci
            Range: chr3:34107373-34109023 to chr17:36526480-36528893
            Regions: ['Sox2', 'Nestin', 'Klf4', 'gene-desert', 'Nanog-V2',
                      'Olig1-Olig2', 'Oct4']
            primerset: 314_ES-NPC
        >>> empty_locus_map = LocusMap([])
        >>> print empty_locus_map
        Empty LocusMap
        """
        if self.size():
            string_repr = 'LocusMap comprising %i loci' \
                          '\n\tRange: %s:%i-%i to %s:%i-%i' %\
                          (self.size(), self[0].chrom, self[0].start,
                           self[0].end, self[-1].chrom, self[-1].start,
                           self[-1].end)
            if self.get_regions():
                string_repr += '\n\tRegions: %s' % self.get_regions()
            if self.data:
                string_repr += Annotatable.__str__(self)
        else:
            string_repr = 'Empty LocusMap'
        return string_repr

    def __iter__(self):
        """
        Iterator for LocusMap.

        Yields
        ------
        Locus
            The next Locus object in the LocusMap.

        Examples
        --------
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [Locus('chr3', 34109023, 34113109),
        ...               Locus('chr3', 34113147, 34116141)]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> for locus in locus_map:
        ...     print locus
        ...
        Locus chr3:34109023-34113109
        Locus chr3:34113147-34116141
        >>> locus_list_rev = [Locus('chr3', 34113147, 34116141),
        ...                   Locus('chr3', 34109023, 34113109)]
        ...
        >>> locus_map_rev = LocusMap(locus_list_rev)
        >>> for locus in locus_map_rev:
        ...     print locus  # still prints in order of genomic coordinate
        ...
        Locus chr3:34109023-34113109
        Locus chr3:34113147-34116141
        """
        index = 0
        while index < len(self.locus_list):
            yield self.locus_list[index]
            index += 1

    def __getitem__(self, item):
        """
        Provides shortcuts to access selected Locus objects of this LocusMap.

        Parameters
        ----------
        item : int or str or slice
            Pass a Locus name as a string to get the Locus with that name. Pass
            an int to get the Locus object at that index. Pass a slice to get
            a new LocusMap representing the subset of Locus objects with the
            specified indices.

        Returns
        -------
        Locus or LocusMap
            The desired Locus if ``item`` is an int or str. The desired
            LocusMap if ``item`` is a slice.

        Examples
        --------
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [
        ...     Locus('chr3', 34109023, 34113109, name='Sox2_FOR_2'),
        ...     Locus('chr3', 34113147, 34116141, name='Sox2_REV_4'),
        ...     Locus('chr3', 87282063, 87285636, name='Nestin_REV_9'),
        ...     Locus('chr3', 87285637, 87295935, name='Nestin_FOR_10')
        ... ]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> print locus_map[1]
        Locus chr3:34113147-34116141
            name: Sox2_REV_4
        >>> print locus_map['Sox2_REV_4']
        Locus chr3:34113147-34116141
            name: Sox2_REV_4
        >>> sliced_map = locus_map[1:3]
        >>> for locus in sliced_map:
        ...     print locus
        ...
        Locus chr3:34113147-34116141
            name: Sox2_REV_4
        Locus chr3:87282063-87285636
            name: Nestin_REV_9
        """
        if type(item) == int:
            return self.locus_list[item]
        elif type(item) == str:
            return self.by_name(item)
        elif type(item) == slice:
            return self.extract_slice(item)

    def __add__(self, other):
        """
        Defines the addition of two LocusMap objects by concatenation.

        Parameters
        ----------
        other : LocusMap
            The other LocusMap to add this one to.

        Returns
        -------
        LocusMap
            The concatenation of both LocusMap objects.

        Examples
        --------
        >>> from lib5c.core.loci import LocusMap
        >>> locus_map = LocusMap.from_primerfile('test/primers.bed')
        >>> sox2_locus_map = locus_map.extract_region('Sox2')
        >>> sox2_locus_map.size()
        265
        >>> sox2_locus_map.get_regions()
        ['Sox2']
        >>> klf4_locus_map = locus_map.extract_region('Klf4')
        >>> klf4_locus_map.size()
        251
        >>> klf4_locus_map.get_regions()
        ['Klf4']
        >>> added_locus_map = sox2_locus_map + klf4_locus_map
        >>> added_locus_map.print_log()
        LocusMap created
        created from addition
        >>> added_locus_map.size()
        516
        >>> added_locus_map.get_regions()
        ['Sox2', 'Klf4']
        """
        instance = LocusMap(self.locus_list + other.locus_list)
        instance.log_event('created from addition')
        instance.data.update(self.data)
        instance.data.update(other.data)
        return instance

    def delete(self, index):
        """
        Creates a new LocusMap object that excludes the Locus at a specified
        index.

        Parameters
        ----------
        index : int
            The index of the Locus to exclude.

        Returns
        -------
        LocusMap
            The new LocusMap.

        Examples
        --------
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [
        ...     Locus('chr3', 34109023, 34113109, name='Sox2_FOR_2'),
        ...     Locus('chr3', 34113147, 34116141, name='Sox2_REV_4'),
        ...     Locus('chr3', 87282063, 87285636, name='Nestin_REV_9'),
        ...     Locus('chr3', 87285637, 87295935, name='Nestin_FOR_10')
        ... ]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> deleted_locus_map = locus_map.delete(2)
        >>> deleted_locus_map.print_log()
        LocusMap created
        deleted locus at index 2 with name Nestin_REV_9
        >>> for locus in deleted_locus_map:
        ...    print locus
        Locus chr3:34109023-34113109
            name: Sox2_FOR_2
        Locus chr3:34113147-34116141
            name: Sox2_REV_4
        Locus chr3:87285637-87295935
            name: Nestin_FOR_10
        """
        instance = LocusMap([self.locus_list[i] for i in range(self.size())
                             if i != index])
        instance.data = self.data
        instance.log = copy(self.log)
        deleted_name = self.locus_list[index].get_name()
        if deleted_name is not None:
            instance.log_event('deleted locus at index %i with name %s' %
                               (index, deleted_name))
        else:
            instance.log_event('deleted locus at index %i' % index)
        return instance

    def size(self):
        """
        Get the number of Locus objects in the LocusMap.

        Returns
        -------
        int
            The number of Locus objects in the LocusMap.

        Examples
        --------
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [Locus('chr3', 34109023, 34113109),
        ...               Locus('chr3', 34113147, 34116141)]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> locus_map.size()
        2
        """
        return len(self.locus_list)

    def by_name(self, name):
        """
        Get the Locus object contained in this LocusMap with a specified name.

        Parameters
        ----------
        name : str
            The name of the Locus to get.

        Returns
        -------
        Locus
            The Locus object with the specified name.

        Examples
        --------
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [Locus('chr3', 34109023, 34113109, name='Sox2_FOR_2'),
        ...               Locus('chr3', 34113147, 34116141, name='Sox2_REV_4')]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> print locus_map.by_name('Sox2_REV_4')
        Locus chr3:34113147-34116141
            name: Sox2_REV_4
        """
        if name in self.name_dict:
            return self.name_dict[name]
        else:
            raise ValueError('primer with name %s does not exist' % name)

    def get_index_by_hash(self, hash_value):
        """
        Get the Locus object contained in this LocusMap with a specified hash.

        Parameters
        ----------
        hash_value : int
            The hash of the Locus object to find.

        Returns
        -------
        int or None
            The index of the desired Locus object within ``locus_list`` if it
            exists within this LocusMap object, or None if it doesn't.

        Examples
        --------
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [Locus('chr3', 34109023, 34113109),
        ...               Locus('chr3', 34113147, 34116141)]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> locus_hash = hash(Locus('chr3', 34113147, 34116141))
        >>> locus_map.get_index_by_hash(locus_hash)
        1
        >>> locus_map.get_index_by_hash(123) is None
        True
        """
        if hash_value in self.hash_to_index_dict:
            return self.hash_to_index_dict[hash_value]
        else:
            return None

    def by_index(self, index):
        """
        Get the Locus object contained in this LocusMap with a specified index.

        Parameters
        ----------
        index : int
            The index of the Locus to get.

        Returns
        -------
        Locus
            The Locus object with the specified index.

        Examples
        --------
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [Locus('chr3', 34109023, 34113109, name='Sox2_FOR_2'),
        ...               Locus('chr3', 34113147, 34116141, name='Sox2_REV_4')]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> print locus_map.by_index(1)
        Locus chr3:34113147-34116141
            name: Sox2_REV_4
        """
        if index < 0:
            raise ValueError('index must be nonnegative')
        if index >= len(self.locus_list):
            raise ValueError('index %s larger than number of primers' % index)
        return self.locus_list[index]

    def by_region_index(self, region, index):
        """
        Get the Locus object contained in this LocusMap with a specified index
        within a specified region. In other words, the ``index`` th Locus of the
        region with name ``region``.

        Parameters
        ----------
        region : str
            The name of the region to look for the Locus in.
        index : int
            The index of the desired Locus within the specified region.

        Returns
        -------
        Locus
            The specified Locus.

        Examples
        --------
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [Locus('chr3', 34109023, 34113109, region='Sox2'),
        ...               Locus('chr3', 34113147, 34116141, region='Sox2'),
        ...               Locus('chr3', 87282063, 87285636, region='Nestin'),
        ...               Locus('chr3', 87285637, 87295935, region='Nestin')]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> print locus_map.by_region_index('Nestin', 1)
        Locus chr3:87285637-87295935
            region: Nestin
        """
        if region in self.region_index_dict:
            if index < 0:
                raise ValueError('index must be nonnegative')
            if index >= len(self.region_index_dict[region]):
                raise ValueError('index %s bigger than region size' % index)
            return self.region_index_dict[region][index]
        else:
            raise ValueError('region with name %s does not exist' % region)

    def as_list_of_dict(self):
        """
        Gets a primitive representation of the LocusMap. Converts the
        ``locus_list`` attribute of this LocusMap from a list of Locus objects
        to a list of dicts representing those Locus objects.

        Returns
        -------
        list of dict
            The primitive representation of the LocusMap.

        Examples
        --------
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [Locus('chr3', 34109023, 34113109, name='Sox2_FOR_2'),
        ...               Locus('chr3', 34113147, 34116141, name='Sox2_REV_4')]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> print locus_map.as_list_of_dict()
        [{'start': 34109023, 'end': 34113109, 'chrom': 'chr3', 'name':
        'Sox2_FOR_2'}, {'start': 34113147, 'end': 34116141, 'chrom': 'chr3',
        'name': 'Sox2_REV_4'}]
        """
        return [locus.as_dict() for locus in self.locus_list]

    def as_dict_of_list_of_dict(self):
        """
        Gets a primitive representation of the LocusMap, organized by region.
        Converts the ``locus_list`` attribute of this LocusMap from a list of
        Locus objects to dict whose keys are region names as strings and whose
        values are list of dicts representing the Locus objects in each region.

        Returns
        -------
        dict(str -> list of dict)
            The primitive representation of the LocusMap.

        Examples
        --------
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [Locus('chr3', 34109023, 34113109, region='Sox2'),
        ...               Locus('chr3', 34113147, 34116141, region='Sox2'),
        ...               Locus('chr3', 87282063, 87285636, region='Nestin'),
        ...               Locus('chr3', 87285637, 87295935, region='Nestin')]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> print locus_map.as_dict_of_list_of_dict()
        {'Sox2': [{'start': 34109023, 'region': 'Sox2', 'end': 34113109,
        'chrom': 'chr3'}, {'start': 34113147, 'region': 'Sox2', 'end':
        34116141, 'chrom': 'chr3'}], 'Nestin': [{'start': 87282063, 'region':
        'Nestin', 'end': 87285636, 'chrom': 'chr3'}, {'start': 87285637,
        'region': 'Nestin', 'end': 87295935, 'chrom': 'chr3'}]}
        """
        return {region: [locus.as_dict()
                         for locus in self.locus_list
                         if locus.get_region() == region]
                for region in self.regions}

    def get_regions(self):
        """
        Gets the regions spanned by the Locus objects in this LocusMap.

        Returns
        -------
        list of str
            The ordered list of region names.

        Examples
        --------
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [Locus('chr3', 34109023, 34113109, region='Sox2'),
        ...               Locus('chr3', 34113147, 34116141, region='Sox2'),
        ...               Locus('chr3', 87282063, 87285636, region='Nestin'),
        ...               Locus('chr3', 87285637, 87295935, region='Nestin')]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> print locus_map.get_regions()
        ['Sox2', 'Nestin']
        """
        return self.regions

    def get_region_sizes(self):
        """
        Gets information about the number of Locus objects in each region.

        Returns
        -------
        dict(str -> int)
            A dict mapping region names as strings to the number of Locus
            objects in that region.

        Examples
        --------
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [Locus('chr3', 34109023, 34113109, region='Sox2'),
        ...               Locus('chr3', 34113147, 34116141, region='Sox2'),
        ...               Locus('chr3', 87282063, 87285636, region='Nestin')]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> print locus_map.get_region_sizes()
        {'Sox2': 2, 'Nestin': 1}
        """
        return {region: len(self.region_index_dict[region])
                for region in self.regions}

    def extract_region(self, region):
        """
        Create a LocusMap representing the Locus objects in only one specified
        region of this LocusMap.

        Parameters
        ----------
        region : str
            The name of the region to extract.

        Returns
        -------
        LocusMap
            A new LocusMap restricted to the specified region.

        Examples
        --------
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [Locus('chr3', 34109023, 34113109, region='Sox2'),
        ...               Locus('chr3', 34113147, 34116141, region='Sox2'),
        ...               Locus('chr3', 87282063, 87285636, region='Nestin'),
        ...               Locus('chr3', 87285637, 87295935, region='Nestin')]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> extracted_locus_map = locus_map.extract_region('Sox2')
        >>> extracted_locus_map.print_log()
        LocusMap created
        extracted region Sox2
        >>> for locus in extracted_locus_map:
        ...     print locus
        ...
        Locus chr3:34109023-34113109
            region: Sox2
        Locus chr3:34113147-34116141
            region: Sox2
        """
        if region not in self.regions:
            raise ValueError('region with name %s does not exist' % region)
        instance = LocusMap(locus_list=self.region_index_dict[region])
        instance.log = copy(self.log)
        instance.data = self.data
        instance.log_event('extracted region %s' % region)
        return instance

    def extract_slice(self, desired_slice):
        """
        Gets a new LocusMap object representing a subset of the Locus objects
        in this LocusMap specified by a slice.

        Parameters
        ----------
        desired_slice : slice
            The slice to use to subset this LocusMap.

        Returns
        -------
        LocusMap
            The new LocusMap.

        Notes
        -----
        Since LocusMap objects are sorted, the returned LocusMap will always be
        sorted, regardless of the slice direction.

        Examples
        --------
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [
        ...     Locus('chr3', 34109023, 34113109, name='Sox2_FOR_2'),
        ...     Locus('chr3', 34113147, 34116141, name='Sox2_REV_4'),
        ...     Locus('chr3', 87282063, 87285636, name='Nestin_REV_9'),
        ...     Locus('chr3', 87285637, 87295935, name='Nestin_FOR_10')
        ... ]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> sliced_map = locus_map[1:3]
        >>> sliced_map.print_log()
        LocusMap created
        sliced out slice(1, 3, None)
        >>> for locus in sliced_map:
        ...     print locus
        ...
        Locus chr3:34113147-34116141
            name: Sox2_REV_4
        Locus chr3:87282063-87285636
            name: Nestin_REV_9
        """
        instance = LocusMap(self.locus_list[desired_slice])
        instance.log = copy(self.log)
        instance.data = self.data
        instance.log_event('sliced out %s' % desired_slice)
        return instance

    def get_index(self, name):
        """
        Get the index of the Locus object in this LocusMap with a specified
        name.

        Parameters
        ----------
        name : str
            The name of the Locus to get the index for.

        Returns
        -------
        int
            The index of the Locus object with the specified name.

        Examples
        --------
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [Locus('chr3', 34109023, 34113109, name='Sox2_FOR_2'),
        ...               Locus('chr3', 34113147, 34116141, name='Sox2_REV_4')]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> print locus_map.get_index('Sox2_REV_4')
        1
        """
        if name in self.name_to_index_dict:
            return self.name_to_index_dict[name]
        else:
            raise ValueError('primer with name %s does not exist' % name)

    def to_bedfile(self, filename, fields=('name',)):
        """
        Write this LocusMap to disk as a BED-formatted file.

        Parameters
        ----------
        filename : str
            String reference to the file to write to.
        fields : list of str, optional
            Specify additional columns in the BED file after the traditional
            chromosome, start, end. Columns should be specified in order as
            strings corresponding to keys in the ``data`` attributes on the
            Locus objects that make up this LocusMap.

        Examples
        --------
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> lm1 = LocusMap([
        ...     Locus('chr3', 34109023, 34113109, name='5C_329_Sox2_FOR_2'),
        ...     Locus('chr3', 34113147, 34116141, name='5C_329_Sox2_REV_4')
        ... ])
        ...
        >>> lm1.to_bedfile('test/core_test_locusmap.bed')
        >>> lm2 = LocusMap.from_primerfile('test/core_test_locusmap.bed')
        >>> for locus in lm2:
        ...     print locus
        Locus chr3:34109023-34113109
            orientation: 3'
            region: Sox2
            name: 5C_329_Sox2_FOR_2
            strand: +
            number: 2
        Locus chr3:34113147-34116141
            orientation: 5'
            region: Sox2
            name: 5C_329_Sox2_REV_4
            strand: -
            number: 4
        """
        with open(filename, 'w') as handle:
            for locus in self.locus_list:
                handle.write('%s\t%i\t%i' % (locus.chrom, locus.start,
                                             locus.end))
                for field in fields:
                    handle.write('\t%s' % locus.get_value(field))
                handle.write('\n')
