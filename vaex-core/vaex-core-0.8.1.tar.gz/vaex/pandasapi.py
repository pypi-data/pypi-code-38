import pandas.core.common as com


class PandasAPI():
    def __init__(self, df):
        self.df = df
        self._stat_axis_number = 0
    
    @property
    def shape(self):
        return (len(self.df), )

    def _get_axis_number(self, axis):
        return 0

    def sample(self, n=None, frac=None, replace=False, weights=None,
               random_state=None, axis=None):
        """
        Return a random sample of items from an axis of object.
        You can use `random_state` for reproducibility.
        Parameters
        ----------
        n : int, optional
            Number of items from axis to return. Cannot be used with `frac`.
            Default = 1 if `frac` = None.
        frac : float, optional
            Fraction of axis items to return. Cannot be used with `n`.
        replace : bool, default False
            Sample with or without replacement.
        weights : str or ndarray-like, optional
            Default 'None' results in equal probability weighting.
            If passed a Series, will align with target object on index. Index
            values in weights not found in sampled object will be ignored and
            index values in sampled object not in weights will be assigned
            weights of zero.
            If called on a DataFrame, will accept the name of a column
            when axis = 0.
            Unless weights are a Series, weights must be same length as axis
            being sampled.
            If weights do not sum to 1, they will be normalized to sum to 1.
            Missing values in the weights column will be treated as zero.
            Infinite values not allowed.
        random_state : int or numpy.random.RandomState, optional
            Seed for the random number generator (if int), or numpy RandomState
            object.
        axis : int or string, optional
            Axis to sample. Accepts axis number or name. Default is stat axis
            for given data type (0 for Series and DataFrames, 1 for Panels).
        Returns
        -------
        Series or DataFrame
            A new object of same type as caller containing `n` items randomly
            sampled from the caller object.
        See Also
        --------
        numpy.random.choice: Generates a random sample from a given 1-D numpy
            array.
        Examples
        --------
        >>> df = pd.DataFrame({'num_legs': [2, 4, 8, 0],
        ...                    'num_wings': [2, 0, 0, 0],
        ...                    'num_specimen_seen': [10, 2, 1, 8]},
        ...                   index=['falcon', 'dog', 'spider', 'fish'])
        >>> df
                num_legs  num_wings  num_specimen_seen
        falcon         2          2                 10
        dog            4          0                  2
        spider         8          0                  1
        fish           0          0                  8
        Extract 3 random elements from the ``Series`` ``df['num_legs']``:
        Note that we use `random_state` to ensure the reproducibility of
        the examples.
        >>> df['num_legs'].sample(n=3, random_state=1)
        fish      0
        spider    8
        falcon    2
        Name: num_legs, dtype: int64
        A random 50% sample of the ``DataFrame`` with replacement:
        >>> df.sample(frac=0.5, replace=True, random_state=1)
              num_legs  num_wings  num_specimen_seen
        dog          4          0                  2
        fish         0          0                  8
        Using a DataFrame column as weights. Rows with larger value in the
        `num_specimen_seen` column are more likely to be sampled.
        >>> df.sample(n=2, weights='num_specimen_seen', random_state=1)
                num_legs  num_wings  num_specimen_seen
        falcon         2          2                 10
        fish           0          0                  8
        """

        if axis is None:
            axis = self._stat_axis_number

        axis = self._get_axis_number(axis)
        axis_length = self.shape[axis]

        # Process random_state argument
        rs = com.random_state(random_state)

        # Check weights for compliance
        if weights is not None:

            # If a series, align with frame
            if isinstance(weights, pd.Series):
                weights = weights.reindex(self.axes[axis])

            # Strings acceptable if a dataframe and axis = 0
            if isinstance(weights, string_types):
                if isinstance(self, pd.DataFrame):
                    if axis == 0:
                        try:
                            weights = self[weights]
                        except KeyError:
                            raise KeyError("String passed to weights not a "
                                           "valid column")
                    else:
                        raise ValueError("Strings can only be passed to "
                                         "weights when sampling from rows on "
                                         "a DataFrame")
                else:
                    raise ValueError("Strings cannot be passed as weights "
                                     "when sampling from a Series or Panel.")

            weights = pd.Series(weights, dtype='float64')

            if len(weights) != axis_length:
                raise ValueError("Weights and axis to be sampled must be of "
                                 "same length")

            if (weights == np.inf).any() or (weights == -np.inf).any():
                raise ValueError("weight vector may not include `inf` values")

            if (weights < 0).any():
                raise ValueError("weight vector many not include negative "
                                 "values")

            # If has nan, set to zero.
            weights = weights.fillna(0)

            # Renormalize if don't sum to 1
            if weights.sum() != 1:
                if weights.sum() != 0:
                    weights = weights / weights.sum()
                else:
                    raise ValueError("Invalid weights: weights sum to zero")

            weights = weights.values

        # If no frac or n, default to n=1.
        if n is None and frac is None:
            n = 1
        elif n is not None and frac is None and n % 1 != 0:
            raise ValueError("Only integers accepted as `n` values")
        elif n is None and frac is not None:
            n = int(round(frac * axis_length))
        elif n is not None and frac is not None:
            raise ValueError('Please enter a value for `frac` OR `n`, not '
                             'both')

        # Check for negative sizes
        if n < 0:
            raise ValueError("A negative number of rows requested. Please "
                             "provide positive value.")

        locs = rs.choice(axis_length, size=n, replace=replace, p=weights)
        return self.df.take(locs, axis=axis, is_copy=False)