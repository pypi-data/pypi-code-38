from lib5c.operators.base import MultiInteractionMatrixOperator
from lib5c.operators.standardization import Standardizer
from lib5c.algorithms.qnorm import qnorm


class QuantileNormalizer(MultiInteractionMatrixOperator):
    """
    Operator for quantile normalizing InteractionMatrix objects.

    Attributes
    ----------
    tie : {'lowest', 'average'}
        How this QuantileNormalizer will resolve ties. If ``'lowest'``, it will
        set all tied entries to the value of the lowest rank. If ``'average'``,
        it will set all tied entries to the average value across the tied ranks.

    Notes
    -----
    This operator will first standardize the target InteractionMatrix objects,
    including propagation of nan's, if they have ``locusmap`` attributes
    defined. Otherwise, the target InteractionMatrix objects must be the same
    size.
    """

    def __init__(self, tie='lowest'):
        """
        Constructor. See class docstring for description of parameters.

        Parameters
        ----------
        tie : {'lowest', 'average'}
        """
        self.tie = tie

    def apply_inplace(self, targets, **kwargs):
        """
        Quantile normalizes the target InteractionMatrix objects.

        Parameters
        ----------
        targets : list of InteractionMatrix
            The InteractionMatrix objects to quantile normalize. These must
            either have ``locusmap`` attributes or be the same size.
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
        >>> from lib5c.operators.qnorm import QuantileNormalizer
        >>> q = QuantileNormalizer()
        >>> im1 = InteractionMatrix([[    5., np.nan,     3.],
        ...                          [np.nan,     2., np.nan],
        ...                          [    3., np.nan,     4.]])
        ...
        >>> im2 = InteractionMatrix([[    4., np.nan,     4.],
        ...                          [np.nan,     1., np.nan],
        ...                          [    4., np.nan,     2.]])
        ...
        >>> im3 = InteractionMatrix([[    3., np.nan,     6.],
        ...                          [np.nan,     4., np.nan],
        ...                          [    6., np.nan,     8.]])
        ...
        >>> results = q.apply([im1, im2, im3])
        >>> print results[0]
        InteractionMatrix of size 3
        [[5.66666667        nan 3.        ]
         [       nan 2.                nan]
         [3.                nan 4.66666667]]
        >>> print results[1]
        InteractionMatrix of size 3
        [[4.66666667        nan 4.66666667]
         [       nan 2.                nan]
         [4.66666667        nan 3.        ]]
        >>> print results[2]
        InteractionMatrix of size 3
        [[2.                nan 4.66666667]
         [       nan 3.                nan]
         [4.66666667        nan 5.66666667]]

        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> from lib5c.operators.qnorm import QuantileNormalizer
        >>> q = QuantileNormalizer()
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
        ...                          [np.nan,    11.,    21.],
        ...                          [   11.,    21.,    16.]], locusmap=lm[:3])
        ...
        >>> results = q.apply([im1, im2])
        >>> print results[0]
        InteractionMatrix of size 3
        [[ 0.5  nan 10.5]
         [ nan 10.5 15.5]
         [10.5 15.5 20.5]]
        Associated LocusMap:
        LocusMap comprising 3 loci
            Range: chr3:34109023-34113109 to chr3:87282063-87285636
        >>> print results[1]
        InteractionMatrix of size 3
        [[ 0.5  nan 10.5]
         [ nan 10.5 20.5]
         [10.5 20.5 15.5]]
        Associated LocusMap:
        LocusMap comprising 3 loci
            Range: chr3:34109023-34113109 to chr3:87282063-87285636
        >>> results[0].print_log()
        InteractionMatrix created
        standardized with propagate_nan=True
        deleted locus at index 3
        qnormed with tie=lowest

        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> from lib5c.operators.qnorm import QuantileNormalizer
        >>> from lib5c.core.loci import Locus, LocusMap
        >>> locus_list = [Locus('chr3', 34109023, 34113109, region='Sox2'),
        ...               Locus('chr3', 34113147, 34116141, region='Sox2'),
        ...               Locus('chr3', 87282063, 87285636, region='Nestin'),
        ...               Locus('chr3', 87285637, 87295935, region='Nestin')]
        ...
        >>> locus_map = LocusMap(locus_list)
        >>> X = np.reshape(range(16), (4, 4)).astype(float)
        >>> im1 = InteractionMatrix(X + X.T, locusmap=locus_map)
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
        >>> im2 = InteractionMatrix((X + X.T) + 1, locusmap=locus_map)
        >>> print im2
        InteractionMatrix of size 4
        [[ 1.  6. 11. 16.]
         [ 6. 11. 16. 21.]
         [11. 16. 21. 26.]
         [16. 21. 26. 31.]]
        Associated LocusMap:
        LocusMap comprising 4 loci
            Range: chr3:34109023-34113109 to chr3:87285637-87295935
            Regions: ['Sox2', 'Nestin']
        >>> q = QuantileNormalizer()
        >>> results = q.apply_by_region([im1, im2])
        >>> print results[0]
        InteractionMatrix of size 4
        [[  0.5   5.5   0.    0. ]
         [  5.5  10.5   0.    0. ]
         [  0.    0.   20.5  25.5]
         [  0.    0.   25.5  30.5]]
        Associated LocusMap:
        LocusMap comprising 4 loci
            Range: chr3:34109023-34113109 to chr3:87285637-87295935
            Regions: ['Sox2', 'Nestin']
        >>> print results[1]
        InteractionMatrix of size 4
        [[  0.5   5.5   0.    0. ]
         [  5.5  10.5   0.    0. ]
         [  0.    0.   20.5  25.5]
         [  0.    0.   25.5  30.5]]
        Associated LocusMap:
        LocusMap comprising 4 loci
            Range: chr3:34109023-34113109 to chr3:87285637-87295935
            Regions: ['Sox2', 'Nestin']
        >>> results[0].print_log()
        InteractionMatrix created
        applying by region
        extracted region Sox2
        standardized with propagate_nan=True
        qnormed with tie=lowest
        done applying by region
        """
        # standardize targets
        if all(target.locusmap is not None for target in targets):
            s = Standardizer()
            targets = s.apply_inplace(targets)

        # flatten targets
        flattened_targets = {i: targets[i].flatten(discard_nan=False)
                             for i in range(len(targets))}

        # qnorm
        qnormed_flattened_targets = qnorm(flattened_targets, tie=self.tie)

        # regenerate InteractionMatrix objects
        for i in range(len(targets)):
            targets[i].unflatten(qnormed_flattened_targets[i])
            targets[i].log_event('qnormed with tie=%s' % self.tie)

        return targets
