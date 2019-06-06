import numpy as np

from lib5c.operators.base import MultiInteractionMatrixOperator
from lib5c.core.loci import LocusMap


class Standardizer(MultiInteractionMatrixOperator):
    """
    Operator for standardizing InteractionMatrix objects. This process reduces
    all InteractionMatrix objects passed to the lowest common denominator of
    loci. In other words, loci that are not present in every InteractionMatrix
    object will be discarded from all InteractionMatrix objects.

    Attributes
    ----------
    propagate_nan : bool
        If True, nan values will be propagated across InteractionMatrix objects.

    Notes
    -----
    The InteractionMatrix objects supplied must have ``locusmap`` attributes.
    """

    def __init__(self, propagate_nan=True):
        """
        Constructor. See class docstring for description of parameters.

        Parameters
        ----------
        propagate_nan : bool
        """
        self.propoagate_nan = propagate_nan

    def apply_inplace(self, targets, **kwargs):
        """
        Apply the standardization operation to the target InteractionMatrix
        objects.

        Parameters
        ----------
        targets : list of InteractionMatrix
            The InteractionMatrix objects to standardize.
        kwargs : other keyword arguments
            To be utilized by subclasses.

        Returns
        -------
        list of InteractionMatrix
            The standardized InteractionMatrix objects.

        Examples
        --------
        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> from lib5c.operators.standardization import Standardizer
        >>> s = Standardizer()
        >>> lm = LocusMap([
        ...     Locus('chr3', 34109023, 34113109),
        ...     Locus('chr3', 34113147, 34116141),
        ...     Locus('chr3', 87282063, 87285636),
        ...     Locus('chr3', 87285637, 87295935)
        ... ])
        ...
        >>> im1 = InteractionMatrix([[  0.,   5.,  10.,  15.],
        ...                          [  5.,  10.,  15.,  20.],
        ...                          [ 10.,  15.,  20.,  25.],
        ...                          [ 15.,  20.,  25.,  30.]], locusmap=lm)
        ...
        >>> im2 = InteractionMatrix([[    1., np.nan,    11.],
        ...                          [np.nan,    11.,    16.],
        ...                          [   11.,    16.,    21.]], locusmap=lm[:3])
        ...
        >>> results = s.apply([im1, im2])
        >>> print results[0]
        InteractionMatrix of size 3
        [[ 0. nan 10.]
         [nan 10. 15.]
         [10. 15. 20.]]
        Associated LocusMap:
        LocusMap comprising 3 loci
            Range: chr3:34109023-34113109 to chr3:87282063-87285636
        >>> print results[1]
        InteractionMatrix of size 3
        [[ 1. nan 11.]
         [nan 11. 16.]
         [11. 16. 21.]]
        Associated LocusMap:
        LocusMap comprising 3 loci
            Range: chr3:34109023-34113109 to chr3:87282063-87285636
        >>> results[0].print_log()
        InteractionMatrix created
        standardized with propagate_nan=True
        deleted locus at index 3
        """
        # check for locusmap attributes
        for target in targets:
            if target.locusmap is None:
                raise ValueError('Target InteractionMatrix objects must possess'
                                 'locusmap attributes for standardization.')
        # log
        for target in targets:
            target.log_event('standardized with propagate_nan=%s' %
                             self.propoagate_nan)

        # determine total LocusMap
        total_locus_set = set()
        for target in targets:
            for locus in target.locusmap:
                total_locus_set.add(locus)
        total_locusmap = LocusMap(list(total_locus_set))

        # delete non-common loci
        for locus in total_locusmap:
            # information for this locus
            locus_hash = hash(locus)
            discard_flag = False

            # if the locus is missing from any target, set the flag
            for target in targets:
                if target.locusmap.get_index_by_hash(locus_hash) is None:
                    discard_flag = True
                    break

            # if the flag was set, delete this locus from all targets
            if discard_flag:
                for target in targets:
                    delete_index = target.locusmap.get_index_by_hash(locus_hash)
                    if delete_index is not None:
                        target.delete(delete_index)

        # honor propagate_nan
        if self.propoagate_nan:
            for i in range(targets[0].size()):
                for j in range(i+1):
                    # if this position is nan in any target, set the flag
                    nan_flag = False
                    for target in targets:
                        if not np.isfinite(target[i, j]):
                            nan_flag = True
                            break

                    # if the flag was set, set nan in all targets
                    if nan_flag:
                        for target in targets:
                            target[i, j] = np.nan

        return targets
