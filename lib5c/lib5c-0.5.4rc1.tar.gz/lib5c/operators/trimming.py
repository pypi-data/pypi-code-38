import numpy as np

from lib5c.operators.base import InteractionMatrixOperator


class LocusTrimmer(InteractionMatrixOperator):
    """
    Operator for removing Loci from an InteractionMatrix object according to
    specified criteria.

    Attributes
    ----------
    sum_threshold_upper : float or None
        If not None, Loci whose row sums are greater than this value will be
        removed.
    sum_threshold_lower : float or None
        If not None, Loci whose row sums are less than this value will be
        removed.
    max_threshold : float or None
        If not None, Loci containing at least one interaction above this value
        will be removed.
    min_threshold : float or None
        If not None, Loci containing at least one interaction below this value
        will be removed.
    percentage_threshold_lower : float or None
        If not None, this percentage of of the Loci with the lowest row sums
        will be removed.
    percentage_threshold_upper : float or None
        If not None, this percentage of of the Loci with the highest row sums
        will be removed.
    fold_threshold_upper : float or None
        If not None, Loci whose row sums are more than this many times the
        median row sum will be removed.
    fold_threshold_lower : float or None
        If not None, Loci whose row sums are less than this many times the
        median row sum will be removed.
    """

    def __init__(self, sum_threshold_upper=None, sum_threshold_lower=None,
                 max_threshold=None, min_threshold=None,
                 percentage_threshold_lower=None,
                 percentage_threshold_upper=None,
                 fold_threshold_upper=None, fold_threshold_lower=None):
        """
        Constructor. See class docstring for description of parameters.

        Parameters
        ----------
        sum_threshold_upper : float or None
        sum_threshold_lower : float or None
        max_threshold : float or None
        min_threshold : float or None
        percentage_threshold_lower : float or None
        percentage_threshold_upper : float or None
        fold_threshold_upper : float or None
        fold_threshold_lower : float or None
        """
        self.sum_threshold_upper = sum_threshold_upper
        self.sum_threshold_lower = sum_threshold_lower
        self.max_threshold = max_threshold
        self.min_threshold = min_threshold
        self.percentage_threshold_lower = percentage_threshold_lower
        self.percentage_threshold_upper = percentage_threshold_upper
        self.fold_threshold_upper = fold_threshold_upper
        self.fold_threshold_lower = fold_threshold_lower

    def apply_inplace(self, target, **kwargs):
        """
        Apply the trimming operation to the target InteractionMatrix.

        Parameters
        ----------
        target : InteractionMatrix
            The InteractionMatrix object to trim.
        kwargs : other keyword arguments
            To be utilized by subclasses.

        Returns
        -------
        InteractionMatrix
            The trimmed InteractionMatrix.

        Examples
        --------
        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> from lib5c.operators.trimming import LocusTrimmer
        >>> X = np.reshape(range(16), (4, 4)).astype(float)
        >>> im = InteractionMatrix(X + X.T)
        >>> print im
        InteractionMatrix of size 4
        [[ 0.  5. 10. 15.]
         [ 5. 10. 15. 20.]
         [10. 15. 20. 25.]
         [15. 20. 25. 30.]]
        >>> locus_trimmer = LocusTrimmer(sum_threshold_lower=35)
        >>> print locus_trimmer.apply(im)
        InteractionMatrix of size 3
        [[10. 15. 20.]
         [15. 20. 25.]
         [20. 25. 30.]]
        >>> locus_trimmer = LocusTrimmer(percentage_threshold_lower=50.0)
        >>> print locus_trimmer.apply(im)
        InteractionMatrix of size 2
        [[20. 25.]
         [25. 30.]]
        >>> locus_trimmer = LocusTrimmer(sum_threshold_upper=80.0)
        >>> print locus_trimmer.apply(im)
        InteractionMatrix of size 3
        [[ 0.  5. 10.]
         [ 5. 10. 15.]
         [10. 15. 20.]]
        >>> locus_trimmer = LocusTrimmer(percentage_threshold_upper=50.0)
        >>> print locus_trimmer.apply(im)
        InteractionMatrix of size 2
        [[  0.   5.]
         [  5.  10.]]
        >>> locus_trimmer = LocusTrimmer(min_threshold=0.0)
        >>> print locus_trimmer.apply(im)
        InteractionMatrix of size 3
        [[10. 15. 20.]
         [15. 20. 25.]
         [20. 25. 30.]]
        >>> locus_trimmer = LocusTrimmer(max_threshold=30.0)
        >>> print locus_trimmer.apply(im)
        InteractionMatrix of size 3
        [[ 0.  5. 10.]
         [ 5. 10. 15.]
         [10. 15. 20.]]
        >>> locus_trimmer = LocusTrimmer(fold_threshold_lower=0.5)
        >>> print locus_trimmer.apply(im)
        InteractionMatrix of size 3
        [[10. 15. 20.]
         [15. 20. 25.]
         [20. 25. 30.]]
        >>> locus_trimmer = LocusTrimmer(fold_threshold_upper=1.5)
        >>> result = locus_trimmer.apply(im)
        >>> result.print_log()
        InteractionMatrix created
        loci trimmed with:
            fold_threshold_upper=1.5
        deleted locus at index 3
        >>> print result
        InteractionMatrix of size 3
        [[ 0.  5. 10.]
         [ 5. 10. 15.]
         [10. 15. 20.]]
        >>> result = locus_trimmer.apply_inplace(im)
        >>> im.print_log()
        InteractionMatrix created
        loci trimmed with:
            fold_threshold_upper=1.5
        deleted locus at index 3
        >>> print im
        InteractionMatrix of size 3
        [[ 0.  5. 10.]
         [ 5. 10. 15.]
         [10. 15. 20.]]

        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> from lib5c.operators.trimming import LocusTrimmer
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [Locus('chr3', 34109023, 34113109, region='Sox2'),
        ...               Locus('chr3', 34113147, 34116141, region='Sox2'),
        ...               Locus('chr3', 87282063, 87285636, region='Nestin'),
        ...               Locus('chr3', 87285637, 87295935, region='Nestin')]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> X = np.reshape(range(16), (4, 4)).astype(float)
        >>> im = InteractionMatrix(X + X.T, locusmap=locus_map)
        >>> im.matrix
        matrix([[ 0.,  5., 10., 15.],
                [ 5., 10., 15., 20.],
                [10., 15., 20., 25.],
                [15., 20., 25., 30.]])
        >>> locus_trimmer = LocusTrimmer(percentage_threshold_lower=50.0)
        >>> result = locus_trimmer.apply_by_region(im)
        >>> print result
        InteractionMatrix of size 2
        [[10.  0.]
         [ 0. 30.]]
        Associated LocusMap:
        LocusMap comprising 2 loci
            Range: chr3:34113147-34116141 to chr3:87285637-87295935
            Regions: ['Sox2', 'Nestin']
        >>> result.print_log()
        InteractionMatrix created
        applying by region
        extracted region Sox2
        loci trimmed with:
            percentage_threshold_lower=50.0
        deleted locus at index 0
        done applying by region
        """
        # log
        event = 'loci trimmed with:'
        for parameter in self.__dict__:
            if self.__dict__[parameter] is not None:
                event += '\n\t%s=%s' % (parameter, self.__dict__[parameter])
        target.log_event(event)

        # maintain a set of indices to delete
        deleted_indices = set()

        # comupte row sums
        row_sums = np.nansum(target.matrix, axis=0)
        median_row_sum = np.median(row_sums, axis=1)

        # resolve sum_threshold_lower
        if self.sum_threshold_lower is not None:
            for index in range(target.size()):
                if row_sums[0, index] <= self.sum_threshold_lower:
                    deleted_indices.add(index)

        # resolve sum_threshold_upper
        if self.sum_threshold_upper is not None:
            for index in range(target.size()):
                if row_sums[0, index] >= self.sum_threshold_upper:
                    deleted_indices.add(index)

        # resolve percentage_threshold_lower
        if self.percentage_threshold_lower is not None:
            sum_threshold_lower = np.percentile(
                row_sums, self.percentage_threshold_lower)
            for index in range(target.size()):
                if row_sums[0, index] <= sum_threshold_lower:
                    deleted_indices.add(index)

        # resolve percentage_threshold_upper
        if self.percentage_threshold_upper is not None:
            sum_threshold_upper = np.percentile(
                row_sums, self.percentage_threshold_upper)
            for index in range(target.size()):
                if row_sums[0, index] >= sum_threshold_upper:
                    deleted_indices.add(index)

        # resolve fold_threshold_lower
        if self.fold_threshold_lower is not None and median_row_sum:
            for index in range(target.size()):
                if row_sums[0, index] / median_row_sum <=\
                        self.fold_threshold_lower:
                    deleted_indices.add(index)

        # resolve fold_threshold_upper
        if self.fold_threshold_upper is not None and median_row_sum:
            for index in range(target.size()):
                if row_sums[0, index] / median_row_sum >=\
                        self.fold_threshold_upper:
                    deleted_indices.add(index)

        # resolve min_threshold
        if self.min_threshold is not None:
            for index in range(target.size()):
                if np.any(target.matrix[index] <= self.min_threshold):
                    deleted_indices.add(index)

        # resolve max_threshold
        if self.max_threshold is not None:
            for index in range(target.size()):
                if np.any(target.matrix[index] >= self.max_threshold):
                    deleted_indices.add(index)

        # delete indices
        for index in sorted(deleted_indices, reverse=True):
            target.delete(index)

        return target


class InteractionTrimmer(InteractionMatrixOperator):
    """
    Operator for removing specific interactions from an InteractionMatrix object
    according to specified criteria by setting their values to ``np.nan``.

    Attributes
    ----------
    value_threshold_lower : float or None
        If not None, interactions with values lower than this number will be
        removed.
    value_threshold_upper : float or None
        If not None, interactions with values higher than this number will be
        removed.
    locus_percentage_threshold_lower : float or None
        If not None, this percentage of interactions at each locus with the
        lowest values will be removed.
    locus_percentage_threshold_upper : float or None
        If not None, this percentage of interactions at each locus with the
        highest values will be removed.
    global_percentage_threshold_lower : float or None
        If not None, this percentage of interactions with the lowest values will
        be removed.
    global_percentage_threshold_upper : float or None
        If not None, this percentage of interactions with the highest values
        will be removed.
    locus_fold_threshold_lower : float or None
        If not None, interactions whose values are less than this many times the
        median value across either participating locus will be removed.
    locus_fold_threshold_upper : float or None
        If not None, interactions whose values are more than this many times the
        median value across either participating locus will be removed.
    global_fold_threshold_lower : float or None
        If not None, interactions whose values are less than this many times the
        median value across all interactions will be removed.
    global_fold_threshold_upper : float or None
        If not None, interactions whose values are more than this many times the
        median value across all interactions will be removed.
    """

    def __init__(self,
                 value_threshold_lower=None,
                 value_threshold_upper=None,
                 locus_percentage_threshold_lower=None,
                 locus_percentage_threshold_upper=None,
                 global_percentage_threshold_lower=None,
                 global_percentage_threshold_upper=None,
                 locus_fold_threshold_lower=None,
                 locus_fold_threshold_upper=None,
                 global_fold_threshold_lower=None,
                 global_fold_threshold_upper=None):
        """
        Constructor. See class docstring for description of parameters.

        Parameters
        ----------
        value_threshold_lower : float or None
        value_threshold_upper : float or None
        locus_percentage_threshold_lower : float or None
        locus_percentage_threshold_upper : float or None
        global_percentage_threshold_lower : float or None
        global_percentage_threshold_upper : float or None
        locus_fold_threshold_lower : float or None
        locus_fold_threshold_upper : float or None
        global_fold_threshold_lower : float or None
        global_fold_threshold_upper : float or None
        """
        self.value_threshold_lower = value_threshold_lower
        self.value_threshold_upper = value_threshold_upper
        self.locus_percentage_threshold_lower = locus_percentage_threshold_lower
        self.locus_percentage_threshold_upper = locus_percentage_threshold_upper
        self.global_percentage_threshold_lower =\
            global_percentage_threshold_lower
        self.global_percentage_threshold_upper =\
            global_percentage_threshold_upper
        self.locus_fold_threshold_lower = locus_fold_threshold_lower
        self.locus_fold_threshold_upper = locus_fold_threshold_upper
        self.global_fold_threshold_lower = global_fold_threshold_lower
        self.global_fold_threshold_upper = global_fold_threshold_upper

    def apply_inplace(self, target, **kwargs):
        """
        Apply the trimming operation to the target InteractionMatrix.

        Parameters
        ----------
        target : InteractionMatrix
            The InteractionMatrix object to trim.
        kwargs : other keyword arguments
            To be utilized by subclasses.

        Returns
        -------
        InteractionMatrix
            The trimmed InteractionMatrix.

        Examples
        --------
        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> from lib5c.operators.trimming import InteractionTrimmer
        >>> X = np.reshape(range(16), (4, 4)).astype(float)
        >>> im = InteractionMatrix(X + X.T)
        >>> print im
        InteractionMatrix of size 4
        [[ 0.  5. 10. 15.]
         [ 5. 10. 15. 20.]
         [10. 15. 20. 25.]
         [15. 20. 25. 30.]]
        >>> trimmer = InteractionTrimmer(value_threshold_lower=5.0)
        >>> print trimmer.apply(im)
        InteractionMatrix of size 4
        [[nan nan 10. 15.]
        [nan 10. 15. 20.]
        [10. 15. 20. 25.]
        [15. 20. 25. 30.]]
        >>> trimmer = InteractionTrimmer(value_threshold_upper=25.0)
        >>> print trimmer.apply(im)
        InteractionMatrix of size 4
        [[ 0.  5. 10. 15.]
         [ 5. 10. 15. 20.]
         [10. 15. 20. nan]
         [15. 20. nan nan]]
        >>> trimmer = InteractionTrimmer(locus_percentage_threshold_lower=25.0)
        >>> print trimmer.apply(im)
        InteractionMatrix of size 4
        [[nan nan nan nan]
         [nan 10. 15. 20.]
         [nan 15. 20. 25.]
         [nan 20. 25. 30.]]
        >>> trimmer = InteractionTrimmer(locus_percentage_threshold_upper=75.0)
        >>> print trimmer.apply(im)
        InteractionMatrix of size 4
        [[ 0.  5. 10. nan]
         [ 5. 10. 15. nan]
         [10. 15. 20. nan]
         [nan nan nan nan]]
        >>> trimmer = InteractionTrimmer(global_percentage_threshold_lower=25.0)
        >>> print trimmer.apply(im)
        InteractionMatrix of size 4
        [[nan nan nan 15.]
         [nan nan 15. 20.]
         [nan 15. 20. 25.]
         [15. 20. 25. 30.]]
        >>> trimmer = InteractionTrimmer(global_percentage_threshold_upper=75.0)
        >>> print trimmer.apply(im)
        InteractionMatrix of size 4
        [[ 0.  5. 10. 15.]
         [ 5. 10. 15. nan]
         [10. 15. nan nan]
         [15. nan nan nan]]
        >>> trimmer = InteractionTrimmer(locus_fold_threshold_lower=0.5)
        >>> print trimmer.apply(im)
        InteractionMatrix of size 4
        [[nan nan 10. 15.]
         [nan 10. 15. 20.]
         [10. 15. 20. 25.]
         [15. 20. 25. 30.]]
        >>> trimmer = InteractionTrimmer(locus_fold_threshold_upper=2.0)
        >>> print trimmer.apply(im)
        InteractionMatrix of size 4
        [[ 0.  5. 10. nan]
         [ 5. 10. 15. 20.]
         [10. 15. 20. 25.]
         [nan 20. 25. 30.]]
        >>> trimmer = InteractionTrimmer(global_fold_threshold_lower=0.25)
        >>> print trimmer.apply(im)
        InteractionMatrix of size 4
        [[nan  5. 10. 15.]
         [ 5. 10. 15. 20.]
         [10. 15. 20. 25.]
         [15. 20. 25. 30.]]
        >>> trimmer = InteractionTrimmer(global_fold_threshold_upper=2.0)
        >>> result = trimmer.apply(im)
        >>> print result
        InteractionMatrix of size 4
        [[ 0.  5. 10. 15.]
         [ 5. 10. 15. 20.]
         [10. 15. 20. 25.]
         [15. 20. 25. nan]]
        >>> result.print_log()
        InteractionMatrix created
        interactions trimmed with:
            global_fold_threshold_upper=2.0
        """
        # log
        event = 'interactions trimmed with:'
        for parameter in self.__dict__:
            if self.__dict__[parameter] is not None:
                event += '\n\t%s=%s' % (parameter, self.__dict__[parameter])
        target.log_event(event)

        # set of coordinates to remove
        removed_coords = set()

        # resolve value_threshold_lower
        if self.value_threshold_lower is not None:
            for i in range(target.size()):
                for j in range(i+1):
                    if target[i, j] <= self.value_threshold_lower:
                        removed_coords.add((i, j))

        # resolve value_threshold_upper
        if self.value_threshold_upper is not None:
            for i in range(target.size()):
                for j in range(i+1):
                    if target[i, j] >= self.value_threshold_upper:
                        removed_coords.add((i, j))

        # resolve locus_percentage_threshold_lower
        if self.locus_percentage_threshold_lower is not None:
            for i in range(target.size()):
                value_threshold_lower = np.percentile(
                    target.matrix[i], self.locus_percentage_threshold_lower)
                for j in range(target.size()):
                    if target[i, j] <= value_threshold_lower:
                        removed_coords.add((i, j))

        # resolve locus_percentage_threshold_upper
        if self.locus_percentage_threshold_upper is not None:
            for i in range(target.size()):
                value_threshold_upper = np.percentile(
                    target.matrix[i], self.locus_percentage_threshold_upper)
                for j in range(target.size()):
                    if target[i, j] >= value_threshold_upper:
                        removed_coords.add((i, j))

        # resolve global_percentage_threshold_lower
        if self.global_percentage_threshold_lower is not None:
            value_threshold_lower = np.percentile(
                target.flatten(), self.global_percentage_threshold_lower)
            for i in range(target.size()):
                for j in range(i+1):
                    if target[i, j] <= value_threshold_lower:
                        removed_coords.add((i, j))

        # resolve global_percentage_threshold_upper
        if self.global_percentage_threshold_upper is not None:
            value_threshold_upper = np.percentile(
                target.flatten(), self.global_percentage_threshold_upper)
            for i in range(target.size()):
                for j in range(i+1):
                    if target[i, j] >= value_threshold_upper:
                        removed_coords.add((i, j))

        # resolve locus_fold_threshold_lower
        if self.locus_fold_threshold_lower is not None:
            for i in range(target.size()):
                median_value = np.median(target.matrix[i], axis=1)
                if median_value:
                    for j in range(target.size()):
                        if target[i, j] / median_value <=\
                                self.locus_fold_threshold_lower:
                            removed_coords.add((i, j))

        # resolve locus_fold_threshold_upper
        if self.locus_fold_threshold_upper is not None:
            for i in range(target.size()):
                median_value = np.median(target.matrix[i], axis=1)
                if median_value:
                    for j in range(target.size()):
                        if target[i, j] / median_value >=\
                                self.locus_fold_threshold_upper:
                            removed_coords.add((i, j))

        # resolve global_fold_threshold_lower
        if self.global_fold_threshold_lower is not None:
            median_value = np.median(target.flatten())
            if median_value:
                for i in range(target.size()):
                    for j in range(i+1):
                        if target[i, j] / median_value <=\
                                self.global_fold_threshold_lower:
                            removed_coords.add((i, j))

        # resolve global_fold_threshold_upper
        if self.global_fold_threshold_upper is not None:
            median_value = np.median(target.flatten())
            if median_value:
                for i in range(target.size()):
                    for j in range(i+1):
                        if target[i, j] / median_value >=\
                                self.global_fold_threshold_upper:
                            removed_coords.add((i, j))

        # remove removed coordinates
        for removed_coord in removed_coords:
            target[removed_coord] = np.nan

        return target
