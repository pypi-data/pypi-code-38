from scipy import stats

from lib5c.operators.base import InteractionMatrixOperator


class EmpiricalPvalueOperator(InteractionMatrixOperator):
    """
    Operator for assigning empirical right-tail p-values to all interactions in
    an InteractionMatrix.
    """

    def apply_inplace(self, target, **kwargs):
        """
        Transform the target InteractionMatrix, setting its interactions to
        their emprical right-tail p-values.

        Parameters
        ----------
        target : InteractionMatrix
            The InteractionMatrix object to transform.
        kwargs : other keyword arguments
            To be utilized by subclasses.

        Returns
        -------
        InteractionMatrix
            The transformed InteractionMatrix.

        Notes
        -----
        This transformation uses the ``kind='strict'`` kwarg of
        ``scipy.stats.percentileofscore()``, which means the resulting values
        represent the fraction of all the values that are greater than or equal
        to the value at that position.

        Examples
        --------
        >>> import numpy as np
        >>> from lib5c.core.interactions import InteractionMatrix
        >>> from lib5c.operators.modeling import EmpiricalPvalueOperator
        >>> X = np.reshape(range(16), (4, 4)).astype(float)
        >>> im = InteractionMatrix(X + X.T)
        >>> print im
        InteractionMatrix of size 4
        [[ 0.  5. 10. 15.]
         [ 5. 10. 15. 20.]
         [10. 15. 20. 25.]
         [15. 20. 25. 30.]]
        >>> epo = EmpiricalPvalueOperator()
        >>> result = epo.apply(im)
        >>> print result
        InteractionMatrix of size 4
        [[1.  0.9 0.8 0.6]
         [0.9 0.8 0.6 0.4]
         [0.8 0.6 0.4 0.2]
         [0.6 0.4 0.2 0.1]]
        >>> result.print_log()
        InteractionMatrix created
        transformed to empirical p-values
        """
        # log
        target.log_event('transformed to empirical p-values')

        # operate
        flattened_values = target.flatten()
        for i in range(target.size()):
            for j in range(i + 1):
                target[i, j] = 1 - stats.percentileofscore(
                    flattened_values, target[i, j], kind='strict') / 100

        return target
