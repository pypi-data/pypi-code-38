from fnmatch import fnmatchcase
from itertools import combinations

import numpy as np

from ._data_obj import (
    NDVar, Case, Dataset,
    ascategorial, asdataobject, assub,
    cellname, dataobj_repr,
)
from ._stats.stats import variability
from ._utils.numpy_utils import FULL_SLICE


class Celltable:
    """Divide y into cells defined by x.

    Parameters
    ----------
    y : data-object
        dependent measurement
    x : categorial
        Model (Factor or Interaction) for dividing y.
    match : categorial
        Factor on which cases are matched (i.e. subject for a repeated
        measures comparisons). If several data points with the same
        case fall into one cell of x, they are combined using
        match_func. If match is not None, Celltable.groups contains the
        {Xcell -> [match values of data points], ...} mapping corres-
        ponding to self.data
    sub : bool array
        Bool array of length N specifying which cases to include
    cat : None | sequence of cells of x
        Only retain data for these cells. Data will be sorted in the order
        of cells occuring in cat.
    ds : Dataset
        If a Dataset is specified, input items (y / x / match / sub) can
        be str instead of data-objects, in which case they will be
        retrieved from the Dataset.
    coercion : callable
        Function to convert the y parameter to to the dependent varaible
        (default: asdataobject).


    Examples
    --------
    Split a repeated-measure variable y into cells defined by the
    interaction of A and B::

        >>> c = Celltable(y, A % B, match=subject)


    Attributes
    ----------
    y : data-object
        ``y`` after evaluating input parameters.
    x : categorial
        ``x`` after evaluating input parameters.
    match : categorial | None
        ``match`` after evaluating input parameters.
    sub : bool array | None
        ``sub`` after evaluating input parameters.
    cells : list of (str | tuple)
        List of all cells in x.
    data : dict(cell -> data)
        Data (``y[index]``) in each cell.
    data_indexes : dict(cell -> index-array)
        For each cell, a boolean-array specifying the index for that cell in
        ``x``.

    **If ``match`` is specified**:

    within : dict(cell1, cell2 -> bool)
        Dictionary that specifies for each cell pair whether the corresponding
        comparison is a repeated-measures or an independent measures
        comparison (only available when the input argument ``match`` is
        specified.
    all_within : bool
        Whether all comparison are repeated-measures comparisons or not.
    groups : dict(cell -> group)
        A slice of the match argument describing the group members for each
        cell.

    """
    def __init__(self, y, x=None, match=None, sub=None, cat=None, ds=None,
                 coercion=asdataobject, dtype=None):
        self.sub = sub
        sub, n_cases = assub(sub, ds, return_n=True)

        if x is None:
            if cat is not None:
                raise TypeError(f"cat={cat!r}: cat is only a valid argument if x is provided")
            y, n_cases = coercion(y, sub, ds, n_cases, return_n=True)
        else:
            x, n_cases = ascategorial(x, sub, ds, n_cases, return_n=True)
            if cat is not None:
                # reconstruct cat if some cells are provided as None
                is_none = [c is None for c in cat]
                if any(is_none):
                    if len(cat) == len(x.cells):
                        if all(is_none):
                            cat = x.cells
                        else:
                            cells = [c for c in x.cells if c not in cat]
                            cat = tuple(cells.pop(0) if c is None else c for c in cat)
                    else:
                        raise ValueError(
                            f"cat={cat!r}: categories can only be specified as "
                            f"None if all cells in x are used, but there are more "
                            f"than {len(cat)} cells: {x.cells}")

                # make sure all categories are in data
                if not all(c in x.cells for c in cat):
                    raise ValueError(
                        f"cat={cat!r} contains categories that are not in the "
                        f"data: {', '.join(str(c) for c in cat if c not in x.cells)}")

                # apply cat
                sort_idx = x.sort_index(order=cat)
                x = x[sort_idx]
                if sub is None:
                    sub = sort_idx
                else:
                    if sub.dtype.kind == 'b':
                        sub = np.flatnonzero(sub)
                    sub = sub[sort_idx]
            y = coercion(y, sub, ds, n_cases)

        sort_idx = aggregate = None
        if match is not None:
            match = ascategorial(match, sub, ds, n_cases)
            cell_model = match if x is None else x % match
            if len(cell_model) > len(cell_model.cells):
                aggregate = cell_model

            if aggregate is not None:
                # need to aggregate
                y = y.aggregate(aggregate)
                match = match.aggregate(aggregate)
                if x is not None:
                    x = x.aggregate(aggregate)
                    if cat is not None:
                        sort_idx = x.sort_index(order=cat)
            else:
                sort_idx = cell_model.sort_index()
                if x is not None and cat is not None:
                    X_ = x[sort_idx]
                    sort_X_idx = X_.sort_index(order=cat)
                    sort_idx = sort_idx[sort_X_idx]

            if sort_idx is not None:
                if sort_idx[0] == 0 and np.all(np.diff(sort_idx) == 1):
                    sort_idx = None
                else:
                    y = y[sort_idx]
                    match = match[sort_idx]
                    if x is not None:
                        x = x[sort_idx]

        if dtype is not None and y.x.dtype != dtype:
            y = y.astype(dtype)

        # save args
        self.y = y
        self.x = x
        self.cat = cat
        self.match = match
        self.coercion = coercion.__name__
        self.n_cases = len(y)
        # allow aligning additional variables
        self._n_cases = n_cases
        self._sub = sub
        self._aggregate = aggregate
        self._sort_idx = sort_idx

        # extract cell data
        self.data = {}
        self.data_indexes = {}
        if x is None:
            self.data[None] = y
            self.data_indexes[None] = FULL_SLICE
            self.cells = (None,)
            self.n_cells = 1
            self.all_within = match is not None
            return
        self.cells = cat if cat is not None else x.cells
        self.n_cells = len(self.cells)
        self.groups = {}
        for cell in x.cells:
            idx = x.index_opt(cell)
            self.data_indexes[cell] = idx
            self.data[cell] = y[idx]
            if match:
                self.groups[cell] = match[idx]

        # determine which comparisons are within subject comparisons
        if match:
            self.within = {}
            for cell1, cell2 in combinations(x.cells, 2):
                group1 = self.groups[cell1]
                if len(group1) == 0:
                    continue
                group2 = self.groups[cell2]
                if len(group2) == 0:
                    continue
                within = np.all(group1 == group2)
                self.within[cell1, cell2] = within
                self.within[cell2, cell1] = within
            self.any_within = any(self.within.values())
            self.all_within = all(self.within.values())
        else:
            self.any_within = False
            self.all_within = False

    def __repr__(self):
        args = [dataobj_repr(self.y), dataobj_repr(self.x)]
        if self.match is not None:
            args.append("match=%s" % dataobj_repr(self.match))
        if self.sub is not None:
            args.append("sub=%s" % dataobj_repr(self.sub))
        if self.coercion != 'asdataobject':
            args.append("coercion=%s" % self.coercion)
        return "Celltable(%s)" % (', '.join(args))

    def __len__(self):
        return self.n_cells

    def _align_ds(self, ds, rm=False, skip=(), filter=None):
        """Align a Dataset to the celltable"""
        out = Dataset()
        reference_cell = self.cells[0]
        for k, v in ds.items():
            if k in skip:
                continue
            elif filter and not filter(v):
                continue
            try:
                values = self._align(v, rm)
            except ValueError:  # aggregating failed
                continue
            reference_v = values.pop(reference_cell)
            if all(np.all(vi == reference_v) for vi in values.values()):
                out[k] = reference_v
        return out

    def _align(self, y, rm=False):
        """Align an additional variable to the celltable

        Parameters
        ----------
        y : data-object
            Data-object to align.
        rm : bool
            If the celltable is a repeated-measures celltable, align ``y`` to
            the repeated measures table rather than the long form table.
        """
        y_ = asdataobject(y, self._sub, n=self._n_cases)
        if self._aggregate is not None:
            y_ = y_.aggregate(self._aggregate)
        if self._sort_idx is not None:
            y_ = y_[self._sort_idx]
        if rm:
            return {cell: y_[index] for cell, index in self.data_indexes.items()}
        else:
            return y_

    def cellname(self, cell, delim=' '):
        """Produce a str label for a cell.

        Parameters
        ----------
        cell : tuple | str
            Cell.
        delim : str
            Interaction cells (represented as tuple of strings) are joined by
            ``delim``.
        """
        return cellname(cell, delim=delim)

    def cellnames(self, delim=' '):
        """Return a list of all cell names as strings.

        See Also
        --------
        .cellname : Produce a str label for a single cell.
        """
        return [cellname(cell, delim) for cell in self.cells]

    def data_for_cell(self, cell):
        """Retrieve data for a cell, allowing advanced cell combinations

        Parameters
        ----------
        cell : str | tuple of str
            Name fo the cell. See notes for special cell names. After a special
            cell is retrieved for the first time it is also add to
            ``self.data``.

        Notes
        -----
        Special cell names can be used to retrieve averages between different
        primary cells. The names should be composed so that a case sensitive
        version of fnmatch will find the source cells. For examples, if all
        cells are ``[('a', '1'), ('a', '2'), ('b', '1'), ('b', '2')]``,
        ``('a', '*')`` will retrieve the average of ``('a', '1')`` and
        ``('a', '2')``.
        """
        if cell in self.data:
            return self.data[cell]

        # find cells matched by `cell`
        if isinstance(cell, str):
            cells = [c for c in self.cells if fnmatchcase(c, cell)]
            name = cell
        else:
            cells = [c for c in self.cells if
                     all(fnmatchcase(c_, cp) for c_, cp in zip(c, cell))]
            name = '|'.join(cell)

        # check that all are repeated measures
        for cell1, cell2 in combinations(cells, 2):
            if not self.within[(cell1, cell2)]:
                err = ("Combinatory cells can only be formed from repeated "
                       "measures cells, %r and %r are not." % (cell1, cell2))
                raise ValueError(err)

        # combine data
        cell0 = cells[0]
        x = np.empty_like(self.data[cell0].x)
        for cell_ in cells:
            x += self.data[cell_].x
        x /= len(cells)
        out = NDVar(x, cell0.dims, {}, name)
        self.data[cell] = out
        return out

    def get_data(self, out=list):
        if out is dict:
            return self.data
        elif out is list:
            return [self.data[cell] for cell in self.cells]

    def get_statistic(self, func=np.mean):
        """Return a list with ``a * func(data)`` for each data cell.

        Parameters
        ----------
        func : callable | str
            statistics function that is applied to the data. Can be string,
            such as '[x]sem' or '[x]ci', e.g. '2sem'.

        See also
        --------
        .get_statistic_dict : return statistics in a ``{cell: data}`` dict
        """
        if isinstance(func, str):
            var_spec = func

            def func(y):
                return variability(y, None, None, var_spec, False)

        return [func(self.data[cell].x) for cell in self.cells]

    def get_statistic_dict(self, func=np.mean):
        """Return a ``{cell: func(data)}`` dictionary.

        Parameters
        ----------
        func : callable | str
            statistics function that is applied to the data. Can be string,
            such as '[x]sem', '[x]std', or '[x]ci', e.g. '2sem'.

        See Also
        --------
        .get_statistic : statistic in a list
        """
        return dict(zip(self.cells, self.get_statistic(func)))

    def variability(self, error='sem', pool=None):
        """Variability measure

        Parameters
        ----------
        error : str
            Measure of variability. Examples:
            ``sem``: Standard error of the mean (default);
            ``2sem``: 2 standard error of the mean;
            ``ci``: 95% confidence interval;
            ``99%ci``: 99% confidence interval (default).
        pool : bool
            Pool the errors for the estimate of variability (default is True
            for complete within-subject designs, False otherwise).

        Notes
        -----
        Returns within-subject standard error for complete within-subject
        designs (see Loftus & Masson, 1994).
        """
        match = self.match if self.all_within else None
        if pool is None:
            pool = self.all_within
        x = variability(self.y.x, self.x, match, error, pool)
        if isinstance(self.y, NDVar):
            dims = self.y.dims[1:]
            if not pool:
                dims = (Case,) + dims
            return NDVar(x, dims, self.y.info.copy(), error)
        else:
            return x
