from copy import deepcopy, copy
from math import sqrt

import numpy as np

from lib5c.core.loci import LocusMap
from lib5c.core.mixins import Picklable, Annotatable, Loggable
from lib5c.parsers.counts import load_counts_by_name, set_cis_trans_nans
from lib5c.util.counts import flatten_regional_counts
from lib5c.writers.counts import write_cis_trans_counts


class InteractionMatrix(object, Picklable, Annotatable, Loggable):
    """
    Class representing pairwise architectural contact frequencies between
    genomic loci. At its heart, this is a square, symmetric matrix whose
    :math:`ij` th entry corresponds to the interaction frequency between the
    :math:`i` th genomic locus and the :math:`j` th genomic locus. Optionally,
    some metadata for the genomic loci may be included.

    Attributes
    ----------
    matrix : square, symmetric numpy matrix
        The matrix of interaction frequencies.
    locusmap : LocusMap, optional
            Metadata for the genomic loci in the form of a LocusMap object. The
            size of the LocusMap passed should be equal to the size of
            ``matrix``.

    Notes
    -----
    Several accessor shortcuts are provided via this class's implementation of
    ``__getitem__()``. Consult that function's docstring for more details.

    Some elements of the ``matrix`` of an InteractionMatrix may be set to
    ``np.nan`` in cases where data is not available or where interactions are
    impossible. Impossible interactions are those involving fragments with the
    same directionality. If a LocusMap whose constituent Locus objects have
    ``strand`` keys in their ``data`` attribute is provided when an
    InteractionMatrix is created, the impossible interactions will be set to
    ``np.nan`` automatically.
    """

    def __init__(self, matrix, locusmap=None):
        """
        Constructor.

        Parameters
        ----------
        matrix : square, symmetric numpy matrix
            The matrix interaction frequencies.
        locusmap : LocusMap, optional
            Metadata for the genomic loci in the form of a LocusMap object. The
            size of the LocusMap passed should be equal to the size of
            ``matrix``.
        """
        if locusmap is not None and locusmap.size() != len(matrix):
            raise ValueError('locusmap and matrix size mismatch')
        self.matrix = np.matrix(matrix)
        self.locusmap = locusmap
        if self.locusmap is not None:
            set_cis_trans_nans(self.matrix, self.locusmap.as_list_of_dict())
        Annotatable.__init__(self)
        Loggable.__init__(self)
        self.log_event('InteractionMatrix created')

    @classmethod
    def from_countsfile(cls, countsfile, locusmap=None, primerfile=None,
                        binfile=None):
        """
        Factory method that creates an InteractionMatrix object from a .counts
        file.

        Parameters
        ----------
        countsfile : str
            String reference to the .counts file to parse.
        locusmap : LocusMap, optional
            Metadata for the genomic loci in the form of a LocusMap object.
        primerfile : str, optional
            String reference to a BED file containing primer information to be
            parsed and used as metadata for the genomic loci.
        binfile : str, optional
            String reference to a BED file containing bin information to be
            parsed and used as metadata for the genomic loci.

        Returns
        -------
        InteractionMatrix
            InteractionMatrix object parsed from the .counts file.

        Notes
        -----
        At least one of ``locusmap``, ``primerfile``, or ``binfile`` must be
        passed. The ``matrix`` attribute of the returned InteractionMatrix will
        have the same size as whichever of these was passed.

        Examples
        --------
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> im = InteractionMatrix.from_countsfile(
        ...     'test/test_raw.counts', primerfile='test/primers.bed')
        ...
        >>> im.print_log()
        InteractionMatrix created
        source countsfile: test/test_raw.counts
        source primerfile: test/primers.bed
        >>> im.locusmap.size()
        1551
        >>> im.size()
        1551
        >>> im['5C_325_Olig1-Olig2_FOR_38', '5C_331_gene-desert_REV_62']
        1.0
        >>> im['5C_325_Olig1-Olig2_REV_237', '5C_325_Olig1-Olig2_REV_230']
        nan
        """
        if primerfile:
            locusmap = LocusMap.from_primerfile(primerfile)
        elif binfile:
            locusmap = LocusMap.from_binfile(binfile)
        if locusmap is None:
            raise ValueError('insufficient parameters for InteractionMatrix'
                             'creation')
        matrix = load_counts_by_name(countsfile, locusmap=locusmap)
        instance = cls(matrix, locusmap=locusmap)
        instance.log_event('source countsfile: %s' % countsfile)
        if primerfile is not None:
            instance.log_event('source primerfile: %s' % primerfile)
        if binfile is not None:
            instance.log_event('source binfile: %s' % binfile)
        return instance

    @classmethod
    def from_primerfile(cls, primerfile):
        """
        Factory method that creates an InteractionMatrix object whose ``matrix``
        attribute is initialized with all zeros and whose genomic loci are
        described by data parsed from a BED file containing primer information.

        Parameters
        ----------
        primerfile : str
            String reference to a BED file containing primer information to be
            parsed and used as metadata for the genomic loci.

        Returns
        -------
        InteractionMatrix
            InteractionMatrix object.

        Examples
        --------
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> im = InteractionMatrix.from_primerfile('test/primers.bed')
        >>> im.print_log()
        InteractionMatrix created
        source primerfile: test/primers.bed
        >>> im.locusmap.size()
        1551
        >>> im.size()
        1551
        >>> im['5C_325_Olig1-Olig2_FOR_38', '5C_331_gene-desert_REV_62']
        0.0
        >>> im['5C_325_Olig1-Olig2_REV_237', '5C_325_Olig1-Olig2_REV_230']
        nan
        """
        locusmap = LocusMap.from_primerfile(primerfile)
        size = locusmap.size()
        matrix = np.zeros([size, size])
        instance = cls(matrix, locusmap=locusmap)
        instance.log_event('source primerfile: %s' % primerfile)
        return instance

    @classmethod
    def from_binfile(cls, binfile):
        """
        Factory method that creates an InteractionMatrix object whose ``matrix``
        attribute is initialized with all zeros and whose genomic loci are
        described by data parsed from a BED file containing bin information.

        Parameters
        ----------
        binfile : str
            String reference to a BED file containing bin information to be
            parsed and used as metadata for the genomic loci.

        Returns
        -------
        InteractionMatrix
            InteractionMatrix object.

        Examples
        --------
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> im = InteractionMatrix.from_binfile('test/bins_new.bed')
        >>> im.print_log()
        InteractionMatrix created
        source binfile: test/bins_new.bed
        >>> im.locusmap.size()
        1807
        >>> im.size()
        1807
        >>> im['gene-desert_BIN_047', 'Nestin_BIN_000']
        0.0
        """
        locusmap = LocusMap.from_binfile(binfile)
        size = locusmap.size()
        matrix = np.zeros([size, size])
        instance = cls(matrix, locusmap=locusmap)
        instance.log_event('source binfile: %s' % binfile)
        return instance

    @classmethod
    def from_locusmap(cls, locusmap):
        """
        Factory method that creates an InteractionMatrix object whose ``matrix``
        attribute is initialized with all zeros and whose genomic loci are
        described by a LocusMap object.

        Parameters
        ----------
        locusmap : LocusMap
            Metadata for the genomic loci in the form of a LocusMap object.

        Returns
        -------
        InteractionMatrix
            InteractionMatrix object.

        Examples
        --------
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> from lib5c.core.loci import LocusMap, Locus
        >>> locus_list = [Locus('chr3', 34109023, 34113109),
        ...               Locus('chr3', 34113147, 34116141)]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> im = InteractionMatrix.from_locusmap(locus_map)
        >>> im.print_log()
        InteractionMatrix created
        created from locusmap
        >>> im.matrix
        matrix([[0., 0.],
                [0., 0.]])
        """
        size = locusmap.size()
        matrix = np.zeros([size, size])
        instance = cls(matrix, locusmap=locusmap)
        instance.log_event('created from locusmap')
        return instance

    @classmethod
    def from_size(cls, size):
        """
        Factory method that creates an InteractionMatrix object whose ``matrix``
        attribute is initialized with all zeros and whose size is specified.

        Parameters
        ----------
        size : int
            Size of the ``matrix`` attribute of the desired InteractionMatrix
            object.

        Returns
        -------
        InteractionMatrix
            InteractionMatrix object.

        Examples
        --------
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> im = InteractionMatrix.from_size(2)
        >>> im.print_log()
        InteractionMatrix created
        created from size 2
        >>> im.matrix
        matrix([[0., 0.],
                [0., 0.]])
        """
        matrix = np.zeros([size, size])
        instance = cls(matrix)
        instance.log_event('created from size %i' % size)
        return instance

    @classmethod
    def from_list(cls, list_of_interaction_matrices):
        """
        Factory method that creates an InteractionMatrix object via iterative
        addition of a list of InteractionMatrix objects.

        Parameters
        ----------
        list_of_interaction_matrices : list of InteractionMatrix
            The InteractionMatrix objects to concatenate.

        Returns
        -------
        InteractionMatrix
            The resulting InteractionMatrix.

        Notes
        -----
        This function operates via naive iterate addition and so the following
        are basically equivalent::

            summed_im = InteractionMatrix.from_list(list_of_im)
            summed_im = sum(list_of_im, InteractionMatrix([]))

        Neither implementation is particularly efficient. See the Examples
        section for details.

        Examples
        --------
        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> im1 = InteractionMatrix(np.matrix([[1.0, 2.0], [2.0, 1.0]]))
        >>> im2 = InteractionMatrix(np.matrix([[3.0, 4.0], [4.0, 3.0]]))
        >>> summed_im = InteractionMatrix.from_list([im1, im2])
        >>> summed_im.print_log()
        InteractionMatrix created
        created from addition
        created from list
        >>> summed_im.matrix
        matrix([[1., 2., 0., 0.],
                [2., 1., 0., 0.],
                [0., 0., 3., 4.],
                [0., 0., 4., 3.]])

        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> im1 = InteractionMatrix(np.matrix([[np.nan, 1.0], [1.0, np.nan]]),
        ...                         locusmap=LocusMap([
        ...     Locus('chr3', 34109023, 34113109, name='5C_329_Sox2_FOR_2',
        ...           strand='+'),
        ...     Locus('chr3', 34113147, 34116141, name='5C_329_Sox2_REV_4',
        ...           strand='-')]))
        ...
        >>> im2 = InteractionMatrix(np.matrix([[np.nan, 2.0], [2.0, np.nan]]),
        ...                         locusmap=LocusMap([
        ...     Locus('chr3', 87282063, 87285636, name='5C_326_Nestin_REV_9',
        ...           strand='-'),
        ...     Locus('chr3', 87285637, 87295935, name='5C_326_Nestin_FOR_10',
        ...           strand='+')]))
        ...
        >>> summed_im = InteractionMatrix.from_list([im1, im2])
        >>> summed_im.matrix
        matrix([[nan,  1.,  0., nan],
                [ 1., nan, nan,  0.],
                [ 0., nan, nan,  2.],
                [nan,  0.,  2., nan]])
        """
        instance = sum(list_of_interaction_matrices, InteractionMatrix([]))
        instance.log_event('created from list')
        for existing_im in list_of_interaction_matrices:
            instance.data.update(existing_im.data)
        return instance

    def __str__(self):
        """
        Gets a pretty string representation of this InteractionMatrix.

        Returns
        -------
        str
            String representation of this InteractionMatrix.

        Examples
        --------
        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> X = np.reshape(range(16), (4, 4)).astype(float)
        >>> counts = X + X.T
        >>> im = InteractionMatrix(counts,
        ...                        locusmap=LocusMap([
        ...     Locus('chr3', 34109023, 34113109, name='5C_329_Sox2_FOR_2',
        ...           strand='+', region='Sox2'),
        ...     Locus('chr3', 34113147, 34116141, name='5C_329_Sox2_REV_4',
        ...           strand='-', region='Sox2'),
        ...     Locus('chr3', 87282063, 87285636, name='5C_326_Nestin_REV_9',
        ...           strand='-', region='Nestin'),
        ...     Locus('chr3', 87285637, 87295935, name='5C_326_Nestin_FOR_10',
        ...           strand='+', region='Nestin')]))
        ...
        >>> im.set_value('replicate', 1)
        >>> print im
        InteractionMatrix of size 4
        [[nan  5. 10. nan]
         [ 5. nan nan 20.]
         [10. nan nan 25.]
         [nan 20. 25. nan]]
        Annotation:
            replicate: 1
        Associated LocusMap:
        LocusMap comprising 4 loci
            Range: chr3:34109023-34113109 to chr3:87285637-87295935
            Regions: ['Sox2', 'Nestin']
        """
        string_repr = 'InteractionMatrix of size %i' % self.size()
        string_repr += '\n' + str(self.matrix)
        if self.data:
            string_repr += '\nAnnotation:'
            string_repr += Annotatable.__str__(self)
        if self.locusmap is not None:
            string_repr += '\nAssociated LocusMap:'
            string_repr += '\n' + str(self.locusmap)
        return string_repr

    def __getitem__(self, item):
        """
        Provides shortcuts to access selected submatrices or elements of this
        InteractionMatrix.

        Parameters
        ----------
        item : str or tuple of int or tuple of str
            Pass a region name as a string to get the submatrix corresponding
            to that region as a new InteractionMatrix. Pass a Locus name as a
            string to get the index of that Locus within this InteractionMatrix.
            Pass a tuple of two ints :math:`(i, j)` to get the :math:`ij` th
            entry of this InteractionMatrix's matrix. Pass a tuple of two Locus
            names as strings to get the corresponding entry from this
            InteractionMatrix's matrix.

        Returns
        -------
        InteractionMatrix or int or float
            If ``item`` is a string corresponding to a region name, an
            InteractionMatrix is returned. If ``item`` is a string corresponding
            to a Locus name, an int is returned. If ``item`` is a tuple, a float
            is returned.

        Examples
        --------
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> im = InteractionMatrix.from_countsfile(
        ...     'test/test_raw.counts', primerfile='test/primers.bed')
        ...
        >>> im['5C_325_Olig1-Olig2_FOR_38', '5C_331_gene-desert_REV_62']
        1.0
        >>> i = im['5C_325_Olig1-Olig2_FOR_38']
        >>> i
        985
        >>> j = im['5C_331_gene-desert_REV_62']
        >>> j
        763
        >>> im[i, j]
        1.0
        >>> sox2_im = im['Sox2']
        >>> im.get_regions()
        ['Sox2', 'Nestin', 'Klf4', 'gene-desert', 'Nanog-V2', 'Olig1-Olig2',
        'Oct4']
        >>> im.size()
        1551
        >>> sox2_im.get_regions()
        ['Sox2']
        >>> sox2_im.size()
        265
        >>> sliced_im = im[100:200]
        >>> sliced_im.size()
        100
        """
        if type(item) == str:
            if item in self.locusmap.get_regions():
                return self.extract_region(item)
            else:
                return self.locusmap.get_index(item)
        elif type(item) == tuple:
            if type(item[0]) == int:
                return self.matrix[item]
            elif type(item[0]) == str:
                return self.matrix[self.locusmap.get_index(item[0]),
                                   self.locusmap.get_index(item[1])]
        elif type(item) == slice:
            return self.extract_slice(item)

    def __setitem__(self, key, value):
        """
        Provides value-setting versions of the shortcuts implemented in this
        class's implementation of ``__getitem__()``.

        Parameters
        ----------
        key : tuple of int or tuple of str
            Identifies what element of ``matrix`` should be set. Pass a tuple of
            two ints :math:`(i, j)` to set the :math:`ij` th entry of this
            InteractionMatrix's matrix. Pass a tuple of two Locus names as
            strings to set the corresponding entry from this InteractionMatrix's
            matrix.
        value : float
            The value to set this InteractionMatrix object's matrix to at the
            position specified by ``key``.

        Examples
        --------
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> im = InteractionMatrix.from_countsfile(
        ...     'test/test_raw.counts', primerfile='test/primers.bed')
        ...
        >>> im['5C_325_Olig1-Olig2_FOR_38', '5C_331_gene-desert_REV_62']
        1.0
        >>> im['5C_325_Olig1-Olig2_FOR_38', '5C_331_gene-desert_REV_62'] = 2.0
        >>> im['5C_325_Olig1-Olig2_FOR_38', '5C_331_gene-desert_REV_62']
        2.0
        >>> im['5C_331_gene-desert_REV_62', '5C_325_Olig1-Olig2_FOR_38']
        2.0
        >>> i = im['5C_325_Olig1-Olig2_FOR_38']
        >>> i
        985
        >>> j = im['5C_331_gene-desert_REV_62']
        >>> j
        763
        >>> im[i, j]
        2.0
        >>> im[i, j] = 3.0
        >>> im[i, j]
        3.0
        >>> im[j, i]
        3.0

        >>> from lib5c.core.interactions import InteractionMatrix
        >>> im = InteractionMatrix.from_primerfile('test/primers.bed')
        >>> im['5C_325_Olig1-Olig2_FOR_38', '5C_331_gene-desert_REV_62'] = 2.0
        >>> im['5C_325_Olig1-Olig2_FOR_38', '5C_331_gene-desert_REV_62']
        2.0
        """
        if type(key[0]) == int:
            self.matrix[key] = value
            self.matrix[key[::-1]] = value
        else:
            self.matrix[self.locusmap.get_index(key[0]),
                        self.locusmap.get_index(key[1])] = value
            self.matrix[self.locusmap.get_index(key[1]),
                        self.locusmap.get_index(key[0])] = value

    def __add__(self, other):
        """
        Defines the addition of two InteractionMatrix objects by
        concatenation.

        Parameters
        ----------
        other : InteractionMatrix
            The other InteractionMatrix to add to this one.

        Returns
        -------
        InteractionMatrix
            The concatenated InteractionMatrix.

        Notes
        -----
        The InteractionMatrices are concatenated as block matrices with the
        offdiagonal blocks set to all zeros, except at impossible
        interactions which are set to ``np.nan``.

        If both InteractionMatrix objects being concatenated have associated
        ``locusmap`` attributes, these LocusMap objects will also be
        concatenated.

        Examples
        --------
        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> im1 = InteractionMatrix(np.matrix([[1.0, 2.0], [2.0, 1.0]]))
        >>> im2 = InteractionMatrix(np.matrix([[3.0, 4.0, 5.0],
        ...                                    [4.0, 6.0, 7.0],
        ...                                    [5.0, 7.0, 8.0]]))
        ...
        >>> added_im = im1 + im2
        >>> added_im.matrix
        matrix([[1., 2., 0., 0., 0.],
                [2., 1., 0., 0., 0.],
                [0., 0., 3., 4., 5.],
                [0., 0., 4., 6., 7.],
                [0., 0., 5., 7., 8.]])

        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> im1 = InteractionMatrix(np.matrix([[np.nan, 1.0], [1.0, np.nan]]),
        ...                         locusmap=LocusMap([
        ...     Locus('chr3', 34109023, 34113109, name='5C_329_Sox2_FOR_2',
        ...           strand='+'),
        ...     Locus('chr3', 34113147, 34116141, name='5C_329_Sox2_REV_4',
        ...           strand='-')]))
        ...
        >>> im2 = InteractionMatrix(np.matrix([[np.nan, 2.0], [2.0, np.nan]]),
        ...                         locusmap=LocusMap([
        ...     Locus('chr3', 87282063, 87285636, name='5C_326_Nestin_REV_9',
        ...           strand='-'),
        ...     Locus('chr3', 87285637, 87295935, name='5C_326_Nestin_FOR_10',
        ...           strand='+')]))
        ...
        >>> added_im = im1 + im2
        >>> added_im.print_log()
        InteractionMatrix created
        created from locusmap
        created from addition
        >>> added_im.matrix
        matrix([[nan,  1.,  0., nan],
                [ 1., nan, nan,  0.],
                [ 0., nan, nan,  2.],
                [nan,  0.,  2., nan]])

        >>> from lib5c.core.interactions import InteractionMatrix
        >>> im = InteractionMatrix.from_primerfile('test/primers.bed')
        >>> im['5C_329_Sox2_FOR_2', '5C_329_Sox2_REV_4'] = 1.0
        >>> im['5C_329_Sox2_FOR_2', '5C_329_Sox2_REV_4']
        1.0
        >>> im['5C_330_Klf4_FOR_8', '5C_330_Klf4_REV_5'] = 2.0
        >>> im['5C_330_Klf4_FOR_8', '5C_330_Klf4_REV_5']
        2.0
        >>> sox2_im = im['Sox2']
        >>> sox2_im['5C_329_Sox2_FOR_2', '5C_329_Sox2_REV_4']
        1.0
        >>> klf4_im = im['Klf4']
        >>> klf4_im['5C_330_Klf4_FOR_8', '5C_330_Klf4_REV_5']
        2.0
        >>> added_im = sox2_im + klf4_im
        >>> added_im.get_regions()
        ['Sox2', 'Klf4']
        >>> added_im['5C_329_Sox2_FOR_2', '5C_329_Sox2_REV_4']
        1.0
        >>> added_im['5C_330_Klf4_FOR_8', '5C_330_Klf4_REV_5']
        2.0
        >>> added_im['5C_329_Sox2_FOR_2', '5C_330_Klf4_REV_5']
        0.0
        >>> added_im['5C_329_Sox2_FOR_2', '5C_330_Klf4_FOR_8']
        nan
        """
        if self.locusmap is not None and other.locusmap is not None:
            # concatenate the locusmaps
            locusmap = self.locusmap + other.locusmap

            # create a new blank InteractionMatrix
            im = InteractionMatrix.from_locusmap(locusmap)

            # figure out which source object the ith row came from
            source_object = [
                self
                if self.locusmap.get_index_by_hash(hash(im.locusmap[i]))
                is not None
                else other
                for i in range(im.size())
            ]

            # fill in the concatenated matrix
            for i in range(im.size()):
                for j in range(im.size()):
                    if source_object[i] == source_object[j]:
                        im[i, j] = source_object[i][
                            source_object[i].locusmap.get_index_by_hash(
                                hash(im.locusmap[i])),
                            source_object[j].locusmap.get_index_by_hash(
                                hash(im.locusmap[j]))]

            # rewrite nan's
            set_cis_trans_nans(im.matrix, im.locusmap.as_list_of_dict())

            # log and data
            im.log_event('created from addition')
            im.data.update(self.data)
            im.data.update(other.data)

            return im
        else:
            if self.matrix.shape[1] and other.matrix.shape[1]:
                a = self.matrix
                d = other.matrix
                b = np.zeros((len(a), len(d)))
                c = np.zeros((len(d), len(a)))
                im = InteractionMatrix(np.bmat([[a, b], [c, d]]))
                im.log_event('created from addition')
                im.data.update(self.data)
                im.data.update(other.data)
                return im
            elif other.matrix.shape[1]:
                return other
            else:
                return self

    def delete(self, index, inplace=True):
        """
        Delete a Locus and all its interaction information from this
        InteractionMatrix.

        Parameters
        ----------
        index : int
            The index of the Locus to delete.
        inplace : bool, optional
            If True, the deletion is performed inplace, preserving the reference
            to the original InteractionMatrix, though the underlying ``matrix``
            and ``locusmap`` attributes will be present as new objects. If
            False, the original InteractionMatrix object will be unaffected.

        Returns
        -------
        InteractionMatrix
            The resulting InteractionMatrix. If the operation was performed
            in-place, this is just a reference to ``this``.

        Examples
        --------
        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> X = np.reshape(range(16), (4, 4)).astype(float)
        >>> counts = X + X.T
        >>> im = InteractionMatrix(counts,
        ...                        locusmap=LocusMap([
        ...     Locus('chr3', 34109023, 34113109, name='5C_329_Sox2_FOR_2',
        ...           strand='+', region='Sox2'),
        ...     Locus('chr3', 34113147, 34116141, name='5C_329_Sox2_REV_4',
        ...           strand='-', region='Sox2'),
        ...     Locus('chr3', 87282063, 87285636, name='5C_326_Nestin_REV_9',
        ...           strand='-', region='Nestin'),
        ...     Locus('chr3', 87285637, 87295935, name='5C_326_Nestin_FOR_10',
        ...           strand='+', region='Nestin')]))
        ...
        >>> print im
        InteractionMatrix of size 4
        [[nan  5. 10. nan]
         [ 5. nan nan 20.]
         [10. nan nan 25.]
         [nan 20. 25. nan]]
        Associated LocusMap:
        LocusMap comprising 4 loci
            Range: chr3:34109023-34113109 to chr3:87285637-87295935
            Regions: ['Sox2', 'Nestin']
        >>> deleted_im = im.delete(2, inplace=False)  # non-in-place delete
        >>> deleted_im.print_log()
        InteractionMatrix created
        deleted locus at index 2 with name 5C_326_Nestin_REV_9
        >>> print deleted_im
        InteractionMatrix of size 3
        [[nan  5. nan]
         [ 5. nan 20.]
         [nan 20. nan]]
        Associated LocusMap:
        LocusMap comprising 3 loci
            Range: chr3:34109023-34113109 to chr3:87285637-87295935
            Regions: ['Sox2', 'Nestin']
        >>> im.size()  # original object unaffected
        4
        >>> deleted_im['5C_329_Sox2_REV_4', '5C_326_Nestin_FOR_10']
        20.0
        >>> deleted_im = im.delete(2)  # in-place delete
        >>> deleted_im.print_log()
        InteractionMatrix created
        deleted locus at index 2 with name 5C_326_Nestin_REV_9
        >>> print im  # original object affected
        InteractionMatrix of size 3
        [[nan  5. nan]
         [ 5. nan 20.]
         [nan 20. nan]]
        Associated LocusMap:
        LocusMap comprising 3 loci
            Range: chr3:34109023-34113109 to chr3:87285637-87295935
            Regions: ['Sox2', 'Nestin']
        """
        # honor inplace=False
        if not inplace:
            return deepcopy(self).delete(index, inplace=True)

        # log
        if self.locusmap is not None and\
                self.locusmap[index].get_name() is not None:
            self.log_event('deleted locus at index %i with name %s' %
                           (index, self.locusmap[index].get_name()))
        else:
            self.log_event('deleted locus at index %i' % index)

        # delete from locusmap if present
        if self.locusmap is not None:
            self.locusmap = self.locusmap.delete(index)

        # delete from matrix
        self.matrix = np.delete(np.delete(self.matrix, index, 0), index, 1)

        return self

    def get_regions(self):
        """
        Get the regions covered by this InteractionMatrix, if this can be
        deduced from its metadata. For this to work, the metadata in this
        InteractionMatrix's ``locusmap`` attribute must consist of Locus objects
        with ``'name'`` keys in their ``data`` attributes.

        Returns
        -------
        list of str
            The ordered list of region names as strings.

        Examples
        --------
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> im = InteractionMatrix.from_primerfile('test/primers.bed')
        >>> im.get_regions()
        ['Sox2', 'Nestin', 'Klf4', 'gene-desert', 'Nanog-V2', 'Olig1-Olig2',
        'Oct4']
        """
        if self.locusmap:
            return self.locusmap.get_regions()
        return None

    def size(self):
        """
        Get the size of the InteractionMatrix. This value is equal to either
        dimension of the ``matrix`` attribute as well as the number of Locus
        objects in the associated LocusMap, if present.

        Returns
        -------
        long
            Size of this InteractionMatrix.

        Examples
        --------
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> im = InteractionMatrix.from_size(2)
        >>> im.matrix
        matrix([[0., 0.],
                [0., 0.]])
        >>> im.size()
        2
        """
        return int(self.matrix.shape[0])

    def extract_region(self, region):
        """
        Extract a submatrix of this Interaction Matrix corresponding to a
        specified region.

        Parameters
        ----------
        region : str
            The name of the region to extract.

        Returns
        -------
        InteractionMatrix
            The submatrix of this InteractionMatrix corresponding to the
            specified region. This is returned as a new, independent
            InteractionMatrix object (see Examples below).

        Examples
        --------
        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> X = np.reshape(range(16), (4, 4)).astype(float)
        >>> counts = X + X.T
        >>> im = InteractionMatrix(counts,
        ...                        locusmap=LocusMap([
        ...     Locus('chr3', 34109023, 34113109, name='5C_329_Sox2_FOR_2',
        ...           strand='+', region='Sox2'),
        ...     Locus('chr3', 34113147, 34116141, name='5C_329_Sox2_REV_4',
        ...           strand='-', region='Sox2'),
        ...     Locus('chr3', 87282063, 87285636, name='5C_326_Nestin_REV_9',
        ...           strand='-', region='Nestin'),
        ...     Locus('chr3', 87285637, 87295935, name='5C_326_Nestin_FOR_10',
        ...           strand='+', region='Nestin')]))
        ...
        >>> im.matrix
        matrix([[nan,  5., 10., nan],
                [ 5., nan, nan, 20.],
                [10., nan, nan, 25.],
                [nan, 20., 25., nan]])
        >>> im.get_regions()
        ['Sox2', 'Nestin']
        >>> sox2_im = im.extract_region('Sox2')
        >>> sox2_im.print_log()
        InteractionMatrix created
        extracted region Sox2
        >>> sox2_im.matrix
        matrix([[nan,  5.],
                [ 5., nan]])
        >>> nestin_im = im.extract_region('Nestin')
        >>> nestin_im.matrix
        matrix([[nan, 25.],
                [25., nan]])

        >>> from lib5c.core.interactions import InteractionMatrix
        >>> im = InteractionMatrix.from_primerfile('test/primers.bed')
        >>> im.get_regions()
        ['Sox2', 'Nestin', 'Klf4', 'gene-desert', 'Nanog-V2', 'Olig1-Olig2',
        'Oct4']
        >>> im.size()
        1551
        >>> im['5C_329_Sox2_FOR_2', '5C_329_Sox2_REV_4'] = 1.0
        >>> im['5C_329_Sox2_FOR_2', '5C_329_Sox2_REV_4']
        1.0
        >>> sox2_im = im.extract_region('Sox2')
        >>> sox2_im.get_regions()
        ['Sox2']
        >>> sox2_im.size()
        265
        >>> sox2_im['5C_329_Sox2_FOR_2', '5C_329_Sox2_REV_4']
        1.0
        >>> sox2_im['5C_329_Sox2_FOR_2', '5C_329_Sox2_REV_4'] = 2.0
        >>> im['5C_329_Sox2_FOR_2', '5C_329_Sox2_REV_4']
        1.0
        """
        region_sizes = self.locusmap.get_region_sizes()
        lower_limit = 0
        upper_limit = 0
        for iterating_region in self.locusmap.get_regions():
            upper_limit += region_sizes[iterating_region]
            if iterating_region == region:
                break
            lower_limit += region_sizes[iterating_region]
        instance = InteractionMatrix(
            self.matrix[lower_limit:upper_limit, lower_limit:upper_limit],
            locusmap=self.locusmap.extract_region(region)
        )
        instance.log = copy(self.log)
        instance.log_event('extracted region %s' % region)
        instance.data = self.data
        return instance

    def extract_slice(self, desired_slice):
        """
        Gets a new InteractionMatrix object representing the interactions of a
        subset of the loci described in this InteractionMatrix as specified by
        a slice object.

        Parameters
        ----------
        desired_slice : slice
            The slice to use to subset this InteractionMatrix.

        Returns
        -------
        InteractionMatrix
            The new InteractionMatrix.

        Notes
        -----
        Since LocusMap objects are sorted, slices with negative steps will be
        reversed before being applied to the ``matrix`` attribute.

        Examples
        --------
        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> X = np.reshape(range(16), (4, 4)).astype(float)
        >>> im = InteractionMatrix(X + X.T)
        >>> im.matrix
        matrix([[ 0.,  5., 10., 15.],
                [ 5., 10., 15., 20.],
                [10., 15., 20., 25.],
                [15., 20., 25., 30.]])
        >>> sliced_im = im[1:3]
        >>> sliced_im.print_log()
        InteractionMatrix created
        sliced out slice(1, 3, None)
        >>> sliced_im.matrix
        matrix([[10., 15.],
                [15., 20.]])
        >>> reverse_sliced_im = im[3:1:-1]
        >>> reverse_sliced_im.matrix
        matrix([[10., 15.],
                [15., 20.]])

        >>> from lib5c.core.interactions import InteractionMatrix
        >>> im = InteractionMatrix.from_primerfile('test/primers.bed')
        >>> i = im['5C_329_Sox2_FOR_33']
        >>> j = im['5C_329_Sox2_REV_89']
        >>> im[i, i+1] = 1.0
        >>> im[j, j-1] = 2.0
        >>> im[i, j] = 3.0
        >>> sliced_im = im[i:j+1]
        >>> sliced_im[0, 1]
        1.0
        >>> sliced_im[-1, -2]
        2.0
        >>> sliced_im[0, -1]
        3.0
        >>> sliced_im.size() == 1 + j - i
        True
        >>> sliced_im.get_regions()
        ['Sox2']
        >>> sliced_im.locusmap[0].get_name()
        '5C_329_Sox2_FOR_33'
        >>> sliced_im.locusmap[-1].get_name()
        '5C_329_Sox2_REV_89'
        """
        if desired_slice.step is not None and desired_slice.step < 0:
            desired_slice = slice(desired_slice.stop, desired_slice.start,
                                  -desired_slice.step)
        if self.locusmap:
            inst = InteractionMatrix(self.matrix[desired_slice, desired_slice],
                                     locusmap=self.locusmap[desired_slice])
        else:
            inst = InteractionMatrix(self.matrix[desired_slice, desired_slice])
        inst.data = self.data
        inst.log = copy(self.log)
        inst.log_event('sliced out %s' % desired_slice)
        return inst

    def flatten(self, discard_nan=True):
        r"""
        Flattens the interaction values in this InteractionMatrix into a flat,
        non-redundant array.

        Parameters
        ----------
        discard_nan : bool, optional
            If True, nan's will not be filtered out of the returned array.

        Returns
        -------
        1d numpy array
            A flat, nonredundant array of the interaction values. The
            :math:`(i, j)` th element of this InteractionMatrix's ``matrix``
            attribute (for :math:`i >= j` ) ends up at the
            :math:`(i\times(i+1)/2 + j)` th index of the flattened array. If
            ``discard_nan`` was True, these indices will not necessarily match
            up and it will not be possible to unflatten the array.

        Notes
        -----
        A more intuitive way to think about the ordering is to read down the
        columns of ``matrix`` from left to right, going to the next column
        whenever you reach the diagonal.

        Examples
        --------
        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> im = InteractionMatrix(np.matrix([[   3.0, np.nan,    5.0],
        ...                                   [np.nan,    6.0, np.nan],
        ...                                   [   5.0, np.nan,    8.0]]))
        ...
        >>> im.flatten()
        array([3., 6., 5., 8.])
        >>> im.flatten(discard_nan=False)
        array([  3.,  nan,   6.,   5.,  nan,   8.])
        """
        return flatten_regional_counts(np.asarray(self.matrix),
                                       discard_nan=discard_nan)

    def unflatten(self, values):
        r"""
        Overwrite the ``matrix`` attribite of this InteractionMatrix object with
        values from a flat list, such as that created by
        ``InteractionMatrix.flatten()``.

        Parameters
        ----------
        values : 1d iterable of float
            A flat, nonredundant list of the interaction values. The
            :math:`(i, j)` th element of this InteractionMatrix's ``matrix``
            attribute (for :math:`i >= j` ) will be set to the
            :math:`(i\times(i+1)/2 + j)` th value of the flattened list.

        Examples
        --------
        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> im = InteractionMatrix(np.matrix([[   3.0, np.nan,    5.0],
        ...                                   [np.nan,    6.0, np.nan],
        ...                                   [   5.0, np.nan,    8.0]]))
        ...
        >>> values = im.flatten(discard_nan=False)
        >>> values
        array([  3.,  nan,   6.,   5.,  nan,   8.])
        >>> values += 1
        >>> values
        array([  4.,  nan,   7.,   6.,  nan,   9.])
        >>> im.unflatten(values)
        >>> print im
        InteractionMatrix of size 3
        [[ 4. nan  6.]
         [nan  7. nan]
         [ 6. nan  9.]]
        """
        size = int(0.5 * (-1 + sqrt(8*len(values) + 1)))
        for i in range(size):
            for j in range(i+1):
                self[i, j] = values[i*(i+1)/2 + j]

    def flatten_cis(self, discard_nan=True):
        r"""
        Flattens only the cis interaction values in this InteractionMatrix into
        a flat, non-redundant array.

        Parameters
        ----------
        discard_nan : bool, optional
            If True, nan's will not be filtered out of the returned array.

        Returns
        -------
        1d numpy array
            The result of ``flatten()``-ing each region separately and
            concatenating the results.

        Examples
        --------
        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> X = np.reshape(range(16), (4, 4)).astype(float)
        >>> counts = X + X.T
        >>> im = InteractionMatrix(counts,
        ...                        locusmap=LocusMap([
        ...     Locus('chr3', 34109023, 34113109, name='5C_329_Sox2_FOR_2',
        ...           region='Sox2'),
        ...     Locus('chr3', 34113147, 34116141, name='5C_329_Sox2_REV_4',
        ...           region='Sox2'),
        ...     Locus('chr3', 87282063, 87285636, name='5C_326_Nestin_REV_9',
        ...           region='Nestin'),
        ...     Locus('chr3', 87285637, 87295935, name='5C_326_Nestin_FOR_10',
        ...           region='Nestin')]))
        ...
        >>> im[0, 1] = np.nan
        >>> im[3, 3] = np.nan
        >>> print im
        InteractionMatrix of size 4
        [[ 0. nan 10. 15.]
         [nan 10. 15. 20.]
         [10. 15. 20. 25.]
         [15. 20. 25. nan]]
        Associated LocusMap:
        LocusMap comprising 4 loci
            Range: chr3:34109023-34113109 to chr3:87285637-87295935
            Regions: ['Sox2', 'Nestin']
        >>> im.flatten_cis()
        array([  0.,  10.,  20.,  25.])
        >>> im.flatten_cis(discard_nan=False)
        array([  0.,  nan,  10.,  20.,  25.,  nan])
        """
        return np.concatenate([self[region].flatten(discard_nan=discard_nan)
                               for region in self.get_regions()])

    def unflatten_cis(self, values):
        r"""
        Overwrite only the cis interaction values of the ``matrix`` attribite of
        this InteractionMatrix object with values from a flat list, such as that
        created by ``InteractionMatrix.flatten_cis()``.

        Parameters
        ----------
        values : 1d list of float
            A flat, nonredundant list of the cis interaction values. The order
            should match what would be expected from ``flatten()``-ing each
            region of the InteractionMatrix seperately and concatenating the
            results.

        Examples
        --------
        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> X = np.reshape(range(16), (4, 4)).astype(float)
        >>> counts = X + X.T
        >>> im = InteractionMatrix(counts,
        ...                        locusmap=LocusMap([
        ...     Locus('chr3', 34109023, 34113109, name='5C_329_Sox2_FOR_2',
        ...           strand='+', region='Sox2'),
        ...     Locus('chr3', 34113147, 34116141, name='5C_329_Sox2_REV_4',
        ...           strand='-', region='Sox2'),
        ...     Locus('chr3', 87282063, 87285636, name='5C_326_Nestin_REV_9',
        ...           strand='-', region='Nestin'),
        ...     Locus('chr3', 87285637, 87295935, name='5C_326_Nestin_FOR_10',
        ...           strand='+', region='Nestin')]))
        ...
        >>> print im
        InteractionMatrix of size 4
        [[nan  5. 10. nan]
         [ 5. nan nan 20.]
         [10. nan nan 25.]
         [nan 20. 25. nan]]
        Associated LocusMap:
        LocusMap comprising 4 loci
            Range: chr3:34109023-34113109 to chr3:87285637-87295935
            Regions: ['Sox2', 'Nestin']
        >>> values = im.flatten_cis(discard_nan=False)
        >>> values
        array([nan,  5., nan, nan, 25., nan])
        >>> values += 1
        >>> values
        array([nan,  6., nan, nan, 26., nan])
        >>> im.unflatten_cis(values)
        >>> print im
        InteractionMatrix of size 4
        [[nan  6. 10. nan]
         [ 6. nan nan 20.]
         [10. nan nan 26.]
         [nan 20. 26. nan]]
        Associated LocusMap:
        LocusMap comprising 4 loci
            Range: chr3:34109023-34113109 to chr3:87285637-87295935
            Regions: ['Sox2', 'Nestin']
        """
        values_index = 0  # index tracking position within values
        locus_index = 0  # index over loci in the locusmap
        for region in self.get_regions():
            region_start = locus_index
            region_size = self.locusmap.extract_region(region).size()
            for i in range(region_start, region_start + region_size):
                for j in range(region_start, i + 1):
                    self[i, j] = values[values_index]
                    values_index += 1
                locus_index += 1

    def to_countsfile(self, filename, omit_zeros=True):
        """
        Write the interaction values in this InteractionMatrix to a countsfile.

        Parameters
        ----------
        filename : str
            String reference to file to write to.
        omit_zeros : bool, optional
            If True, lines will not be written to the outfile if the counts for
            that line are zero.

        Examples
        --------
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> from lib5c.operators.standardization import Standardizer
        >>> s = Standardizer()
        >>> lm = LocusMap([
        ...     Locus('chr3', 34109023, 34113109, name='5C_329_Sox2_FOR_2',
        ...           region='Sox2'),
        ...     Locus('chr3', 34113147, 34116141, name='5C_329_Sox2_REV_4',
        ...           region='Sox2'),
        ...     Locus('chr3', 87282063, 87285636, name='5C_326_Nestin_REV_9',
        ...           region='Nestin'),
        ...     Locus('chr3', 87285637, 87295935, name='5C_326_Nestin_FOR_10',
        ...           region='Nestin')
        ... ])
        ...
        >>> im1 = InteractionMatrix([[  0.,   5.,  10.,  15.],
        ...                          [  5.,  10.,  15.,  20.],
        ...                          [ 10.,  15.,  20.,  25.],
        ...                          [ 15.,  20.,  25.,  30.]], locusmap=lm)
        ...
        >>> print im1
        InteractionMatrix of size 4
        [[ 0.  5. 10. 15.]
         [ 5. 10. 15. 20.]
         [10. 15. 20. 25.]
         [15. 20. 25. 30.]]
        Associated LocusMap:
        LocusMap comprising 4 loci
            Range: chr3:34109023-34113109 to chr3:87285637-87295935
            Regions: ['Sox2', 'Nestin']
        >>> im1.to_countsfile('test/core_test.counts')
        >>> im2 = InteractionMatrix.from_countsfile('test/core_test.counts',
        ...                                         locusmap=lm)
        ...
        >>> print im2
        InteractionMatrix of size 4
        [[ 0.  5. 10. 15.]
         [ 5. 10. 15. 20.]
         [10. 15. 20. 25.]
         [15. 20. 25. 30.]]
        Associated LocusMap:
        LocusMap comprising 4 loci
            Range: chr3:34109023-34113109 to chr3:87285637-87295935
            Regions: ['Sox2', 'Nestin']
        """
        if self.locusmap is not None:
            primermap = self.locusmap.as_dict_of_list_of_dict()
        else:
            primermap = {'dummy_region': [{'name': 'BIN_%03d' % i}
                                          for i in range(self.size())]}
        write_cis_trans_counts(self.matrix, filename, primermap,
                               omit_zeros=omit_zeros)
