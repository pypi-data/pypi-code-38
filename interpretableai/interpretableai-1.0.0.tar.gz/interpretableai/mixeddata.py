from pandas import Categorical


class MixedData(Categorical):
    """Represents a mixed data feature

    `MixedData` features can represent a feature with either numeric/categoric
    or ordinal/categoric values.

    Examples
    --------
    >>> MixedData(values, ordinal_levels=None)

    Parameters
    ----------
    values : list-like
        The values of the mixed feature. In a numeric/categoric mix, all
        numeric elements will be treated as numeric and all remaining elements
        as categoric. In an ordinal/categoric mix, all elements belonging to
        the `ordinal_levels` will be treated as ordinal, and all remaining
        elements as categoric.
    ordinal_levels : Index-like, optional
        If not supplied, the feature is treated as a numeric/categoric mix. If
        supplied, these are the ordered levels of the ordinal values in the
        ordinal/categoric mix.
    """
    def __init__(self, values, ordinal_levels=None, categories=None,
                 dtype=None, fastpath=False):
        if not ordinal_levels:
            ordinal_levels = None
        self._ordinal_levels = ordinal_levels
        Categorical.__init__(self, values, categories, None, dtype, fastpath)

    def __unicode__(self):
        cat_msg = Categorical.__unicode__(self)
        ord_msg = 'Ordinal levels: {vals}'.format(vals=self._ordinal_levels)
        return cat_msg + '\n' + ord_msg

    def copy(self):
        ordinal_levels = self._ordinal_levels
        if ordinal_levels:
            ordinal_levels = ordinal_levels[:]
        return MixedData(values=self._codes.copy(),
                         ordinal_levels=ordinal_levels,
                         dtype=self.dtype,
                         fastpath=True)
