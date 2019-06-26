"""Create tables from data-objects"""
# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
import re

import numpy as np

from . import fmtxt
from ._celltable import Celltable
from ._data_obj import (
    Categorial, Dataset, Factor, Interaction, NDVar, Scalar, UTS,
    Var, ascategorial, as_legal_dataset_key, asndvar, asvar, assub, asuv,
    cellname, combine, isuv)


def difference(y, x, c1, c0, match, by=None, sub=None, ds=None):
    """Subtract data in one cell from another

    Parameters
    ----------
    y : Var | NDVar
        Dependent variable.
    x : categorial
        Model for subtraction, providing categories to compute ``c1 - c0``.
    c1 : str | tuple
        Name of the cell in ``x`` that forms the minuend.
    c0 : str | tuple
        Name of the cell in ``x`` that is to be subtracted from ``c1``.
    match : categorial
        Units over which measurements were repeated. ``c1 - c0`` will be
        calculated separately for each level of ``match`` (e.g. ``"subject"``).
    by : None | categorial
        Calculate ``c1 - c0`` separately for each level in this variables.
    sub : None | index
        Only include a subset of the data.
    ds : None | Dataset
        If a Dataset is specified other arguments can be str instead of
        data-objects and will be retrieved from ``ds``.

    Returns
    -------
    diff : Dataset
        Dataset with the difference between ``c1`` and ``c0`` on ``y``.

    Examples
    --------
    ERP difference wave: assuming a dataset ``ds`` with EEG data
    (``ds['eeg']``), a variable named ``'condition'`` with levels ``'expected'``
    and ``'unexpected'``, and multiple subjects, the following will generate the
    ``unexpected - expected`` difference waves::

        >>> diff = table.difference('eeg', 'condition', 'unexpected', 'expected',
        ... 'subject', ds=ds)

    If ``ds`` also contains a different factor crossed with ``condition``,
    called ``'word'`` with levels ``'verb'`` abd ``'adjective'``, then separate
    difference waves for verbs and adjectives can be computed with::

        >>> diff = table.difference('eeg', 'condition', 'unexpected', 'expected',
        ... 'subject', by='word', ds=ds)

    Given the latter, the difference of the difference waves could be computed
    with::

        >>> diffdiff = table.difference('eeg', 'word', 'verb', 'adjective',
        ... 'subject', ds=diff)

    """
    sub = assub(sub, ds)
    x = ascategorial(x, sub, ds)
    out = Dataset()
    if by is None:
        ct = Celltable(y, x, match, sub, ds=ds)
        if not ct.all_within:
            raise ValueError("Design is not fully balanced")
        out.add(ct.groups[c1])
        yname = y if isinstance(y, str) else ct.y.name
        out[yname] = ct.data[c1] - ct.data[c0]
        # Transfer other variables in ds that are compatible with the rm-structure
        if ds is not None:
            out.update(ct._align_ds(ds, True, out.keys(), isuv))
    else:
        by = ascategorial(by, sub, ds)
        ct = Celltable(y, x % by, match, sub, ds=ds)
        if not ct.all_within:
            raise ValueError("Design is not fully balanced")

        yname = y if isinstance(y, str) else ct.y.name
        if isinstance(c1, str):
            c1 = (c1,)
        if isinstance(c0, str):
            c0 = (c0,)
        dss = []
        ds_keep = None
        for cell in by.cells:
            if isinstance(cell, str):
                cell = (cell,)
            cell_ds = Dataset()
            cell_ds.add(ct.groups[c1 + cell])
            cell_ds[yname] = ct.data[c1 + cell] - ct.data[c0 + cell]
            if isinstance(by, Factor):
                cell_ds[by.name, :] = cell[0]
            else:
                for b, c in zip(by.base, cell):
                    cell_ds[b.name, :] = c
            # Transfer other variables in ds that are compatible with the rm-structure
            if ds_keep is None:
                if ds is None:
                    ds_keep = False
                else:
                    ds_keep = ct._align_ds(ds, True, cell_ds.keys(), isuv)
            if ds_keep:
                cell_ds.update(ds_keep)
            dss.append(cell_ds)
        out = combine(dss)

    return out


def frequencies(y, x=None, of=None, sub=None, ds=None):
    """Calculate frequency of occurrence of the categories in ``y``

    Parameters
    ----------
    y : univariate
        Values whose frequencies are of interest.
    x : categorial
        Optional model defining cells for which frequencies are displayed
        separately.
    of : categorial
        With ``x`` constant within ``of``, only count frequencies for each value
        in ``of`` once. (Compress y and x before calculating frequencies.)
    sub : index
        Only use a subset of the data.
    ds : Dataset
        If ds is specified, other parameters can be strings naming for
        variables in ``ds``.

    Returns
    -------
    freq : Dataset
        Dataset with frequencies.

    Examples
    --------
    A simple sample dataset::

        >>> ds = Dataset()
        >>> ds['a'] = Factor('aabbcc')
        >>> ds['x'] = Factor('xxxyyy')

    Display frequency of a single factor's cells::

        >>> print(table.frequencies('a', ds=ds))
        cell   n
        --------
        a      2
        b      2
        c      2

    Display frequency of interaction cells::

        >>> print(table.frequencies('a', 'x', ds=ds))
        x   a   b   c
        -------------
        x   2   1   0
        y   0   1   2

    """
    sub = assub(sub, ds)
    y = asuv(y, sub, ds, interaction=True)
    if x is not None:
        x = ascategorial(x, sub, ds)
    if of is not None:
        of = ascategorial(of, sub, ds)
        y = y.aggregate(of)
        if x is not None:
            x = x.aggregate(of)

    name = "Frequencies of %s" % (y.name,) if y.name else "Frequencies"
    if isinstance(y, Var):
        cells = np.unique(y.x)
    else:
        cells = y.cells

    # special case
    if x is None:
        out = Dataset(name=name)
        if isinstance(y, Interaction):
            for i, f in enumerate(y.base):
                out[f.name] = Factor((c[i] for c in x.cells),
                                     random=getattr(f, 'random', False))
        elif isinstance(y, Factor):
            out[y.name or 'y'] = Factor(cells, random=y.random)
        elif isinstance(y, Var):
            out[y.name or 'y'] = Var(cells)
        else:
            raise RuntimeError("y=%r" % (y,))
        n = np.fromiter((np.sum(y == cell) for cell in cells), int, len(cells))
        out['n'] = Var(n)
        return out

    # header
    if getattr(x, 'name', None):
        name += ' by %s' % x.name
    out = Dataset(name=name)

    if isinstance(x, Interaction):
        for i, f in enumerate(x.base):
            random = getattr(f, 'random', False)
            out[f.name] = Factor((c[i] for c in x.cells), random=random)
    else:
        out[x.name] = Factor(x.cells)

    y_idx = {cell: y == cell for cell in cells}
    x_idx = {cell: x == cell for cell in x.cells}
    for y_cell in cells:
        n = (np.sum(np.logical_and(y_idx[y_cell], x_idx[x_cell]))
             for x_cell in x.cells)
        name = as_legal_dataset_key(cellname(y_cell, '_'))
        out[name] = Var(np.fromiter(n, int, len(x.cells)))

    return out


def melt(name, cells, cell_var_name, ds, labels=None):
    """
    Restructure a Dataset such that a measured variable is in a single column

    Restructure a Dataset with a certain variable represented in several
    columns into a longer dataset in which the variable is represented in a
    single column along with an identifying variable.

    Additional variables are automatically included.

    Parameters
    ----------
    name : str
        Name of the variable in the new Dataset.
    cells : sequence of str | str
        Names of the columns representing the variable in the input Dataset.
        Names can either pe specified explicitly as a sequence of str, or
        implicitly as a str containing '%i' for an integer.
    cell_var_name : str
        Name of the variable to contain the cell identifier.
    ds : Dataset
        Input Dataset.
    labels : dict
        Labels mapping from names in ``cells`` to labels assigned in the new
        :class:`Factor` describing the cells.

    Examples
    --------
    Simple example data::

        >>> ds = Dataset()
        >>> ds['y1'] = Var([1, 2, 3])
        >>> ds['y2'] = Var([4, 5, 6])
        >>> print(ds)
        y1   y2
        -------
        1    4
        2    5
        3    6
        >>> print(table.melt('y', ['y1', 'y2'], 'id', ds))
        y   id
        ------
        1   y1
        2   y1
        3   y1
        4   y2
        5   y2
        6   y2

    Additional variables are automatically included::

        >>> ds['rm'] = Factor('abc')
        >>> print(ds)
        y1   y2   rm
        ------------
        1    4    a
        2    5    b
        3    6    c
        >>> print(table.melt('y', ['y1', 'y2'], 'id', ds))
        rm   y   id
        -----------
        a    1   y1
        b    2   y1
        c    3   y1
        a    4   y2
        b    5   y2
        c    6   y2

    """
    if labels is None:
        labels = {}

    # find source cells
    if isinstance(cells, str):
        cell_expression = cells
        cells = []
        cell_values = []
        if '%i' in cell_expression:
            pattern = cell_expression.replace('%i', r'(\d+)')
            for key in ds:
                m = re.match(pattern, key)
                if m:
                    cells.append(key)
                    cell_values.append(int(m.group(1)))
        else:
            raise ValueError("If cells is a string, it needs to contain '%i' "
                             "as a place-holder for an integer that "
                             "identifies columns")
    else:
        cell_values = cells

    # melt the Dataset
    dss = []
    for cell, cell_value in zip(cells, cell_values):
        cell_ds = ds.copy()
        cell_ds.rename(cell, name)
        for src in cells:
            if src != cell:
                del cell_ds[src]
        cell_ds[cell_var_name, :] = labels.get(cell_value, cell_value)
        dss.append(cell_ds)
    out = combine(dss)
    return out


def melt_ndvar(ndvar, dim=None, cells=None, ds=None, varname=None):
    """
    Transform data to long format by converting an NDVar dimension into a variable

    Parameters
    ----------
    ndvar : NDVar | str
        The NDVar (or name of the NDVar in ``ds``).
    dim : str
        The name of the dimension that should be unwrapped (optional if
        ``ndvar`` has only one non-case dimension).
    cells : sequence
        The values on ``dim`` that should be included in the output Dataset
        (default is to include all values).
    ds : Dataset
        Dataset with additional variables that should be included in the long
        table.
    varname : str
        Name for the transformed ``ndvar`` (default is ``ndvar.name``).

    Returns
    -------
    long_table : Dataset
        Dataset in long format.
    """
    ndvar = asndvar(ndvar, ds=ds)
    if dim is None:
        if ndvar.ndim == ndvar.has_case + 1:
            dim = ndvar.dims[-1]
            dimname = dim.name
        else:
            raise ValueError("The ndvar has more than one possible dimensions, "
                             "the dim parameter must be one of %s"
                             % repr(ndvar.dimnames[ndvar.has_case:]))
    else:
        dimname = dim
        dim = ndvar.get_dim(dimname)

    if cells is None:
        cells = dim._as_uv()

    if varname is None:
        if ndvar.name is None:
            raise TypeError("Need to provide a name")
        varname = ndvar.name

    if ds is None:
        base_ds = Dataset()
    else:
        uv_keys = tuple(k for k, v in ds.items() if isuv(v))
        base_ds = ds[uv_keys]

    dss = []
    for cell in cells:
        ds_ = base_ds.copy()
        ds_[varname] = ndvar.sub(**{dimname: cell})
        ds_[dimname, :] = cell
        dss.append(ds_)
    return combine(dss)


def cast_to_ndvar(data, dim_values, match, sub=None, ds=None, dim=None,
                  name=None):
    """Create an NDVar by converting a data column to a dimension
    
    Parameters
    ----------
    data : Var
        Data to be cast.
    dim_values : Var | Factor
        Location on the new dimension.
    match : Factor | Interaction
        Indicating rows which belong the the same case in the NDvar.
    sub : index
        Use a subset of the data.
    ds : Dataset
        Dataset with data for operation.
    dim : str   
        Name for the new dimension. Use ``dim='uts'`` to create :class:`UTS` 
        time dimension from scalar ``dim_values``.
    name : str
        Name for the new :class:`NDVar` (the default is the name of 
        ``dim_values``).
        
    Returns
    -------
    short_ds : Dataset
        Copy of ``ds``, aggregated over ``dim_values``, and with an 
        :class:`NDVar` containing the values form ``data`` and a new dimension
        reflecting ``dim_values``. If ``dim_values`` is a Factor, the new 
        dimension is :class:`Categorial`; if ``dim_values`` is a :class:`Var`, 
        it is :class:`Scalar`. The new dimension's name is ``dim``. The only
        exception to this is that when ``dim='uts'``, the new dimension is 
        :class:`UTS` named ``'time'``.
    """
    sub = assub(sub, ds)
    data = asvar(data, sub, ds)
    dim_values = asuv(dim_values, sub, ds)
    match = ascategorial(match, sub, ds)

    # determine NDVar dimension
    if isinstance(dim_values, Factor):
        unique_dim_vales = dim_values.cells
        dim = Categorial(dim or dim_values.name, unique_dim_vales)
    else:
        unique_dim_vales = np.unique(dim_values.x)
        if dim == 'uts':
            diff = np.diff(unique_dim_vales)
            unique_diff = np.unique(diff)
            if len(unique_diff) > 1:
                if np.diff(unique_diff).max() > 1e-15:
                    raise NotImplementedError(
                        "Can't create UTS dimension from data with irregular "
                        "sampling (detected time-steps of %s" %
                        ', '.join(map(str, unique_diff)))
                tstep = round(unique_diff.mean(), 17)
            else:
                tstep = unique_diff[0]
            dim = UTS(unique_dim_vales[0], tstep, len(unique_dim_vales))
        else:
            dim = Scalar(dim or dim_values.name, unique_dim_vales)

    # find NDVar data
    n_samples = len(dim)
    n_cases = len(match.cells)
    case_indexes = [match == case for case in match.cells]
    samples_indexes = [dim_values == v for v in unique_dim_vales]
    x = np.empty((n_cases, n_samples))
    index = None
    for i, case_index in enumerate(case_indexes):
        for j, sample_index in enumerate(samples_indexes):
            x[i, j] = data.x[np.logical_and(case_index, sample_index, index)]

    # package output dataset
    if ds is None:
        out = Dataset()
    else:
        out = ds if sub is None else ds.sub(sub)
        out = out.aggregate(match, drop_bad=True, count=False)
    out[name or data.name] = NDVar(x, ('case', dim))
    return out


def stats(y, row, col=None, match=None, sub=None, fmt='%.4g', funcs=[np.mean],
          ds=None, title=None, caption=None):
    """Make a table with statistics

    Parameters
    ----------
    y : Var
        Dependent variable.
    row : categorial
        Model specifying rows
    col : categorial | None
        Model specifying columns.
    funcs : list of callables
        A list of statistics functions to show (all functions must take an
        array argument and return a scalar).
    ds : Dataset
        If a Dataset is provided, y, row, and col can be strings specifying
        members.
    title : str | FMText
        Table title.
    caption : str | FMText
        Table caption.


    Returns
    -------
    table : fmtxt.Table
        Table with statistics.

    Examples
    --------
    >>> ds = datasets.get_uts()
    >>> table.stats('Y', 'A', 'B', ds=ds)
                B
         -----------------
         b0        b1
    ----------------------
    a0   0.1668    -0.3646
    a1   -0.4897   0.8746

    >>> table.stats('Y', 'A', ds=ds, funcs=[np.mean, np.std])
    Condition   mean     std
    --------------------------
    a0          0.6691   1.37
    a1          0.8596   1.192

    """
    sub = assub(sub, ds)
    y = asvar(y, sub, ds)
    row = ascategorial(row, sub, ds)
    if match is not None:
        match = ascategorial(match, sub, ds)

    if col is None:
        ct = Celltable(y, row, match=match)

        # table header
        n_disp = len(funcs)
        table = fmtxt.Table('l' * (n_disp + 1), title=title, caption=caption)
        table.cell('Condition', 'bf')
        for func in funcs:
            table.cell(func.__name__, 'bf')
        table.midrule()

        # table entries
        for cell in ct.cells:
            data = ct.data[cell]
            table.cell(cell)
            for func in funcs:
                table.cell(fmt % func(data.x))
    else:
        col = ascategorial(col, sub, ds)
        ct = Celltable(y, row % col, match=match)

        N = len(col.cells)
        table = fmtxt.Table('l' * (N + 1), title=title, caption=caption)

        # table header
        table.cell()
        table.cell(col.name, width=N, just='c')
        table.midrule(span=(2, N + 1))
        table.cell()

        table.cells(*col.cells)
        table.midrule()

        # table body
        fmt_n = fmt.count('%')
        if fmt_n == 1:
            fmt_once = False
        elif len(funcs) == fmt_n:
            fmt_once = True
        else:
            raise ValueError("fmt does not match funcs")

        for Ycell in row.cells:
            table.cell(Ycell)
            for Xcell in col.cells:
                # construct address
                a = ()
                if isinstance(Ycell, tuple):
                    a += Ycell
                else:
                    a += (Ycell,)
                if isinstance(Xcell, tuple):
                    a += Xcell
                else:
                    a += (Xcell,)

                # cell
                data = ct.data[a]
                values = (f(data.x) for f in funcs)
                if fmt_once:
                    txt = fmt % values
                else:
                    txt = ', '.join((fmt % v for v in values))

                table.cell(txt)

    return table


def repmeas(y, x, match, sub=None, ds=None):
    """Create a repeated-measures table

    Parameters
    ----------
    y :
        Dependent variable (can be model with several dependents).
    x : categorial
        Model defining the cells that should be restructured into variables.
    match : categorial
        Model identifying the source of the measurement across repetitions,
        i.e. the model that should be retained.
    sub :
        boolean array specifying which values to include (generate e.g.
        with 'sub=T==[1,2]')
    ds : None | Dataset
        If a Dataset is specified other arguments can be str instead of
        data-objects and will be retrieved from ds.

    Returns
    -------
    rm_table : Dataset
        Repeated measures table. Entries for cells of ``x`` correspond to the
        data in ``y`` on these levels of ``x`` (if cell names are not valid
        Dataset keys they are modified).

    Examples
    --------
    Generate test data in long format::

        >>> ds = Dataset()
        >>> ds['y'] = Var([1,2,3,5,6,4])
        >>> ds['x'] = Factor('aaabbb')
        >>> ds['rm'] = Factor('123231', random=True)
        >>> print(ds)
        y   x   rm
        ----------
        1   a   1
        2   a   2
        3   a   3
        5   b   2
        6   b   3
        4   b   1

    Compute difference between two conditions::

        >>> ds_rm = table.repmeas('y', 'x', 'rm', ds=ds)
        >>> print(ds_rm)
        rm   a   b
        ----------
        1    1   4
        2    2   5
        3    3   6
        >>> ds_rm['difference'] = ds_rm.eval("b - a")
        >>> print(ds_rm)
        rm   a   b   difference
        -----------------------
        1    1   4   3
        2    2   5   3
        3    3   6   3

    """
    ct = Celltable(y, x, match, sub, ds=ds)
    if not ct.all_within:
        raise ValueError("Incomplete data")

    out = Dataset()
    x_ = ct.groups[ct.x.cells[0]]
    if isinstance(x_, Interaction):
        for f in x_.base:
            out.add(f)
    else:
        out[ct.match.name] = x_

    for cell in ct.x.cells:
        if len(ct.data[cell]):  # for models with empty cells
            key = as_legal_dataset_key(cellname(cell, '_'))
            out[key] = ct.data[cell]

    # Transfer other variables in ds that are compatible with the rm-structure
    if ds is not None:
        out.update(ct._align_ds(ds, True, out.keys(), isuv))

    return out
