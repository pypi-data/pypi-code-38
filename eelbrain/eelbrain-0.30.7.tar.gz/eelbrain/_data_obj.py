# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""Data containers and basic operations

Data Representation
===================

Data is stored in three main vessels:

:class:`Factor`:
    stores categorical data
:class:`Var`:
    stores numeric data
:class:`NDVar`:
    stores numerical data where each cell contains an array if data (e.g., EEG
    or MEG data)


managed by

    * Dataset


Effect types
------------

These are elementary effects in a Model, and identified by :func:`is_effect`

 - _Effect
   - Factor
   - Interaction
   - NestedEffect
 - Var
 - NonBasicEffect


"""
from collections import Iterable, Iterator, OrderedDict, Sequence
from copy import deepcopy
from functools import partial
from itertools import chain, product, zip_longest
from keyword import iskeyword
from math import ceil, log
from numbers import Integral, Number
from pathlib import Path
import pickle
import operator
import os
import re
import string
import typing

from matplotlib.ticker import (
    FixedLocator, FormatStrFormatter, FuncFormatter, IndexFormatter)
import mne
from mne.source_space import label_src_vertno_sel
import nibabel
from nibabel.freesurfer import read_annot, read_geometry
import numpy as np
import scipy.signal
import scipy.stats
from scipy.linalg import inv, norm
from scipy.optimize import leastsq
from scipy.spatial import ConvexHull
from scipy.spatial.distance import cdist, pdist, squareform

from . import fmtxt, _info
from ._exceptions import DimensionMismatchError, IncompleteModel
from ._data_opt import gaussian_smoother
from ._utils import (
    intervals, ui, LazyProperty, n_decimals, natsorted)
from ._utils.numpy_utils import (
    INT_TYPES, FULL_SLICE, FULL_AXIS_SLICE,
    apply_numpy_index, digitize_index, digitize_slice_endpoint,
    index_length, index_to_int_array, newaxis, take_slice, slice_to_arange)
from .mne_fixes import MNE_EPOCHS, MNE_EVOKED, MNE_RAW, MNE_LABEL
from functools import reduce


preferences = dict(fullrepr=False,  # whether to display full arrays/dicts in __repr__ methods
                   repr_len=5,  # length of repr
                   dataset_str_n_cases=500,
                   var_repr_n_cases=100,
                   factor_repr_n_cases=100,
                   bool_fmt='%s',
                   float_fmt='%.6g',
                   int_fmt='%s',
                   factor_repr_use_labels=True,
                   short_repr=True,  # "A % B" vs "Interaction(A, B)"
                   )


SRC_RE = re.compile('^(ico|vol)-(\d+)(?:-(\w+))?$')
UNNAMED = '<?>'
LIST_INDEX_TYPES = (*INT_TYPES, slice)
EXPAND_INDEX_TYPES = (*INT_TYPES, np.ndarray)
_pickled_ds_wildcard = ("Pickled Dataset (*.pickled)", '*.pickled')
_tex_wildcard = ("TeX (*.tex)", '*.tex')
_tsv_wildcard = ("Plain Text Tab Separated Values (*.txt)", '*.txt')
_txt_wildcard = ("Plain Text (*.txt)", '*.txt')
EVAL_CONTEXT = vars(np)  # updated at end of file


def _effect_eye(n):
    """Effect coding for n categories. E.g.::

    Examples
    --------
    >>> _effect_eye(4)
    array([[ 1,  0,  0],
           [ 0,  1,  0],
           [ 0,  0,  1],
           [-1, -1, -1]])
    """
    x = np.zeros((n, n - 1))
    np.fill_diagonal(x, 1.)
    x[-1] = -1.
    return x


def _effect_interaction(a, b):
    k = a.shape[1]
    out = [a[:, i, None] * b for i in range(k)]
    return np.hstack(out)


def cellname(cell, delim=' '):
    """Consistent ``str`` representation for cells.

    * for Factor cells: the cell (str)
    * for Interaction cell: delim.join(cell).

    """
    if isinstance(cell, str):
        return cell
    elif isinstance(cell, (list, tuple)):
        return delim.join(cell)
    elif cell is None:
        return ''
    else:
        return str(cell)


def longname(x):
    if isnumeric(x) and 'longname' in x.info:
        return x.info['longname']
    elif getattr(x, 'name', None) is not None:
        return x.name
    elif np.isscalar(x):
        return repr(x)
    return '<unnamed>'


def nice_label(x, labels={}):
    if x.name in labels:
        return labels[x.name]
    elif 'label' in x.info:
        return x.info['label']
    else:
        return longname(x)


def array_repr(a):
    "Concise array repr where class does not matter"
    if a.ndim == 0:
        return str(a)
    elif a.ndim == 1:
        return '[%s]' % ', '.join(map(str, a))
    else:
        raise RuntimeError("Array with ndim > 1")


def dataobj_repr(obj):
    """Describe data-objects as parts of __repr__"""
    if obj is None:
        return 'None'
    elif isdataobject(obj) and obj.name is not None:
        return obj.name
    else:
        return '<%s>' % obj.__class__.__name__


def rank(x, tol=1e-8):
    """Rank of a matrix

    http://mail.scipy.org/pipermail/numpy-discussion/2008-February/031218.html

    """
    s = np.linalg.svd(x, compute_uv=0)
    return np.sum(np.where(s > tol, 1, 0))


def check_length(objs, n=None):
    for obj in objs:
        if obj is None:
            pass
        elif n is None:
            n = len(obj)
        elif n != len(obj):
            err = ("%r has wrong length: %i (%i needed)." %
                   (obj.name, len(obj), n))
            raise ValueError(err)


def isbalanced(x):
    """Determine whether x is balanced

    Parameters
    ----------
    x : categorial
        Categorial Model, Factor or Interaction.
    """
    if isinstance(x, Model):
        return all(isbalanced(e) for e in x.effects)
    else:
        return len({np.sum(x == c) for c in x.cells}) <= 1


def iscategorial(x):
    "Determine wether x is categorial"
    if isinstance(x, (Factor, NestedEffect)):
        return True
    elif isinstance(x, Interaction):
        return x.is_categorial
    elif isinstance(x, Model):
        return all(iscategorial(e) for e in x.effects)
    else:
        return False


# type checks
#############
# _Effect -> Factor, Interaction, NestedEffect
def isdatacontainer(x):
    "Determine whether x is a data-object, including Datasets"
    return isinstance(x, (Datalist, Dataset, Model, NDVar, Var, _Effect,
                          NonbasicEffect))


def isdataobject(x):
    "Determine whether x is a data-object, excluding Datasets"
    return isinstance(x, (Datalist, Model, NDVar, Var, _Effect, NonbasicEffect))


def isdatalist(x, contains=None, test_all=True):
    """Test whether x is a Datalist instance

    Parameters
    ----------
    x : object
        Object to test.
    contains : None | class
        Test whether the content is instances of a specific class.
    test_all : bool
        If contains is provided, test all items' class (otherwise just test the
        first item).
    """
    is_dl = isinstance(x, Datalist)
    if is_dl and contains:
        if test_all:
            is_dl = all(isinstance(item, contains) for item in x)
        else:
            is_dl = isinstance(x[0], contains)
    return is_dl


def iseffect(x):
    return isinstance(x, (Var, _Effect, NonbasicEffect))


def isnestedin(item, item2):
    "Determine whether ``item`` is nested in ``item2``"
    if isinstance(item, NestedEffect):
        return item2 in find_factors(item.nestedin)
    else:
        return False


def partially_nested(item1, item2):
    """Determine whether there is a complete or partial nesting relationship

    Used to determine whether a model should include an interaction effect
    between item1 and item2.
    """
    if isinstance(item2, NestedEffect):
        if isinstance(item1, NestedEffect):
            raise NotImplementedError(
                "Interaction between two nested effects is not implemented. "
                "Please specify model explicitly")
        return partially_nested(item2, item1)
    elif isinstance(item1, NestedEffect):
        nestedin = find_factors(item1.nestedin)
        return any(e in nestedin for e in find_factors(item2))
    else:
        return False


def isnumeric(x):
    "Determine wether x is numeric (a Var or an NDVar)"
    return isinstance(x, (NDVar, Var))


def isuv(x, interaction=False):
    "Determine whether x is univariate (a Var or a Factor)"
    if interaction:
        return isinstance(x, (Factor, Var, Interaction))
    else:
        return isinstance(x, (Factor, Var))


def isboolvar(x):
    "Determine whether x is a Var whose data type is boolean"
    return isinstance(x, Var) and x.x.dtype.kind == 'b'


def isintvar(x):
    "Determine whether x is a Var whose data type is integer"
    return isinstance(x, Var) and x.x.dtype.kind in 'iu'


def is_higher_order_effect(e1, e0):
    """Determine whether e1 is a higher order term of e0

    Return True if e1 is a higher order term of e0 (i.e., if all factors in
    e0 are contained in e1).

    Parameters
    ----------
    e1, e0 : effects
        The effects to compare.
    """
    f1s = find_factors(e1)
    return all(f in f1s for f in find_factors(e0))


def empty_cells(x):
    return [cell for cell in x.cells if not np.any(x == cell)]


def assert_has_no_empty_cells(x):
    """Raise a ValueError iff a categorial has one or more empty cells"""
    if isinstance(x, Factor):
        return
    elif isinstance(x, Interaction):
        if not x.is_categorial:
            return
        empty = empty_cells(x)
        if empty:
            raise NotImplementedError("%s contains empty cells: %s" %
                                      (dataobj_repr(x), ', '.join(empty)))
    elif isinstance(x, Model):
        empty = []
        for e in x.effects:
            if isinstance(e, Interaction) and e.is_categorial:
                empty_in_e = empty_cells(e)
                if empty_in_e:
                    empty.append((dataobj_repr(e), ', '.join(empty_in_e)))
        if empty:
            items = ['%s (%s)' % pair for pair in empty]
            raise NotImplementedError("%s contains empty cells in %s" %
                                      (dataobj_repr(x), ' and '.join(items)))
    else:
        raise TypeError("Need categorial (got %s)" % repr(x))


def hasrandom(x):
    """True if x is or contains a random effect, False otherwise"""
    if isinstance(x, (Factor, NestedEffect)):
        return x.random
    elif isinstance(x, Interaction):
        for e in x.base:
            if isinstance(e, Factor) and e.random:
                return True
    elif isinstance(x, Model):
        return any(hasrandom(e) for e in x.effects)
    return False


def as_case_identifier(x, ds=None):
    "Coerce input to a variable that can identify each of its cases"
    if isinstance(x, str):
        if ds is None:
            raise TypeError("Parameter was specified as string, but no Dataset "
                            "was specified")
        x = ds.eval(x)

    if isinstance(x, Var):
        n = len(x.values)
    elif isinstance(x, Factor):
        n = x.n_cells
    elif isinstance(x, Interaction):
        n = len(set(x))
    else:
        raise TypeError("Need a Var, Factor or Interaction to identify cases, "
                        "got %s" % repr(x))

    if n < len(x):
        raise ValueError("%s can not serve as a case identifier because it has "
                         "at least one non-unique value" % x.name.capitalize())

    return x


def asarray(x, kind=None, ds=None):
    "Coerce input to array"
    if isinstance(x, str):
        if ds is None:
            raise TypeError("Parameter was specified as string, but no Dataset "
                            "was specified")
        x = ds.eval(x)

    if isinstance(x, Var):
        x = x.x
    else:
        x = np.asarray(x)

    if kind is not None and x.dtype.kind not in kind:
        # boolean->int conversion
        if 'i' in kind and x.dtype.kind == 'b':
            x = x.astype(int)
        else:
            raise TypeError("Expected array of kind %r, got %r (%s)"
                            % (kind, x.dtype.kind, x.dtype))
    return x


def _apply_sub(x, sub, n, return_n):
    if n is None:
        if return_n:
            n = len(x)
    elif len(x) != n:
        raise ValueError("Arguments have different length")
    if sub is not None:
        x = x[sub]
    return (x, n) if return_n else x


def ascategorial(x, sub=None, ds=None, n=None, return_n=False):
    if isinstance(x, str):
        if ds is None:
            raise TypeError(f"{x!r}: Parameter was specified as string, but no Dataset was specified")
        x = ds.eval(x)

    if iscategorial(x):
        pass
    elif isinstance(x, Interaction):
        x = Interaction([e if isinstance(e, Factor) else e.as_factor() for
                         e in x.base])
    else:
        x = asfactor(x)

    return _apply_sub(x, sub, n, return_n)


def asdataobject(x, sub=None, ds=None, n=None, return_n=False):
    "Convert to any data object or numpy array."
    if isinstance(x, str):
        if ds is None:
            err = ("Data object was specified as string, but no Dataset was "
                   "specified")
            raise TypeError(err)
        x = ds.eval(x)

    if isdataobject(x):
        pass
    elif isinstance(x, np.ndarray):
        pass
    else:
        x = Datalist(x)

    return _apply_sub(x, sub, n, return_n)


def asepochs(x, sub=None, ds=None, n=None, return_n=False):
    "Convert to mne Epochs object"
    if isinstance(x, str):
        if ds is None:
            err = ("Epochs object was specified as string, but no Dataset was "
                   "specified")
            raise TypeError(err)
        x = ds.eval(x)

    if isinstance(x, MNE_EPOCHS):
        pass
    else:
        raise TypeError("Need mne Epochs object, got %s" % repr(x))

    return _apply_sub(x, sub, n, return_n)


def asfactor(x, sub=None, ds=None, n=None, return_n=False):
    if isinstance(x, str):
        if ds is None:
            raise TypeError(f"{x!r}: Factor was specified as string, but no Dataset was specified")
        x = ds.eval(x)

    if isinstance(x, Factor):
        pass
    elif hasattr(x, 'as_factor'):
        x = x.as_factor(name=x.name)
    else:
        x = Factor(x)

    return _apply_sub(x, sub, n, return_n)


def asindex(x):
    if isinstance(x, Factor):
        return x != ''
    elif isinstance(x, Var):
        return x.x
    else:
        return x


def asmodel(x, sub=None, ds=None, n=None, return_n=False):
    if isinstance(x, str):
        if ds is None:
            raise TypeError("Model was specified as string, but no Dataset was "
                            "specified")
        elif sub is not None:
            # need to sub dataset before building model to get right number of
            # df
            names = set(re.findall('\w+', x))
            if isinstance(sub, str):
                names.update(re.findall('\w+', sub))
            names.intersection_update(ds)
            ds = ds[names].sub(sub)
            sub = None
        x = ds.eval(x)

    if isinstance(x, Model):
        pass
    else:
        x = Model(x)

    return _apply_sub(x, sub, n, return_n)


def asndvar(x, sub=None, ds=None, n=None, dtype=None, return_n=False):
    if isinstance(x, str):
        if ds is None:
            raise TypeError("Ndvar was specified as string, but no Dataset was specified")
        x = ds.eval(x)

    # convert MNE objects
    if isinstance(x, NDVar):
        pass
    elif isinstance(x, MNE_EPOCHS):
        from .load.fiff import epochs_ndvar
        x = epochs_ndvar(x)
    elif isinstance(x, MNE_EVOKED):
        from .load.fiff import evoked_ndvar
        x = evoked_ndvar(x)
    elif isinstance(x, MNE_RAW):
        from .load.fiff import raw_ndvar
        x = raw_ndvar(x)
    elif isinstance(x, list):
        if isinstance(x[0], MNE_EVOKED):
            from .load.fiff import evoked_ndvar
            x = evoked_ndvar(x)
        else:
            x = combine(map(asndvar, x))
    elif hasattr(x, '_default_plot_obj'):
        x = x._default_plot_obj()
    else:
        raise TypeError("NDVar required, got %s" % repr(x))

    x, n = _apply_sub(x, sub, n, return_n=True)
    if dtype is not None and x.x.dtype != dtype:
        x = x.astype(dtype)
    return (x, n) if return_n else x


def asnumeric(x, sub=None, ds=None, n=None, return_n=False):
    "Var, NDVar"
    if isinstance(x, str):
        if ds is None:
            raise TypeError("Numeric argument was specified as string, but no "
                            "Dataset was specified")
        x = ds.eval(x)

    if not isnumeric(x):
        raise TypeError("Numeric argument required (Var or NDVar), got %s" % repr(x))

    return _apply_sub(x, sub, n, return_n)


def assub(sub, ds=None, return_n=False):
    "Interpret the sub argument."
    if sub is None:
        return (None, None) if return_n else None
    elif isinstance(sub, str):
        if ds is None:
            raise TypeError("the sub parameter was specified as string, but no "
                            "Dataset was specified")
        sub = ds.eval(sub)

    if isinstance(sub, Var):
        sub = sub.x
    elif not isinstance(sub, np.ndarray):
        raise TypeError(f"sub={sub}: needs to be Var or array")

    if return_n:
        n = len(sub) if sub.dtype.kind == 'b' else None
        return sub, n
    else:
        return sub


def asuv(x, sub=None, ds=None, n=None, return_n=False, interaction=False):
    "Coerce to Var or Factor"
    if isinstance(x, str):
        if ds is None:
            raise TypeError("Parameter was specified as string, but no Dataset "
                            "was specified")
        x = ds.eval(x)

    if isuv(x, interaction):
        pass
    elif all(isinstance(v, str) for v in x):
        x = Factor(x)
    else:
        x = Var(x)

    return _apply_sub(x, sub, n, return_n)


def asvar(x, sub=None, ds=None, n=None, return_n=False):
    "Coerce to Var"
    if isinstance(x, str):
        if ds is None:
            raise TypeError("Var was specified as string, but no Dataset was "
                            "specified")
        x = ds.eval(x)

    if not isinstance(x, Var):
        x = Var(x)

    return _apply_sub(x, sub, n, return_n)


def index_ndim(index):
    """Determine the dimensionality of an index

    Parameters
    ----------
    index : numpy_index
        Any valid numpy index.

    Returns
    -------
    ndim : int
        Number of index dimensions: 0 for an index to a single element, 1 for
        an index to a sequence.
    """
    if isinstance(index, slice):
        return 1
    elif isinstance(index, Integral):
        return 0
    elif np.iterable(index):
        return 1
    else:
        raise TypeError("unknown index type: %s" % repr(index))


def _empty_like(obj, n=None, name=None):
    "Create an empty object of the same type as obj"
    n = n or len(obj)
    name = name or obj.name
    if isinstance(obj, Factor):
        return Factor([''], repeat=n, name=name)
    elif isinstance(obj, Var):
        return Var(np.empty(n) * np.NaN, name=name)
    elif isinstance(obj, NDVar):
        shape = (n,) + obj.shape[1:]
        return NDVar(np.empty(shape) * np.NaN, dims=obj.dims, name=name)
    elif isdatalist(obj):
        return Datalist([None] * n, name, obj._fmt)
    else:
        err = "Type not supported: %s" % type(obj)
        raise TypeError(err)


def all_equal(a, b, nan_equal=False):
    """Test two data-objects for equality

    Equivalent to ``numpy.all(a == b)`` but faster and capable of treating nans
    as equal.

    Paramaters
    ----------
    a : Var | Factor | NDVar
        Variable to compare.
    a : Var | Factor | NDVar
        Variable to compare.
    nan_equal : bool
        Treat ``nan == nan`` as ``True``.

    Returns
    -------
    all_equal : bool
        True if all entries in
    """
    if a.__class__ is not b.__class__:
        raise TypeError("Comparing %s with %s" % (a.__class__, b.__class__))
    elif len(a) != len(b):
        raise ValueError("a and b have different lengths (%i vs %i)" %
                         (len(a), len(b)))
    elif isinstance(a, Factor):
        if a._codes == b._codes:
            return np.array_equal(a.x, b.x)
        else:
            return np.all(a == b)
    elif isinstance(a, (Var, NDVar)):
        if not nan_equal or a.x.dtype.kind in 'ib':  # can't be nan
            return np.array_equal(a.x, b.x)
        else:
            mask = np.isnan(a.x)
            buf = np.isnan(b.x)
            mask &= buf
            np.equal(a.x, b.x, buf)
            buf |= mask
            return buf.all()
    else:
        raise TypeError("Comparison for %s is not implemented" % a.__class__)


# --- sorting ---

def align(d1, d2, i1='index', i2=None, out='data'):
    """Align two data-objects based on index variables

    Before aligning, two data-objects ``d1`` and ``d2`` describe the same cases,
    but their order does not correspond. :func:`align` uses the index variables
    ``i1`` and ``i2`` to match each case in ``d2`` to a case in ``d1`` (i.e.,
    ``d1`` is used as the basis for the case order in the output), and returns
    reordered versions of of ``d1`` and ``d2`` with matching cases. Cases that
    are present in only one of ``d1`` and ``d2`` are dropped.

    Parameters
    ----------
    d1, d2 : data-object
        Two data objects which are to be aligned
    i1, i2 : str | Var | Factor | Interaction
        Indexes for cases in d1 and d2. If d1 and d2 are Datasets, i1 and i2
        can be keys for variables in d1 and d2.  If i2 is identical to i1 it can
        be omitted. Indexes have to supply a unique value for each case.
    out : 'data' | 'index'
        **'data'**: returns the two aligned data objects. **'index'**: returns
        two indices index1 and index2 which can be used to align the datasets
        with ``d1[index1]; d2[index2]``.

    Returns
    -------
    d1_aligned : data-object | array
        Aligned copy of ``d1`` (or index to align ``d1`` if ``out='index'``).
    d2_aligned : data-object | array
        Aligned copy of ``d2`` (or index to align ``d2`` if ``out='index'``).

    See Also
    --------
    align1 : Align one data-object to an index variable

    Examples
    --------
    See `examples/datasets/align.py <https://github.com/christianbrodbeck/
    Eelbrain/blob/master/examples/datasets/align.py>`_.
    """
    if i2 is None and isinstance(i1, str):
        i2 = i1
    i1 = as_case_identifier(i1, ds=d1)
    i2 = as_case_identifier(i2, ds=d2)
    if type(i1) is not type(i2):
        raise TypeError("i1 and i2 need to be of the same type, got: \n"
                        "i1=%r\ni2=%r" % (i1, i2))

    idx1 = []
    idx2 = []
    for i, case_id in enumerate(i1):
        if case_id in i2:
            idx1.append(i)
            idx2.append(i2.index(case_id)[0])

    if out == 'data':
        if all(i == v for i, v in enumerate(idx1)):
            return d1, d2[idx2]
        else:
            return d1[idx1], d2[idx2]
    elif out == 'index':
        return idx1, idx2
    else:
        raise ValueError("Invalid value for out parameter: %r" % out)


def align1(d, to, by='index', out='data'):
    """Align a data object to an index variable

    Parameters
    ----------
    d : data-object
        Data object with cases that should be aligned to ``idx``.
    to : data-object
        Index array to which ``d`` should be aligned. If ``to`` is a
        :class:`Dataset`, use ``to[by]``.
    by : str | data-object
        Variable labeling cases in ``d`` for aligning them to ``to``. If ``d``
        is a :class:`Dataset`, ``by`` can be the name of a variable in ``d``.
    out : 'data' | 'index'
        Return a restructured copy of ``d`` (default) or an index array into
        ``d``.

    Returns
    -------
    d_aligned : data-object | array
        Aligned copy of ``d`` (or index to align ``d`` to ``idx`` if
        ``out='index'``).

    See Also
    --------
    align : Align two data-objects
    """
    if isinstance(to, Dataset):
        if not isinstance(by, str):
            raise TypeError(f"by={by}: needs to be a str if to is a Dataset")
        to = asuv(by, ds=to)
    else:
        to = asuv(to)
    if not isinstance(by, str):
        # check d_idx length
        if isinstance(d, Dataset):
            if len(by) != d.n_cases:
                raise ValueError(f"by={by}: does not have the same number of cases as d (by: {len(by)}, d: {d.n_cases})")
        elif len(by) != len(d):
            raise ValueError(f"by={by}: does not have the same number of cases as d (d_idx: {len(by)}, d: {len(d)})")
    by = asuv(by, ds=d)

    align_idx = np.empty(len(to), int)
    for i, v in enumerate(to):
        where = by.index(v)
        if len(where) == 1:
            align_idx[i] = where[0]
        elif len(where) == 0:
            raise ValueError(f"{v} does not occur in d_idx")
        else:
            raise ValueError(f"{v} occurs more than once in d_idx")

    if out == 'data':
        return d[align_idx]
    elif out == 'index':
        return align_idx
    else:
        raise ValueError(f"out={out!r}")


def choose(choice, sources, name=None):
    """Combine data-objects picking from a different object for each case

    Parameters
    ----------
    choice : array of int
        Array specifying for each case from which of the sources the data should
        be taken.
    sources : list of data-objects
        Data that should be combined.
    name : str
        Name for the new data-object (optional).

    Notes
    -----
    Analogous to :func:`numpy.choose`. Only implemented for NDVars at this time.
    """
    choice = asarray(choice, 'i')
    if choice.min() < 0:
        raise ValueError("Choice can not be < 0")
    elif choice.max() > len(sources) - 1:
        raise ValueError("choice contains values exceeding the number of sources")

    s0 = sources[0]
    s1 = sources[1:]
    if isinstance(s0, NDVar):
        if not all(isinstance(s, NDVar) for s in s1):
            raise TypeError("Sources have different types")
        elif any(s.dims != s0.dims for s in s1):
            raise DimensionMismatchError("Sources have different dimensions")
        x = np.empty_like(s0.x)
        index_flat = np.empty(len(choice), bool)
        index = index_flat.reshape(index_flat.shape + (1,) * (x.ndim - 1))
        for i, s in enumerate(sources):
            np.equal(choice, i, index_flat)
            np.copyto(x, s.x, where=index)
        return NDVar(x, s0.dims, {}, name)
    else:
        raise NotImplementedError


def shuffled_index(n, cells=None):
    """Return an index to shuffle a data-object

    Parameters
    ----------
    n : int
        Number of cases in the index.
    cells : categorial
        Only shuffle cases within cells.

    Returns
    -------
    index : array of int
        Array with in indexes for shuffling a data-object.

    Notes
    -----
    If ``cells`` is not specified, this is equivalent to
    ``numpy.random.permutation(n)``.
    """
    if cells is None:
        return np.random.permutation(n)
    cells = ascategorial(cells, n=n)
    out = np.arange(n)
    for cell in cells.cells:
        index = cells == cell
        out[index] = np.random.permutation(out[index])
    return out


def combine(items, name=None, check_dims=True, incomplete='raise'):
    """Combine a list of items of the same type into one item.

    Parameters
    ----------
    items : sequence
        Sequence of data objects to combine (Dataset, Var, Factor, 
        NDVar or Datalist). A sequence of numbers is converted to :class:`Var`, 
        a sequence of strings is converted to :class:`Factor`.
    name : None | str
        Name for the resulting data-object. If None, the name of the combined
        item is the common prefix of all items.
    check_dims : bool
        For NDVars, check dimensions for consistency between items (e.g.,
        channel locations in a Sensor dimension). Default is ``True``. Set to
        ``False`` to ignore non-fatal mismatches.
    incomplete : "raise" | "drop" | "fill in"
        Only applies when combining Datasets: how to handle variables that are
        missing from some of the input Datasets. With ``"raise"`` (default), a
        KeyError to be raised. With ``"drop"``, partially missing variables are
        dropped. With ``"fill in"``, they are retained and missing values are
        filled in with empty values (``""`` for factors, ``NaN`` for variables).

    Notes
    -----
    The info dict inherits only entries that are equal (``x is y or
    np.array_equal(x, y)``) for all items.
    """
    if not isinstance(incomplete, str):
        raise TypeError("incomplete=%s, need str" % repr(incomplete))
    elif incomplete not in ('raise', 'drop', 'fill in'):
        raise ValueError("incomplete=%s" % repr(incomplete))

    # check input
    if isinstance(items, Iterator):
        items = list(items)
    if len(items) == 0:
        raise ValueError("combine() called with empty sequence %s" % repr(items))

    # find type
    first_item = items[0]
    if isinstance(first_item, Number):
        return Var(items, name=name)
    elif isinstance(first_item, str):
        return Factor(items)
    stype = type(first_item)
    if isinstance(first_item, mne.BaseEpochs):
        return mne.concatenate_epochs(items)
    elif not isdatacontainer(first_item):
        return Datalist(items)
    elif any(type(item) is not stype for item in items[1:]):
        raise TypeError("All items to be combined need to have the same type, "
                        "got %s." %
                        ', '.join(str(i) for i in {type(i) for i in items}))

    # find name
    if name is None:
        names = list(filter(None, (item.name for item in items)))
        name = os.path.commonprefix(names) or None

    # combine objects
    if stype is Dataset:
        out = Dataset(name=name, info=_info.merge_info(items))
        if incomplete == 'fill in':
            # find all keys and data types
            keys = list(first_item.keys())
            sample = dict(first_item)
            for item in items:
                for key in item:
                    if key not in keys:
                        keys.append(key)
                        sample[key] = item[key]
            # create output
            for key in keys:
                pieces = [ds[key] if key in ds else
                          _empty_like(sample[key], ds.n_cases) for ds in items]
                out[key] = combine(pieces, check_dims=check_dims)
        else:
            keys = set(first_item)
            if incomplete == 'raise':
                if any(set(item) != keys for item in items[1:]):
                    raise KeyError("Datasets have unequal keys. Use with "
                                   "incomplete='drop' or incomplete='fill in' "
                                   "to combine anyways.")
                out_keys = first_item
            else:
                keys.intersection_update(*items[1:])
                out_keys = (k for k in first_item if k in keys)

            for key in out_keys:
                out[key] = combine([ds[key] for ds in items])
        return out
    elif stype is Var:
        x = np.hstack([i.x for i in items])
        return Var(x, name, info=_info.merge_info(items))
    elif stype is Factor:
        random = set(f.random for f in items)
        if len(random) > 1:
            raise ValueError("Factors have different values for random parameter")
        random = random.pop()
        labels = first_item._labels
        if all(f._labels == labels for f in items[1:]):
            x = np.hstack([f.x for f in items])
            return Factor(x, name, random, labels=labels)
        else:
            x = sum((i.as_labels() for i in items), [])
            return Factor(x, name, random)
    elif stype is NDVar:
        v_have_case = [v.has_case for v in items]
        if all(v_have_case):
            has_case = True
            all_dims = (item.dims[1:] for item in items)
        elif any(v_have_case):
            raise DimensionMismatchError("Some items have a 'case' dimension, "
                                         "others do not")
        else:
            has_case = False
            all_dims = (item.dims for item in items)

        dims = reduce(lambda x, y: intersect_dims(x, y, check_dims), all_dims)
        idx = {d.name: d for d in dims}
        # reduce data to common dimension range
        sub_items = []
        for item in items:
            if item.dims[has_case:] == dims:
                sub_items.append(item)
            else:
                sub_items.append(item.sub(**idx))
        # combine data
        if has_case:
            x = np.concatenate([v.x for v in sub_items], axis=0)
        else:
            x = np.array([v.x for v in sub_items])
        dims = ('case',) + dims
        return NDVar(x, dims, _info.merge_info(sub_items), name)
    elif stype is Datalist:
        return Datalist(sum(items, []), name, items[0]._fmt)
    else:
        raise RuntimeError("combine with stype = %r" % stype)


def find_factors(obj):
    "Return the list of all factors contained in obj"
    if isinstance(obj, EffectList):
        f = OrderedDict((id(f), f) for e in obj for f in find_factors(e))
        return EffectList(f.values())
    elif isuv(obj):
        return EffectList([obj])
    elif isinstance(obj, Model):
        f = OrderedDict((id(f), f) for e in obj.effects for f in find_factors(e))
        return EffectList(f.values())
    elif isinstance(obj, NestedEffect):
        return find_factors(obj.effect)
    elif isinstance(obj, Interaction):
        return obj.base
    else:  # NonbasicEffect
        try:
            return EffectList(obj.factors)
        except:
            raise TypeError("%r has no factors" % obj)


class EffectList(list):
    def __repr__(self):
        return 'EffectList((%s))' % ', '.join(self.names())

    def __contains__(self, item):
        for f in self:
            if ((f.name == item.name) and (type(f) is type(item)) and
                    (len(f) == len(item)) and np.all(item == f)):
                return True
        return False

    def index(self, item):
        for i, f in enumerate(self):
            if (len(f) == len(item)) and np.all(item == f):
                return i
        raise ValueError("Factor %r not in EffectList" % item.name)

    def names(self):
        names = [e.name if isuv(e) else repr(e) for e in self]
        return [UNNAMED if n is None else n for n in names]


class Var:
    """Container for scalar data.

    Parameters
    ----------
    x : array_like
        Data; is converted with ``np.asarray(x)``. Multidimensional arrays
        are flattened as long as only 1 dimension is longer than 1.
    name : str | None
        Name of the variable
    repeat : int | array of int
        repeat each element in ``x``, either a constant or a different number
        for each element.
    tile : int
        Repeat ``x`` as a whole ``tile`` many times.
    info : dict
        Info dictionary. The "longname" entry is used for display purposes.

    Attributes
    ----------
    x : numpy.ndarray
        The data stored in the Var.
    name : None | str
        The Var's name.

    Notes
    -----
    While :py:class:`Var` objects support a few basic operations in a
    :py:mod:`numpy`-like fashion (``+``, ``-``, ``*``, ``/``, ``//``), their
    :py:attr:`Var.x` attribute provides access to the corresponding
    :py:class:`numpy.array` which can be used for anything more complicated.
    :py:attr:`Var.x` can be read and modified, but should not be replaced.
    """
    ndim = 1

    def __init__(self, x, name=None, repeat=1, tile=1, info=None):
        if isinstance(x, str):
            raise TypeError("Var can't be initialized with a string")

        if isinstance(x, Iterator):
            x = list(x)
        x = np.asarray(x)
        if x.dtype.kind in 'OUSV':
            alt_type = 'Factor' if x.dtype.kind == 'S' else 'Datalist'
            raise TypeError(f"x with numpy dtype.kind={x.dtype.kind!r}: Var needs numerical data type. Consider using a {alt_type} instead.")
        elif x.ndim > 1:
            if sum(i > 1 for i in x.shape) <= 1:
                x = np.ravel(x)
            else:
                raise ValueError(
                    f"x with shape {x.shape}; x needs to be one-dimensional. "
                    f"Use NDVar class for data with more than one dimension.")

        if not (isinstance(repeat, Integral) and repeat == 1):
            x = np.repeat(x, repeat)

        if tile > 1:
            x = np.tile(x, tile)

        info = {} if info is None else dict(info)
        self.__setstate__((x, name, info))

    def __setstate__(self, state):
        if len(state) == 3:
            x, name, info = state
        else:
            x, name = state
            info = {}
        # raw
        self.name = name
        self.x = x
        self.info = info
        # constants
        self._n_cases = len(x)
        self.df = 1
        self.random = False

    def __getstate__(self):
        return (self.x, self.name, self.info)

    def __repr__(self, full=False):
        n_cases = preferences['var_repr_n_cases']

        if isintvar(self):
            fmt = preferences['int_fmt']
        elif isboolvar(self):
            fmt = preferences['bool_fmt']
        else:
            fmt = preferences['float_fmt']

        if full or len(self.x) <= n_cases:
            x = [fmt % v for v in self.x]
        else:
            x = [fmt % v for v in self.x[:n_cases]]
            x.append('... (N=%s)' % len(self.x))

        args = ['[%s]' % ', '.join(x)]
        if self.name is not None:
            args.append('name=%r' % self.name)

        if self.info:
            args.append('info=%r' % self.info)

        return "Var(%s)" % ', '.join(args)

    def __str__(self):
        return self.__repr__(True)

    __array_priority__ = 15

    @property
    def __array_interface__(self):
        return self.x.__array_interface__

    # container ---
    def __len__(self):
        return self._n_cases

    def __getitem__(self, index):
        index = asindex(index)
        x = self.x[index]
        if isinstance(x, np.ndarray):
            return Var(x, self.name, info=self.info.copy())
        else:
            return x

    def __setitem__(self, index, value):
        self.x[index] = value

    def __contains__(self, value):
        return value in self.x

    # numeric ---
    def __neg__(self):
        info = {**self.info, 'longname': f"-{longname(self)}"}
        return Var(-self.x, self.name, info=info)

    def __pos__(self):
        return self

    def __abs__(self):
        return self.abs()

    def _arg_x(self, other):
        if isnumeric(other):
            return other.x
        else:
            return other

    def __add__(self, other):
        if isdataobject(other):
            # ??? should Var + Var return sum or Model?
            return Model((self, other))
        x = self.x + self._arg_x(other)
        info = {**self.info, 'longname': f"{longname(self)} + {longname(other)}"}
        return Var(x, self.name, info=info)

    def __iadd__(self, other):
        self.x += self._arg_x(other)
        return self

    def __radd__(self, other):
        x = self._arg_x(other) + self.x
        info = {**self.info, 'longname': f"{longname(other)} + {longname(self)}"}
        return Var(x, self.name, info=info)

    def __sub__(self, other):
        "subtract: values are assumed to be ordered. Otherwise use .sub method."
        x = self.x - self._arg_x(other)
        info = {**self.info, 'longname': f"{longname(self)} - {longname(other)}"}
        return Var(x, self.name, info=info)

    def __isub__(self, other):
        self.x -= self._arg_x(other)
        return self

    def __rsub__(self, other):
        x = self._arg_x(other) - self.x
        info = {**self.info, 'longname': f"{longname(other)} - {longname(self)}"}
        return Var(x, self.name, info=info)

    def __mul__(self, other):
        if isinstance(other, Model):
            return Model((self,)) * other
        elif iscategorial(other):
            return Model((self, other, self % other))
        x = self.x * self._arg_x(other)
        info = {**self.info, 'longname': f"{longname(self)} * {longname(other)}"}
        return Var(x, self.name, info=info)

    def __imul__(self, other):
        self.x *= self._arg_x(other)
        return self

    def __rmul__(self, other):
        x = self._arg_x(other) * self.x
        info = {**self.info, 'longname': f"{longname(other)} * {longname(self)}"}
        return Var(x, self.name, info=info)

    def __floordiv__(self, other):
        x = self.x // self._arg_x(other)
        info = {**self.info, 'longname': f"{longname(self)} // {longname(other)}"}
        return Var(x, self.name, info=info)

    def __ifloordiv__(self, other):
        self.x //= self._arg_x(other)
        return self

    def __mod__(self, other):
        if isinstance(other, Model):
            return Model(self) % other
        elif isinstance(other, Var):
            pass
        elif isdataobject(other):
            return Interaction((self, other))
        x = self.x % self._arg_x(other)
        info = {**self.info, 'longname': f"{longname(self)} % {longname(other)}"}
        return Var(x, self.name, info=info)

    def __imod__(self, other):
        self.x %= self._arg_x(other)
        return self

    def __lt__(self, y):
        return self.x < self._arg_x(y)

    def __le__(self, y):
        return self.x <= self._arg_x(y)

    def __eq__(self, y):
        return self.x == self._arg_x(y)

    def __ne__(self, y):
        return self.x != self._arg_x(y)

    def __gt__(self, y):
        return self.x > self._arg_x(y)

    def __ge__(self, y):
        return self.x >= self._arg_x(y)

    def __truediv__(self, other):
        return self.__div__(other)

    def __itruediv__(self, other):
        return self.__idiv__(other)

    def __div__(self, other):
        if isinstance(other, Var):
            pass
        elif iscategorial(other):  # separate slope for each level (for ANCOVA)
            dummy_factor = other.as_dummy_complete
            codes = dummy_factor * self.as_effects
            # center
            means = codes.sum(0) / dummy_factor.sum(0)
            codes -= dummy_factor * means
            # create effect
            name = '%s per %s' % (self.name, other.name)
            return NonbasicEffect(codes, [self, other], name, beta_labels=other.dummy_complete_labels)
        x = self.x / self._arg_x(other)
        info = {**self.info, 'longname': f"{longname(self)} / {longname(other)}"}
        return Var(x, self.name, info=info)

    def __idiv__(self, other):
        self.x /= self._arg_x(other)
        return self

    def __pow__(self, other):
        x = self.x ** self._arg_x(other)
        info = {**self.info, 'longname': f"{longname(self)} ** {longname(other)}"}
        return Var(x, self.name, info=info)

    def __round__(self, n=0):
        return Var(np.round(self.x, n), self.name)

    def _coefficient_names(self, method):
        return longname(self),

    def _summary(self, width=80):
        is_nan = np.isnan(self.x)
        n_nan = np.sum(is_nan)
        nan_str = f'NaN:{n_nan}' if n_nan else ''
        x = self.x[~is_nan] if n_nan else self.x
        unique = np.unique(x)
        if len(unique) <= 10:
            ns = [(v, np.sum(self.x == v)) for v in unique]
            items = [f'{v:g}:{n}' if n > 1 else f'{v:g}' for v, n in ns]
            if nan_str:
                items.append(nan_str)
            # check whether all items fit
            n = -2
            for i, item in enumerate(items):
                n += 2 + len(item)
                if n >= width:
                    break
            else:
                return ', '.join(items)
        out = f'{x.min():g} - {x.max():g}'
        if nan_str:
            out += f', {nan_str}'
        return out

    def abs(self, name=None):
        "Return a Var with the absolute value."
        if name is None:
            name = self.name
        info = {**self.info, 'longname': f"abs({longname(self)})"}
        return Var(np.abs(self.x), name, info=info)

    def argmax(self):
        """:func:`numpy.argmax`"""
        return np.argmax(self.x)

    def argmin(self):
        """:func:`numpy.argmin`"""
        return np.argmin(self.x)

    def argsort(self, kind='quicksort'):
        """:func:`numpy.argsort`

        Parameters
        ----------
        kind : 'quicksort' | 'mergesort' | 'heapsort'
            Sorting algorithm (default 'quicksort').

        Returns
        -------
        index_array : array of int
            Array of indices that sort `a` along the specified axis.
            In other words, ``a[index_array]`` yields a sorted `a`.
        """
        return np.argsort(self.x, kind=kind)

    def astype(self, dtype):
        """Copy of the Var with data cast to the specified type

        Parameters
        ----------
        dtype : numpy dtype
            Numpy data-type specification (see :meth:`numpy.ndarray.astype`).
        """
        return Var(self.x.astype(dtype), self.name, info=self.info.copy())

    @property
    def as_dummy(self):
        "For dummy coding"
        return self.x[:, None]

    @property
    def as_effects(self):
        "For effect coding"
        return self.x[:, None] - self.x.mean()

    def as_factor(self, labels='%r', name=None, random=False):
        """Convert the Var into a Factor

        Parameters
        ----------
        labels : str | dict
            Either a format string for converting values into labels (default:
            ``'%r'``) or a dictionary mapping values to labels (see examples).
            In a dictionary, multiple values can be assigned the same label by
            providing multiple keys in a tuple. A special key 'default' can be
            used to assign values that are not otherwise specified in the
            dictionary (by default this is the empty string ``''``).
        name : str
            Name of the output Factor (default is the current name).
        random : bool
            Whether the Factor is a random Factor (default ``False``).

        Examples
        --------
        >>> v = Var([0, 1, 2, 3])
        >>> v.as_factor()
        Factor(['0', '1', '2', '3'])
        >>> v.as_factor({0: 'a', 1: 'b'})
        Factor(['a', 'b', '', ''])
        >>> v.as_factor({(0, 1): 'a', (2, 3): 'b'})
        Factor(['a', 'a', 'b', 'b'])
        >>> v.as_factor({0: 'a', 1: 'b', 'default': 'c'})
        Factor(['a', 'b', 'c', 'c'])
        """
        labels_ = {}
        if isinstance(labels, dict):
            # flatten
            for key, v in labels.items():
                if (isinstance(key, Sequence) and not isinstance(key, str)):
                    for k in key:
                        labels_[k] = v
                else:
                    labels_[key] = v

            default = labels_.pop('default', '')
            if default is not None:
                for key in np.unique(self.x):
                    if key not in labels_:
                        labels_[key] = default
        else:
            for value in np.unique(self.x):
                labels_[value] = labels % value

        if name is None or name is True:
            name = self.name

        return Factor(self.x, name, random, labels=labels_)

    def copy(self, name=None):
        "Return a deep copy"
        x = self.x.copy()
        if name is None or name is True:
            name = self.name
        return Var(x, name, info=deepcopy(self.info))

    def count(self):
        """Count the number of occurrence of each value

        Notes
        -----
        Counting starts with zero (see examples). This is to facilitate
        integration with indexing.

        Examples
        --------
        >>> v = Var([1, 2, 3, 1, 1, 1, 3])
        >>> v.count()
        Var([0, 0, 0, 1, 2, 3, 1])
        """
        x = np.empty(len(self.x), int)
        index = np.empty(len(self.x), bool)
        for v in np.unique(self.x):
            np.equal(self.x, v, index)
            x[index] = np.arange(index.sum())
        return Var(x, self.name)

    def aggregate(self, x, func=np.mean, name=None):
        """Summarize cases within cells of x

        Parameters
        ----------
        x : categorial
            Model defining cells in which to aggregate.
        func : callable
            Function that converts arrays into scalars, used to summarize data
            within each cell of x.
        name : str
            Name of the output (default is the current name).

        Returns
        -------
        aggregated_var : Var
            A Var instance with a single value for each cell in x.
        """
        if len(x) != len(self):
            err = "Length mismatch: %i (Var) != %i (x)" % (len(self), len(x))
            raise ValueError(err)

        x_out = []
        for cell in x.cells:
            x_cell = self.x[x == cell]
            if len(x_cell) > 0:
                x_out.append(func(x_cell))

        if name is None or name is True:
            name = self.name

        return Var(x_out, name, info=self.info.copy())

    @property
    def beta_labels(self):
        return [self.name]

    def diff(self, to_end=None, to_begin=None):
        """The differences between consecutive values

        Parameters
        ----------
        to_end : scalar (optional)
            Append ``to_end`` at the end.
        to_begin : scalar (optional)
            Add ``to_begin`` at the beginning.

        Returns
        -------
        diff : Var
            Difference.
        """
        if len(self) == 0:
            return Var(np.empty(0), info=self.info.copy())
        return Var(np.ediff1d(self.x, to_end, to_begin), info=self.info.copy())

    # def difference(self, x, v1, v2, match):
    #     """
    #     Subtract x==v2 from x==v1; sorts values according to match (ascending)
    #
    #     Parameters
    #     ----------
    #     x : categorial
    #         Model to define cells.
    #     v1, v2 : str | tuple
    #         Cells on x for subtraction.
    #     match : categorial
    #         Model that defines how to mach cells in v1 to cells in v2.
    #     """
    #     raise NotImplementedError
    #     # FIXME: use celltable
    #     assert isinstance(x, Factor)
    #     I1 = (x == v1);         I2 = (x == v2)
    #     Y1 = self[I1];          Y2 = self[I2]
    #     m1 = match[I1];         m2 = match[I2]
    #     s1 = np.argsort(m1);    s2 = np.argsort(m2)
    #     y = Y1[s1] - Y2[s2]
    #     name = "{n}({x1}-{x2})".format(n=self.name,
    #                                    x1=x.cells[v1],
    #                                    x2=x.cells[v2])
    #     return Var(y, name, info=self.info.copy())

    @classmethod
    def from_dict(cls, base, values, name=None, default=0, info=None):
        """
        Construct a Var object by mapping ``base`` to ``values``.

        Parameters
        ----------
        base : sequence
            Sequence to be mapped to the new Var.
        values : dict
            Mapping from values in base to values in the new Var.
        name : str
            Name for the new Var.
        default : scalar
            Default value to supply for entries in ``base`` that are not in
            ``values``.

        Examples
        --------
        >>> base = Factor('aabbcde')
        >>> Var.from_dict(base, {'a': 5, 'e': 8}, default=0)
        Var([5, 5, 0, 0, 0, 0, 8])
        """
        return cls([values.get(b, default) for b in base], name, info=info)

    @classmethod
    def from_apply(cls, base, func, name=None, info=None):
        """
        Construct a Var instance by applying a function to each value in a base

        Parameters
        ----------
        base : sequence, len = n
            Base for the new Var. Can be an NDVar, if ``func`` is a
            dimensionality reducing function such as :func:`numpy.mean`.
        func : callable
            A function that when applied to each element in ``base`` returns
            the desired value for the resulting Var.
        name : str
            Name for the new Var.
        info : dict
            Info for the new Var.
        """
        if isinstance(base, (Var, NDVar)):
            base = base.x

        if isinstance(func, np.ufunc):
            x = func(base)
        elif getattr(base, 'ndim', 1) > 1:
            x = func(base.reshape((len(base), -1)), axis=1)
        else:
            x = np.array([func(val) for val in base])

        return cls(x, name, info=info)

    def index(self, value):
        "``v.index(value)`` returns an array of indices where v equals value"
        return np.flatnonzero(self == value)

    def isany(self, *values):
        "Boolean index, True where the Var is equal to one of the values"
        return np.in1d(self.x, values)

    def isin(self, values):
        "Boolean index, True where the Var value is in values"
        if isinstance(values, dict):
            values = tuple(values)
        return np.in1d(self.x, values)

    def isnot(self, *values):
        "Boolean index, True where the Var is not equal to one of the values"
        return np.in1d(self.x, values, invert=True)

    def isnotin(self, values):
        "Boolean index, True where the Var value is not in values"
        return np.in1d(self.x, values, invert=True)

    def log(self, base=None, name=None):
        """Element-wise log

        Parameters
        ----------
        base : scalar
            Base of the log (default is the natural log).
        name : str
            Name of the output Var (default is the current name).
        """
        if base is None:
            x = np.log(self.x)
        elif base == 2:
            x = np.log2(self.x)
        elif base == 10:
            x = np.log10(self.x)
        else:
            x = np.log(self.x)
            x /= log(base)
        if name is None:
            name = self.name
        info = self.info.copy()
        if base is None:
            info['longname'] = f'log({longname(self)})'
        else:
            info['longname'] = f'log{base}({longname(self)})'
        return Var(x, name, info=info)

    def max(self):
        "The highest value"
        return self.x.max()

    def mean(self):
        "The mean"
        return self.x.mean()

    def min(self):
        "The smallest value"
        return self.x.min()

    def repeat(self, repeats, name=None):
        """
        Repeat each element ``repeats`` times

        Parameters
        ----------
        repeats : int | array of int
            Number of repeats, either a constant or a different number for each
            element.
        name : str
            Name of the output Var (default is current name).
        """
        if name is None or name is True:
            name = self.name
        return Var(self.x.repeat(repeats), name, info=self.info.copy())

    def split(self, n=2, name=None):
        """
        A Factor splitting y into ``n`` categories with equal number of cases

        Parameters
        ----------
        n : int
            number of categories
        name : str
            Name of the output Var (default is current name).

        Examples
        --------
        Use n = 2 for a median split::

            >>> y = Var([1,2,3,4])
            >>> y.split(2)
            Factor(['0', '0', '1', '1'])

            >>> z = Var([7, 6, 5, 4, 3, 2])
            >>> z.split(3)
            Factor(['2', '2', '1', '1', '0', '0'])

        """
        y = self.x

        d = 100. / n
        percentile = np.arange(d, 100., d)
        values = [scipy.stats.scoreatpercentile(y, p) for p in percentile]
        x = np.zeros(len(y), dtype=int)
        for v in values:
            x += y > v
        if name is None:
            name = self.name
        return Factor(x, name)

    def std(self):
        "The standard deviation"
        return self.x.std()

    def sort_index(self, descending=False):
        """Create an index that could be used to sort the Var.

        Parameters
        ----------
        descending : bool
            Sort in descending instead of an ascending order.
        """
        idx = np.argsort(self.x, kind='mergesort')
        if descending:
            idx = idx[::-1]
        return idx

    def sum(self):
        "The sum over all values"
        return self.x.sum()

    @property
    def values(self):
        return np.unique(self.x)


class _Effect:
    # numeric ---
    def __add__(self, other):
        return Model(self) + other

    def __mul__(self, other):
        if partially_nested(other, self):
            return Model((self, other))
        return Model((self, other, self % other))

    def __mod__(self, other):
        if isinstance(other, Model):
            return Model((self % e for e in other.effects))
        return Interaction((self, other))

    def as_var(self, labels, default=None, name=None):
        """Convert into a Var

        Parameters
        ----------
        labels : dict
            A ``{old_value: new_value}`` mapping.
        default : None | scalar
            Default value for old values not mentioned in ``labels``. If not
            specified, old values missing from ``labels`` will raise a
            ``KeyError``.
        name : str
            Name of the output Var (default is current name).
        """
        if default is None:
            x = [labels[v] for v in self]
        else:
            x = [labels.get(v, default) for v in self]
        return Var(x, name or self.name)

    def count(self, value, start=-1):
        """Cumulative count of the occurrences of ``value``

        Parameters
        ----------
        value : str | tuple  (value in .cells)
            Cell value which is to be counted.
        start : int
            Value at which to start counting (with the default of -1, the first
            occurrence will be 0).

        Returns
        -------
        count : Var of int,  len = len(self)
            Cumulative count of value in self.

        Examples
        --------
        >>> a = Factor('abc', tile=3)
        >>> a
        Factor(['a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c'])
        >>> a.count('a')
        array([0, 0, 0, 1, 1, 1, 2, 2, 2])
        """
        return Var(np.cumsum(self == value) + start)

    def enumerate_cells(self, name=None):
        """Enumerate the occurrence of each cell value throughout the data

        Parameters
        ----------
        name : None | str
            Name for the returned Var.

        Returns
        -------
        enum : Var
            Result.

        Examples
        --------
        >>> f = Factor('aabbccabc')
        >>> f.enumerate_cells()
        Var([0, 1, 0, 1, 0, 1, 2, 2, 2])
        """
        counts = {cell: 0 for cell in self.cells}
        enum = np.empty(len(self), int)
        for i, value in enumerate(self):
            enum[i] = counts[value]
            counts[value] += 1
        return Var(enum, name)

    def index(self, cell):
        """Array with ``int`` indices equal to ``cell``

        Examples
        --------
        >>> f = Factor('abcabcabc')
        >>> f
        Factor(['a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c'])
        >>> f.index('b')
        array([1, 4, 7])
        >>> f[f.index('b')] = 'new_b'
        >>> f
        Factor(['a', 'new_b', 'c', 'a', 'new_b', 'c', 'a', 'new_b', 'c'])
        """
        return np.flatnonzero(self == cell)

    def index_opt(self, cell):
        """Find an optimized index for a given cell.

        Returns
        -------
        index : slice | array
            If possible, a ``slice`` object is returned. Otherwise, an array
            of indices (as with ``e.index(cell)``).
        """
        index = np.flatnonzero(self == cell)
        d_values = np.unique(np.diff(index))
        if len(d_values) == 1:
            start = index.min() or None
            step = d_values[0]
            stop = index.max() + 1
            if stop > len(self) - step:
                stop = None
            if step == 1:
                step = None
            index = slice(start, stop, step)
        return index

    def sort_index(self, descending=False, order=None):
        """Create an index that could be used to sort this data_object.

        Parameters
        ----------
        descending : bool
            Sort in descending instead of the default ascending order.
        order : None | sequence
            Sequence of cells to define a custom order. Any cells that are not
            present in ``order`` will be omitted in the sort_index, i.e. the
            sort_index will be shorter than its source.

        Returns
        -------
        sort_index : array of int
            Array which can be used to sort a data_object in the desired order.
        """
        idx = np.empty(len(self), dtype=np.intp)
        if order is None:
            cells = self.cells
        else:
            cells = order
            idx.fill(-1)

        for i, cell in enumerate(cells):
            idx[self == cell] = i

        sort_idx = np.argsort(idx, kind='mergesort')
        if order is not None:
            excluded = np.count_nonzero(idx == -1)
            if excluded:
                sort_idx = sort_idx[excluded:]

        if descending:
            if not isinstance(descending, bool):
                raise TypeError("descending=%s, need bool" % repr(descending))
            sort_idx = sort_idx[::-1]

        return sort_idx


class Factor(_Effect):
    """Container for categorial data.

    Parameters
    ----------
    x : iterator
        Sequence of Factor values (see also the ``labels`` kwarg).
    name : str
        Name of the Factor.
    random : bool
        Treat Factor as random factor (for ANOVA; default is False).
    repeat : int | array of int
        repeat each element in ``x``, either a constant or a different number
        for each element.
    tile : int
        Repeat ``x`` as a whole ``tile`` many times.
    labels : dict
        An optional dictionary mapping values as they occur in ``x`` to the
        Factor's cell labels.
    default : str
        Label to assign values not in ``label`` (by default this is
        ``str(value)``).

    Attributes
    ----------
    .name : None | str
        The Factor's name.
    .cells : tuple of str
        Sorted names of all cells.
    .random : bool
        Whether the Factor is defined as random factor (for ANOVA).

    Examples
    --------
    The most obvious way to initialize a Factor is a list of strings::

        >>> Factor(['in', 'in', 'in', 'out', 'out', 'out'])
        Factor(['in', 'in', 'in', 'out', 'out', 'out'])

    The same can be achieved with a list of integers plus a labels dict::

        >>> Factor([1, 1, 1, 0, 0, 0], labels={1: 'in', 0: 'out'})
        Factor(['in', 'in', 'in', 'out', 'out', 'out'])

    Or more parsimoniously:

        >>> Factor([1, 0], labels={1: 'in', 0: 'out'}, repeat=3)
        Factor(['in', 'in', 'in', 'out', 'out', 'out'])

    Since the Factor initialization simply iterates over the ``x``
    argument, a Factor with one-character codes can also be initialized
    with a single string::

        >>> Factor('iiiooo')
        Factor(['i', 'i', 'i', 'o', 'o', 'o'])
    """
    def __init__(self, x, name=None, random=False, repeat=1, tile=1, labels=None, default=None):
        if isinstance(x, Iterator):
            x = list(x)
        n_cases = len(x)
        self.name = name
        self.random = random

        if n_cases == 0 or not (np.any(repeat) or np.any(tile)):
            self.x = np.empty(0, np.uint32)
            self._labels = {}
            self._init_secondary()
            return

        # find mapping and ordered values
        labels = {} if labels is None else dict(labels)

        if isinstance(x, Factor):
            labels = {x._codes[s]: d for s, d in labels.items() if s in x._codes}
            labels.update({code: label for code, label in x._labels.items() if code not in labels})
            x = x.x

        if isinstance(x, np.ndarray) and x.dtype.kind in 'ifb':
            assert x.ndim == 1
            unique = np.unique(x)
            for v in unique:
                if v not in labels:
                    if default is None:
                        labels[v] = str(v)
                    else:
                        labels[v] = default
            # find labels corresponding to unique values
            u_labels = [labels[v] for v in unique]
            # merge identical labels
            u_label_index = np.array([u_labels.index(label) for label in u_labels])
            x_ = u_label_index[np.digitize(x, unique, True)]
            # {label: code}
            codes = dict(zip(u_labels, u_label_index))
        else:
            # convert x to codes
            highest_code = -1
            codes = {}  # {label -> code}
            x_ = np.empty(n_cases, dtype=np.uint32)
            for i, value in enumerate(x):
                if value in labels:
                    label = labels[value]
                elif default is not None:
                    label = labels[value] = default
                elif isinstance(value, str):
                    label = labels[value] = value
                else:
                    label = labels[value] = str(value)

                if label in codes:
                    x_[i] = codes[label]
                else:  # new code
                    x_[i] = codes[label] = highest_code = highest_code + 1

            if highest_code >= 2**32:
                raise RuntimeError("Too many categories in this Factor")

        # redefine labels for new codes
        labels = {codes[label]: label for label in labels.values() if label in codes}

        if not (isinstance(repeat, int) and repeat == 1):
            x_ = x_.repeat(repeat)
        if tile != 1:
            x_ = np.tile(x_, tile)
        self.x = x_
        self._labels = labels
        self._init_secondary()

    def _init_secondary(self):
        self._codes = {label: code for code, label in self._labels.items()}
        self._n_cases = len(self.x)

    def __setstate__(self, state):
        self.x = state['x']
        self.name = state['name']
        self.random = state['random']
        if 'ordered_labels' in state:
            # 0.13:  ordered_labels replaced labels
            self._labels = state['ordered_labels']
        else:
            labels = state['labels']
            codes = {label: code for code, label in labels.items()}
            self._labels = {codes[label]: label for label in natsorted(labels.values())}
        self._init_secondary()

    def __getstate__(self):
        state = {'x': self.x,
                 'name': self.name,
                 'random': self.random,
                 'ordered_labels': self._labels}
        return state

    def __repr__(self, full=False):
        use_labels = preferences['factor_repr_use_labels']
        n_cases = preferences['factor_repr_n_cases']

        if use_labels:
            values = self.as_labels()
        else:
            values = self.x.tolist()

        if full or len(self.x) <= n_cases:
            x = repr(values)
        else:
            x = [repr(v) for v in values[:n_cases]]
            x.append('<... N=%s>' % len(self.x))
            x = '[' + ', '.join(x) + ']'

        args = [x]

        if self.name is not None:
            args.append('name=%r' % self.name)

        if self.random:
            args.append('random=True')

        if not use_labels:
            args.append('labels=%s' % self._labels)

        return 'Factor(%s)' % ', '.join(args)

    def __str__(self):
        return self.__repr__(True)

    # container ---
    def __len__(self):
        return self._n_cases

    def __getitem__(self, index):
        index = asindex(index)
        x = self.x[index]
        if isinstance(x, np.ndarray):
            return Factor(x, self.name, self.random, labels=self._labels)
        else:
            return self._labels[x]

    def __setitem__(self, index, x):
        # convert x to code
        if isinstance(x, str):
            self.x[index] = self._get_code(x)
        else:
            self.x[index] = list(map(self._get_code, x))

        # obliterate redundant labels
        for code in set(self._labels).difference(self.x):
            del self._codes[self._labels.pop(code)]

    def _get_code(self, label):
        "Add the label if it does not exists and return its code"
        try:
            return self._codes[label]
        except KeyError:
            code = 0
            while code in self._labels:
                code += 1

            if code >= 2**32:
                raise ValueError("Too many categories in this Factor.")

            self._labels[code] = label
            self._codes[label] = code
            return code

    def __iter__(self):
        return (self._labels[i] for i in self.x)

    def __contains__(self, value):
        return value in self._codes

    # numeric ---
    def __eq__(self, other):
        return self.x == self._encode(other)

    def __ne__(self, other):
        return self.x != self._encode(other)

    def _encode(self, x):
        if isinstance(x, str):
            return self._codes.get(x, -1)
        elif len(x) == 0:
            return np.empty(0, dtype=int)
        elif isinstance(x, Factor):
            mapping = [self._codes.get(x._labels.get(xcode, -1), -1) for
                       xcode in range(x.x.max() + 1)]
            return np.array(mapping)[x.x]
        else:
            return np.array([self._codes.get(label, -1) for label in x])

    def __call__(self, other):
        """Create a nested effect.

        A factor A is nested in another factor B if
        each level of A only occurs together with one level of B.

        """
        return NestedEffect(self, other)

    @property
    def as_dummy(self):  # x_dummy_coded
        codes = np.empty((self._n_cases, self.df))
        for i, cell in enumerate(self.cells[:-1]):
            codes[:, i] = (self == cell)
        return codes

    @property
    def as_dummy_complete(self):
        x = self.x
        categories = np.unique(x)
        out = np.empty((len(self), len(categories)))
        for i, cat in enumerate(categories):
            np.equal(x, cat, out[:, i])
        return out

    @property
    def as_effects(self):  # x_deviation_coded
        shape = (self._n_cases, self.df)
        codes = np.empty(shape)
        for i, cell in enumerate(self.cells[:-1]):
            codes[:, i] = (self == cell)

        contrast = (self == self.cells[-1])
        codes -= contrast[:, None]
        return codes

    def _coefficient_names(self, method):
        if method == 'dummy':
            return ["%s:%s" % (self.name, cell) for cell in self.cells[:-1]]
        contrast_cell = self.cells[-1]
        return ["%s:%s-%s" % (self.name, cell, contrast_cell)
                for cell in self.cells[:-1]]

    def as_labels(self):
        "Convert the Factor to a list of str"
        return [self._labels[v] for v in self.x]

    @property
    def beta_labels(self):
        cells = self.cells
        txt = '{0}=={1}'
        return [txt.format(cells[i], cells[-1]) for i in range(len(cells) - 1)]

    @property
    def cells(self):
        return tuple(self._labels.values())

    def _cellsize(self):
        "int if all cell sizes are equal, otherwise a {cell: size} dict"
        buf = np.empty(self.x.shape, bool)
        ns = {value: np.equal(self.x, code, buf).sum() for code, value
              in self._labels.items()}
        n_set = set(ns.values())
        if len(n_set) == 1:
            return n_set.pop()
        else:
            return ns

    def _summary(self, width=80):
        ns = [(label, np.sum(self.x == code)) for code, label in self._labels.items()]
        items = [f'{label}:{n}' if n > 1 else label for label, n in ns]
        if sum(map(len, items)) + 2 * len(items) - 2 <= width:
            return ', '.join(items)
        n_cells = f'... ({len(items)} cells)'
        n = len(n_cells)
        for i, item in enumerate(items):
            if n + len(item) > width:
                break
            n += len(item) + 2
        return f"{', '.join(items[:i])}{n_cells}"

    def aggregate(self, x, name=None):
        """
        Summarize the Factor by collapsing within cells in `x`.

        Raises an error if there are cells that contain more than one value.

        Parameters
        ----------
        x : categorial
            A categorial model defining cells to collapse.
        name : str
            Name of the output Factor (default is current name).

        Returns
        -------
        f : Factor
            A copy of self with only one value for each cell in x
        """
        if len(x) != len(self):
            raise ValueError(
                f"x={dataobj_repr(x)} of length {len(x)} for Factor "
                f"{dataobj_repr(self)} of length {len(self)}")

        x_out = []
        for cell in x.cells:
            idx = (x == cell)
            if np.sum(idx):
                x_i = np.unique(self.x[idx])
                if len(x_i) > 1:
                    labels = tuple(self._labels[code] for code in x_i)
                    raise ValueError(
                        f"Can not determine aggregated value for Factor "
                        f"{dataobj_repr(self)} in cell {cell!r} because the "
                        f"cell contains multiple values {labels}. Set "
                        f"drop_bad=True in order to ignore this inconsistency "
                        f"and drop the Factor.")
                else:
                    x_out.append(x_i[0])

        if name is None or name is True:
            name = self.name

        return Factor(x_out, name, self.random, labels=self._labels)

    def copy(self, name=None, repeat=1, tile=1):
        "A deep copy"
        if name is None or name is True:
            name = self.name
        return Factor(self.x, name, self.random, repeat, tile, self._labels)

    @property
    def df(self):
        return max(0, len(self._labels) - 1)

    def endswith(self, substr):
        """An index that is true for all cases whose name ends with ``substr``

        Parameters
        ----------
        substr : str
            String for selecting cells that end with substr.

        Returns
        -------
        idx : boolean array,  len = len(self)
            Index that is true wherever the value ends with ``substr``.

        Examples
        --------
        >>> a = Factor(['a1', 'a2', 'b1', 'b2'])
        >>> a.endswith('1')
        array([True, False,  True,  False], dtype=bool)
        """
        values = [v for v in self.cells if v.endswith(substr)]
        return self.isin(values)

    def floodfill(self, regions, empty=''):
        """Fill in empty regions in a Factor from the nearest non-empty value

        Parameters
        ----------
        regions : array_like | str
            How to define regions to fill. Can be an object with same length as
            the factor that indicates regions to fill (see example). Can also
            be ``"previous"``, in which case the last value before the empty
            cell is used.
        empty : str
            Value that is to be treated as empty (default is '').

        Examples
        --------
        >>> f = Factor(['', '', 'a', '', '', '', 'b', ''])
        >>> f.floodfill([1, 1, 1, 1, 2, 2, 2, 2])
        Factor(['a', 'a', 'a', 'a', 'b', 'b', 'b', 'b'])
        >>> f.floodfill([1, 1, 1, 2, 2, 2, 2, 2])
        Factor(['a', 'a', 'a', 'b', 'b', 'b', 'b', 'b'])
        >>> f.floodfill([1, 1, 1, 1, 1, 1, 1, 1])
        Factor(['a', 'a', 'a', 'a', 'a', 'a', 'b', 'b'])
        """
        if isinstance(regions, str) and regions not in ('previous',):
            raise ValueError("demarcation=%r" % (regions,))

        out = self.copy(None)
        if empty not in self._codes:
            return out
        empty = out._codes[empty]
        x = out.x

        if isinstance(regions, str):
            if regions == 'previous':
                is_empty = np.flatnonzero(x == empty)
                if is_empty[0] == 0:
                    is_empty = is_empty[1:]
                for i in is_empty:
                    x[i] = x[i - 1]
            else:
                raise RuntimeError("demarcation=%r" % (regions,))
        else:
            assert(len(regions) == self._n_cases)
            i_region_start = 0
            region_v = -1 if regions[0] is None else None
            fill_with = empty
            for i in range(self._n_cases):
                if regions[i] == region_v:
                    if x[i] == empty:
                        if fill_with != empty:
                            x[i] = fill_with
                    else:
                        if fill_with == empty:
                            x[i_region_start:i] = x[i]
                        fill_with = x[i]
                else:  # region change
                    region_v = regions[i]
                    fill_with = x[i]
                    if fill_with == empty:
                        i_region_start = i

        # remove redundant label
        if empty not in x:
            del out._codes[out._labels.pop(empty)]

        return out

    def get_index_to_match(self, other):
        """Generate index to conform to another Factor's order

        Assuming that ``other`` is a reordered version of self,
        ``get_index_to_match()`` generates an index to transform from the order
        of ``self`` to the order of ``other``.
        To guarantee exact matching, each value can only occur once in ``self``.

        Examples
        --------
        >>> index = factor1.get_index_to_match(factor2)
        >>> all(factor1[index] == factor2)
        True

        """
        assert self._labels == other._labels
        index = []
        for v in other.x:
            where = np.where(self.x == v)[0]
            if len(where) == 1:
                index.append(where[0])
            else:
                msg = "%r contains several cases of %r" % (self, v)
                raise ValueError(msg)
        return np.array(index)

    def isany(self, *values):
        """Find the index of entries matching one of the ``*values``

        Returns
        -------
        index : array of bool
            For each case True if the value is in values, else False.

        Examples
        --------
        >>> a = Factor('aabbcc')
        >>> b.isany('b', 'c')
        array([False, False,  True,  True,  True,  True], dtype=bool)
        """
        return self.isin(values)

    def isin(self, values):
        """Find the index of entries matching one of the ``values``

        Returns
        -------
        index : array of bool
            For each case True if the value is in values, else False.

        Examples
        --------
        >>> f = Factor('aabbcc')
        >>> f.isin(('b', 'c'))
        array([False, False,  True,  True,  True,  True], dtype=bool)
        """
        return np.in1d(self.x, self._encode(values))

    def isnot(self, *values):
        """Find the index of entries not in ``values``

        Returns
        -------
        index : array of bool
            For each case False if the value is in values, else True.
        """
        return self.isnotin(values)

    def isnotin(self, values):
        """Find the index of entries not in ``values``

        Returns
        -------
        index : array of bool
            For each case False if the value is in values, else True.
        """
        return np.in1d(self.x, self._encode(values), invert=True)

    def label_length(self, name=None):
        """Create Var with the length of each label string

        Parameters
        ----------
        name : str
            Name of the output Factor (default is current name).

        Examples
        --------
        >>> f = Factor(['a', 'ab', 'long_label'])
        >>> f.label_length()
        Var([1, 2, 10])
        """
        label_lengths = {code: len(label) for code, label in self._labels.items()}
        x = np.empty(len(self))
        for i, code in enumerate(self.x):
            x[i] = label_lengths[code]

        if name is None:
            name = self.name
            if self.name:
                longname = self.name + '.label_length()'
            else:
                longname = 'label_length'
        else:
            longname = name

        return Var(x, name, info={"longname": longname})

    @property
    def n_cells(self):
        return len(self._labels)

    def update_labels(self, labels):
        """Change one or more labels in place

        Parameters
        ----------
        labels : dict
            Mapping from old labels to new labels. Existing labels that are not
            in ``labels`` are kept.

        Examples
        --------
        >>> f = Factor('aaabbbccc')
        >>> f
        Factor(['a', 'a', 'a', 'b', 'b', 'b', 'c', 'c', 'c'])
        >>> f.update_labels({'a': 'v1', 'b': 'v2'})
        >>> f
        Factor(['v1', 'v1', 'v1', 'v2', 'v2', 'v2', 'c', 'c', 'c'])

        In order to create a copy of the Factor with different labels just
        use the labels argument when initializing a new Factor:

        >>> Factor(f, labels={'c': 'v3'})
        Factor(['v1', 'v1', 'v1', 'v2', 'v2', 'v2', 'v3', 'v3', 'v3'])

        Notes
        -----
        If ``labels`` contains a key that is not a label of the Factor, a
        ``KeyError`` is raised.
        """
        missing = [old for old in labels if old not in self._codes]
        if missing:
            if len(missing) == 1:
                msg = ("Factor does not contain label %r" % missing[0])
            else:
                msg = ("Factor does not contain labels %s"
                       % ', '.join(repr(m) for m in missing))
            raise KeyError(msg)

        # check for merged labels
        new_labels = {c: labels.get(l, l) for c, l in self._labels.items()}
        codes_ = sorted(new_labels)
        labels_ = tuple(new_labels[c] for c in codes_)
        for i, label in enumerate(labels_):
            if label in labels_[:i]:
                old_code = codes_[i]
                new_code = codes_[labels_.index(label)]
                self.x[self.x == old_code] = new_code
                del new_labels[old_code]

        self._labels = new_labels
        self._codes = {l: c for c, l in new_labels.items()}

    def sort_cells(self, order):
        """Reorder the cells of the Factor (in-place)

        The cell order controls the order in which data are displayed in tables
        and plots.

        Parameters
        ----------
        order : sequence of str
            New cell order. Needs to contain each cell exactly once.
        """
        new_order = tuple(order)
        new = set(new_order)
        old = set(self.cells)
        if new != old:
            invalid = new.difference(old)
            if invalid:
                raise ValueError("Factor does not have cells: %s" % ', '.join(invalid))
            missing = old.difference(new)
            if missing:
                raise ValueError("Factor has cennls not in order: %s" % ', '.join(missing))
            raise RuntimeError("Factor.sort_cells comparing %s and %s" % (old, new))
        self._labels = {self._codes[cell]: cell for cell in new_order}

    def startswith(self, substr):
        """An index that is true for all cases whose name starts with ``substr``

        Parameters
        ----------
        substr : str
            String for selecting cells that start with substr.

        Returns
        -------
        idx : boolean array,  len = len(self)
            Index that is true wherever the value starts with ``substr``.

        Examples
        --------
        >>> a = Factor(['a1', 'a2', 'b1', 'b2'])
        >>> a.startswith('b')
        array([False, False,  True,  True], dtype=bool)
        """
        values = [v for v in self.cells if v.startswith(substr)]
        return self.isin(values)

    def table_categories(self):
        "A table containing information about categories"
        table = fmtxt.Table('rll')
        table.title(self.name)
        for title in ['i', 'Label', 'n']:
            table.cell(title)
        table.midrule()
        for code, label in self._labels.items():
            table.cell(code)
            table.cell(label)
            table.cell(np.sum(self.x == code))
        return table

    def repeat(self, repeats, name=None):
        """Repeat each element ``repeats`` times

        Parameters
        ----------
        repeats : int | array of int
            Number of repeats, either a constant or a different number for each
            element.
        name : str
            Name of the output Factor (default is current name).
        """
        if name is None or name is True:
            name = self.name
        return Factor(self.x, name, self.random, repeats, labels=self._labels)

    def tile(self, repeats, name=None):
        """Construct a Factor by repeating ``self`` ``repeats`` times

        Parameters
        ----------
        repeats : int
            Number of repeats.
        name : str
            Name of the output Factor (default is current name).
        """
        if name is None or name is True:
            name = self.name
        return Factor(self.x, name, self.random, tile=repeats, labels=self._labels)


class NDVar:
    """Container for n-dimensional data.

    Parameters
    ----------
    x : array_like
        The data.
    dims : Sequence of Dimension
        The dimensions characterizing the axes of the data. If present, ``Case``
        should always occupy the first position.
    info : dict
        A dictionary with data properties (can contain arbitrary
        information that will be accessible in the info attribute).
    name : str
        Name for the NDVar.


    Notes
    -----
    An :class:`NDVar` consists of the following components:

    - A :class:`numpy.ndarray`, stored in the :attr:`.x` attribute.
    - Meta-information describing each axis of the array using a
      :class:`Dimension` object (for example, :class:`UTS` for uniform
      time series, or :class:`Sensor` for a sensor array). These
      dimensions are stored in the :attr:`.dims` attribute, with the ith
      element of :attr:`.dims` describing the ith axis of :attr:`.x`.
    - A dictionary containing other meta-information stored in the
      :attr:`.info` attribute.
    - A name stored in the :attr:`.name` attribute.

    *Indexing*: For classical indexing, indexes need to be provided in the
    correct sequence. For example, assuming ``ndvar``'s first axis is time,
    ``ndvar[0.1]`` retrieves a slice at time = 0.1 s. If time is the second
    axis, the same can be achieved with ``ndvar[:, 0.1]``.
    In :meth:`NDVar.sub`, dimensions can be specified as keywords, for example,
    ``ndvar.sub(time=0.1)``, regardless of which axis represents the time
    dimension.

    *Shallow copies*: When generating a derived NDVars, :attr:`x` and
    :attr:`dims` are generated without copying data whenever possible.
    A shallow copy of :attr:`info` is stored. This means that modifying a
    derived NDVar in place can affect the NDVar it was derived from.
    When indexing an NDVar, the new NDVar will contain a view
    on the data whenever possible based on the underlying array (See `NumPy
    Indexing <https://docs.scipy.org/doc/numpy/reference/arrays.indexing
    .html>`_). This only matters when explicitly modifying an NDVar in place
    (e.g., ``ndvar += 1``) because NDVar methods that return NDVars never
    implicitly modify the original NDVars in place (see `this note
    <https://mail.python.org/pipermail/python-dev/2003-October/038855.html>`_).


    Examples
    --------
    Create an NDVar for 600 time series of 80 time points each:

    >>> data.shape
    (600, 80)
    >>> time = UTS(-.2, .01, 80)
    >>> ndvar = NDVar(data, dims=(Case, time))

    Baseline correction:

    >>> ndvar -= ndvar.mean(time=(None, 0))

    """
    def __init__(self, x, dims, info={}, name=None):
        # check data shape
        if (isinstance(dims, Dimension) or dims is Case or isinstance(dims, str)):
            dims_ = [dims]
        else:
            dims_ = list(dims)

        x = np.asanyarray(x)
        if len(dims_) != x.ndim:
            raise DimensionMismatchError(
                "Unequal number of dimensions (data: %i, dims: %i)" %
                (x.ndim, len(dims_)))

        first_dim = dims_[0]
        if first_dim is Case or (isinstance(first_dim, str) and first_dim == 'case'):
            dims_[0] = Case(len(x))

        if not all(isinstance(dim, Dimension) for dim in dims_):
            raise TypeError(
                "Invalid dimension in dims=%r. All dimensions need to be "
                "Dimension subclass objects, with the exception of the "
                "first dimension which can also be 'case'" % (dims,))
        elif any(isinstance(dim, Case) for dim in dims_[1:]):
            raise TypeError(
                "Invalid dimension in dims=%r. Only the first dimension can be "
                "Case." % (dims,))

        # check dimensions
        for dim, n in zip(dims_, x.shape):
            if len(dim) != n:
                raise DimensionMismatchError(
                    "Dimension %r length mismatch: %i in data, %i in dimension "
                    "%r" % (dim.name, n, len(dim), dim.name))

        self.x = x
        self.dims = tuple(dims_)
        self.info = dict(info)
        self.name = name
        self._init_secondary()

    def _init_secondary(self):
        self.has_case = isinstance(self.dims[0], Case)
        self._truedims = self.dims[self.has_case:]
        self.dimnames = tuple(dim.name for dim in self.dims)
        self.ndim = len(self.dims)
        self.shape = self.x.shape
        self._dim_2_ax = {dimname: i for i, dimname in enumerate(self.dimnames)}
        # Dimension attributes
        for dim in self._truedims:
            if hasattr(self, dim.name):
                raise ValueError("Invalid dimension name: %r (name is reserved "
                                 "for an NDVar attribute)" % dim.name)
            else:
                setattr(self, dim.name, dim)

    def __setstate__(self, state):
        # backwards compatibility
        if 'properties' in state:
            state['info'] = state.pop('properties')
        if isinstance(state['dims'][0], str):
            state['dims'] = (Case(len(state['x'])),) + state['dims'][1:]

        self.x = state['x']
        self.dims = state['dims']
        self.name = state['name']
        self.info = state['info']
        self._init_secondary()

    def __getstate__(self):
        return {'dims': self.dims,
                'x': self.x,
                'name': self.name,
                'info': self.info}

    __array_priority__ = 15

    @property
    def __array_interface__(self):
        return self.x.__array_interface__

    # numeric ---
    def __neg__(self):
        return NDVar(-self.x, self.dims, self.info, self.name)

    def __pos__(self):
        return self

    def __abs__(self):
        return self.abs()

    def __invert__(self):
        return NDVar(~self.x, self.dims, self.info, self.name)

    def __lt__(self, other):
        return NDVar(self.x < self._ialign(other),
                     self.dims, _info.for_boolean(self.info), self.name)

    def __le__(self, other):
        return NDVar(self.x <= self._ialign(other),
                     self.dims, _info.for_boolean(self.info), self.name)

    def __eq__(self, other):
        return NDVar(self.x == self._ialign(other),
                     self.dims, _info.for_boolean(self.info), self.name)

    def __ne__(self, other):
        return NDVar(self.x != self._ialign(other),
                     self.dims, _info.for_boolean(self.info), self.name)

    def __gt__(self, other):
        return NDVar(self.x > self._ialign(other),
                     self.dims, _info.for_boolean(self.info), self.name)

    def __ge__(self, other):
        return NDVar(self.x >= self._ialign(other),
                     self.dims, _info.for_boolean(self.info), self.name)

    def _align(self, other):
        """Align data from 2 NDVars.

        Notes
        -----
        For unequal but overlapping dimensions, the intersection is used.
        For example, ``c = a + b`` with ``a`` [-100 300] ms and ``b`` [0 400] ms
        ``c`` will be [0 300] ms.
        """
        if isinstance(other, Var):
            return self.dims, self.x, self._ialign(other)
        elif isinstance(other, NDVar):
            dimnames = list(self.dimnames)
            i_add = 0
            for dimname in other.dimnames:
                if dimname not in dimnames:
                    dimnames.append(dimname)
                    i_add += 1

            # find data axes
            self_axes = self.dimnames
            if i_add:
                self_axes += (None,) * i_add
            other_axes = tuple(name if name in other.dimnames else None
                               for name in dimnames)

            # find dims
            dims = []
            crop = False
            crop_self = []
            crop_other = []
            for name, other_name in zip(self_axes, other_axes):
                if name is None:
                    dim = other.get_dim(other_name)
                    cs = co = FULL_SLICE
                elif other_name is None:
                    dim = self.get_dim(name)
                    cs = co = FULL_SLICE
                else:
                    self_dim = self.get_dim(name)
                    other_dim = other.get_dim(other_name)
                    if self_dim == other_dim:
                        dim = self_dim
                        cs = co = FULL_SLICE
                    else:
                        dim = self_dim.intersect(other_dim)
                        crop = True
                        cs = self_dim._array_index(dim)
                        co = other_dim._array_index(dim)
                dims.append(dim)
                crop_self.append(cs)
                crop_other.append(co)

            x_self = self.get_data(self_axes)
            x_other = other.get_data(other_axes)
            if crop:
                x_self = x_self[tuple(crop_self)]
                x_other = x_other[tuple(crop_other)]
            return dims, x_self, x_other
        elif np.isscalar(other):
            return self.dims, self.x, other
        else:
            raise TypeError("%r; need NDVar, Var or scalar")

    def _ialign(self, other, index=None):
        """Align for self-modifying operations (+=, ...)

        Parameters
        ----------
        other : NDVar
            NDVar with data to align
        index : tuple
            Array-index into self to which to align (for assignment).
        """
        if np.isscalar(other):
            return other
        elif isinstance(other, Var):
            assert self.has_case
            n = len(other)
            shape = (n,) + (1,) * (self.x.ndim - 1)
            return other.x.reshape(shape)
        elif isinstance(other, NDVar):
            # filter out dimensions that are skipped in assignment
            if index is None:
                self_dims = self.dimnames
            elif isinstance(index, INT_TYPES):
                self_dims = self.dimnames[1:]
            else:
                self_dims = [dim for i, dim in zip_longest(index, self.dimnames) if not isinstance(i, INT_TYPES)]
            # make sure other does not have dimensions not in self
            missing = set(other.dimnames).difference(self_dims)
            if missing:
                raise ValueError(f"{other!r} contains dimensions not in NDVar: {', '.join(missing)}")
            # find index into other
            i_other = []
            for dim in self_dims:
                if dim in other.dimnames:
                    i_other.append(dim)
                else:
                    i_other.append(None)
            return other.get_data(i_other)
        else:
            raise TypeError(f"{other!r}; need NDVar, Var or scalar")

    def __add__(self, other):
        dims, x_self, x_other = self._align(other)
        return NDVar(x_self + x_other, dims, self.info, self.name)

    def __iadd__(self, other):
        if self.x.dtype.kind == 'b':
            return self.__add__(other)
        self.x += self._ialign(other)
        return self

    def __radd__(self, other):
        return NDVar(other + self.x, self.dims, self.info, self.name)

    def __div__(self, other):
        dims, x_self, x_other = self._align(other)
        return NDVar(x_self / x_other, dims, self.info, self.name)

    def __idiv__(self, other):
        if self.x.dtype.kind == 'b':
            return self.__div__(other)
        self.x /= self._ialign(other)
        return self

    def __rdiv__(self, other):
        return NDVar(other / self.x, self.dims, self.info, self.name)

    def __truediv__(self, other):
        return self.__div__(other)

    def __itruediv__(self, other):
        return self.__idiv__(other)

    def __rtruediv__(self, other):
        return self.__rdiv__(other)

    def __mul__(self, other):
        dims, x_self, x_other = self._align(other)
        return NDVar(x_self * x_other, dims, self.info, self.name)

    def __imul__(self, other):
        if self.x.dtype.kind == 'b':
            return self.__mul__(other)
        self.x *= self._ialign(other)
        return self

    def __rmul__(self, other):
        return NDVar(other * self.x, self.dims, self.info, self.name)

    def __pow__(self, other):
        dims, x_self, x_other = self._align(other)
        return NDVar(np.power(x_self, x_other), dims, self.info, self.name)

    def __ipow__(self, other):
        if self.x.dtype.kind == 'b':
            return self.__pow__(other)
        self.x **= self._ialign(other)
        return self

    def __rpow__(self, other):
        return NDVar(other ** self.x, self.dims, self.info, self.name)

    def __round__(self, n=0):
        return NDVar(np.round(self.x, n), self.dims, self.info, self.name)

    def __sub__(self, other):
        dims, x_self, x_other = self._align(other)
        return NDVar(x_self - x_other, dims, self.info, self.name)

    def __isub__(self, other):
        if self.x.dtype.kind == 'b':
            return self.__sub__(other)
        self.x -= self._ialign(other)
        return self

    def __rsub__(self, other):
        return NDVar(other - self.x, self.dims, self.info, self.name)

    def __and__(self, other):
        dims, x_self, x_other = self._align(other)
        return NDVar(x_self & x_other, dims, self.info, self.name)

    def __iand__(self, other):
        self.x &= self._ialign(other)
        return self

    def __rand__(self, other):
        return NDVar(other & self.x, self.dims, self.info, self.name)

    def __xor__(self, other):
        dims, x_self, x_other = self._align(other)
        return NDVar(x_self ^ x_other, dims, self.info, self.name)

    def __ixor__(self, other):
        self.x ^= self._ialign(other)
        return self

    def __rxor__(self, other):
        return NDVar(other ^ self.x, self.dims, self.info, self.name)

    def __or__(self, other):
        dims, x_self, x_other = self._align(other)
        return NDVar(x_self | x_other, dims, self.info, self.name)

    def __ior__(self, other):
        self.x |= self._ialign(other)
        return self

    def __ror__(self, other):
        return NDVar(other | self.x, self.dims, self.info, self.name)

    # container ---
    def _dim_index_unravel(self, index):
        "Convert ravelled array index to dimension index"
        if self.ndim == 1:
            return self.dims[0]._dim_index(index)
        return self._dim_index(np.unravel_index(index, self.x.shape))

    def _dim_index(self, index):
        "Convert array index to dimension index"
        if isinstance(index, tuple):
            return tuple(dim._dim_index(i) for dim, i in zip(self.dims, index))
        return self.dims[0]._dim_index(index)

    def __getitem__(self, index):
        if isinstance(index, tuple):
            return self.sub(*index)
        else:
            return self.sub(index)

    def __setitem__(self, key, value):
        index = self._array_index(key)
        if isinstance(value, NDVar):
            value = self._ialign(value, index)
        self.x[index] = value

    def __len__(self):
        return len(self.x)

    def __iter__(self):
        dim = self.dims[0]
        name = self.dimnames[0]
        for value in dim:
            yield self.sub(**{name: value})

    def __repr__(self):
        return '<NDVar%(name)s: %(dims)s>' % {
            'name': '' if self.name is None else ' %r' % self.name,
            'dims': ', '.join(f'{len(dim)} {dim.name}' for dim in self.dims)}

    def _summary(self, width=80):
        items = [f'{len(dim)} {dim.name}' for dim in self.dims[1:]]
        n = 0
        for i, item in enumerate(items):
            n += len(item)
            if n > width - 3:
                return ', '.join(items[:i]) + '...'
        out = ', '.join(items)
        range_desc = f'{np.nanmin(self.x):g} - {np.nanmax(self.x):g}'
        if len(out) + 2 + len(range_desc) <= width:
            if out:
                out += '; '
            out += range_desc
        return out

    def abs(self, name=None):
        """Compute the absolute values

        Parameters
        ----------
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        abs : NDVar
            NDVar with same dimensions and absolute values.
        """
        return NDVar(np.abs(self.x), self.dims, self.info, name or self.name)

    def all(self, dims=(), **regions):
        """Whether all values are nonzero over given dimensions

        Parameters
        ----------
        dims : str | tuple of str | boolean NDVar
            Dimensions over which to operate. A str is used to specify a single
            dimension, a tuple of str to specify several dimensions, None to
            compute whether there are any nonzero values at all.
            An boolean NDVar with the same dimensions as the data can be used
            to find nonzero values in specific elements (if the NDVar has cases
            on a per case basis).
        **regions
            Regions over which to aggregate as keywords. 
            For example, to check whether all values between time=0.1 and 
            time=0.2 are non-zero, use ``ndvar.all(time=(0.1, 0.2))``.
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        any : NDVar | Var | bool
            Boolean data indicating presence of nonzero value over specified
            dimensions. Return a Var if only the case dimension remains, and a
            boolean if the function collapses over all data.
            
        Examples
        --------
        Examples for
        
        >>> ndvar
        <NDVar 'utsnd': 60 case, 5 sensor, 100 time>

        Check whether all values are nonzero:
        
        >>> ndvar.all()
        True
        
        Check whether each time point contains at least one non-zero value
        
        >>> ndvar.all(('case', 'sensor'))
        <NDVar 'utsnd': 100 time>
        
        Check for nonzero values between time=0.1 and time=0.2
        
        >>> ndvar.all(time=(0.1, 0.2))
        <NDVar 'utsnd': 60 case, 5 sensor>
        
        """
        return self._aggregate_over_dims(dims, regions, np.all)

    def any(self, dims=(), **regions):
        """Compute presence of any value other than zero over given dimensions

        Parameters
        ----------
        dims : str | tuple of str | boolean NDVar
            Dimensions over which to operate. A str is used to specify a single
            dimension, a tuple of str to specify several dimensions, None to
            compute whether there are any nonzero values at all.
            An boolean NDVar with the same dimensions as the data can be used
            to find nonzero values in specific elements (if the NDVar has cases
            on a per case basis).
        **regions
            Regions over which to aggregate. For example, to check for nonzero
            values between time=0.1 and time=0.2, use
            ``ndvar.any(time=(0.1, 0.2))``.
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        any : NDVar | Var | bool
            Boolean data indicating presence of nonzero value over specified
            dimensions. Return a Var if only the case dimension remains, and a
            boolean if the function collapses over all data.
        """
        return self._aggregate_over_dims(dims, regions, np.any)

    def argmax(self):
        """Find the index of the largest value.

        ``ndvar[ndvar.argmax()]`` is equivalent to ``ndvar.max()``.

        Returns
        -------
        argmax : index | tuple
            Index appropriate for the NDVar's dimensions. If NDVar has more
            than one dimensions, a tuple of indices.
        """
        return self._dim_index_unravel(self.x.argmax())

    def argmin(self):
        """Find the index of the smallest value.

        ``ndvar[ndvar.argmin()]`` is equivalent to ``ndvar.min()``.

        Returns
        -------
        argmin : index | tuple
            Index appropriate for the NDVar's dimensions. If NDVar has more
            than one dimensions, a tuple of indices.
        """
        return self._dim_index_unravel(self.x.argmin())

    def _array_index(self, arg):
        "Convert dimension index to array index"
        if isinstance(arg, NDVar):
            if arg.x.dtype.kind != 'b':
                raise IndexError("Only boolean NDVar can be used as index")
            elif arg.dims == self.dims:
                return arg.x
            target_dims = tuple(dim if dim in arg.dimnames else None for dim in self.dimnames)
            shared_dims = tuple(filter(None, target_dims))
            self_dims = self.get_dims(shared_dims)
            args_dims = arg.get_dims(shared_dims)
            if args_dims != self_dims:
                raise DimensionMismatchError(
                    f'The index has different dimensions than the NDVar\n'
                    f'NDVar: {self_dims}\nIndex: {args_dims}')
            x = arg.x
            if arg.dimnames != shared_dims:
                if any(dim not in shared_dims for dim in arg.dimnames):
                    missing = (dim for dim in arg.dimnames if dim not in shared_dims)
                    raise DimensionMismatchError(
                        f"Index has dimensions {', '.join(missing)} not in {self}")
                source_axes = tuple(range(arg.ndim))
                dest_axes = tuple(shared_dims.index(dim) for dim in arg.dimnames)
                x = np.moveaxis(x, source_axes, dest_axes)
            for axis, dim in enumerate(target_dims):
                if dim is None:
                    x = np.expand_dims(x, axis)
                    x = np.repeat(x, self.shape[axis], axis)
            return x
        elif isinstance(arg, tuple):
            return tuple(dim._array_index(i) for dim, i in zip(self.dims, arg))
        elif isinstance(arg, np.ndarray) and arg.ndim > 1:
            raise NotImplementedError
        else:
            return self.dims[0]._array_index(arg)

    def assert_dims(self, dims):
        if self.dimnames != dims:
            err = "Dimensions of %r do not match %r" % (self, dims)
            raise DimensionMismatchError(err)

    def aggregate(self, x, func=np.mean, name=None):
        """
        Summarize data in each cell of ``x``.

        Parameters
        ----------
        x : categorial
            Categorial whose cells define which cases to aggregate.
        func : function with axis argument
            Function that is used to create a summary of the cases falling
            into each cell of x. The function needs to accept the data as
            first argument and ``axis`` as keyword-argument. Default is
            ``numpy.mean``.
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        aggregated_ndvar : NDVar
            NDVar with data aggregated over cells of ``x``.
        """
        if not self.has_case:
            raise DimensionMismatchError("%r has no case dimension" % self)
        if len(x) != len(self):
            err = "Length mismatch: %i (Var) != %i (x)" % (len(self), len(x))
            raise ValueError(err)

        x_out = []
        for cell in x.cells:
            idx = (x == cell)
            if np.sum(idx):
                x_cell = self.x[idx]
                x_out.append(func(x_cell, axis=0))

        # update info for summary
        info = self.info
        if 'summary_info' in info:
            info = info.copy()
            info.update(info.pop('summary_info'))
        return NDVar(np.array(x_out), (Case(len(x_out)),) + self.dims[1:], info, name or self.name)

    def _aggregate_over_dims(self, axis, regions, func):
        name = regions.pop('name', self.name)
        if regions:
            data = self.sub(**regions)
            additional_axis = [dim for dim in regions if data.has_dim(dim)]
            if additional_axis:
                if isinstance(axis, NDVar):
                    data = data.sub(axis)
                    axis = additional_axis
                elif not axis:
                    axis = additional_axis
                elif isinstance(axis, str):
                    axis = [axis] + additional_axis
                else:
                    axis = list(axis) + additional_axis
            return data._aggregate_over_dims(axis, {'name': name}, func)
        elif not axis:
            return func(self.x)
        elif isinstance(axis, NDVar):
            if axis.ndim == 1:
                dim = axis.dims[0]
                if self.get_dim(dim.name) != dim:
                    raise DimensionMismatchError("Index dimension %s does not "
                                                 "match data dimension" %
                                                 dim.name)
                dim_axis = self.get_axis(dim.name)
                index = FULL_AXIS_SLICE * dim_axis + (axis.x,)
                x = func(self.x[index], dim_axis)
                dims = tuple(self.dims[i] for i in range(self.ndim) if i != dim_axis)
            else:
                # if the index does not contain all dimensions, numpy indexing
                # is weird
                if self.ndim - self.has_case != axis.ndim - axis.has_case:
                    raise NotImplementedError(
                        "If the index is not one dimensional, it needs to have "
                        "the same dimensions as the data.")
                dims, self_x, index = self._align(axis)
                if self.has_case:
                    if axis.has_case:
                        x = np.array([func(x_[i]) for x_, i in zip(self_x, index)])
                    else:
                        index = index[0]
                        x = np.array([func(x_[index]) for x_ in self_x])
                    return Var(x, name, info=_info.for_data(x, self.info))
                elif axis.has_case:
                    raise IndexError("Index with case dimension can not be "
                                     "applied to data without case dimension")
                else:
                    return func(self_x[index])
        elif isinstance(axis, str):
            axis = self._dim_2_ax[axis]
            x = func(self.x, axis=axis)
            dims = tuple(self.dims[i] for i in range(self.ndim) if i != axis)
        else:
            axes = tuple(self._dim_2_ax[dim_name] for dim_name in axis)
            x = func(self.x, axes)
            dims = tuple(self.dims[i] for i in range(self.ndim) if i not in axes)

        return self._package_aggregated_output(x, dims, _info.for_data(x, self.info), name)

    def astype(self, dtype):
        """Copy of the NDVar with data cast to the specified type

        Parameters
        ----------
        dtype : numpy dtype
            Numpy data-type specification (see :meth:`numpy.ndarray.astype`).
        """
        return NDVar(self.x.astype(dtype), self.dims, self.info, self.name)

    def bin(self, step=None, start=None, stop=None, func=None, dim=None,
            name=None, nbins=None):
        """Bin the data along a given dimension (default ``'time'``)

        Parameters
        ----------
        step : scalar
            Time step between bins.
        start : None | scalar
            Earliest time point (default is from the beginning).
        stop : None | scalar
            End of the data to use (the default is to use as many whole
            ``tstep`` intervals as fit in the data).
        func : callable | str
            How to summarize data in each time bin. Can be the name of a numpy
            function that takes an axis parameter (e.g., 'sum', 'mean', 'max') or
            'extrema' which selects the value with the maximum absolute value.
            The default depends on ``ndvar.info['meas']``:
            'p': minimum;
            'f': maximum;
            't', 'r': extrema;
            otherwise: mean.
        dim : str
            Dimension over which to bin. If the NDVar has more than one
            dimension, the default is ``'time'``.
        name : str
            Name of the output NDVar (default is the current name).
        nbins : int
            Instead of specifying ``step``, ``nbins`` can be specified to divide
            ``dim`` into an even number of bins.

        Returns
        -------
        binned_ndvar : NDVar
            NDVar with data binned along the time axis (i.e., each time point
            reflects one time bin).
        """
        if nbins is not None:
            if step is not None:
                raise TypeError("can only specify one of step and nbins")
            elif not isinstance(nbins, int):
                raise TypeError(f"nbins={nbins!r}: need int")
            elif nbins < 1:
                raise ValueError(f"nbins={nbins}: needs to be >= 1")
        elif step is None and nbins is None:
            raise TypeError("need to specify one of step and nbins")

        if dim is None:
            if len(self.dims) == 1 + self.has_case:
                dim = self.dims[-1].name
            elif self.has_dim('time'):
                dim = 'time'
            else:
                raise TypeError("NDVar has more then 1 dimensions, the dim argument needs to be specified")

        # summary-func
        if func is None:
            meas = self.info.get('meas', '').lower()
            if meas == 'p':
                func = np.min
            elif meas == 'f':
                func = np.max
            elif meas in ('t', 'r'):
                func = extrema
            else:
                func = np.mean
        elif isinstance(func, str):
            if func not in EVAL_CONTEXT:
                raise ValueError(f"func={func!r}: unknown summary function")
            func = EVAL_CONTEXT[func]
        elif not callable(func):
            raise TypeError(f"func={func!r}")

        axis = self.get_axis(dim)
        dim = self.get_dim(dim)
        edges, out_dim = dim._bin(start, stop, step, nbins)

        out_shape = list(self.shape)
        out_shape[axis] = len(edges) - 1
        x = np.empty(out_shape)
        bins = []
        idx_prefix = FULL_AXIS_SLICE * axis
        for i, bin_ in enumerate(intervals(edges)):
            src_idx = idx_prefix + (dim._array_index(bin_),)
            dst_idx = idx_prefix + (i,)
            x[dst_idx] = func(self.x[src_idx], axis=axis)
            bins.append(bin_)

        dims = list(self.dims)
        dims[axis] = out_dim
        info = {**self.info, 'bins': tuple(bins)}
        return NDVar(x, dims, info, name or self.name)

    def clip(self, min=None, max=None, name=None, out=None):
        """Clip data (see :func:`numpy.clip`)

        Parameters
        ----------
        min : scalar | Var | NDVar
            Minimum value.
        max : scalar | Var | NDVar
            Maximum value.
        name : str
            Name of the output NDVar (default is the current name).
        out : NDVar
            Container for output.
        """
        if min is not None:
            min = self._ialign(min)
        if max is not None:
            max = self._ialign(max)
        if out is not None:
            if out is not self:
                assert out.dims == self.dims
            self.x.clip(min, max, out.x)
            return out
        else:
            x = self.x.clip(min, max)
            return NDVar(x, self.dims, self.info, name or self.name)

    def copy(self, name=None):
        """A deep copy of the NDVar's data

        Parameters
        ----------
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        ndvar_copy : NDVar
            An copy of the ndvar with a deep copy of the data.

        Notes
        -----
        The info dictionary is still a shallow copy.
        """
        return NDVar(self.x.copy(), self.dims, self.info, name or self.name)

    def diff(self, dim=None, n=1, pad=True, name=None):
        """Discrete difference

        parameters
        ----------
        dim : str
            Dimension along which to operate.
        n : int
            Number of times to difference (default 1).
        pad : bool
            Pad the ``dim`` dimension of the result to conserve NDVar shape
            (default).
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        diff : NDVar
            NDVar with the ``n`` th differences.
        """
        if dim is None:
            if self.ndim - self.has_case == 1:
                axis = -1
            else:
                raise TypeError("Need to specify dimension over which to "
                                "differentiate")
        else:
            axis = self.get_axis(dim)

        x = np.diff(self.x, n, axis)
        if pad == 1:
            idx = FULL_AXIS_SLICE * axis + (slice(0, n),)
            x = np.concatenate((np.zeros_like(x[idx]), x), axis)
        else:
            raise NotImplementedError("pad != 1")

        return NDVar(x, self.dims, self.info, name or self.name)

    def dot(self, ndvar, dim=None, name=None):
        """Dot product

        Parameters
        ----------
        ndvar : NDVar
            Second NDVar, has to have at least the dimension ``dim``.
        dim : str
            Dimension over which to form the dot product (default is the last
            dimension).
        name : str
            Name of the output NDVar (default is ``ndvar.name``).

        Examples
        --------
        >>> to_dss, from_dss = dss(x)
        >>> x_dss_6 = to_dss[:6].dot(x, 'sensor')
        """
        if dim is None:
            for dim in self.dimnames[::-1]:
                if ndvar.has_dim(dim):
                    break
        if dim == 'case':
            raise NotImplementedError("dim='case': dot-product along Case dimension")
        dim_x1 = self.get_dim(dim)
        dim_x2 = ndvar.get_dim(dim)
        if dim_x1 == dim_x2:
            x1_index = x2_index = None
        else:
            out_dim = dim_x1.intersect(dim_x2)
            x1_index = None if dim_x1 == out_dim else dim_x1._array_index_to(out_dim)
            x2_index = None if dim_x2 == out_dim else dim_x2._array_index_to(out_dim)

        v1_dimnames = self.get_dimnames((None,) * (self.ndim - 1) + (dim,))
        dims = [self.get_dim(d) for d in v1_dimnames[:-1]]

        v2_dimnames = (dim,)
        if ndvar.has_case:
            v2_dimnames = ('case',) + v2_dimnames
            dims.insert(0, Case)
        v2_dimnames += (None,) * (ndvar.ndim - ndvar.has_case - 1)
        v2_dimnames = ndvar.get_dimnames(v2_dimnames)
        dims.extend(ndvar.get_dim(d) for d in v2_dimnames[1 + ndvar.has_case:])

        x1 = self.get_data(v1_dimnames)
        if x1_index is not None:
            x1 = np.take(x1, x1_index, -1)
        x2 = ndvar.get_data(v2_dimnames)
        if x2_index is not None:
            x2 = np.take(x2, x2_index, v2_dimnames.index(dim))

        if ndvar.has_case:
            x = np.array([np.tensordot(x1, x2_, 1) for x2_ in x2])
        else:
            x = np.tensordot(x1, x2, 1)
            if not dims:
                return x

        if name is None:
            name = ndvar.name

        if len(dims) == 1 and dims[0] is Case:
            return Var(x, name)
        else:
            return NDVar(x, dims, {}, name)

    def envelope(self, dim='time', name=None):
        """Compute the Hilbert envelope of a signal

        Parameters
        ----------
        dim : str
            Dimension over which to compute the envelope (default 'time').
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        envelope : NDVar
            NDVar with identical dimensions containing the envelope.

        Notes
        -----
        The Hilbert envelope is computed with :func:`scipy.signal.hilbert`::

        >>> numpy.abs(scipy.signal.hilbert(x))

        This function can be very slow when the number of time samples is
        uneven.
        """
        x = np.abs(scipy.signal.hilbert(self.x, axis=self.get_axis(dim)))
        return NDVar(x, self.dims, self.info, name or self.name)

    def extrema(self, dims=(), **regions):
        """Extrema (value farthest away from 0) over given dimensions

        For each data point,
        ``extremum = max(x) if max(x) >= abs(min(x)) else min(x)``.

        Parameters
        ----------
        dims : str | tuple of str | boolean NDVar
            Dimensions over which to operate. A str is used to specify a single
            dimension, a tuple of str to specify several dimensions, ``None`` to
            compute the maximum over all dimensions.
            An boolean NDVar with the same dimensions as the data can be used
            to compute the extrema in specific elements (if the data has a case
            dimension, the extrema are computed for each case).
        **regions
            Regions over which to aggregate. For example, to get the extrema
            between 0.1 and 0.2 s, use ``ndvar.extrema(time=(0.1, 0.2))``.
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        extrema : NDVar | Var | float
            Extrema over specified dimensions. Return a Var if only the
            case dimension remains, and a float if the function collapses over
            all data.
        """
        return self._aggregate_over_dims(dims, regions, extrema)

    def fft(self, dim=None, name=None):
        """Fast fourier transform

        Parameters
        ----------
        dim : str
            Dimension along which to operate (the default is the ``time``
            dimension if present).
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        fft : NDVar
            NDVar containing the FFT, with the ``time`` dimension replaced by
            ``frequency``.
        """
        if dim is None:
            if self.ndim - self.has_case == 1:
                dim = self.dimnames[-1]
            elif self.has_dim('time'):
                dim = 'time'
            else:
                raise ValueError("NDVar has more than one dimension, you need "
                                 "to specify along which dimension to operate.")
        axis = self.get_axis(dim)
        x = np.abs(np.fft.rfft(self.x, axis=axis))
        if dim == 'time':
            uts = self.get_dim(dim)
            freqs = np.fft.rfftfreq(len(uts), uts.tstep)
            freq = Scalar('frequency', freqs, 'Hz')
        else:
            n = self.shape[axis]
            freqs = np.fft.rfftfreq(n, 1. / n)
            freq = Scalar('frequency', freqs, 'Hz')
        dims = self.dims[:axis] + (freq,) + self.dims[axis + 1:]
        info = _info.default_info('Amplitude', self.info)
        return NDVar(x, dims, info, name or self.name)

    def flatnonzero(self):
        """Return indices where a 1-d NDVar is non-zero

        Like :func:`numpy.flatnonzero`.
        """
        if self.ndim != 1:
            raise ValueError("flatnonzero only applies to 1-d NDVars")
        dim = self.dims[0]
        return [dim._dim_index(index) for index in np.flatnonzero(self.x)]

    def get_axis(self, name):
        "Return the data axis for a given dimension name"
        if self.has_dim(name):
            return self._dim_2_ax[name]
        else:
            raise DimensionMismatchError("%r has no dimension named %r" %
                                         (self, name))

    def get_data(self, dims, mask=None):
        """Retrieve the NDVar's data with a specific axes order.

        Parameters
        ----------
        dims : str | sequence of str
            Sequence of dimension names (or single dimension name). The array
            that is returned will have axes in this order. To insert a new
            axis with size 1 use ``numpy.newaxis``/``None``.
        mask : scalar
            If data is a masked array, set masked values to ``mask``.

        Notes
        -----
        A shallow copy of the data is returned. To retrieve the data with the
        stored axes order use the .x attribute.
        """
        if isinstance(dims, str):
            dims = (dims,)

        dims_ = tuple(d for d in dims if d is not newaxis)
        if set(dims_) != set(self.dimnames) or len(dims_) != len(self.dimnames):
            raise DimensionMismatchError("Requested dimensions %r from %r" %
                                         (dims, self))

        # transpose
        axes = tuple(self.dimnames.index(d) for d in dims_)
        x = self.x.transpose(axes)

        # apply mask
        if mask is not None and isinstance(x, np.ma.MaskedArray):
            if x.mask.any():
                mask_index = x.mask
                x = x.data.copy()
                x[mask_index] = mask
            else:
                x = x.data

        # insert axes
        if len(dims) > len(dims_):
            expand_dims = np.ma.expand_dims if isinstance(x, np.ma.MaskedArray) else np.expand_dims
            for ax, dim in enumerate(dims):
                if dim is newaxis:
                    x = expand_dims(x, ax)

        return x

    def get_dim(self, name):
        "Return the Dimension object named ``name``"
        return self.dims[self.get_axis(name)]

    def get_dimnames(self, names=None, first=None, last=None):
        """Fill in a partially specified tuple of Dimension names

        Parameters
        ----------
        names : sequence of {str | None}
            Dimension names. Names specified as ``None`` are inferred.
        first : str | sequence of str
            Instead of ``names``, specify a constraint on the initial
            dimension(s) only.
        last : str | sequence of str
            Instead of ``names``, specify a constraint on the last
            dimension(s) only.

        Returns
        -------
        inferred_names : tuple of str
            Dimension names in the same order as in ``names``.
        """
        if first is not None or last is not None:
            if names is not None:
                raise TypeError("Can only specify names or first/last, not both")
            head = () if first is None else (first,) if isinstance(first, str) else first
            tail = () if last is None else (last,) if isinstance(last, str) else last
            dims = list(self.dimnames)
            for dim in chain(head, tail):
                try:
                    dims.remove(dim)
                except ValueError:
                    raise ValueError(f"NDVar has no {dim} dimension")
            for dim in reversed(head):
                dims.insert(0, dim)
            for dim in tail:
                dims.append(dim)
            return tuple(dims)

        if not all(n is None or n in self.dimnames for n in names):
            raise ValueError(f"{names} contains dimension not in {self}")
        elif len(names) != len(self.dims):
            raise ValueError(f"{names}: wrong number of dimensions for {self}")
        elif any(names.count(n) > 1 for n in names if n is not None):
            raise ValueError(f"{names}: duplicate name")
        elif None in names:
            if len(names) != len(self.dims):
                raise ValueError(f"{names}: ambiguous (more than one unspecified dimension)")
            none_dims = [n for n in self.dimnames if n not in names]
            return tuple(n if n is not None else none_dims.pop(0) for
                         n in names)
        else:
            return tuple(names)

    def get_dims(self, names=None, first=None, last=None):
        """Return a tuple with the requested Dimension objects

        Parameters
        ----------
        names : sequence of {str | None}
            Names of the dimension objects. If ``None`` is inserted in place of
            names, these dimensions are inferred.
        first : str | sequence of str
            Instead of ``names``, specify a constraint on the initial
            dimension(s) only.
        last : str | sequence of str
            Instead of ``names``, specify a constraint on the last
            dimension(s) only.

        Returns
        -------
        dims : tuple of Dimension
            Dimension objects in the same order as in ``names``.
        """
        if first or last or names is None or None in names:
            names = self.get_dimnames(names, first, last)
        return tuple(self.get_dim(name) for name in names)

    def has_dim(self, name):
        return name in self._dim_2_ax

    def label_clusters(self, threshold=0, tail=0, name=None):
        """Find and label clusters of values exceeding a threshold

        Parameters
        ----------
        threshold : scalar
            Threshold value for clusters (default 0 to find clusters of
            non-zero values).
        tail : 0 | -1 | 1
            Whether to label cluster smaller than threshold, larger than
            threshold, or both (default).
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        clusters : NDVar
            NDVar of int, each cluster labeled with a unique integer value.
            ``clusters.info['cids']`` contains an array of all cluster IDs.
        """
        from ._stats.testnd import Connectivity, label_clusters

        custom = [dim._connectivity_type == 'custom' for dim in self.dims]
        if any(custom):
            if sum(custom) > 1:
                raise NotImplementedError("More than one non-adjacent dimension")
            nad_ax = custom.index(True)
        else:
            nad_ax = 0

        if nad_ax:
            x = self.x.swapaxes(0, nad_ax)
            connectivity = Connectivity(
                (self.dims[nad_ax],) + self.dims[:nad_ax] + self.dims[nad_ax + 1:])
        else:
            x = self.x
            connectivity = Connectivity(self.dims)

        cmap, cids = label_clusters(x, threshold, tail, connectivity, None)

        if nad_ax:
            cmap = cmap.swapaxes(0, nad_ax)

        info = {**self.info, 'cids': cids}
        return NDVar(cmap, self.dims, info, name or self.name)

    def log(self, base=None, name=None):
        """Element-wise log

        Parameters
        ----------
        base : scalar
            Base of the log (default is the natural log).
        name : str
            Name of the output NDVar (default is the current name).
        """
        if base is None:
            x = np.log(self.x)
        elif base == 2:
            x = np.log2(self.x)
        elif base == 10:
            x = np.log10(self.x)
        else:
            x = np.log(self.x)
            x /= log(base)
        return NDVar(x, self.dims, self.info, name or self.name)

    def mask(self, mask, name=None):
        """Create a masked version of this NDVar (see :class:`numpy.ma.MaskedArray`)

        Parameters
        ----------
        mask : bool NDVar
            Mask, with equal dimensions (``True`` values will be masked).
        name : str
            Name of the output NDVar (default is the current name).

        See Also
        --------
        .unmask : remove mask
        """
        x_mask = self._ialign(mask)
        if x_mask.dtype.kind != 'b':
            x_mask = x_mask.astype(bool)
        if x_mask.shape != self.x.shape:
            for ax, (n_mask, n_self) in enumerate(zip(x_mask.shape, self.x.shape)):
                if n_mask != n_self:
                    if n_mask != 1:
                        raise ValueError("Unable to broadcast mask to NDVar")
                    x_mask = np.repeat(x_mask, n_self, ax)
        x = np.ma.MaskedArray(self.x, x_mask)
        return NDVar(x, self.dims, self.info, name or self.name)

    def unmask(self, name=None):
        """Remove mask from a masked ``NDVar``"""
        x = self.x.data if isinstance(self.x, np.ma.masked_array) else self.x
        return NDVar(x, self.dims, self.info, name or self.name)

    def max(self, dims=(), **regions):
        """Compute the maximum over given dimensions

        Parameters
        ----------
        dims : str | tuple of str | boolean NDVar
            Dimensions over which to operate. A str is used to specify a single
            dimension, a tuple of str to specify several dimensions, None to
            compute the maximum over all dimensions.
            An boolean NDVar with the same dimensions as the data can be used
            to compute the maximum in specific elements (if the data has a case
            dimension, the maximum is computed for each case).
        **regions
            Regions over which to aggregate. For example, to get the maximum
            between time=0.1 and time=0.2, use ``ndvar.max(time=(0.1, 0.2))``.
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        max : NDVar | Var | float
            The maximum over specified dimensions. Return a Var if only the
            case dimension remains, and a float if the function collapses over
            all data.
        """
        return self._aggregate_over_dims(dims, regions, np.max)

    def mean(self, dims=(), **regions):
        """Compute the mean over given dimensions

        Parameters
        ----------
        dims : str | tuple of str | boolean NDVar
            Dimensions over which to operate. A str is used to specify a single
            dimension, a tuple of str to specify several dimensions, None to
            compute the mean over all dimensions.
            A boolean NDVar with the same dimensions as the data can be used
            to compute the mean in specific elements (if the data has a case
            dimension, the mean is computed for each case).
        **regions
            Regions over which to aggregate. For example, to get the mean
            between time=0.1 and time=0.2, use ``ndvar.mean(time=(0.1, 0.2))``.
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        mean : NDVar | Var | float
            The mean over specified dimensions. Return a Var if only the case
            dimension remains, and a float if the function collapses over all
            data.
        """
        return self._aggregate_over_dims(dims, regions, np.mean)

    def min(self, dims=(), **regions):
        """Compute the minimum over given dimensions

        Parameters
        ----------
        dims : str | tuple of str | boolean NDVar
            Dimensions over which to operate. A str is used to specify a single
            dimension, a tuple of str to specify several dimensions, None to
            compute the minimum over all dimensions.
            A boolean NDVar with the same dimensions as the data can be used
            to compute the minimum in specific elements (if the data has a case
            dimension, the minimum is computed for each case).
        **regions
            Regions over which to aggregate. For example, to get the minimum
            between time=0.1 and time=0.2, use ``ndvar.min(time=(0.1, 0.2))``.
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        min : NDVar | Var | float
            The minimum over specified dimensions. Return a Var if only the
            case dimension remains, and a float if the function collapses over
            all data.
        """
        return self._aggregate_over_dims(dims, regions, np.min)

    def norm(self, dim, ord=2, name=None):
        """Norm over ``dim``

        Parameters
        ----------
        dim : str
            Dimension over which to operate.
        ord : scalar
            See description of vector norm for :func:`scipy.linalg.norm` 
            (default 2).
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        norm : NDVar
            Norm over ``dim``.

        Examples
        --------
        To normalize ``x`` along the sensor dimension:

        >>> x /= x.norm('sensor')
        """
        axis = self.get_axis(dim)
        x = norm(self.x, ord, axis)
        if self.ndim == 1:
            return x
        if isinstance(self.x, np.ma.masked_array):
            all_masked = np.all(self.x.mask, axis)
            any_masked = np.any(self.x.mask, axis)
            if np.any(all_masked != any_masked):
                raise ValueError(f"Norm along {dim!r} with inconsistent mask")
            mask = all_masked
            x = np.ma.masked_array(x, mask)
        dims = self.dims[:axis] + self.dims[axis + 1:]
        return NDVar(x, dims, self.info, name or self.name)

    def ols(self, x, name=None):
        """Sample-wise ordinary least squares regressions

        Parameters
        ----------
        x : Model | str
            Predictor or predictors. A Model to regress over cases, or a
            dimension name to regress against values of one of the
            ``NDVar``'s dimensions. A Model with multiple ``Var``s can be
            supplied as argument list of ``Var``.
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        beta : NDVar
            Per sample beta weights. The case dimension reflects the predictor
            variables in the same order as the Model's effects.

        Notes
        -----
        The intercept is generated internally, and betas for the intercept are
        not returned. If you need access to more details of the results,
        consider using :class:`testnd.LM`.

        See Also
        --------
        .ols_t : T-values for regression coefficients
        """
        from ._stats import stats

        info = _info.default_info('beta', self.info)
        if 'summary_info' in info:
            del info['summary_info']

        if isinstance(x, str):
            if x.startswith('.'):
                x = x[:]
            dimnames = self.get_dimnames((x,) + (None,) * (self.ndim - 1))
            dim = self.get_dim(x)
            values = dim._as_scalar_array()
            y = self.get_data(dimnames)
            betas = stats.betas(y, Var(values, x))[1]
            out_dims = self.get_dims(dimnames[1:])
        elif not self.has_case:
            raise DimensionMismatchError(
                "Can only apply regression to NDVar with case dimension")
        else:
            x = asmodel(x)
            if len(x) != len(self):
                raise DimensionMismatchError(
                    "Predictors do not have same number of cases (%i) as the "
                    "dependent variable (%i)" % (len(x), len(self)))

            betas = stats.betas(self.x, x)[1:]  # drop intercept
            out_dims = (Case,) + self.dims[1:]
        return self._package_aggregated_output(betas, out_dims, info, name or self.name)

    def ols_t(self, x, name=None):
        """
        Compute T-values for sample-wise ordinary least squares regressions

        Parameters
        ----------
        x : Model
            Predictor or predictors. Can also be supplied as argument that can
            be converted to a Model, for example ``Var`` or list of ``Var``.
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        t : NDVar
            Per sample t-values. The case dimension reflects the predictor
            variables in the same order as the Model's effects.

        Notes
        -----
        Betas for the intercept are not returned.

        See Also
        --------
        .ols : Regression coefficients
        """
        from ._stats import stats

        if not self.has_case:
            raise DimensionMismatchError(
                "Can only apply regression to NDVar with case dimension")

        x = asmodel(x)
        if len(x) != len(self):
            raise DimensionMismatchError(
                "Predictors do not have same number of cases (%i) as the "
                "dependent variable (%i)" % (len(x), len(self)))

        t = stats.lm_t(self.x, x._parametrize())[1:]  # drop intercept
        return NDVar(t, ('case',) + self.dims[1:], self.info, name or self.name)

    @staticmethod
    def _package_aggregated_output(x, dims, info, name):
        ndims = len(dims)
        if ndims == 0:
            return x
        elif ndims == 1 and isinstance(dims[0], Case):
            return Var(x, name, info=info)
        else:
            return NDVar(x, dims, info, name)

    def repeat(self, repeats, name=None):
        """Repeat slices of the NDVar along the case dimension

        Parameters
        ----------
        repeats : int | array of ints
            The number of repetitions for each element. `repeats` is
            broadcasted to fit the shape of the given dimension.
        name : str
            Name of the output NDVar (default is the current name).
        """
        if self.has_case:
            x = self.x.repeat(repeats, axis=0)
            dims = self.dims
        else:
            x = self.x[newaxis].repeat(repeats, axis=0)
            dims = (Case(repeats),) + self.dims
        return NDVar(x, dims, self.info, name or self.name)

    def residuals(self, x, name=None):
        """
        The residuals of sample-wise ordinary least squares regressions

        Parameters
        ----------
        x : Model
            Predictor or predictors. Can also be supplied as argument that can
            be converted to a Model, for example ``Var`` or list of ``Var``.
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        residuals : NDVar
            Residual for each case and sample (same dimensions as data).
        """
        if not self.has_case:
            raise DimensionMismatchError(
                "Can only apply regression to NDVar with case dimension")

        x = asmodel(x)
        if len(x) != len(self):
            raise DimensionMismatchError(
                "Predictors do not have same number of cases (%i) as the "
                "dependent variable (%i)" % (len(x), len(self)))

        from ._stats import stats
        res = stats.residuals(self.x, x)
        return NDVar(res, self.dims, self.info, name or self.name)

    def rms(self, axis=(), **regions):
        """Compute the root mean square over given dimensions

        Parameters
        ----------
        axis : str | tuple of str | boolean NDVar
            Dimensions over which to operate. A str is used to specify a single
            dimension, a tuple of str to specify several dimensions, None to
            compute the standard deviation over all values.
            An boolean NDVar with the same dimensions as the data can be used
            to compute the RMS in specific elements (if the data has a case
            dimension, the RMS is computed for each case).
        **regions
            Regions over which to aggregate. For example, to get the RMS
            between time=0.1 and time=0.2, use ``ndvar.rms(time=(0.1, 0.2))``.
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        rms : NDVar | Var | float
            The root mean square over specified dimensions. Return a Var if
            only the case dimension remains, and a float if the function
            collapses over all data.
        """
        from ._stats.stats import rms
        return self._aggregate_over_dims(axis, regions, rms)

    def sign(self, name=None):
        """Element-wise indication of the sign

        Parameters
        ----------
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        sign : NDVar
            NDVar of same shape, ``-1 if x < 0, 0 if x==0, 1 if x > 0``.

        Notes
        -----
        Like :func:`numpy.sign`.
        """
        return NDVar(np.sign(self.x), self.dims, self.info, name or self.name)

    def smooth(self, dim, window_size=None, window='hamming', mode='center', window_samples=None, name=None):
        """Smooth data by convolving it with a window

        Parameters
        ----------
        dim : str
            Dimension along which to smooth.
        window_size : scalar
            Size of the window (in dimension units, i.e., for time in
            seconds). For finite windows this is the full size of the window, 
            for a gaussian window it is the standard deviation.
        window : str | tuple
            Window type, input to :func:`scipy.signal.get_window`. For example
            'boxcar', 'triang', 'hamming' (default). For dimensions with
            irregular spacing, such as :class:`SourceSpace`, only ``gaussian``
            is implemented.
        mode : 'left' | 'center' | 'right'
            Alignment of the output to the input relative to the window:

            - ``left``: sample in the output corresponds to the left edge of
              the window.
            - ``center``: sample in the output corresponds to the center of
              the window.
            - ``right``: sample in the output corresponds to the right edge of
              the window.

        window_samples : scalar
            Size of the window in samples (this parameter is used to specify
            window size in array elemnts rather than in units of the dimension;
            it is mutually exclusive with ``window_size``).
        name : str
            Name for the smoothed NDVar.

        Returns
        -------
        smoothed_ndvar : NDVar
            NDVar with idential dimensions containing the smoothed data.

        Notes
        -----
        To perform Gaussian smoothing with a given full width at half maximum,
        the standard deviation can be calculated with the following conversion::

        >>> std = fwhm / (2 * (sqrt(2 * log(2))))
        """
        if (window_size is None) == (window_samples is None):
            desc = "" if window_size is None else f"window_size={window_size!r}, window_samples={window_samples!r}: "
            raise TypeError(f"{desc}Must specify either window_size or window_samples")
        axis = self.get_axis(dim)
        dim_object = self.get_dim(dim)
        dims = self.dims
        if window == 'gaussian':
            if mode != 'center':
                raise ValueError(f"mode={mode!r}; for gaussian smoothing, mode must be 'center'")
            elif dim_object._connectivity_type == 'custom':
                if window_samples is not None:
                    raise ValueError(f"window_samples for dimension with connectivity not based on adjacency")
                m = gaussian_smoother(dim_object._distances(), window_size)
            else:
                raise NotImplementedError(f"Gaussian smoothing for {dim_object.__class__.__name__} dimension")
            x = np.tensordot(m, self.x, (1, axis))
            if axis:
                x = x.swapaxes(0, axis)
        elif dim_object._connectivity_type == 'custom':
            raise ValueError(f"window={window}; for {dim_object.__class__.__name__} dimension (must be 'gaussian')")
        else:
            if window_samples:
                n = window_samples
            elif dim == 'time':
                n = int(round(window_size / dim_object.tstep))
                if not n:
                    raise ValueError(f"window_size={window_size}: Window too small for sampling rate")
            else:
                raise NotImplementedError("dim=%r" % (dim,))
            window = scipy.signal.get_window(window, n, False)
            window /= window.sum()
            window.shape = (1,) * axis + (n,) + (1,) * (self.ndim - axis - 1)
            if mode == 'center':
                x = scipy.signal.convolve(self.x, window, 'same')
            else:
                x = scipy.signal.convolve(self.x, window, 'full')
                if mode == 'left':
                    x = take_slice(x, axis, stop=self.shape[axis])
                elif mode == 'right':
                    x = take_slice(x, axis, start=-self.shape[axis])
                elif mode == 'full':
                    if not isinstance(dim_object, UTS):
                        raise NotImplementedError(f"mode='full' for {dim_object.__class__.__name__} dimension")
                    dims = list(dims)
                    tmin = dim_object.tmin - dim_object.tstep * ((n - 1) / 2)
                    dims[axis] = UTS(tmin, dim_object.tstep, dim_object.nsamples + n -1)
                else:
                    raise ValueError("mode=%r" % (mode,))
        return NDVar(x, dims, self.info, name or self.name)

    def std(self, dims=(), **regions):
        """Compute the standard deviation over given dimensions

        Parameters
        ----------
        dims : str | tuple of str | boolean NDVar
            Dimensions over which to operate. A str is used to specify a single
            dimension, a tuple of str to specify several dimensions, None to
            compute the standard deviation over all values.
            An boolean NDVar with the same dimensions as the data can be used
            to compute the standard deviation in specific elements (if the data
            has a case dimension, the standard deviation is computed for each
            case).
        **regions
            Regions over which to aggregate. For example, to get the STD
            between time=0.1 and time=0.2, use ``ndvar.std(time=(0.1, 0.2))``.
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        std : NDVar | Var | float
            The standard deviation over specified dimensions. Return a Var if
            only the case dimension remains, and a float if the function
            collapses over all data.
        """
        return self._aggregate_over_dims(dims, regions, np.std)

    def summary(self, *dims, **regions):
        r"""Aggregate specified dimensions.

        .. warning::
            Data is collapsed over the different dimensions in turn using the
            provided function with an axis argument. For certain functions
            this is not equivalent to collapsing over several axes concurrently
            (e.g., np.var).

        dimension:
            A whole dimension is specified as string argument. This
            dimension is collapsed over the whole range.
        range:
            A range within a dimension is specified through a keyword-argument.
            Only the data in the specified range is included. Use like the
            :py:meth:`.sub` method.


        **additional kwargs:**

        func : callable
            Function used to collapse the data. Needs to accept an "axis"
            kwarg (default: np.mean)
        name : str
            Name for the new NDVar.

        Returns
        -------
        summary : float | Var | NDVar
            Result of applying the summary function over specified dimensions.

        Examples
        --------
        Assuming ``data`` is a normal time series. Get the average in a time
        window::

            >>> y = data.summary(time=(.1, .2))

        Get the peak in a time window::

            >>> y = data.summary(time=(.1, .2), func=np.max)

        Assuming ``meg`` is an NDVar with dimensions time and sensor. Get the
        average across sensors 5, 6, and 8 in a time window::

            >>> roi = [5, 6, 8]
            >>> y = meg.summary(sensor=roi, time=(.1, .2))

        Get the peak in the same data:

            >>> roi = [5, 6, 8]
            >>> peak = meg.summary(sensor=roi, time=(.1, .2), func=np.max)

        Get the RMS over all sensors

            >>> meg_rms = meg.summary('sensor', func=rms)

        """
        if 'func' in regions:
            func = regions.pop('func')
        elif 'summary_func' in self.info:
            func = self.info['summary_func']
        else:
            func = np.mean
        name = regions.pop('name', None)
        if len(dims) + len(regions) == 0:
            dims = ('case',)

        if regions:
            dims = list(dims)
            data = self.sub(**regions)
            dims.extend(dim for dim in regions if data.has_dim(dim))
            return data.summary(*dims, func=func, name=name)
        else:
            x = self.x
            axes = [self._dim_2_ax[dim] for dim in dims]
            dims = list(self.dims)
            for axis in sorted(axes, reverse=True):
                x = func(x, axis=axis)
                dims.pop(axis)

            # update info for summary
            info = self.info
            if 'summary_info' in info:
                info = info.copy()
                info.update(info.pop('summary_info'))
            return self._package_aggregated_output(x, dims, info, name)

    def sub(self, *args, **kwargs):
        """Retrieve a slice through the NDVar.

        Return a new NDVar with a slice of the current NDVar's data.
        The slice is specified using arguments and keyword arguments.

        Indexes for dimensions can be either specified as arguments in the
        order of the data axes, or with dimension names as keywords; for::

            >>> x = datasets.get_uts(True)['utsnd']
            >>> x
            <NDVar 'utsnd': 60 case, 5 sensor, 100 time>
            >>> x.sub(time=0.1)
            <NDVar 'utsnd': 60 case, 5 sensor>

        ``x.sub(time=0.1)`` is equivalent to ``x.sub((), (), 0.1)`` and
        ``x[:, :, 0.1]``.

        Tuples are reserved for slicing and are treated like ``slice`` objects.
        Use lists for indexing arbitrary sequences of elements.

        The name of the new NDVar can be set with a ``name`` keyword
        (``x.sub(time=0.1, name="new_name")``). The default is the name of the
        current NDVar.
        """
        var_name = kwargs.pop('name', self.name)
        dims = list(self.dims)
        n_axes = len(dims)
        index = [FULL_SLICE] * n_axes
        index_args = [None] * n_axes
        add_axis = False

        # sequence args
        for i, arg in enumerate(args):
            if isinstance(arg, NDVar):
                if arg.has_case:
                    raise ValueError("NDVar with case dimension can not serve"
                                     "as NDVar index")
                dimax = self.get_axis(arg.dims[0].name)
                if index_args[dimax] is None:
                    index_args[dimax] = arg
                else:
                    raise IndexError("Index for %s dimension specified twice."
                                     % arg.dims[0].name)
            elif arg is newaxis:
                if i > 0:
                    raise IndexError("newaxis must be in first index position")
                elif self.has_case:
                    raise IndexError("NDVar already has case dimension")
                add_axis = True
            else:
                index_args[i] = arg

        # sequence kwargs
        for dimname, arg in kwargs.items():
            dimax = self.get_axis(dimname)
            if index_args[dimax] is None:
                index_args[dimax] = arg
            else:
                raise RuntimeError("Index for %s dimension specified twice." % dimname)

        # process indexes
        for dimax, idx in enumerate(index_args):
            if idx is None:
                continue
            dim = self.dims[dimax]

            # find index
            idx = dim._array_index(idx)
            index[dimax] = idx

            # find corresponding dim
            if np.isscalar(idx):
                dims[dimax] = None
            elif dimax >= self.has_case:
                dims[dimax] = dim[idx]
            else:
                dims[dimax] = Case
        if add_axis:
            dims.insert(0, Case)

        # adjust index dimension
        if sum(isinstance(idx, EXPAND_INDEX_TYPES) for idx in index) > 1:
            ndim_increment = 0
            for i in range(n_axes - 1, -1, -1):
                idx = index[i]
                if ndim_increment and isinstance(idx, (slice, np.ndarray)):
                    if isinstance(idx, slice):
                        idx = slice_to_arange(idx, self.x.shape[i])
                    elif idx.dtype.kind == 'b':
                        idx = np.flatnonzero(idx)
                    index[i] = idx[FULL_AXIS_SLICE + (None,) * ndim_increment]

                if isinstance(idx, np.ndarray):
                    ndim_increment += 1

        # create NDVar
        x = self.x[tuple(index)]
        if add_axis:
            x = np.expand_dims(x, 0)
        dims = tuple(dim for dim in dims if dim is not None)
        return self._package_aggregated_output(x, dims, self.info, var_name)

    def sum(self, dims=(), **regions):
        """Compute the sum over given dimensions

        Parameters
        ----------
        dims : str | tuple of str | boolean NDVar
            Dimensions over which to operate. A str is used to specify a single
            dimension, a tuple of str to specify several dimensions, None to
            compute the sum over all dimensions.
            An boolean NDVar with the same dimensions as the data can be used
            to compute the sum in specific elements (if the data has a case
            dimension, the sum is computed for each case).
        **regions
            Regions over which to aggregate. For example, to get the sum
            between time=0.1 and time=0.2, use ``ndvar.sum(time=(0.1, 0.2))``.
        name : str
            Name of the output NDVar (default is the current name).

        Returns
        -------
        sum : NDVar | Var | float
            The sum over specified dimensions. Return a Var if only the
            case dimension remains, and a float if the function collapses over
            all data.
        """
        return self._aggregate_over_dims(dims, regions, np.sum)

    def threshold(self, v, tail=1, name=None):
        """Set all values below a threshold to 0.

        Parameters
        ----------
        v : scalar
            Threshold value.
        tail : -1 | 0 | 1
            Tailedness.
            1: set values below v to 0 (default);
            0: set values between -v and v to 0;
            -1: set values above v to 0.
        name : str
            Name of the output NDVar (default is the current name).
        """
        if tail == 0:
            v = abs(v)
            idx = self.x >= v
            np.logical_or(idx, self.x <= -v, idx)
        elif tail == 1:
            idx = self.x >= v
        elif tail == -1:
            idx = self.x <= v
        else:
            raise ValueError("Invalid value tail=%r; need -1, 0 or 1" % (tail,))
        return NDVar(np.where(idx, self.x, 0), self.dims, self.info, name or self.name)

    def var(self, dims=(), ddof=0, **regions):
        """Compute the variance over given dimensions

        Parameters
        ----------
        dims : str | tuple of str | boolean NDVar
            Dimensions over which to operate. A str is used to specify a single
            dimension, a tuple of str to specify several dimensions, None to
            compute the sum over all dimensions.
            An boolean NDVar with the same dimensions as the data can be used
            to compute the variance in specific elements (if the data has a case
            dimension, the variance is computed for each case).
        ddof : int
            Degrees of freedom (default 0; see :func:`numpy.var`).
        name : str
            Name of the output NDVar (default is the current name).
        **regions
            Regions over which to aggregate. For example, to get the variance
            between time=0.1 and time=0.2, use ``ndvar.var(time=(0.1, 0.2))``.

        Returns
        -------
        var : NDVar | Var | float
            The variance over specified dimensions. Return a Var if only the
            case dimension remains, and a float if the function collapses over
            all data.
        """
        return self._aggregate_over_dims(dims, regions,
                                         partial(np.var, ddof=ddof))

    def nonzero(self):
        """Return indices where the NDVar is non-zero 
        
        Like :func:`numpy.nonzero`.
        """
        return tuple(dim._dim_index(index) for dim, index in
                     zip(self.dims, self.x.nonzero()))


def extrema(x, axis=None):
    "Extract the extreme values in x"
    max = np.max(x, axis)
    min = np.min(x, axis)
    if np.isscalar(max):
        return max if abs(max) > abs(min) else min
    return np.where(np.abs(max) >= np.abs(min), max, min)


class Datalist(list):
    """:py:class:`list` subclass for including lists in in a Dataset.

    Parameters
    ----------
    items : sequence
        Content for the Datalist.
    name : str
        Name of the Datalist.
    fmt : 'repr' | 'str' | 'strlist'
        How to format items when converting Datasets to tables (default 'repr'
        uses the normal object representation).


    Notes
    -----
    Modifications:

     - adds certain methods that makes indexing behavior more similar to numpy
       and other data objects
     - blocks methods for in place modifications that would change the lists's
       length


    Examples
    --------
    Concise string representation:

    >>> l = [['a', 'b'], [], ['a']]
    >>> print(Datalist(l))
    [['a', 'b'], [], ['a']]
    >>> print(Datalist(l, fmt='strlist'))
    [[a, b], [], [a]]
    """
    _fmt = 'repr'  # for backwards compatibility with old pickles

    def __init__(self, items=None, name=None, fmt='repr'):
        if fmt not in ('repr', 'str', 'strlist'):
            raise ValueError("fmt=%s" % repr(fmt))

        self.name = name
        self._fmt = fmt
        if items:
            super(Datalist, self).__init__(items)
        else:
            super(Datalist, self).__init__()

    def __deepcopy__(self, memo):
        return Datalist((deepcopy(item, memo) for item in self), self.name, self._fmt)

    def __repr__(self):
        args = super(Datalist, self).__repr__()
        if self.name is not None:
            args += ', %s' % repr(self.name)
        if self._fmt != 'repr':
            args += ', fmt=%s' % repr(self._fmt)
        return "Datalist(%s)" % args

    def __str__(self):
        return "[%s]" % ', '.join(self._item_repr(i) for i in self)

    def _item_repr(self, item):
        if self._fmt == 'str':
            return str(item)
        elif self._fmt == 'repr':
            out = repr(item)
            if len(out) > 15:
                return out[:12] + '...'
            else:
                return out
        elif self._fmt == 'strlist':
            return "[%s]" % ', '.join(item)
        else:
            raise RuntimeError("Datalist._fmt=%s" % repr(self._fmt))

    def _summary(self, width=80):
        types = sorted({type(v) for v in self})
        if len(types) == 1:
            return f'{types[0].__name__}'
        items = [f'{t.__name__}:{sum(isinstance(v, t) for v in self)}' for t in types]
        n = 0
        for i, item in enumerate(items):
            if n + len(item) > width:
                return ', '.join(items[:i]) + '...'
            n += len(item) + 2
        return ', '.join(items)

    def __eq__(self, other):
        if len(self) != len(other):
            raise ValueError("Unequal length")
        return np.array([s == o for s, o in zip(self, other)])

    def __ne__(self, other):
        if len(self) != len(other):
            raise ValueError("Unequal length")
        return np.array([s != o for s, o in zip(self, other)])

    def __getitem__(self, index):
        if isinstance(index, Integral):
            return list.__getitem__(self, index)
        elif isinstance(index, slice):
            return Datalist(list.__getitem__(self, index), fmt=self._fmt)
        else:
            index = asindex(index)
            return Datalist(apply_numpy_index(self, index), fmt=self._fmt)

    def __setitem__(self, key, value):
        if isinstance(key, LIST_INDEX_TYPES):
            list.__setitem__(self, key, value)
        elif isinstance(key, np.ndarray):
            if key.dtype.kind == 'b':
                key = np.flatnonzero(key)
            elif key.dtype.kind != 'i':
                raise TypeError("Array index needs to be int or bool type")

            if np.iterable(value):
                if len(key) != len(value):
                    raise ValueError("Need one value per index when setting a "
                                     "range of entries in a Datalist.")
                for k, v in zip(key, value):
                    list.__setitem__(self, k, v)
            else:
                for k in key:
                    list.__setitem__(self, k, value)
        else:
            raise NotImplementedError("Datalist indexing with %s" % type(key))

    def __add__(self, other):
        return Datalist(super(Datalist, self).__add__(other), fmt=self._fmt)

    def aggregate(self, x, merge='mean'):
        """
        Summarize cases for each cell in x

        Parameters
        ----------
        x : categorial
            Cells which to aggregate.
        merge : str
            How to merge entries.
            ``'mean'``: sum elements and dividie by cell length
        """
        if len(x) != len(self):
            raise ValueError(f"x={dataobj_repr(x)}: Length mismatch, len(x)={len(x)}, len(self)={len(self)}")

        x_out = []
        for cell in x.cells:
            x_cell = self[x == cell]
            n = len(x_cell)
            if n == 1:
                x.append(x_cell)
            elif n > 1:
                if merge == 'mean':
                    try:
                        xc = reduce(operator.add, x_cell)
                        xc /= n
                    except TypeError:
                        raise TypeError(f"{dataobj_repr(self)}: Objects in Datalist do not support averaging (if aggregating a Dataset, dry dropping this variable)")
                else:
                    raise ValueError(f"merge={merge!r}")
                x_out.append(xc)

        return Datalist(x_out, fmt=self._fmt)

    def __iadd__(self, other):
        return self + other

    def append(self, p_object):
        raise TypeError("Datalist has fixed length to conform to Dataset")

    def insert(self, index, p_object):
        raise TypeError("Datalist has fixed length to conform to Dataset")

    def pop(self, index=None):
        raise TypeError("Datalist has fixed length to conform to Dataset")

    def remove(self, value):
        raise TypeError("Datalist has fixed length to conform to Dataset")

    def _update_listlist(self, other):
        "Update list elements from another list of lists"
        if len(self) != len(other):
            raise ValueError("Unequal length")
        for i in range(len(self)):
            if any(item not in self[i] for item in other[i]):
                self[i] = sorted(set(self[i]).union(other[i]))


legal_dataset_key_re = re.compile("[_A-Za-z][_a-zA-Z0-9]*$")


def assert_is_legal_dataset_key(key):
    if iskeyword(key):
        raise ValueError(f"{key!r} is a reserved keyword and can not be used as variable name in a Dataset")
    elif not legal_dataset_key_re.match(key):
        raise ValueError(f"{key!r} is not a valid keyword and can not be used as variable name in a Dataset")


def as_legal_dataset_key(key):
    "Convert str to a legal dataset key"
    if iskeyword(key):
        return "%s_" % key
    elif legal_dataset_key_re.match(key):
        return key
    else:
        if ' ' in key:
            key = key.replace(' ', '_')
        for c in string.punctuation:
            if c in key:
                key = key.replace(c, '_')

        if key == '':
            key = '_'
        elif key[0].isdigit():
            key = "_%s" % key

        if legal_dataset_key_re.match(key):
            return key
        else:
            raise RuntimeError("Could not convert %r to legal dataset key")


def cases_arg(cases, n_cases) -> Iterable:
    "Coerce cases argument to iterator"
    if isinstance(cases, Integral):
        if cases < 1:
            cases = n_cases + cases
            if cases < 0:
                raise ValueError(f"cases={cases}: Can't get table for fewer than 0 cases")
        else:
            cases = min(cases, n_cases)
        return range(cases)
    elif isinstance(cases, Iterable):
        return cases
    else:
        raise TypeError(f"cases={cases}")


class Dataset(OrderedDict):
    """
    Stores multiple variables pertaining to a common set of measurement cases

    Superclass: :class:`collections.OrderedDict`

    Parameters
    ----------
    items : iterator
        Items contained in the Dataset. Items can be either named
        data-objects or ``(name, data_object)`` tuples. The Dataset stores
        the input items themselves, without making a copy().
    name : str
        Name for the Dataset.
    caption : str
        Caption for the table.
    info : dict
        Info dictionary, can contain arbitrary entries and can be accessed
        as ``.info`` attribute after initialization. The Dataset makes a
        shallow copy.
    n_cases : int
        Specify the number of cases in the Dataset if no items are added
        upon initialization (by default the number is inferred when the
        fist item is added).


    Attributes
    ----------
    n_cases : None | int
        The number of cases in the Dataset (corresponding to the number of
        rows in the table representation). None if no variables have been
        added.
    n_items : int
        The number of items (variables) in the Dataset (corresponding to the
        number of columns in the table representation).


    Notes
    -----
    A Dataset represents a data table as a ``{variable_name: value_list}``
    dictionary. Each variable corresponds to a column, and each index in the
    value list corresponds to a row, or case.

    The Dataset class inherits most of its behavior from its superclass
    :py:class:`collections.OrderedDict`.
    Dictionary keys are enforced to be :py:class:`str` objects and should
    correspond to the variable names.
    As for a dictionary, The Dataset's length (``len(ds)``) reflects the number
    of variables in the Dataset (i.e., the number of rows).


    **Assigning data**

    The :class:`Dataset` assumes certain properties of the items that are
    assigned, for example they need to support :mod:`numpy` indexing.
    When assigning items that are not :mod:`eelbrain` data containers, they are
    coerced in the following manner:

    - 1-d :class:`numpy.ndarray` are coerced to :class:`Var`; other
      :class:`numpy.ndarray` are assigned as is
    - Objects conforming to the Python :class:`collections.Sequence` abstract
      base class are coerced to :class:`Datalist`
    - :class:`mne.Epochs` are assigned as is
    - For advanced use, additional classes can be assigned as is by extending the
      :attr:`Dataset._value_type_exceptions` class attribute tuple


    **Accessing Data**

    Standard indexing with :class:`str` is used to access the contained Var
    and Factor objects:

    - ``ds['var1']`` --> ``var1``.
    - ``ds['var1',]`` --> ``Dataset([var1])``.
    - ``ds['var1', 'var2']`` --> ``Dataset([var1, var2])``

    When indexing numerically, the first index defines cases (rows):

    - ``ds[1]`` --> row 1
    - ``ds[1:5]`` or ``ds[1,2,3,4]`` --> rows 1 through 4
    - ``ds[1, 5, 6, 9]`` or ``ds[[1, 5, 6, 9]]`` --> rows 1, 5, 6 and 9

    The second index accesses columns, so case indexing can be combined with
    column indexing:

     - ``ds[:4, :2]`` --> first 4 rows of first 2 columns

    Index a single case retrieves an individual case as ``{name: value}``
    dictionaries:

    - ``ds[1]`` --> ``{'var': 1, 'factor': 'value', ...}``

    The :meth:`.itercases` method can be used to iterate over cases as
    :class:`dict`.


    **Naming**

    While Var and Factor objects themselves need not be named, they need
    to be named when added to a Dataset. This can be done by a) adding a
    name when initializing the Dataset::

        >>> ds = Dataset((('v1', var1), ('v2', var2)))

    or b) by adding the Var or Factor with a key::

        >>> ds['v3'] = var3

    If a Var/Factor that is added to a Dataset does not have a name, the new
    key is automatically assigned to the Var/Factor's ``.name`` attribute.


    Examples
    --------
    Datasets can be initialize with data-objects, or with
    ('name', data-object) tuples::

        >>> ds = Dataset((var1, var2))
        >>> ds = Dataset((('v1', var1), ('v2', var2)))

    Alternatively, variables can be added after initialization::

        >>> ds = Dataset(n_cases=3)
        >>> ds['var', :] = 0
        >>> ds['factor', :] = 'a'
        >>> print(ds)
        var    factor
        -------------
        0      a
        0      a
        0      a

    """
    _value_type_exceptions = (MNE_EPOCHS,)

    @staticmethod
    def _args(items=(), name=None, caption=None, info={}, n_cases=None):
        return items, name, caption, info, n_cases

    def __init__(self, *args, **kwargs):
        # backwards compatibility
        if args and isinstance(args[0], tuple) and isinstance(args[0][0], str):
            items, name, caption, info, n_cases = self._args(args, **kwargs)
        else:
            items, name, caption, info, n_cases = self._args(*args, **kwargs)

        # unpack data-objects
        args = []
        for item in items:
            if isdataobject(item):
                if not item.name:
                    raise ValueError("items need to be named in a Dataset; use "
                                     "Dataset(('name', item), ...), or ds = "
                                     "Dataset(); ds['name'] = item")
                args.append((item.name, item))
            else:
                args.append(item)

        # set state
        self.n_cases = None if n_cases is None else int(n_cases)
        # uses __setitem__() which checks items and length:
        super(Dataset, self).__init__(args)
        self.name = name
        self.info = dict(info)
        self._caption = caption

    def __setstate__(self, state):
        # for backwards compatibility
        self.name = state['name']
        self.info = state['info']
        self._caption = state.get('caption', None)

    def __reduce__(self):
        return self.__class__, (tuple(self.items()), self.name, self._caption,
                                self.info, self.n_cases)

    def __delitem__(self, key):
        if isinstance(key, str):
            super(Dataset, self).__delitem__(key)
        elif isinstance(key, tuple):
            m = super(Dataset, self).__delitem__
            for k in key:
                m(k)
        else:
            raise KeyError("Invalid Dataset key: %s" % repr(key))

    def __getitem__(self, index):
        """
        possible::

            >>> ds[9]        (int) -> dictionary for one case
            >>> ds[9:12]     (slice) -> subset with those cases
            >>> ds[[9, 10, 11]]     (list) -> subset with those cases
            >>> ds['MEG1']  (strings) -> Var
            >>> ds['MEG1', 'MEG2']  (list of strings) -> list of vars; can be nested!

        """
        if isinstance(index, slice):
            return self.sub(index)
        elif isinstance(index, str):
            return super(Dataset, self).__getitem__(index)
        elif isinstance(index, Integral):
            return self.get_case(index)
        elif not np.iterable(index):
            raise KeyError("Invalid index for Dataset: %r" % index)
        elif len(index) == 0:
            return self.sub(index)
        elif all(isinstance(item, str) for item in index):
            return self.sub(keys=index)
        elif isinstance(index, tuple):
            if len(index) != 2:
                raise KeyError("Invalid index for Dataset: %s" % repr(index))

            i0, i1 = index
            if isinstance(i0, str):
                return self[i0][i1]
            elif isinstance(i1, str):
                return self[i1][i0]
            elif np.iterable(i0) and isinstance(i0[0], str):
                return self[i1, i0]
            elif np.iterable(i1) and all(isinstance(item, str) for item in i1):
                keys = i1
            else:
                keys = Datalist(self.keys())[i1]
                if isinstance(keys, str):
                    return self[i1][i0]
            return Dataset(((k, self[k][i0]) for k in keys), self.name,
                           self._caption, self.info)
        else:
            return self.sub(index)

    def __repr__(self):
        class_name = self.__class__.__name__
        if self.n_cases is None:
            items = []
            if self.name:
                items.append('name=%r' % self.name)
            if self.info:
                info = repr(self.info)
                if len(info) > 60:
                    info = '<...>'
                items.append('info=%s' % info)
            return '%s(%s)' % (class_name, ', '.join(items))

        rep_tmp = "<%(class_name)s %(name)s%(N)s{%(items)s}>"
        fmt = {'class_name': class_name}
        fmt['name'] = '%r ' % self.name if self.name else ''
        fmt['N'] = 'n_cases=%i ' % self.n_cases
        items = []
        for key in self:
            v = self[key]
            if isinstance(v, Var):
                lbl = 'V'
            elif isinstance(v, Factor):
                lbl = 'F'
            elif isinstance(v, NDVar):
                lbl = 'Vnd'
            else:
                lbl = type(v).__name__

            if isdataobject(v) and v.name != key:
                item = '%r:%s<%r>' % (key, lbl, v.name)
            else:
                item = '%r:%s' % (key, lbl)

            items.append(item)

        fmt['items'] = ', '.join(items)
        return rep_tmp % fmt

    def _repr_pretty_(self, p, cycle):
        if cycle:
            raise NotImplementedError
        p.text(self.__repr__())

    def __setitem__(self, index, item):
        if isinstance(index, str):
            assert_is_legal_dataset_key(index)

            # coerce to data-object
            if isdataobject(item) or isinstance(object, Datalist):
                item.name = index
                n = 0 if (isinstance(item, NDVar) and not item.has_case) else len(item)
            else:
                if isinstance(item, np.ndarray):
                    if item.ndim == 1:
                        item = Var(item, index)
                elif isinstance(item, self._value_type_exceptions):
                    pass
                elif isinstance(item, Sequence):
                    item = Datalist(item, index)
                else:
                    raise TypeError(f"{item!r}: Unsupported type for Dataset; consider using an eelbrain data-object or a list")
                n = len(item)

            # make sure the item has the right length
            if self.n_cases is None:
                self.n_cases = n
            elif self.n_cases != n:
                raise ValueError(f"Can not assign item to Dataset. The item`s length {n} is different from the number of cases in the Dataset {self.n_cases}.")

            super(Dataset, self).__setitem__(index, item)
        elif isinstance(index, tuple):
            if len(index) != 2:
                raise NotImplementedError(
                    "Dataset indexes can have at most two components; direct "
                    "access to NDVars is not implemented")
            idx, key = index
            if isinstance(idx, str):
                key, idx = idx, key
            elif not isinstance(key, str):
                raise TypeError(f"Dataset key {key!r}; needs to be str")

            if key in self:
                self[key][idx] = item
            elif isinstance(idx, slice):
                if idx.start is None and idx.stop is None:
                    if isdataobject(item):
                        self[key] = item
                    elif self.n_cases is None:
                        raise TypeError("Can't assign slice of empty Dataset")
                    elif isinstance(item, str):
                        self[key] = Factor([item], repeat=self.n_cases)
                    elif np.isscalar(item):
                        self[key] = Var([item], repeat=self.n_cases)
                    else:
                        raise TypeError(
                            f"{item!r} is not supported for slice-assignment of "
                            f"a new variable. Use a str for a new Factor or a "
                            f"scalar for a new Var.")
                else:
                    raise NotImplementedError(
                        "When assigning a new item in a Dataset, all values "
                        "need to be set (ds[:,'name'] = ...)")
            else:
                raise NotImplementedError("Advanced Dataset indexing")
        else:
            raise NotImplementedError("Advanced Dataset indexing")

    def __str__(self):
        if sum(isuv(i) or isdatalist(i) for i in self.values()) == 0:
            return self.__repr__()

        maxn = preferences['dataset_str_n_cases']
        if self.n_cases > maxn:
            caption = "... (use .as_table() method to see the whole Dataset)"
        else:
            caption = None
        txt = self.as_table(maxn, '%.5g', midrule=True, caption=caption,
                            lfmt=True)
        return str(txt)

    def _check_n_cases(self, x, empty_ok=True):
        """Check that an input argument has the appropriate length.

        Also raise an error if empty_ok is False and the Dataset is empty.
        """
        if self.n_cases is None:
            if not empty_ok:
                raise RuntimeError("Dataset is empty.")
        elif self.n_cases != len(x):
            raise ValueError(
                f"{dataobj_repr(x)} with length {len(x)}: The Dataset has a "
                f"different length ({self.n_cases})")

    @staticmethod
    def as_key(name):
        """Convert a string ``name`` to a legal dataset key

        This is a shortcut to simplify storing varaibles with non-compliant
        names, consisting mostly of replacing invalid characters with '_'.
        Note that the result is not unique.

        Examples
        --------
        >>> Dataset.as_key('var-1|2')
        'var_1_2'
        """
        return as_legal_dataset_key(name)

    def add(self, item, replace=False):
        """``ds.add(item)`` -> ``ds[item.name] = item``

        unless the Dataset already contains a variable named item.name, in
        which case a KeyError is raised. In order to replace existing
        variables, set ``replace`` to True::

            >>> ds.add(item, True)

        """
        if not isdataobject(item):
            raise ValueError("Not a valid data-object: %r" % item)
        elif item.name is None:
            raise ValueError("Dataset.add(obj) can only take named objects "
                             "(obj.name can not be None)")
        elif (item.name in self) and not replace:
            raise KeyError("Dataset already contains variable named %r" % item.name)
        else:
            self[item.name] = item

    def add_empty_var(self, name, dtype=np.float64):
        """Create an empty variable in the dataset

        Parameters
        ----------
        name : str
            Name for the new variable.
        dtype : numpy dtype
            Data type of the new variable (default is float64).

        Returns
        -------
        var : Var
            The new variable.
        """
        if self.n_cases is None:
            err = "Can't add variable to a Dataset without length"
            raise RuntimeError(err)
        x = np.empty(self.n_cases, dtype=dtype)
        v = Var(x)
        self[name] = v
        return v

    def as_table(self, cases=0, fmt='%.6g', sfmt='%s', sort=False, header=True,
                 midrule=False, count=False, title=None, caption=None,
                 ifmt='%s', bfmt='%s', lfmt=False):
        r"""
        Create an fmtxt.Table containing all Vars and Factors in the Dataset.

        Can be used for exporting in different formats such as csv.

        Parameters
        ----------
        cases : int | iterator of int
            Cases to include (int includes that many cases from the beginning,
            0 includes all; negative number works like negative indexing).
        fmt : str
            Format string for float variables (default ``'%.6g'``).
        sfmt : str | None
            Formatting for strings (None -> code; default ``'%s'``).
        sort : bool
            Sort the columns alphabetically.
        header : bool
            Include the varibale names as a header row.
        midrule : bool
            print a midrule after table header.
        count : bool
            Add an initial column containing the case number.
        title : None | str
            Title for the table.
        caption : None | str
            Caption for the table (default is the Dataset's caption).
        ifmt : str
            Formatting for integers (default ``'%s'``).
        bfmt : str
            Formatting for booleans (default ``'%s'``).
        lfmt : bool
            Include Datalists.
        """
        cases = cases_arg(cases, self.n_cases)
        if cases is None:
            return fmtxt.Table('')
        keys = [k for k, v in self.items() if isuv(v) or (lfmt and isdatalist(v))]
        if sort:
            keys = sorted(keys)

        if caption is None:
            caption = self._caption

        values = [self[key] for key in keys]
        fmts = []
        for v in values:
            if isinstance(v, Factor):
                fmts.append(sfmt)
            elif isintvar(v):
                fmts.append(ifmt)
            elif isboolvar(v):
                fmts.append(bfmt)
            elif isdatalist(v):
                fmts.append('dl')
            else:
                fmts.append(fmt)

        columns = 'l' * (len(keys) + count)
        table = fmtxt.Table(columns, True, title, caption)

        if header:
            if count:
                table.cell('#')
            for name in keys:
                table.cell(name)

            if midrule:
                table.midrule()

        for i in cases:
            if count:
                table.cell(i)

            for v, fmt_ in zip(values, fmts):
                if fmt_ is None:
                    table.cell(v.x[i])
                elif fmt_ == 'dl':
                    table.cell(v._item_repr(v[i]))
                elif fmt_.endswith(('r', 's')):
                    table.cell(fmt_ % v[i])
                else:
                    table.cell(fmtxt.Number(v[i], fmt=fmt_))

        return table

    def _asfmtext(self):
        return self.as_table()

    def eval(self, expression):
        """
        Evaluate an expression involving items stored in the Dataset.

        Parameters
        ----------
        expression : str
            Python expression to evaluate.

        Notes
        -----
        ``ds.eval(expression)`` is equivalent to
        ``eval(expression, globals, ds)`` with ``globals=numpy`` plus some
        Eelbrain functions.

        Examples
        --------
        In a Dataset containing factors 'A' and 'B'::

            >>> ds.eval('A % B')
            A % B

        """
        if not isinstance(expression, str):
            raise TypeError("Eval needs expression of type unicode or str. Got "
                            "%s" % repr(expression))
        return eval(expression, EVAL_CONTEXT, self)

    @classmethod
    def from_caselist(cls, names, cases):
        """Create a Dataset from a list of cases

        Parameters
        ----------
        names : sequence of str
            Names for the variables.
        cases : sequence of sequence of { str | scalar | NDVar }
            A sequence of cases, whereby each case is itself represented as a
            sequence of values (str or scalar). Variable type (Factor or Var)
            is inferred from whether values are str or not.
        """
        if isinstance(names, Iterator):
            names = tuple(names)
        if isinstance(cases, Iterator):
            cases = tuple(cases)
        n_cases = set(map(len, cases))
        if len(n_cases) > 1:
            raise ValueError('not all cases have same length')
        n_cases = n_cases.pop()
        if len(names) != n_cases:
            raise ValueError('names=%r: %i names but %i cases' % (names, len(names), n_cases))

        ds = cls()
        for i, name in enumerate(names):
            ds[name] = combine(case[i] for case in cases)
        return ds

    @classmethod
    def from_r(cls, name):
        """Create a Dataset from an R data frame through ``rpy2``

        Parameters
        ----------
        name : str
            Name of the dataframe in R.

        Examples
        --------
        Getting an example dataset from R:

        >>> from rpy2.robjects import r
        >>> r('data(sleep)')
        >>> ds = Dataset.from_r('sleep')
        >>> print(ds)
        extra   group   ID
        ------------------
        0.7     1       1
        -1.6    1       2
        -0.2    1       3
        -1.2    1       4
        -0.1    1       5
        3.4     1       6
        3.7     1       7
        0.8     1       8
        0       1       9
        2       1       10
        1.9     2       1
        0.8     2       2
        1.1     2       3
        0.1     2       4
        -0.1    2       5
        4.4     2       6
        5.5     2       7
        1.6     2       8
        4.6     2       9
        3.4     2       10
        """
        from rpy2 import robjects as ro
        df = ro.r[name]
        if not isinstance(df, ro.DataFrame):
            raise ValueError("R object %r is not a DataFrame")
        ds = cls(name=name)
        for item_name, item in df.items():
            if isinstance(item, ro.FactorVector):
                x = np.array(item)
                labels = {i: l for i, l in enumerate(item.levels, 1)}
                ds[item_name] = Factor(x, labels=labels)
            elif isinstance(item, (ro.FloatVector, ro.IntVector)):
                x = np.array(item)
                ds[item_name] = Var(x)
            else:
                raise NotImplementedError(str(type(item)))
        return ds

    def get_case(self, i):
        "The i'th case as a dictionary"
        return {k: v[i] for k, v in self.items()}

    def get_subsets_by(self, x, exclude=(), name='{name}[{cell}]'):
        """Split the Dataset by the cells of ``x``

        Parameters
        ----------
        x : categorial
            Model defining cells into which to split the dataset.
        exclude : sequence of str
            Cells of ``x`` which should be ignored.
        name : str
            Name for the new datasets (formatted with ``self.name`` and
            ``cell``).

        Returns
        -------
        sub_datasets : dict
            ``{cell: sub_dataset}`` dictionary.
        """
        if isinstance(x, str):
            x = self.eval(x)
        return {cell: self.sub(x == cell, name.format(name=self.name, cell=cell)) for
                cell in x.cells if cell not in exclude}

    def aggregate(self, x=None, drop_empty=True, name='{name}', count='n',
                  drop_bad=False, drop=(), equal_count=False, never_drop=()):
        """
        Return a Dataset with one case for each cell in x.

        Parameters
        ----------
        x : None | str | categorial
            Model defining cells to which to reduce cases. By default (``None``)
            the Dataset is reduced to a single case.
        drop_empty : bool
            Drops empty cells in x from the Dataset. This is currently the only
            option.
        name : str
            Name of the new Dataset.
        count : None | str
            Add a variable with this name to the new Dataset, containing the
            number of cases in each cell in x.
        drop_bad : bool
            Drop bad items: silently drop any items for which compression
            raises an error. This concerns primarily factors with non-unique
            values for cells in x (if drop_bad is False, an error is raised
            when such a Factor is encountered)
        drop : sequence of str
            Additional data-objects to drop.
        equal_count : bool
            Make sure the same number of rows go into each average. First, the
            cell with the smallest number of rows is determined. Then, for each
            cell, rows beyond that number are dropped.
        never_drop : sequence of str
            If the drop_bad=True setting would lead to dropping a variable
            whose name is in never_drop, raise an error instead.

        Notes
        -----
        Handle mne Epoch objects by creating a list with an mne Evoked object
        for each cell.
        """
        if not drop_empty:
            raise NotImplementedError('drop_empty = False')

        if x:
            if equal_count:
                self = self.equalize_counts(x)
            x = ascategorial(x, ds=self)
        else:
            x = Factor('a' * self.n_cases)

        ds = Dataset(name=name.format(name=self.name), info=self.info)

        if count:
            ds[count] = Var(filter(None, (np.sum(x == cell) for cell in x.cells)))

        for k, v in self.items():
            if k in drop:
                continue
            try:
                if hasattr(v, 'aggregate'):
                    ds[k] = v.aggregate(x)
                elif isinstance(v, MNE_EPOCHS):
                    evokeds = []
                    for cell in x.cells:
                        idx = (x == cell)
                        if idx.sum():
                            evokeds.append(v[idx].average())
                    ds[k] = evokeds
                else:
                    raise TypeError(f"{v}: unsupported type for Dataset.aggregate()")
            except:
                if drop_bad and k not in never_drop:
                    pass
                else:
                    raise

        return ds

    def copy(self, name=None):
        """Create a shallow copy of the dataset

        Parameters
        ----------
        name : str
            Name for the new dataset (default is ``self.name``).
        """
        return Dataset(self.items(), name or self.name, self._caption,
                       self.info, self.n_cases)

    def equalize_counts(self, x, n=None):
        """Create a copy of the Dataset with equal counts in each cell of x

        Parameters
        ----------
        x : categorial
            Model which defines the cells in which to equalize the counts.
        n : int
            Number of cases per cell (the default is the maximum possible, i.e.
            the number of cases in the cell with the least number of cases).
            Negative numbers to subtract from maximum possible.

        Returns
        -------
        equalized_ds : Dataset
            Dataset with equal number of cases in each cell of x.

        Notes
        -----
        First, the cell with the smallest number of rows is determined (empty
        cells are ignored). Then, for each cell, rows beyond that number are
        dropped.
        """
        x = ascategorial(x, ds=self)
        self._check_n_cases(x, empty_ok=False)
        indexes = np.array([x == cell for cell in x.cells])
        n_by_cell = indexes.sum(1)
        n_max = np.setdiff1d(n_by_cell, [0]).min()
        if n is None:
            n_ = n_max
        elif n < 0:
            n_ = n_max + n
        else:
            n_ = n

        if n_ < 0 or n_ > n_max:
            raise ValueError("Invalid value n=%i; the maximum numer of cases "
                             "per cell is %i" % (n, n_max))

        for index in indexes:
            np.logical_and(index, index.cumsum() <= n_, index)
        index = indexes.any(0)
        return self[index]

    def head(self, n=10):
        "Table with the first n cases in the Dataset"
        return self.as_table(n, '%.5g', midrule=True, lfmt=True)

    def index(self, name='index', start=0):
        """Add an index to the Dataset (i.e., ``range(n_cases)``)

        Parameters
        ----------
        name : str
            Name of the new index variable.
        start : int
            Number at which to start the index.
        """
        if not isinstance(name, str):
            raise TypeError("name=%r" % (name,))
        self[name] = Var(np.arange(start, self.n_cases + start))

    def itercases(self, start=None, stop=None):
        "Iterate through cases (each case represented as a dict)"
        if start is None:
            start = 0

        if stop is None:
            stop = self.n_cases
        elif stop < 0:
            stop = self.n_cases - stop

        for i in range(start, stop):
            yield self.get_case(i)

    @property
    def n_items(self):
        return super(Dataset, self).__len__()

    def rename(self, old, new):
        """Shortcut to rename a data-object in the Dataset.

        Parameters
        ----------
        old : str
            Current name of the data-object.
        new : str
            New name for the data-object.
        """
        if old not in self:
            raise KeyError("No item named %r" % old)
        if new in self:
            raise ValueError("Dataset already has variable named %r" % new)
        assert_is_legal_dataset_key(new)
        self[new] = self.pop(old)

    def repeat(self, repeats, name='{name}'):
        """
        Return a new Dataset with each row repeated ``n`` times.

        Parameters
        ----------
        repeats : int | array of int
            Number of repeats, either a constant or a different number for each
            element.
        name : str
            Name for the new Dataset.
        """
        if self.n_cases is None:
            raise RuntimeError("Can't repeat Dataset with unspecified n_cases")

        if isinstance(repeats, Integral):
            n_cases = self.n_cases * repeats
        else:
            n_cases = sum(repeats)

        return Dataset(((k, v.repeat(repeats)) for k, v in self.items()),
                       name.format(name=self.name), self._caption, self.info,
                       n_cases)

    @property
    def shape(self):
        return (self.n_cases, self.n_items)

    def sort(self, order, descending=False):
        """Sort the Dataset in place.

        Parameters
        ----------
        order : str | data-object
            Data object (Var, Factor or interactions) according to whose values
            to sort the Dataset, or its name in the Dataset.
        descending : bool
            Sort in descending instead of an ascending order.

        See Also
        --------
        .sort_index : Create an index that could be used to sort the Dataset
        .sorted : Create a sorted copy of the Dataset
        """
        idx = self.sort_index(order, descending)
        for k in self:
            self[k] = self[k][idx]

    def sort_index(self, order, descending=False):
        """Create an index that could be used to sort the Dataset.

        Parameters
        ----------
        order : str | data-object
            Data object (Var, Factor or interactions) according to whose values
            to sort the Dataset, or its name in the Dataset.
        descending : bool
            Sort in descending instead of an ascending order.

        See Also
        --------
        .sort : sort the Dataset in place
        .sorted : Create a sorted copy of the Dataset
        """
        if isinstance(order, str):
            order = self.eval(order)

        if not len(order) == self.n_cases:
            err = ("Order must be of same length as Dataset; got length "
                   "%i." % len(order))
            raise ValueError(err)

        return order.sort_index(descending=descending)

    def save(self):
        """Shortcut to save the Dataset, will display a system file dialog

        Notes
        -----
        Use specific save methods for more options.

        See Also
        --------
        .save_pickled : Pickle the Dataset
        .save_txt : Save as text file
        .save_tex : Save as teX table
        .as_table : Create a table with more control over formatting
        """
        title = "Save Dataset"
        if self.name:
            title += ' %s' % self.name
        msg = ""
        filetypes = [_pickled_ds_wildcard, _tsv_wildcard, _tex_wildcard]
        path = ui.ask_saveas(title, msg, filetypes, defaultFile=self.name)
        _, ext = os.path.splitext(path)
        if ext == '.pickled':
            self.save_pickled(path)
        elif ext == '.txt':
            self.save_txt(path)
        elif ext == '.tex':
            self.save_tex(path)
        else:
            err = ("Unrecognized extension: %r. Needs to be .pickled, .txt or "
                   ".tex." % ext)
            raise ValueError(err)

    def save_rtf(self, path=None, fmt='%.3g'):
        """Save the Dataset as TeX table.

        Parameters
        ----------
        path : None | str
            Target file name (if ``None`` is supplied, a save file dialog is
            displayed). If no extension is specified, '.tex' is appended.
        fmt : format string
            Formatting for scalar values.
        """
        table = self.as_table(fmt=fmt)
        table.save_rtf(path)

    def save_tex(self, path=None, fmt='%.3g', header=True, midrule=True):
        """Save the Dataset as TeX table.

        Parameters
        ----------
        path : None | str
            Target file name (if ``None`` is supplied, a save file dialog is
            displayed). If no extension is specified, '.tex' is appended.
        fmt : format string
            Formatting for scalar values.
        header : bool
            Include the varibale names as a header row.
        midrule : bool
            print a midrule after table header.
        """
        if not isinstance(path, str):
            title = "Save Dataset"
            if self.name:
                title += ' %s' % self.name
            title += " as TeX Table"
            msg = ""
            path = ui.ask_saveas(title, msg, [_tex_wildcard],
                                 defaultFile=self.name)

        _, ext = os.path.splitext(path)
        if not ext:
            path += '.tex'

        table = self.as_table(fmt=fmt, header=header, midrule=midrule)
        table.save_tex(path)

    def save_txt(self, path=None, fmt='%s', delim='\t', header=True):
        """Save the Dataset as text file.

        Parameters
        ----------
        path : str
            Target file name (by default, a Save As dialog is displayed). If
            ``path`` is missing an extension, ``'.txt'`` is appended.
        fmt : format string
            Formatting for scalar values.
        delim : str
            Column delimiter (default is tab).
        header : bool
            write the variables' names in the first line
        """
        if path is None:
            path = ui.ask_saveas(f"Save {self.name or 'Dataset'} as Text", "",
                                 [_tsv_wildcard], defaultFile=self.name)
        path = Path(path)
        if not path.suffix:
            path = path.with_suffix('.txt')

        table = self.as_table(fmt=fmt, header=header)
        table.save_tsv(path, fmt=fmt, delimiter=delim)

    def save_pickled(self, path=None):
        """Pickle the Dataset.

        Parameters
        ----------
        path : None | str
            Target file name (if ``None`` is supplied, a save file dialog is
            displayed). If no extension is specified, '.pickled' is appended.
        """
        if not isinstance(path, str):
            title = "Pickle Dataset"
            if self.name:
                title += ' %s' % self.name
            msg = ""
            path = ui.ask_saveas(title, msg, [_pickled_ds_wildcard],
                                 defaultFile=self.name)

        _, ext = os.path.splitext(path)
        if not ext:
            path += '.pickled'

        with open(path, 'wb') as fid:
            pickle.dump(self, fid, pickle.HIGHEST_PROTOCOL)

    def sorted(self, order, descending=False):
        """Create an sorted copy of the Dataset.

        Parameters
        ----------
        order : str | data-object
            Data object (Var, Factor or interactions) according to whose values
            to sort the Dataset, or its name in the Dataset.
        descending : bool
            Sort in descending instead of an ascending order.

        See Also
        --------
        .sort : sort the Dataset in place
        .sort_index : Create an index that could be used to sort the Dataset
        """
        idx = self.sort_index(order, descending)
        return self[idx]

    def sub(self, index=None, keys=None, name=None):
        """Access a subset of the data in the Dataset.

        Parameters
        ----------
        index : int | array | str
            Index for selecting a subset of cases. Can be an valid numpy index
            or a string (the name of a variable in Dataset, or an expression
            to be evaluated in the Dataset's namespace).
        keys : sequence of str | str
            Only include items with those keys (default all items). Use a
            :class:`str` to retrieve a single item directly.
        name : str
            name for the new Dataset.

        Returns
        -------
        data : Dataset | data_object
            Either the :class:`Dataset` with cases restricted to ``index``, or,
            if ``key`` is a :class:`str`, a single item restricted to ``index``.

        Notes
        -----
        Index is passed on to numpy objects, which means that advanced indexing
        always returns a copy of the data, whereas basic slicing (using slices)
        returns a view.
        """
        if index is None:
            if keys is None:
                return self.copy(name)
            elif isinstance(keys, str):
                return OrderedDict.__getitem__(self, keys)
            else:
                items = ((k, OrderedDict.__getitem__(self, k)) for k in keys)
        elif isinstance(index, Integral):
            if keys is None:
                return self.get_case(index)
            elif isinstance(keys, str):
                return OrderedDict.__getitem__(self, keys)[index]
            else:
                return {k: OrderedDict.__getitem__(self, k)[index] for k in keys}
        else:
            if isinstance(index, str):
                index = self.eval(index)
            index = asindex(index)
            if keys is None:
                keys = self.keys()
            elif isinstance(keys, str):
                return OrderedDict.__getitem__(self, keys)[index]
            items = ((k, OrderedDict.__getitem__(self, k)[index]) for k in keys)

        return Dataset(items, name or self.name, self._caption, self.info)

    def summary(self, width=None):
        """A summary of the Dataset's contents

        Parameters
        ----------
        width : int
            Width in characters (default depends on current terminal size).
        """
        if width is None:
            try:
                width = os.get_terminal_size().columns
            except OSError:
                width = 100
        width -= max(map(len, self))
        width -= max(len(v.__class__.__name__) for v in self.values())
        width -= 6
        out = fmtxt.Table('lll')
        out.cells('Key', 'Type', 'Values')
        out.midrule()
        for k, v in self.items():
            out.cell(k)
            out.cell(v.__class__.__name__)
            if hasattr(v, '_summary'):
                summary = v._summary(width)
            else:
                summary = ''
            out.cell(summary)
        out.rules
        name = 'Dataset' if self.name is None else self.name
        out.caption(f"{name}: {self.n_cases} cases")
        return out

    def tail(self, n=10):
        "Table with the last n cases in the Dataset"
        return self.as_table(range(-n, 0), '%.5g', midrule=True, lfmt=True)

    def tile(self, repeats, name=None):
        """Concatenate ``repeats`` copies of the dataset

        Parameters
        ----------
        repeats : int
            Number of repeats.
        name : str
            Name for the new dataset (default is ``self.name``).
        """
        return Dataset(
            ((name, item.tile(repeats)) for name, item in self.items()),
            name or self.name, self._caption, self.info, self.n_cases * repeats)

    def to_r(self, name=None):
        """Place the Dataset into R as dataframe using rpy2

        Parameters
        ----------
        name : str
            Name for the R dataframe (default is self.name).

        Examples
        --------
        >>> from rpy2.robjects import r
        >>> ds = datasets.get_uv()
        >>> print(ds[:6])
        A    B    rm     intvar   fltvar     fltvar2    index
        -----------------------------------------------------
        a1   b1   s000   13       0.25614    0.7428     True
        a1   b1   s001   8        -1.5174    -0.75498   True
        a1   b1   s002   11       -0.5071    -0.13828   True
        a1   b1   s003   11       2.1491     -2.1249    True
        a1   b1   s004   15       -0.19358   -1.03      True
        a1   b1   s005   17       2.141      -0.51745   True
        >>> ds.to_r('df')
        >>> print(r("head(df)"))
           A  B   rm intvar     fltvar    fltvar2 index
        1 a1 b1 s000     13  0.2561439  0.7427957  TRUE
        2 a1 b1 s001      8 -1.5174371 -0.7549815  TRUE
        3 a1 b1 s002     11 -0.5070960 -0.1382827  TRUE
        4 a1 b1 s003     11  2.1490761 -2.1249203  TRUE
        5 a1 b1 s004     15 -0.1935783 -1.0300188  TRUE
        6 a1 b1 s005     17  2.1410424 -0.5174519  TRUE

        """
        import rpy2.robjects as ro

        if name is None:
            name = self.name
            if name is None:
                raise TypeError('Need a valid name for the R data frame')

        items = OrderedDict()
        for k, v in self.items():
            if isinstance(v, Var):
                if v.x.dtype.kind == 'b':
                    item = ro.BoolVector(v.x)
                elif v.x.dtype.kind == 'i':
                    item = ro.IntVector(v.x)
                else:
                    item = ro.FloatVector(v.x)
            elif isinstance(v, Factor):
                x = ro.IntVector(v.x)
                codes = sorted(v._labels)
                levels = ro.IntVector(codes)
                labels = ro.StrVector(tuple(v._labels[c] for c in codes))
                item = ro.FactorVector(x, levels, labels)
            else:
                continue
            items[k] = item

        df = ro.DataFrame(items)
        ro.globalenv[name] = df

    def update(self, ds, replace=False, info=True):
        """Update the Dataset with all variables in ``ds``.

        Parameters
        ----------
        ds : Dataset | dict
            A Dataset or other dictionary-like object whose keys are strings
            and whose values are data-objects.
        replace : bool
            If a variable in ds is already present, replace it. If False,
            duplicates raise a ValueError (unless they are equivalent).
        info : bool
            Also update the info dictionary.

        Notes
        -----
        By default, if a key is present in both Datasets, and the corresponding
        variables are not equal on all cases, a ValueError is raised. If all
        values are equal, the variable in ds is copied into the Dataset that is
        being updated (the expected behavior of .update()).
        """
        if isinstance(ds, Dataset):
            if ds.n_cases is None or self.n_cases is None:
                pass
            elif ds.n_cases != self.n_cases:
                raise ValueError(f"Trying to update dataset with {self.n_cases} cases from dataset with {ds.n_cases} cases")

        if not replace:
            unequal = {}
            for key in set(self).intersection(ds):
                own = self[key]
                other = ds[key]
                if len(own) != len(other):
                    unequal[key] = 'unequal length'
                elif not np.all(own == other):
                    unequal[key] = "unequal values"
            if unequal:
                raise ValueError(
                    "The following variables are present twice but are not "
                    "equal: %s" % ', '.join('%r (%s)' % item for item in unequal.items()))

        super(Dataset, self).update(ds)

        if info and isinstance(ds, Dataset):
            self.info.update(ds.info)

    def zip(self, *variables):
        """Iterate through the values of multiple variables

        ``ds.zip('a', 'b')`` is equivalent to ``zip(ds['a'], ds['b'])``.
        """
        return zip(*map(self.eval, variables))


class Interaction(_Effect):
    """Represents an Interaction effect.

    Usually not initialized directly but through operations on Factors/Vars.

    Parameters
    ----------
    base : sequence
        List of data-objects that form the basis of the interaction.

    Attributes
    ----------
    base : list
        All effects.
    """
    def __init__(self, base):
        base_ = EffectList()
        n_vars = 0

        for b in base:
            if isuv(b):
                base_.append(b.copy())
                n_vars += isinstance(b, Var)
            elif isinstance(b, Interaction):
                base_.extend(b.base)
                n_vars += not b.is_categorial
            elif isinstance(b, NestedEffect):
                base_.append(b)
            else:
                raise TypeError("Invalid type for Interaction: %r" % type(b))

        if n_vars > 1:
            raise TypeError("No Interaction between two Var objects")

        if len(base_) < 2:
            raise ValueError("Interaction needs a base of at least two Factors "
                             "(got %s)" % repr(base))
        N = len(base_[0])
        if not all(len(f) == N for f in base_[1:]):
            raise ValueError("Interactions only between effects with the same "
                             "number of cases")
        self.__setstate__({'base': base_, 'is_categorial': not bool(n_vars)})

    def __setstate__(self, state):
        self.base = state['base']
        self.is_categorial = state['is_categorial']
        # secondary attributes
        self._n_cases = len(self.base[0])
        self.nestedin = EffectList()
        for e in self.base:
            if (isinstance(e, NestedEffect) and
                    not any(np.all(e.nestedin == ne) for ne in self.nestedin)):
                self.nestedin.append(e.nestedin)
        self.base_names = [str(f.name) for f in self.base]
        self.name = ' x '.join(self.base_names)
        self.random = False
        self.df = reduce(operator.mul, [f.df for f in self.base])
        # cells
        factors = EffectList(e for e in self.base if
                             isinstance(e, (Factor, NestedEffect)))
        self.cells = tuple(product(*(f.cells for f in factors)))
        self.cell_header = tuple(f.name for f in factors)
        # TODO: beta-labels
        self.beta_labels = ['?'] * self.df

    def __getstate__(self):
        return {'base': self.base, 'is_categorial': self.is_categorial}

    def __repr__(self):
        names = [UNNAMED if f.name is None else f.name for f in self.base]
        if preferences['short_repr']:
            return ' % '.join(names)
        else:
            return "Interaction({n})".format(n=', '.join(names))

    # container ---
    def __len__(self):
        return self._n_cases

    def __getitem__(self, index):
        if isinstance(index, Var):
            index = index.x

        out = tuple(f[index] for f in self.base)

        if index_ndim(index) == 1:
            return Interaction(out)
        else:
            return out

    def __contains__(self, item):
        if isinstance(item, tuple):
            return item in self._value_set
        return self.base.__contains__(item)

    def __iter__(self):
        for i in range(len(self)):
            yield tuple(b[i] for b in self.base)

    # numeric ---
    def __eq__(self, other):
        if isinstance(other, Interaction) and len(other.base) == len(self.base):
            x = np.vstack([b == bo for b, bo in zip(self.base, other.base)])
            return np.all(x, 0)
        elif isinstance(other, tuple) and len(other) == len(self.base):
            x = np.vstack([factor == level for factor, level in zip(self.base, other)])
            return np.all(x, 0)
        else:
            return np.zeros(len(self), bool)

    def __ne__(self, other):
        if isinstance(other, Interaction) and len(other.base) == len(self.base):
            x = np.vstack([b != bo for b, bo in zip(self.base, other.base)])
            return np.any(x, 0)
        elif isinstance(other, tuple) and len(other) == len(self.base):
            x = np.vstack([factor != level for factor, level in zip(self.base, other)])
            return np.any(x, 0)
        return np.ones(len(self), bool)

    def as_factor(self, delim=' ', name=None):
        """Convert the Interaction to a factor

        Parameters
        ----------
        delim : str
            Delimiter to join factor cell values (default ``" "``).
        name : str
            Name for the Factor (default is None).

        Examples
        --------
        >>> print(ds[::20, 'A'])
        Factor(['a1', 'a1', 'a2', 'a2'], name='A')
        >>> print(ds[::20, 'B'])
        Factor(['b1', 'b2', 'b1', 'b2'], name='B')
        >>> i = ds.eval("A % B")
        >>> print(i.as_factor()[::20])
        Factor(['a1 b1', 'a1 b2', 'a2 b1', 'a2 b2'], name='AxB')
        >>> print(i.as_factor("_")[::20])
        Factor(['a1_b1', 'a1_b2', 'a2_b1', 'a2_b2'], name='AxB')
        """
        return Factor(self.as_labels(delim), name)

    def as_cells(self):
        """All values as a list of tuples."""
        return [case for case in self]

    @LazyProperty
    def as_dummy(self):
        codelist = [f.as_dummy for f in self.base]
        return reduce(_effect_interaction, codelist)

    @LazyProperty
    def as_effects(self):  # Effect coding
        codelist = [f.as_effects for f in self.base]
        return reduce(_effect_interaction, codelist)

    def _coefficient_names(self, method):
        if self.df == 1:
            return [self.name]
        return ["%s %i" % (self.name, i) for i in range(self.df)]

    def as_labels(self, delim=' '):
        """All values as a list of strings.

        Parameters
        ----------
        delim : str
            Delimiter with which to join the elements of cells.
        """
        return [delim.join(filter(None, map(str, case))) for case in self]

    def aggregate(self, x):
        return Interaction(f.aggregate(x) for f in self.base)

    def isin(self, cells):
        """An index that is true where the Interaction equals any of the cells.

        Parameters
        ----------
        cells : sequence of tuples
            Cells for which the index will be true. Cells described as tuples
            of strings.
        """
        is_v = [self == cell for cell in cells]
        return np.any(is_v, 0)

    @LazyProperty
    def _value_set(self):
        return set(self)


def box_cox_transform(x, p, name=None):
    """The Box-Cox transform of x as :class:`Var`

    With ``p=0``, this is the log of x; otherwise ``(x**p - 1) / p``

    Parameters
    ----------
    x : Var
        Source data.
    p : scalar
        Parameter for Box-Cox transform.
    name : str
        Name for the output Var.
    """
    if isinstance(x, Var):
        x = x.x

    if p == 0:
        y = np.log(x)
    else:
        y = (x ** p - 1) / p

    return Var(y, name)


class NestedEffect(_Effect):

    def __init__(self, effect, nestedin):
        if not isinstance(nestedin, (Factor, Interaction)):
            raise TypeError("Nested in %r; Effects can only be nested in Factor "
                            "or Interaction" % (dataobj_repr(nestedin),))
        elif not iscategorial(nestedin):
            raise ValueError("Effects can only be nested in categorial base")

        self.effect = effect
        self.nestedin = nestedin
        self.random = effect.random
        self.cells = effect.cells
        self._n_cases = len(effect)

        if isinstance(self.effect, Factor):
            e_name = self.effect.name
        else:
            e_name = '(%s)' % self.effect
        self.name = "%s(%s)" % (e_name, nestedin.name)

        if len(nestedin) != self._n_cases:
            err = ("Unequal lengths: effect %r len=%i, nestedin %r len=%i" %
                   (e_name, len(effect), nestedin.name, len(nestedin)))
            raise ValueError(err)

    def __repr__(self):
        return self.name

    def __iter__(self):
        return self.effect.__iter__()

    def __len__(self):
        return self._n_cases

    def __eq__(self, other):
        return self.effect == other

    def __getitem__(self, index):
        if isinstance(index, Integral):
            return self.effect[index]
        return NestedEffect(self.effect[index], self.nestedin[index])

    @property
    def df(self):
        return len(self.effect.cells) - len(self.nestedin.cells)

    @property
    def as_effects(self):
        "Effect codes"
        codes = np.zeros((self._n_cases, self.df))
        ix = 0
        for outer_cell in self.nestedin.cells:
            outer_idx = (self.nestedin == outer_cell)
            inner_model = self.effect[outer_idx]
            n = len(inner_model.cells)
            inner_codes = _effect_eye(n)
            for i, cell in enumerate(inner_model.cells):
                codes[self.effect == cell, ix:ix + n - 1] = inner_codes[i]
            ix += n - 1

        return codes

    def _coefficient_names(self, method):
        return ["%s %i" % (self.name, i) for i in range(self.df)]


class NonbasicEffect:

    def __init__(self, effect_codes, factors, name, nestedin=[],
                 beta_labels=None):
        if beta_labels is not None and len(beta_labels) != effect_codes.shape[1]:
            raise ValueError("beta_labels need one entry per model column "
                             "(%s); got %s"
                             % (effect_codes.shape[1], repr(beta_labels)))
        self.nestedin = nestedin
        self.name = name
        self.random = False
        self.as_effects = effect_codes
        self._n_cases, self.df = effect_codes.shape
        self.factors = factors
        self.beta_labels = beta_labels

    def __repr__(self):
        txt = "<NonbasicEffect: {n}>"
        return txt.format(n=self.name)

    # container ---
    def __len__(self):
        return self._n_cases

    def _coefficient_names(self, method):
        if self.beta_labels is None:
            return ["%s %i" % (self.name, i) for i in range(self.df)]
        else:
            return self.beta_labels


class Model:
    """A list of effects.

    Parameters
    ----------
    x : effect | iterator of effects
        Effects to be included in the model (Var, Factor, Interaction ,
        ...). Can also contain models, in which case all the model's
        effects will be added.

    Attributes
    ----------
    effects : list
        Effects included in the model (:class:`Var`, :class:`Factor`, etc. 
        objects)
    """
    def __init__(self, x):
        effects = EffectList()

        # find effects in input
        if iseffect(x):
            effects.append(x)
            n_cases = len(x)
        elif isinstance(x, Model):
            effects += x.effects
            n_cases = len(x)
        else:
            n_cases = None
            for e in x:
                # check n_cases
                if n_cases is None:
                    n_cases = len(e)
                elif len(e) != n_cases:
                    e0 = effects[0]
                    raise ValueError(
                        "All effects contained in a Model need to describe the "
                        "same number of cases. %s has %i cases, %s has %i "
                        "cases." %
                        (dataobj_repr(e0), len(e0), dataobj_repr(e), len(e)))

                # find effects
                if iseffect(e):
                    effects.append(e)
                elif isinstance(e, Model):
                    effects += e.effects
                else:
                    raise TypeError(
                        "Model needs to be initialized with effect (Var, "
                        "Factor, Interaction, ...) and/or Model objects (got "
                        "%s)" % type(e))

        # check dfs
        df = sum(e.df for e in effects) + 1  # intercept
        if df > n_cases:
            raise ValueError(
                "Model overspecified (%i cases for %i model df)" %
                (n_cases, df))

        # beta indices
        for e in effects:
            if isinstance(e, Factor) and len(e.cells) == 1:
                raise ValueError("The Factor %s has only one level (%s). The "
                                 "intercept is implicit in each model and "
                                 "should not be specified explicitly."
                                 % (dataobj_repr(e), e.cells[0]))

        self.effects = effects
        self.df = df
        self._init_secondary()

    def _init_secondary(self):
        self.df_total = len(self.effects[0])
        self.df_error = self.df_total - self.df
        self.name = ' + '.join([str(e.name) for e in self.effects])

    def __setstate__(self, state):
        self.effects = state['effects']
        self.df = sum(e.df for e in self.effects) + 1  # intercept
        self._init_secondary()

    def __getstate__(self):
        return {'effects': self.effects}

    def __repr__(self):
        names = self.effects.names()
        if preferences['short_repr']:
            return ' + '.join(names)
        else:
            x = ', '.join(names)
            return "Model((%s))" % x

    def __str__(self):
        return str(self.as_table())

    def info(self):
        """A :class:`fmtxt.Table` with information about the model"""
        table = fmtxt.Table('rl')
        table.cells('Df', 'Term')
        table.midrule()
        for e in self.effects:
            table.cells(e.df, e.name, )
        if self.df_error:
            table.midrule()
            table.cells(self.df_error, 'Residuals')
        return table

    # container ---
    def __len__(self):
        return self.df_total

    def __getitem__(self, sub):
        if isinstance(sub, str):
            for e in self.effects:
                if e.name == sub:
                    return e
            raise KeyError(sub)
        elif isinstance(sub, INT_TYPES):
            return tuple(e[sub] for e in self.effects)
        else:
            return Model((x[sub] for x in self.effects))

    def __contains__(self, effect):
        return id(effect) in map(id, self.effects)

    def sorted(self):
        """Sorted copy of the Model, interactions last"""
        out = []
        i = 1
        while len(out) < len(self.effects):
            for e in self.effects:
                if len(e.factors) == i:
                    out.append(e)
            i += 1
        return Model(out)

    # numeric ---
    def __add__(self, other):
        return Model((self, other))

    def __mul__(self, other):
        return Model((self, other, self % other))

    def __mod__(self, other):
        out = []
        for e_self in self.effects:
            for e_other in Model(other).effects:
                if isinstance(e_self, Var) and isinstance(e_other, Var):
                    out.append(e_self * e_other)
                elif not partially_nested(e_self, e_other):
                    out.append(e_self % e_other)
        return Model(out)

    def __eq__(self, other):
        if not isinstance(other, Model):
            return False
        elif not len(self) == len(other):
            return False
        elif not len(self.effects) == len(other.effects):
            return False

        for e, eo in zip(self.effects, other.effects):
            if not np.all(e == eo):
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    # repr ---
    @property
    def model_eq(self):
        return self.name

    # coding ---
    @LazyProperty
    def _effect_to_beta(self):
        """An array indicating for each effect which beta weights it occupies

        Returns
        -------
        effects_to_beta : np.ndarray (n_effects, 2)
            For each effect, indicating the first index in betas and df
        """
        out = np.empty((len(self.effects), 2), np.intp)
        beta_start = 1
        for i, e in enumerate(self.effects):
            out[i, 0] = beta_start
            out[i, 1] = e.df
            beta_start += e.df
        return out

    def as_table(self, method='dummy', cases=0, group_terms=True):
        """Return a table with the model codes

        Parameters
        ----------
        method : 'effect' | 'dummy'
            Coding scheme: effect coding or dummy coding.
        cases : int | iterator of int
            Cases to include (int includes that many cases from the beginning,
            0 includes all; negative number works like negative indexing).
        group_terms : bool
            Group model columns that represent the same effect under one
            heading.

        Returns
        --------
        table : FMText Table
            The full model as a table.
        """
        itre_cases = cases_arg(cases, self.df_total)
        p = self._parametrize(method)
        table = fmtxt.Table('l' * len(p.column_names))

        # Header
        if group_terms:
            for term in p.effect_names:
                index = p.terms[term]
                ncolumns = index.stop - index.start
                table.cell(term, width=ncolumns)
        else:
            for term in p.column_names:
                table.cell(term)
        table.midrule()

        # data
        for case in itre_cases:
            for i in p.x[case]:
                table.cell('%g' % i)

        return table

    def head(self, n=10):
        "Table with the first n cases in the Model"
        return self.as_table(cases=n)

    # checking model properties
    def check(self, v=True):
        "Shortcut to check linear independence and orthogonality"
        return self.lin_indep(v) + self.orthogonal(v)

    def lin_indep(self, v=True):
        "Check the Model for linear independence of its factors"
        msg = []
        ne = len(self.effects)
        codes = [e.as_effects for e in self.effects]
        for i in range(ne):
            for j in range(i + 1, ne):
                e1 = self.effects[i]
                e2 = self.effects[j]
                x = np.hstack((codes[i], codes[j]))
                if rank(x) < x.shape[1]:
                    if v:
                        errtxt = "Linear Dependence Warning: {0} and {1}"
                        msg.append(errtxt.format(e1.name, e2.name))
        return msg

    def orthogonal(self, v=True):
        "Check the Model for orthogonality of its factors"
        msg = []
        ne = len(self.effects)
        codes = [e.as_effects for e in self.effects]
#        allok = True
        for i in range(ne):
            for j in range(i + 1, ne):
                ok = True
                e1 = self.effects[i]
                e2 = self.effects[j]
                e1e = codes[i]
                e2e = codes[j]
                for i1 in range(e1.df):
                    for i2 in range(e2.df):
                        dotp = np.dot(e1e[:, i1], e2e[:, i2])
                        if dotp != 0:
                            ok = False
#                            allok = False
                if v and (not ok):
                    errtxt = "Not orthogonal: {0} and {1}"
                    msg.append(errtxt.format(e1.name, e2.name))
        return msg

    def _parametrize(self, method='effect'):
        "Create a design matrix"
        return Parametrization(self, method)

    def _incomplete_error(self, caller):
        df_table = self.info()
        df_table[-1, 1] = 'Unexplained'
        return IncompleteModel(
            "%s requires a fully specified model, but the model has only "
            "%i explained degrees of freedom for %i cases:\n%s" %
            (caller, self.df, self.df_total, df_table))

    def repeat(self, n):
        "Repeat each row of the Model ``n`` times"
        return Model(e.repeat(n) for e in self.effects)

    def tail(self, n=10):
        "Table with the last n cases in the Model"
        return self.as_table(cases=range(-n, 0))


class Parametrization:
    """Parametrization of a statistical model

    Parameters
    ----------
    model : Model
        Model to be parametrized.
    method : 'effect' | 'dummy'
        Coding scheme: effect coding or dummy coding.

    Attributes
    ----------
    model : Model
        The model that is parametrized.
    x : array (n_cases, n_coeffs)
        Design matrix.
    terms : {str: slice}
        Location of each term in x.
    column_names : list of str
        Name of each column.

    Notes
    -----
    A :class:`Model` is a list of effects. A :class:`Parametrization` contains
    a realization of those effects in a model matrix with named columns.
    """
    def __init__(self, model, method):
        model = asmodel(model)
        x = np.empty((model.df_total, model.df))
        x[:, 0] = 1
        column_names = ['intercept']
        effect_names = ['intercept']
        higher_level_effects = {}
        terms = {'intercept': slice(0, 1)}
        i = 1
        for e in model.effects:
            j = i + e.df
            if method == 'effect':
                x[:, i:j] = e.as_effects
            elif method == 'dummy':
                x[:, i:j] = e.as_dummy
            else:
                raise ValueError("method=%s" % repr(method))
            name = longname(e)
            if name in terms:
                raise KeyError("Duplicate term name: %s" % repr(name))
            terms[name] = slice(i, j)
            effect_names.append(name)
            col_names = e._coefficient_names(method)
            column_names.extend(col_names)
            for col, col_name in enumerate(col_names, i):
                terms[col_name] = slice(col, col + 1)
            i = j

            # find comparison models
            higher_level_effects[name] = [
                e_ for e_ in model.effects if
                e_ is not e and is_higher_order_effect(e_, e)
            ]

        # check model
        if np.linalg.matrix_rank(x) < x.shape[1]:
            raise ValueError("Model is rank deficient: %r" % model)

        # model basics
        self.model = model
        self.method = method
        self.x = x
        self.terms = terms
        self.column_names = column_names
        self.effect_names = effect_names
        self._higher_level_effects = higher_level_effects

        # projector
        x_t = x.T
        self.g = inv(x_t.dot(x))
        self.projector = self.g.dot(x_t)

    def reduced_model_index(self, term):
        "Boolean index into model columns for model comparison"
        out = np.ones(self.x.shape[1], bool)
        out[self.terms[term]] = False
        for e in self._higher_level_effects[term]:
            out[self.terms[e.name]] = False
        return out


# ---NDVar dimensions---

def _subgraph_edges(connectivity, int_index):
    "Extract connectivity for a subset of a graph"
    idx = np.logical_and(np.in1d(connectivity[:, 0], int_index),
                         np.in1d(connectivity[:, 1], int_index))
    if np.any(idx):
        new_c = connectivity[idx]

        # remap to new vertex indices
        if np.any(np.diff(int_index) < 1):  # non-monotonic index
            argsort = np.argsort(int_index)
            flat_conn_ = np.digitize(new_c.ravel(), int_index[argsort], True)
            flat_conn = argsort[flat_conn_]
        else:
            flat_conn = np.digitize(new_c.ravel(), int_index, True)

        return flat_conn.reshape(new_c.shape).astype(np.uint32)
    else:
        return np.empty((0, 2), dtype=np.uint32)


def connectivity_from_name_pairs(neighbors, items, allow_missing=False):
    pairs = set()
    for src, dst in neighbors:
        if src not in items or dst not in items:
            if allow_missing:
                continue
            else:
                item = src if src not in items else dst
                raise ValueError(f"Connectivity contains unknown item {item!r}")
        a = items.index(src)
        b = items.index(dst)
        if a < b:
            pairs.add((a, b))
        else:
            pairs.add((b, a))
    return np.array(sorted(pairs), np.uint32)


class Dimension:
    """Base class for dimensions.
    
    Parameters
    ----------
    name : str
        Dimension name.
    connectivity : 'grid' | 'none' | array of int, (n_edges, 2)
        Connectivity between elements. Set to ``"none"`` for no connections or 
        ``"grid"`` to use adjacency in the sequence of elements as connection. 
        Set to :class:`numpy.ndarray` to specify custom connectivity. The array
        should be of shape (n_edges, 2), and each row should specify one 
        connection [i, j] with i < j, with rows sorted in ascending order. If
        the array's dtype is uint32, property checks are disabled to improve 
        efficiency.

    Attributes
    ----------
    x : array_like
        Numerical values (e.g. for locating categories on an axis).
    values : sequence
        Meaningful point descriptions (e.g. time points, sensor names, ...).
    """
    _CONNECTIVITY_TYPES = ('grid', 'none', 'custom', 'vector')
    _axis_unit = None
    _default_connectivity = 'none'  # for loading old pickles

    def __init__(self, name, connectivity):
        # requires __len__ to work
        self.name = name
        if isinstance(connectivity, str):
            self._connectivity = None
        else:
            self._connectivity = self._coerce_connectivity(connectivity)
            connectivity = 'custom'

        if not isinstance(connectivity, str):
            raise TypeError("connectivity=%r" % (connectivity,))
        elif connectivity not in self._CONNECTIVITY_TYPES:
            raise ValueError("connectivity=%r" % (connectivity,))
        self._connectivity_type = connectivity

    def _coerce_connectivity(self, connectivity):
        if isinstance(connectivity, np.ndarray) and connectivity.dtype == np.uint32:
            # assume that connectivity is inherited, skip checks
            return connectivity

        connectivity = np.asarray(connectivity)
        if connectivity.dtype.kind != 'i':
            raise TypeError(f"connectivity array needs to be integer type, got {connectivity.dtype}")
        elif connectivity.shape != (len(connectivity), 2):
            raise ValueError(f"connectivity requires shape (n_edges, 2), got array with shape {connectivity.shape}")
        elif connectivity.min() < 0:
            raise ValueError("connectivity can not have negative values")
        elif connectivity.max() >= len(self):
            raise ValueError("connectivity has value larger than number of elements in dimension")
        elif np.any(connectivity[:, 0] >= connectivity[:, 1]):
            raise ValueError("All edges [i, j] must have i < j")
        elif np.any(np.diff(connectivity, axis=0) > 0):
            edges = list(map(tuple, connectivity))
            edges.sort()
            connectivity = np.array(edges, np.uint32)
        else:
            connectivity = connectivity.astype(np.uint32)
        return connectivity

    def __getstate__(self):
        return {'name': self.name, 'connectivity': self._connectivity,
                'connectivity_type': self._connectivity_type}

    def __setstate__(self, state):
        self.name = state['name']
        self._connectivity = state.get('connectivity', None)
        self._connectivity_type = state.get('connectivity_type', self._default_connectivity)

    def __len__(self):
        raise NotImplementedError

    def __eq__(self, other):
        if isinstance(other, str):
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not self == other

    def __getitem__(self, index):
        """Array-like Indexing

        Possible indexes:

          - int -> label or value for that location
          - [int] -> Dimension object with 1 location
          - [int, ...] -> Dimension object
        """
        raise NotImplementedError

    def _bin(self, start, stop, step, nbins):
        "Divide Dimension into bins"
        raise NotImplementedError(
            "Binning for %s dimension" % self.__class__.__name__)

    def _as_scalar_array(self):
        raise TypeError("%s dimension %r has no scalar representation" %
                        (self.__class__.__name__, self.name))

    def _as_uv(self):
        return Var(self._axis_data(), name=self.name)

    def _axis_data(self):
        "x for plot command"
        return np.arange(len(self))

    def _axis_im_extent(self):
        "Extent for im plots; needs to extend beyond end point locations"
        return -0.5, len(self) - 0.5

    def _axis_format(self, scalar, label):
        """Find axis decoration parameters for this dimension

        Parameters
        ----------
        scalar : bool
            If True, the axis is scalar and labels should correspond to the axis
            value. If False, the axis represents categorial bins (e.g.,
            im-plots).
        label : bool | str
            Label (if True, return an appropriate axis-specific label).

        Returns
        -------
        formatter : matplotlib Formatter
            Axis tick formatter.
        locator : matplotlib Locator
            Tick-locator.
        label : str | None
            Return the default axis label if label==True, otherwise the label
            argument.
        """
        raise NotImplementedError

    def _axis_label(self, label):
        if label is True:
            if self._axis_unit:
                return "%s [%s]" % (self.name.capitalize(), self._axis_unit)
            else:
                return self.name.capitalize()

    def dimindex(self, arg):
        "Convert a dimension index to an array index"
        # backwards compatibility
        return self._array_index(arg)

    def _array_index(self, arg):
        """Convert a dimension-semantic index to an array-like index

        Subclasses need to handle dimension-specific cases

        args that are handled by the Dimension baseclass:
         - None
         - boolean array
         - boolean NDVars
        args handled recursively:
         - list
         - tuple -> slice(*tuple)
         - Var -> Var.x
        """
        if arg is None:
            return None  # pass through None, for example for slice
        elif isinstance(arg, NDVar):
            return self._array_index_for_ndvar(arg)
        elif isinstance(arg, Var):
            return self._array_index(arg.x)
        elif isinstance(arg, np.ndarray):
            if arg.dtype.kind != 'b':
                raise TypeError("array of type %r not supported as index for "
                                "%s" % (arg.dtype.kind, self._dimname()))
            elif arg.ndim != 1:
                raise IndexError("Boolean index for %s needs to be 1d, got "
                                 "array of shape %s" %
                                 (self._dimname(), arg.shape))
            elif len(arg) != len(self):
                raise IndexError(
                    "Got boolean index of length %i for %s of length %i" %
                    (len(arg), self._dimname(), len(self)))
            return arg
        elif isinstance(arg, tuple):
            if len(arg) > 3:
                raise ValueError("Tuple indexes signify intervals and need to "
                                 "be of length 1, 2 or 3 (got %r for %s)" %
                                 (arg, self._dimname()))
            return self._array_index_for_slice(*arg)
        elif isinstance(arg, list):
            if len(arg) == 0:
                return np.empty(0, np.intp)
            return np.array([self._array_index(a) for a in arg])
        elif isinstance(arg, slice):
            return self._array_index_for_slice(arg.start, arg.stop, arg.step)
        else:
            raise TypeError("Unknown index type for %s: %r" %
                            (self._dimname(), arg))

    def _array_index_for_ndvar(self, arg):
        if arg.x.dtype.kind != 'b':
            raise IndexError(f"{arg}: only NDVars with boolean data can serve as indexes")
        elif arg.ndim != 1:
            raise IndexError(f"{arg}: only NDVars with ndim == 1 can serve as indexes")
        dim = arg.dims[0]
        if not isinstance(dim, self.__class__):
            raise IndexError(f"{arg}: must have {self.__class__} dimension")
        elif dim == self:
            return arg.x
        index_to_arg = self._array_index_to(dim)
        return index_to_arg[arg.x]

    def _array_index_for_slice(self, start=None, stop=None, step=None):
        if step is not None and not isinstance(step, Integral):
            raise TypeError("Slice index step for %s must be int, not %r" %
                            (self._dimname(), step))

        if start is None:
            start_ = None
        else:
            start_ = self._array_index(start)
            if not isinstance(start_, int):
                raise TypeError("%r is not an unambiguous slice start for %s" %
                                (start, self._dimname()))

        if stop is None:
            stop_ = None
        else:
            stop_ = self._array_index(stop)
            if not isinstance(stop_, int):
                raise TypeError("%r is not an unambiguous slice start for %s" %
                                (stop, self._dimname()))

        return slice(start_, stop_, step)

    def _array_index_to(self, other):
        "Int index to access data from self in an order consistent with other"
        raise NotImplementedError(f"Internal alignment for {self.__class__}")

    def _is_superset_of(self, dim):
        "Test whether self is a superset of dim"
        raise NotImplementedError

    def index_into_dim(self, dim):
        "Index into a subset dimension"
        raise NotImplementedError

    def _dimname(self):
        if self.name.lower() == self.__class__.__name__.lower():
            return self.__class__.__name__ + ' dimension'
        else:
            return '%s dimension (%r)' % (self.__class__.__name__, self.name)

    def _dim_index(self, arg):
        "Convert an array index to a dimension index"
        if isinstance(arg, slice):
            return slice(None if arg.start is None else self._dim_index(arg.start),
                         None if arg.stop is None else self._dim_index(arg.stop),
                         arg.step)
        elif np.isscalar(arg):
            return arg
        else:
            return [self._dim_index(i) for i in index_to_int_array(arg, len(self))]

    def _distances(self):
        "Distance matrix for dimension elements"
        raise NotImplementedError("Distances for %s" % self.__class__.__name__)

    def intersect(self, dim, check_dims=True):
        """Create a Dimension that is the intersection with dim

        Parameters
        ----------
        dim : Dimension
            Dimension to intersect with.
        check_dims : bool
            Check dimensions for consistency (not applicaple).

        Returns
        -------
        intersection : Dimension
            The intersection with dim (returns itself if dim and self are
            equal).
        """
        raise NotImplementedError

    def _union(self, other):
        """Create a Dimension that is the union with dim

        Parameters
        ----------
        other : Dimension
            Dimension to form union with.

        Returns
        -------
        union : Dimension
            The union with dim (returns itself if dim and self are
            equal).
        """
        raise NotImplementedError

    def _cluster_properties(self, x):
        """Find cluster properties for this dimension

        Parameters
        ----------
        x : array of bool, (n_clusters, len(self))
            The cluster extents, with different clusters stacked along the
            first axis.

        Returns
        -------
        cluster_properties : None | Dataset
            A dataset with variables describing cluster properties.
        """
        return None

    def connectivity(self):
        """Retrieve the dimension's connectivity graph

        Returns
        -------
        connectivity : array of int, (n_pairs, 2)
            array of sorted ``[src, dst]`` pairs, with all ``src < dst``.
        """
        if self._connectivity is None:
            self._connectivity = self._generate_connectivity()
        return self._connectivity

    def _generate_connectivity(self):
        raise NotImplementedError("Connectivity for %s dimension." % self.name)

    def _subgraph(self, index=None):
        """Connectivity parameter for new Dimension instance

        Parameters
        ----------
        index : array_like
            Index if the new dimension is a subset of the current dimension.
        """
        if self._connectivity_type == 'custom':
            if self._connectivity is None:
                return 'custom'
            elif index is None:
                return self._connectivity
            return _subgraph_edges(self._connectivity,
                                   index_to_int_array(index, len(self)))
        return self._connectivity_type


class Case(Dimension):
    """Case dimension
    
    Parameters
    ----------
    n : int
        Number of cases.
    connectivity : 'grid' | 'none' | array of int, (n_edges, 2)
        Connectivity between elements. Set to ``"none"`` for no connections or 
        ``"grid"`` to use adjacency in the sequence of elements as connection. 
        Set to :class:`numpy.ndarray` to specify custom connectivity. The array
        should be of shape (n_edges, 2), and each row should specify one 
        connection [i, j] with i < j, with rows sorted in ascending order. If
        the array's dtype is uint32, property checks are disabled to improve 
        efficiency.
        
    Examples
    --------
    When initializing an :class:`NDVar`, the case dimension can be speciied
    with the bare class and the number of cases will be inferred from the data:
    
    >>> NDVar([[1, 2], [3, 4]], (Case, Categorial('column', ['1', '2'])))
    <NDVar: 2 case, 2 column>
    """
    _DIMINDEX_RAW_TYPES = INT_TYPES + (slice, list)

    def __init__(self, n, connectivity='none'):
        Dimension.__init__(self, 'case', connectivity)
        self.n = int(n)

    def __getstate__(self):
        out = Dimension.__getstate__(self)
        out['n'] = self.n
        return out

    def __setstate__(self, state):
        Dimension.__setstate__(self, state)
        self.n = state['n']

    def __repr__(self):
        if self._connectivity_type == 'none':
            return "Case(%i)" % self.n
        elif self._connectivity_type == 'grid':
            return "Case(%i, 'grid')" % self.n
        else:
            return "Case(%i, <custom connectivity>)" % self.n

    def __len__(self):
        return self.n

    def __eq__(self, other):
        return isinstance(other, Case) and other.n == self.n

    def __getitem__(self, item):
        if isinstance(item, Integral):
            if item < 0:
                if item < -self.n:
                    raise IndexError(item)
                item += self.n
            elif item > self.n:
                raise IndexError(item)
            return item
        else:
            return Case(index_length(item, self.n), self._subgraph(item))

    def __iter__(self):
        return iter(range(self.n))

    def _as_scalar_array(self):
        return np.arange(self.n)

    def _axis_format(self, scalar, label):
        if scalar:
            fmt = FormatStrFormatter('%i')
        else:
            fmt = IndexFormatter(np.arange(self.n))
        return (fmt,
                None if scalar else FixedLocator(np.arange(len(self)), 10),
                self._axis_label(label))

    def _array_index(self, arg):
        if isinstance(arg, self._DIMINDEX_RAW_TYPES):
            return arg
        elif isinstance(arg, Var) and arg.x.dtype.kind in 'bi':
            return arg.x
        elif isinstance(arg, np.ndarray) and arg.dtype.kind in 'bi':
            return arg
        elif isinstance(arg, tuple):
            return slice(*arg) if arg else FULL_SLICE
        else:
            raise TypeError(f"Index {arg} of type {type(arg)} for Case dimension")

    def _dim_index(self, arg):
        return arg


class Space(Dimension):
    """Represent multiple directions in space

    Parameters
    ----------
    directions : str
        A sequence of directions, each indicated by a single capitalized
        character, from the following set: [A]nterior, [P]osterior, [L]eft,
        [R]ight, [S]uperior and [I]nferior.
    name : str
        Dimension name.

    Notes
    -----
    Connectivity is set to ``'none'``, but :class:`Space` is not a valid
    dimension to treat as mass-univariate.
    """

    _DIRECTIONS = {
        'A': 'anterior',
        'P': 'posterior',
        'L': 'left',
        'R': 'right',
        'S': 'superior',
        'I': 'inferior',
    }

    def __init__(self, directions, name='space'):
        if not isinstance(directions, str):
            raise TypeError("directions=%r" % (directions,))
        n = len(directions)
        all_directions = set(directions)
        if len(all_directions) != n:
            raise ValueError("directions=%r contains duplicate direction"
                             % (directions,))
        invalid = all_directions.difference(self._DIRECTIONS)
        if invalid:
            raise ValueError("directions=%r contains invalid directions: %s"
                             % (directions, ', '.join(map(repr, invalid))))
        Dimension.__init__(self, name, 'vector')
        self._directions = directions

    def __getstate__(self):
        out = Dimension.__getstate__(self)
        out['directions'] = self._directions
        return out

    def __setstate__(self, state):
        Dimension.__setstate__(self, state)
        self._directions = state['directions']

    def __repr__(self):
        return "Space(%r)" % self._directions

    def __len__(self):
        return len(self._directions)

    def __eq__(self, other):
        return isinstance(other, Space) and other._directions == self._directions

    def __getitem__(self, item):
        if not all(i in self._directions for i in item):
            raise IndexError(item)
        return Space(item)

    def __iter__(self):
        return iter(self._directions)

    def _axis_format(self, scalar, label):
        # like Categorial
        return (IndexFormatter(self._directions),
                FixedLocator(np.arange(len(self._directions))),
                self._axis_label(label))

    def _array_index(self, arg):
        if isinstance(arg, str):
            if len(arg) == 1:
                return self._directions.index(arg)
            else:
                return [self._directions.index(s) for s in arg]
        elif isinstance(arg, list):
            return [self._directions.index(s) for s in arg]
        elif isinstance(arg, tuple):
            return slice(*map(self._array_index, arg)) if arg else FULL_SLICE
        elif isinstance(arg, slice):
            return slice(
                None if arg.start is None else self._array_index(arg.start),
                None if arg.stop is None else self._array_index(arg.stop),
                arg.step)
        else:
            raise TypeError(f"{arg} is an invalid index for {self.__class__.__name__}")

    def _dim_index(self, arg):
        if isinstance(arg, Integral):
            return self._directions[arg]
        else:
            return ''.join(self._directions[i] for i in arg)

    def intersect(self, dim, check_dims=True):
        """Create a dimension object that is the intersection with dim

        Parameters
        ----------
        dim : Space
            Dimension to intersect with.
        check_dims : bool
            Check dimensions for consistency.

        Returns
        -------
        intersection : Space
            The intersection with ``dim`` (returns itself if ``dim`` and
            ``self`` are equal)
        """
        if self.name != dim.name:
            raise DimensionMismatchError("Dimensions don't match")
        elif self._directions == dim._directions:
            return self
        self_dirs = set(self._directions)
        dim_dirs = set(dim._directions)
        out_dirs = self_dirs.intersection(dim_dirs)
        if self_dirs == out_dirs:
            return self
        elif dim_dirs == out_dirs:
            return dim
        else:
            directions = ''.join(c for c in self._directions if c in dim._directions)
            return Space(directions, self.name)


class Categorial(Dimension):
    """Simple categorial dimension

    Parameters
    ----------
    name : str
        Dimension name.
    values : sequence of str
        Names of the entries.
    connectivity : str | list of (str, str) | array of int, (n_edges, 2)
        Connectivity between elements. Can be specified as:

        - ``"none"`` for no connections
        - ``"grid"`` to use adjacency in ``values``
        - list of connections based on items in ``values`` (e.g.,
          ``values=['v1', 'v2', 'v3'],
          connectivity=[('v1', 'v3'), ('v2', 'v3'), ...]``)
        - :class:`numpy.ndarray` of int, shape (n_edges, 2), to specify
          connections in terms of indices. Each row should specify one
          connection ``[i, j]`` with ``i < j``. If the array's dtype is
          ``uint32``, property checks are disabled to improve efficiency.

    """
    def __init__(self, name, values, connectivity='none'):
        self.values = tuple(values)
        if len(set(self.values)) < len(self.values):
            raise ValueError("Dimension can not have duplicate values")
        if not all(isinstance(x, str) for x in self.values):
            raise ValueError("All Categorial values must be strings; got %r." %
                             (self.values,))
        Dimension.__init__(self, name, connectivity)

    def _coerce_connectivity(self, connectivity):
        if isinstance(connectivity[0][0], str):
            return connectivity_from_name_pairs(connectivity, self.values)
        else:
            return Dimension._coerce_connectivity(self, connectivity)

    def __getstate__(self):
        out = Dimension.__getstate__(self)
        out['values'] = self.values
        return out

    def __setstate__(self, state):
        # backwards compatibility
        if 'connectivity' not in state:
            state['connectivity'] = None
            state['connectivity_type'] = 'none'
        self.values = state['values']
        if isinstance(self.values, np.ndarray):
            self.values = tuple(str(v) for v in self.values)
        # /backwards compatibility
        Dimension.__setstate__(self, state)

    def __repr__(self):
        args = (repr(self.name), str(self.values))
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))

    def __len__(self):
        return len(self.values)

    def __eq__(self, other):
        return Dimension.__eq__(self, other) and self.values == other.values

    def __getitem__(self, index):
        if isinstance(index, Integral):
            return self.values[index]
        else:
            return self.__class__(self.name,
                                  apply_numpy_index(self.values, index),
                                  self._subgraph(index))

    def _as_uv(self):
        return Factor(self.values, name=self.name)

    def _axis_format(self, scalar, label):
        return (IndexFormatter(self.values),
                FixedLocator(np.arange(len(self))),
                self._axis_label(label))

    def _array_index(self, arg):
        if isinstance(arg, str):
            if arg in self.values:
                return self.values.index(arg)
            else:
                raise IndexError(arg)
        elif isinstance(arg, self.__class__):
            return [self._array_index(v) for v in arg.values]
        else:
            return super(Categorial, self)._array_index(arg)

    def _dim_index(self, index):
        if isinstance(index, Integral):
            return self.values[index]
        else:
            return Dimension._dim_index(self, index)

    def intersect(self, dim, check_dims=False):
        """Create a dimension object that is the intersection with dim

        Parameters
        ----------
        dim : type(self)
            Dimension to intersect with.
        check_dims : bool
            Check dimensions for consistency (not applicaple to this subclass).

        Returns
        -------
        intersection : type(self)
            The intersection with dim (returns itself if dim and self are
            equal)
        """
        if self.name != dim.name:
            raise DimensionMismatchError("Dimensions don't match")

        if self.values == dim.values:
            return self
        index = np.array([v in dim.values for v in self.values])
        if np.all(index):
            return self
        elif index.sum() == len(dim):
            return dim
        else:
            return self[index]


class Scalar(Dimension):
    """Scalar dimension

    Parameters
    ----------
    name : str
        Name fo the dimension.
    values : array_like
        Scalar value for each sample of the dimension.
    unit : str (optional)
        Unit of the values.
    tick_format : str (optional)
        Format string for formatting axis tick labels ('%'-format, e.g. '%.0f'
        to round to nearest integer).
    connectivity : 'grid' | 'none' | array of int, (n_edges, 2)
        Connectivity between elements. Set to ``"none"`` for no connections or 
        ``"grid"`` to use adjacency in the sequence of elements as connection. 
        Set to :class:`numpy.ndarray` to specify custom connectivity. The array
        should be of shape (n_edges, 2), and each row should specify one 
        connection [i, j] with i < j, with rows sorted in ascending order. If
        the array's dtype is uint32, property checks are disabled to improve 
        efficiency.
    """
    _default_connectivity = 'grid'

    def __init__(self, name, values, unit=None, tick_format=None, connectivity='grid'):
        values = np.asarray(values)
        if values.ndim != 1:
            raise ValueError(f"values.shape={values.shape}, needs to be one-dimensional")
        elif np.any(np.diff(values) <= 0):
            raise ValueError("Values for Scalar must increase monotonically")
        elif tick_format and '%' not in tick_format:
            raise ValueError(f"tick_format={tick_format}, needs to include '%'")
        self.values = values
        self.unit = unit
        self._axis_unit = unit
        self.tick_format = tick_format
        Dimension.__init__(self, name, connectivity)

    def __getstate__(self):
        out = Dimension.__getstate__(self)
        out.update(values=self.values, unit=self.unit,
                   tick_format=self.tick_format)
        return out

    def __setstate__(self, state):
        # backwards compatibility
        if 'connectivity' not in state:
            state['connectivity'] = None
            state['connectivity_type'] = 'grid'
        Dimension.__setstate__(self, state)
        self.values = state['values']
        self.unit = self._axis_unit = state.get('unit')
        self.tick_format = state.get('tick_format')

    def __repr__(self):
        args = [repr(self.name), array_repr(self.values)]
        if self.unit is not None or self.tick_format is not None:
            args.append(repr(self.unit))
        if self.tick_format is not None:
            args.append(repr(self.tick_format))
        return "%s(%s)" % (self.__class__.__name__, ', '.join(args))

    def __len__(self):
        return len(self.values)

    def __eq__(self, other):
        return (Dimension.__eq__(self, other) and
                np.array_equal(self.values, other.values))

    def __getitem__(self, index):
        if isinstance(index, Integral):
            return self.values[index]
        return self.__class__(self.name, self.values[index], self.unit,
                              self.tick_format, self._subgraph(index))

    def _as_scalar_array(self):
        return self.values

    def _axis_data(self):
        return self.values

    def _axis_format(self, scalar, label):
        if scalar:
            if self.tick_format:
                fmt = FormatStrFormatter(self.tick_format)
            else:
                fmt = None
        elif self.tick_format:
            fmt = IndexFormatter([self.tick_format % v for v in self.values])
        else:
            fmt = IndexFormatter(self.values)
        return (fmt,
                None if scalar else FixedLocator(np.arange(len(self)), 10),
                self._axis_label(label))

    def _bin(
            self,
            start: float = None,
            stop: float = None,
            step: int = None,  # -> step in dim space
            nbins: int = None,  # -> equally divide in array space
    ) -> (list, 'Scalar'):

        islice = self._array_index_for_slice(start, stop, step)
        istart = 0 if islice.start is None else islice.start
        istop = None if islice.stop is None else islice.stop
        start = self.values[0] if istart is None else self.values[istart]
        stop = None if istop is None else self.values[istop]
        if nbins is not None:
            if istop is None:
                istop = len(self)
            n_source_steps = istop - istart
            if n_source_steps % nbins != 0:
                raise ValueError(f"nbins={nbins!r}: length {n_source_steps} {self.name} can not be divided equally")
            istep = int(n_source_steps / nbins)
            edges = list(self.values[istart:istop:istep])
            # values for new Dimension
            if istep % 2:
                loc = np.arange(istart + istep / 2, istep, istop)
                out_values = np.interp(loc, np.arange(len(self.values)), self.values)
            else:
                out_values = self.values[istart + istep // 2: istop: istep]
        else:
            if stop is None:
                n_bins_fraction = (self[-1] - start) / step
                n_bins = int(ceil(n_bins_fraction))
                # if the last value would fall into a new bin
                if n_bins == n_bins_fraction:
                    n_bins += 1
            else:
                n_bins = int(ceil((stop - start) / step))

            # new dimensions
            dim_start = start + step / 2
            dim_stop = dim_start + n_bins * step
            out_values = np.arange(dim_start, dim_stop, step)
            edges = [start + n * step for n in range(n_bins)]
        edges.append(stop)
        out_dim = Scalar(self.name, out_values, self.unit, self.tick_format)
        return edges, out_dim

    def _cluster_properties(self, x):
        """Find cluster properties for this dimension

        Parameters
        ----------
        x : array of bool, (n_clusters, len(self))
            The cluster extents, with different clusters stacked along the
            first axis.

        Returns
        -------
        cluster_properties : None | Dataset
            A dataset with variables describing cluster properties.
        """
        ds = Dataset()
        where = [np.flatnonzero(cluster) for cluster in x]
        ds['%s_min' % self.name] = Var([self.values[w[0]] for w in where])
        ds['%s_max' % self.name] = Var([self.values[w[-1]] for w in where])
        return ds

    @classmethod
    def _concatenate(cls, scalars):
        "Concatenate multiple Scalar instances"
        scalars = tuple(scalars)
        attrs = {}
        for attr in ('name', 'unit', 'tick_format'):
            values = {getattr(s, attr) for s in scalars}
            if len(values) > 1:
                raise DimensionMismatchError(
                    "Trying to concatenate %s dimensions with different %ss: "
                    "%s" % (cls.__name__, attr, values))
            attrs[attr] = values.pop()
        values = np.concatenate(tuple(s.values for s in scalars))
        return cls(attrs['name'], values, attrs['unit'], attrs['tick_format'])

    def _array_index(self, arg):
        if isinstance(arg, self.__class__):
            s_idx, a_idx = np.nonzero(self.values[:, None] == arg.values)
            return s_idx[np.argsort(a_idx)]
        elif np.isscalar(arg):
            try:
                return digitize_index(arg, self.values, 0.3)
            except IndexError as error:
                raise IndexError(f"{error.args[0]}: Ambiguous index for {self._dimname()}")
        elif isinstance(arg, np.ndarray) and arg.dtype.kind == self.values.dtype.kind:
            if np.setdiff1d(arg, self.values):
                raise IndexError("Index %r includes values not in dimension: %s" %
                                 (arg, np.setdiff1d(arg, self.values)))
            return np.digitize(arg, self.values, True)
        else:
            return Dimension._array_index(self, arg)

    def _array_index_for_slice(self, start, stop=None, step=None):
        if start is not None:
            start = digitize_slice_endpoint(start, self.values)
        if stop is not None:
            stop = digitize_slice_endpoint(stop, self.values)
        return slice(start, stop, step)

    def _dim_index(self, index):
        if np.isscalar(index):
            return self.values[index]
        else:
            return Dimension._dim_index(self, index)

    def intersect(self, dim, check_dims=False):
        """Create a dimension object that is the intersection with dim

        Parameters
        ----------
        dim : type(self)
            Dimension to intersect with.
        check_dims : bool
            Check dimensions for consistency (not applicaple to this subclass).

        Returns
        -------
        intersection : type(self)
            The intersection with dim (returns itself if dim and self are
            equal)
        """
        if self.name != dim.name:
            raise DimensionMismatchError("Dimensions don't match")

        if np.all(self.values == dim.values):
            return self
        index = np.in1d(self.values, dim.values)
        if np.all(index):
            return self
        elif index.sum() == len(dim):
            return dim
        return self[index]


# for unpickling backwards compatibility
Ordered = Scalar


class Sensor(Dimension):
    """Dimension class for representing sensor information

    Parameters
    ----------
    locs : array_like  (n_sensor, 3)
        list of sensor locations in ALS coordinates, i.e., for each sensor a
        ``(anterior, left, superior)`` coordinate triplet.
    names : list of str
        Sensor names, same order as ``locs`` (default is ``['0', '1', '2',
        ...]``).
    sysname : str
        Name of the sensor system.
    proj2d : str
        Default 2d projection (default is ``'z-root'``; for options see notes
        below).
    connectivity : str | list of (str, str) | array of int, (n_edges, 2)
        Connectivity between elements. Can be specified as:

        - ``"none"`` for no connections
        - ``"grid"`` to use adjacency in the sensor names
        - list of connections (e.g., ``[('OZ', 'O1'), ('OZ', 'O2'), ...]``)
        - :class:`numpy.ndarray` of int, shape (n_edges, 2), to specify
          connections in terms of indices. Each row should specify one
          connection ``[i, j]`` with ``i < j``. If the array's dtype is
          ``uint32``, property checks are disabled to improve efficiency.

    Attributes
    ----------
    channel_idx : dict
        Dictionary mapping channel names to indexes.
    locs : array  (n_sensors, 3)
        Spatial position of all sensors.
    names : list of str
        Ordered list of sensor names.
    x, y, z : array  (n_sensors,)
        Sensor position x, y and z coordinates.

    Notes
    -----
    The following are possible 2d-projections:

    ``'z root'``:
        the radius of each sensor is set to equal the root of the vertical
        distance from the top of the net.
    ``'cone'``:
        derive x/y coordinate from height based on a cone transformation.
    ``'lower cone'``:
        only use cone for sensors with z < 0.
    Axis and sign :
        For example, ``x+`` for anterior, ``x-`` for posterior.

    Examples
    --------
    >>> locs = [(0,  0,   0),
    ...         (0, -.25, -.45)]
    >>> sensor_dim = Sensor(locs, names=["Cz", "Pz"])
    """
    _default_connectivity = 'custom'
    _proj_aliases = {'left': 'x-', 'right': 'x+', 'back': 'y-', 'front': 'y+',
                     'top': 'z+', 'bottom': 'z-'}

    def __init__(self, locs, names=None, sysname=None, proj2d='z root', connectivity='none'):
        # 'z root' transformation fails with 32-bit floats
        self.locs = locs = np.asarray(locs, dtype=np.float64)
        n = len(locs)
        if locs.shape != (n, 3):
            raise ValueError("locs needs to have shape (n_sensors, 3), got "
                             "array of shape %s" % (locs.shape,))
        self.sysname = sysname
        self.default_proj2d = self._interpret_proj(proj2d)

        if names is None:
            names = [str(i) for i in range(n)]
        elif len(names) != n:
            raise ValueError("Length mismatch: got %i locs but %i names" %
                             (n, len(names)))
        self.names = Datalist(names)
        Dimension.__init__(self, 'sensor', connectivity)
        self._init_secondary()

    def _coerce_connectivity(self, connectivity):
        if isinstance(connectivity[0][0], str):
            return connectivity_from_name_pairs(connectivity, self.names, allow_missing=True)
        else:
            return Dimension._coerce_connectivity(self, connectivity)

    def _init_secondary(self):
        self.x = self.locs[:, 0]
        self.y = self.locs[:, 1]
        self.z = self.locs[:, 2]

        self.channel_idx = {name: i for i, name in enumerate(self.names)}
        # short names
        prefix = os.path.commonprefix(self.names)
        if prefix:
            n_pf = len(prefix)
            self.channel_idx.update({name[n_pf:]: i for i, name in
                                     enumerate(self.names)})

        # cache for transformed locations
        self._transformed = {}

    def __getstate__(self):
        out = Dimension.__getstate__(self)
        out.update(proj2d=self.default_proj2d, locs=self.locs, names=self.names,
                   sysname=self.sysname)
        return out

    def __setstate__(self, state):
        if 'name' not in state:
            state['name'] = 'sensor'
            state['connectivity_type'] = 'custom'
        Dimension.__setstate__(self, state)
        self.locs = state['locs']
        self.names = state['names']
        self.sysname = state['sysname']
        self.default_proj2d = state['proj2d']
        self._init_secondary()

    def __repr__(self):
        return "<Sensor n=%i, name=%r>" % (len(self), self.sysname)

    def __len__(self):
        return len(self.locs)

    def __eq__(self, other):  # Based on equality of sensor names
        return (Dimension.__eq__(self, other) and len(self) == len(other) and
                all(n == no for n, no in zip(self.names, other.names)))

    def __getitem__(self, index):
        if np.isscalar(index):
            return self.names[index]
        else:
            return Sensor(self.locs[index], self.names[index], self.sysname,
                          self.default_proj2d, self._subgraph(index))

    def _as_uv(self):
        return Factor(self.names, name=self.name)

    def _axis_format(self, scalar, label):
        return (IndexFormatter(self.names),
                FixedLocator(np.arange(len(self)), 10),
                self._axis_label(label))

    def _cluster_properties(self, x):
        """Find cluster properties for this dimension

        Parameters
        ----------
        x : array of bool  (n_clusters, n_sensors)
            The cluster extents, with different clusters stacked along the
            first axis.

        Returns
        -------
        cluster_properties : None | Dataset
            A dataset with variables describing cluster properties.
        """
        return Dataset(('n_sensors', Var(x.sum(1))))

    def _array_index(self, arg):
        "Convert a dimension-semantic index to an array-like index"
        if isinstance(arg, str):
            return self.channel_idx[arg]
        elif isinstance(arg, Sensor):
            return np.array([self.names.index(name) for name in arg.names])
        elif isinstance(arg, Integral) or (isinstance(arg, np.ndarray) and
                                           arg.dtype.kind == 'i'):
            return arg
        else:
            return super(Sensor, self)._array_index(arg)

    def _array_index_to(self, other):
        "Int index to access data from self in an order consistent with other"
        try:
            return np.array([self.names.index(name) for name in other.names])
        except ValueError:
            missing = (name for name in other.names if name not in self.names)
            raise IndexError(f"{other}: contains different sensors {', '.join(missing)}")

    def _dim_index(self, index):
        if np.isscalar(index):
            return self.names[index]
        else:
            return Dimension._dim_index(self, index)

    def _generate_connectivity(self):
        raise RuntimeError("Sensor connectivity is not defined. Use "
                           "Sensor.set_connectivity().")

    @classmethod
    def from_xyz(cls, path=None, **kwargs):
        """Create a Sensor instance from a text file with xyz coordinates"""
        locs = []
        names = []
        with open(path) as f:
            l1 = f.readline()
            n = int(l1.split()[0])
            for line in f:
                elements = line.split()
                if len(elements) == 4:
                    x, y, z, name = elements
                    x = float(x)
                    y = float(y)
                    z = float(z)
                    locs.append((x, y, z))
                    names.append(name)
        assert len(names) == n
        return cls(locs, names, **kwargs)

    @classmethod
    def from_sfp(cls, path=None, **kwargs):
        """Create a Sensor instance from an sfp file"""
        locs = []
        names = []
        for line in open(path):
            elements = line.split()
            if len(elements) == 4:
                name, x, y, z = elements
                x = float(x)
                y = float(y)
                z = float(z)
                locs.append((x, y, z))
                names.append(name)
        return cls(locs, names, **kwargs)

    @classmethod
    def from_lout(cls, path=None, transform_2d=None, **kwargs):
        """Create a Sensor instance from a ``*.lout`` file"""
        kwargs['transform_2d'] = transform_2d
        locs = []
        names = []
        with open(path) as fileobj:
            fileobj.readline()
            for line in fileobj:
                w, x, y, t, f, name = line.split('\t')
                x = float(x)
                y = float(y)
                locs.append((x, y, 0))
                names.append(name)
        return cls(locs, names, **kwargs)

    @classmethod
    def from_montage(cls, montage):
        """Create Sensor dimension from :mod:`mne` :class:`~mne.channels.Montage`

        Parameters
        ----------
        montage : str | mne.Montage
            Montage, or name to load a standard montage (see
            :func:`mne.channels.read_montage`).
        """
        if isinstance(montage, str):
            montage = mne.channels.read_montage(montage)
        return cls(montage.pos, montage.ch_names, montage.kind)

    def _interpret_proj(self, proj):
        if proj == 'default':
            return self.default_proj2d
        elif proj in self._proj_aliases:
            return self._proj_aliases[proj]
        elif proj is None:
            return 'z+'
        else:
            return proj

    def get_connectivity(self):
        """Sensor connectivity as list of ``(name_1, name_2)``"""
        if self._connectivity_type != 'custom':
            raise ValueError("No custom connectivity")
        pairs = [(self.names[a], self.names[b]) for a, b in self._connectivity]
        sorted_pairs = [tuple(sorted(pair)) for pair in pairs]
        return sorted(sorted_pairs)

    def get_locs_2d(self, proj='default', extent=1, frame=0, invisible=True):
        """Compute a 2 dimensional projection of the sensor locations

        Parameters
        ----------
        proj : str
            How to transform 3d coordinates into a 2d map; see class
            documentation for options.
        extent : int
            coordinates will be scaled with minimum value 0 and maximum value
            defined by the value of ``extent``.
        frame : scalar
            Distance of the outermost points from 0 and ``extent`` (default 0).
        invisible : bool
            Return invisible sensors (sensors that would be hidden behind the
            head; default True).

        Returns
        -------
        locs_2d : array (n_sensor, 2)
            Sensor position 2d projection in x, y coordinates.
        """
        proj = self._interpret_proj(proj)

        index = (proj, extent, frame)
        if index in self._transformed:
            locs2d = self._transformed[index]
        else:
            locs2d = self._make_locs_2d(proj, extent, frame)
            self._transformed[index] = locs2d

        if not invisible:
            visible = self._visible_sensors(proj)
            if visible is not None:
                return locs2d[visible]
        return locs2d

    @LazyProperty
    def _sphere_fit(self):
        """Fit the 3d sensor locations to a sphere

        Returns
        -------
        params : tuple
            Radius and center (r, cx, cy, cz).
        """
        locs = self.locs

        # error function
        def err(params):
            # params: [r, cx, cy, cz]
            out = np.sum((locs - params[1:]) ** 2, 1)
            out -= params[0] ** 2
            return out

        # initial guess of sphere parameters (radius and center)
        center_0 = np.mean(locs, 0)
        r_0 = np.mean(np.sqrt(np.sum((locs - center_0) ** 2, axis=1)))
        start_params = np.hstack((r_0, center_0))
        # do fit
        estimate, _ = leastsq(err, start_params)
        return tuple(estimate)

    def _make_locs_2d(self, proj, extent, frame):
        if proj in ('cone', 'lower cone', 'z root'):
            r, cx, cy, cz = self._sphere_fit

            # center the sensor locations based on the sphere and scale to
            # radius 1
            sphere_center = np.array((cx, cy, cz))
            locs3d = self.locs - sphere_center
            locs3d /= r

            # implement projection
            locs2d = np.copy(locs3d[:, :2])

            if proj == 'cone':
                locs2d[:, [0, 1]] *= (1 - locs3d[:, [2]])
            elif proj == 'lower cone':
                lower_half = locs3d[:, 2] < 0
                if any(lower_half):
                    locs2d[lower_half] *= (1 - locs3d[lower_half][:, [2]])
            elif proj == 'z root':
                z = locs3d[:, 2]
                z_dist = (z.max() + 0.01) - z  # distance form top (add a small
                # buffer so that multiple points at z-max don't get stuck
                # together)
                r = np.sqrt(z_dist)  # desired 2d radius
                r_xy = np.sqrt(np.sum(locs3d[:, :2] ** 2, 1))  # current radius in xy
                idx = (r_xy != 0)  # avoid zero division
                F = r[idx] / r_xy[idx]  # stretching Factor accounting for current r
                locs2d[idx, :] *= F[:, None]
        else:
            match = re.match('([xyz])([+-])', proj)
            if match:
                ax, sign = match.groups()
                if ax == 'x':
                    locs2d = np.copy(self.locs[:, 1:])
                    if sign == '-':
                        locs2d[:, 0] *= -1
                elif ax == 'y':
                    locs2d = np.copy(self.locs[:, [0, 2]])
                    if sign == '+':
                        locs2d[:, 0] *= -1
                elif ax == 'z':
                    locs2d = np.copy(self.locs[:, :2])
                    if sign == '-':
                        locs2d[:, 1] *= -1
            else:
                raise ValueError("invalid proj kwarg: %r" % proj)

        # correct extent
        if extent:
            locs2d -= np.min(locs2d, axis=0)  # move to bottom left
            locs2d /= (np.max(locs2d) / extent)  # scale to extent
            locs2d += (extent - np.max(locs2d, axis=0)) / 2  # center
            if frame:
                locs2d *= (1 - 2 * frame)
                locs2d += frame

        return locs2d

    def _topomap_outlines(self, proj):
        "Outline argument for mne-python topomaps"
        proj = self._interpret_proj(proj)
        if proj in ('cone', 'lower cone', 'z root', 'z+'):
            return 'top'
        else:
            return None

    def _visible_sensors(self, proj):
        "Create an index for sensors that are visible under a given proj"
        proj = self._interpret_proj(proj)
        match = re.match('([xyz])([+-])', proj)
        if match:
            # logger.debug("Computing sensors visibility for %s" % proj)
            ax, sign = match.groups()

            # depth:  + = closer
            depth = self.locs[:, 'xyz'.index(ax)]
            if sign == '-':
                depth = -depth

            locs2d = self.get_locs_2d(proj)

            n_vertices = len(locs2d)
            all_vertices = np.arange(n_vertices)
            out = np.ones(n_vertices, bool)

            # find duplicate points
            # TODO OPT:  use pairwise distance
            x, y = np.where(cdist(locs2d, locs2d) == 0)
            duplicate_vertices = ((v1, v2) for v1, v2 in zip(x, y) if v1 < v2)
            for v1, v2 in duplicate_vertices:
                if depth[v1] > depth[v2]:
                    out[v2] = False
                    # logger.debug("%s is hidden behind %s" % (self.names[v2], self.names[v1]))
                else:
                    out[v1] = False
                    # logger.debug("%s is hidden behind %s" % (self.names[v1], self.names[v2]))
            use_vertices = all_vertices[out]  # use for hull check

            hull = ConvexHull(locs2d[use_vertices])
            hull_vertices = use_vertices[hull.vertices]

            # for each point:
            # find the closest point on the hull
            # determine whether it's in front or behind
            non_hull_vertices = np.setdiff1d(use_vertices, hull_vertices, True)

            hull_locs = locs2d[hull_vertices]
            non_hull_locs = locs2d[non_hull_vertices]
            dists = cdist(non_hull_locs, hull_locs)

            closest = np.argmin(dists, 1)
            hide_non_hull_vertices = depth[non_hull_vertices] < depth[hull_vertices][closest]
            hide_vertices = non_hull_vertices[hide_non_hull_vertices]
            # logger.debug("%s are hidden behind convex hull" % ' '.join(self.names[hide_vertices]))
            out[hide_vertices] = False
            return out
        else:
            return None

    def index(self, include=None, exclude=None):
        """Construct an index for specified sensors

        Parameters
        ----------
        include : list of str, int
            Sensors to exclude (by name or index).
        exclude : list of str, int
            Sensors to exclude (by name or index).

        Returns
        -------
        index : NDVar
            Boolean :class:`NDVar` indexing selected channels.
        """
        if include is None == exclude is None:
            raise TypeError(f"inclide={include!r}, exclude={exclude!r}: Need to specify exactly one of include, exclude")
        elif include is not None:
            if isinstance(include, str):
                include = [include]
            index = np.zeros(len(self), dtype=bool)
            for ch in include:
                try:
                    index[self.channel_idx[ch]] = True
                except KeyError:
                    raise ValueError(f"Invalid channel name: {ch!r}")
            return NDVar(index, (self,))
        else:
            return ~self.index(exclude)

    def _normalize_sensor_names(self, names, missing='raise'):
        "Process a user-input list of sensor names"
        valid_chs = set()
        missing_chs = set()
        for name in names:
            if isinstance(name, Integral):
                name = '%03i' % name

            if name.isdigit():
                if name in self.names:
                    valid_chs.add(name)
                    continue
                else:
                    name = 'MEG %s' % name

            if name in self.names:
                valid_chs.add(name)
            else:
                missing_chs.add(name)

        if missing == 'raise':
            if missing_chs:
                raise ValueError(f"The following channels are not in the raw data: {', '.join(sorted(missing_chs))}")
            return sorted(valid_chs)
        elif missing == 'return':
            return sorted(valid_chs), missing_chs
        else:
            raise ValueError(f"missing={missing!r}")

    def intersect(self, dim, check_dims=True):
        """Create a Sensor dimension that is the intersection with dim

        Parameters
        ----------
        dim : Sensor
            Sensor dimension to intersect with.
        check_dims : bool
            Check dimensions for consistency (e.g., channel locations). Default
            is ``True``. Set to ``False`` to intersect channels based on names
            only and ignore mismatch between locations for channels with the
            same name.

        Returns
        -------
        sensor : Sensor
            The intersection with dim (returns itself if dim and self are
            equal)
        """
        if self.name != dim.name:
            raise DimensionMismatchError("Dimensions don't match")

        n_self = len(self)
        names = set(self.names)
        names.intersection_update(dim.names)
        n_intersection = len(names)
        if n_intersection == n_self:
            return self
        elif n_intersection == len(dim.names):
            return dim

        index = np.array([name in names for name in self.names])
        if check_dims:
            other_index = np.array([name in names for name in dim.names])
            if not np.all(self.locs[index] == dim.locs[other_index]):
                raise ValueError("Sensor locations don't match between "
                                 "dimension objects")
        return self[index]

    def neighbors(self, connect_dist):
        """Find neighboring sensors.

        Parameters
        ----------
        connect_dist : scalar
            For each sensor, neighbors are defined as those sensors within
            ``connect_dist`` times the distance of the closest neighbor.

        Returns
        -------
        neighbors : dict
            Dictionaries whose keys are sensor indices, and whose values are
            lists of neighbors represented as sensor indices.
        """
        nb = {}
        pd = pdist(self.locs)
        pd = squareform(pd)
        n = len(self)
        for i in range(n):
            d = pd[i, np.arange(n)]
            d[i] = d.max()
            idx = np.nonzero(d < d.min() * connect_dist)[0]
            nb[i] = idx

        return nb

    def set_connectivity(self, neighbors=None, connect_dist=None):
        """Define the sensor connectivity through neighbors or distance

        Parameters
        ----------
        neighbors : sequence of (str, str)
            A list of connections, all assumed to be bidirectional.
        connect_dist : None | scalar
            For each sensor, neighbors are defined as those sensors within
            ``connect_dist`` times the distance of the closest neighbor.
            e.g., 1.75 or 1.6
        """
        pairs = set()
        if neighbors is not None and connect_dist is not None:
            raise TypeError("Can only specify either neighbors or connect_dist")
        elif connect_dist is None:
            for src, dst in neighbors:
                a = self.names.index(src)
                b = self.names.index(dst)
                if a < b:
                    pairs.add((a, b))
                else:
                    pairs.add((b, a))
        else:
            nb = self.neighbors(connect_dist)
            for k, vals in nb.items():
                for v in vals:
                    if k < v:
                        pairs.add((k, v))
                    else:
                        pairs.add((v, k))

        self._connectivity = np.array(sorted(pairs), np.uint32)
        self._connectivity_type = 'custom'

    def set_sensor_positions(self, pos, names=None):
        """Set the sensor positions

        Parameters
        ----------
        pos : array (n_locations, 3) | MNE Montage
            Array with 3 columns describing sensor locations (x, y, and z), or
            an MNE Montage object describing the sensor layout.
        names : None | list of str
            If locations is an array, names should specify a name
            corresponding to each entry.
        """
        # MNE Montage
        if hasattr(pos, 'pos') and hasattr(pos, 'ch_names'):
            if names is not None:
                raise TypeError("Can't specify names parameter with Montage")
            names = pos.ch_names
            pos = pos.pos
        elif names is not None and len(names) != len(pos):
            raise ValueError("Mismatch between number of locations (%i) and "
                             "number of names (%i)" % (len(pos), len(names)))

        if names is not None:
            missing = [name for name in self.names if name not in names]
            if missing:
                raise ValueError("The following sensors are missing: %r" % missing)
            index = np.array([names.index(name) for name in self.names])
            pos = pos[index]
        elif len(pos) != len(self.locs):
            raise ValueError("If names are not specified pos must specify "
                             "exactly one position per channel")
        self.locs[:] = pos

    @property
    def values(self):
        return self.names


def as_sensor(obj):
    "Coerce to Sensor instance"
    if isinstance(obj, Sensor):
        return obj
    elif isinstance(obj, NDVar) and obj.has_dim('sensor'):
        return obj.sensor
    elif hasattr(obj, 'pos') and hasattr(obj, 'ch_names') and hasattr(obj, 'kind'):
        return Sensor(obj.pos, obj.ch_names, obj.kind)
    else:
        raise TypeError("Can't get sensors from %r" % (obj,))


def _point_graph(coords, dist_threshold):
    "Connectivity graph for points based on distance"
    n = len(coords)
    dist = pdist(coords)

    # construct vertex pairs corresponding to dist
    graph = np.empty((len(dist), 2), np.uint32)
    i0 = 0
    for vert, di in enumerate(range(n - 1, 0, -1)):
        i1 = i0 + di
        graph[i0:i1, 0] = vert
        graph[i0:i1, 1] = np.arange(vert + 1, n)
        i0 = i1

    return graph[dist < dist_threshold]


def _matrix_graph(matrix):
    "Create connectivity from matrix"
    coo = matrix.tocoo()
    assert np.all(coo.data)
    edges = {(min(a, b), max(a, b)) for a, b in zip(coo.col, coo.row) if a != b}
    return np.array(sorted(edges), np.uint32)


def _tri_graph(tris):
    """Create connectivity graph from triangles

    Parameters
    ----------
    tris : array_like, (n_tris, 3)
        Triangles.

    Returns
    -------
    edges : array (n_edges, 2)
        All edges between vertices of tris.
    """
    pairs = set()
    for tri in tris:
        a, b, c = sorted(tri)
        pairs.add((a, b))
        pairs.add((a, c))
        pairs.add((b, c))
    return np.array(sorted(pairs), np.uint32)


def _mne_tri_soure_space_graph(source_space, vertices_list):
    "Connectivity graph for a triangulated mne source space"
    i = 0
    graphs = []
    for ss, verts in zip(source_space, vertices_list):
        if len(verts) == 0:
            continue

        tris = ss['use_tris']
        if tris is None:
            raise ValueError("Connectivity unavailable. The source space does "
                             "not seem to be an ico source space.")

        # graph for the whole source space
        src_vertices = ss['vertno']
        graph = _tri_graph(tris)

        # select relevant edges
        if not np.array_equal(verts, src_vertices):
            if not np.all(np.in1d(verts, src_vertices)):
                raise RuntimeError("Not all vertices are in the source space")
            edge_in_use = np.logical_and(np.in1d(graph[:, 0], verts),
                                         np.in1d(graph[:, 1], verts))
            graph = graph[edge_in_use]

        # reassign vertex ids based on present vertices
        if len(verts) != verts.max() + 1:
            graph = (np.digitize(graph.ravel(), verts, True)
                     .reshape(graph.shape).astype(np.uint32))

        # account for index of previous source spaces
        if i > 0:
            graph += i
        i += len(verts)

        graphs.append(graph)
    return np.vstack(graphs)


class SourceSpaceBase(Dimension):
    kind = None
    _default_parc = 'aparc'
    _default_connectivity = 'custom'
    _ANNOT_PATH = os.path.join('{subjects_dir}', '{subject}', 'label', '{hemi}.{parc}.annot')
    _vertex_re = re.compile(r'([RL])(\d+)')

    def __init__(self, vertices, subject, src, subjects_dir, parc, connectivity, name, filename):
        self.vertices = vertices
        self.subject = subject
        self.src = src
        self._subjects_dir = subjects_dir
        self._filename = filename
        self._init_secondary()
        Dimension.__init__(self, name, connectivity)

        # parc
        if parc is None or parc is False:
            self.parc = None
        elif isinstance(parc, Factor):
            if len(parc) != self._n_vert:
                raise ValueError(f"parc={parc!r}: wrong length {len(parc)} for SourceSpace with {self._n_vert} vertices")
            self.parc = parc
        elif isinstance(parc, str):
            self.parc = self._read_parc(parc)
        else:
            raise TypeError(f"parc={parc!r}: needs to be Factor or string")

    def _read_parc(self, parc: str) -> Factor:
        raise NotImplementedError(f"parc={parc!r}: can't set parcellation from annotation files for {self.__class__.__name__}. Consider using a Factor instead.")

    def _init_secondary(self):
        self._n_vert = sum(len(v) for v in self.vertices)
        # The source-space type is needed to determine connectivity
        m = SRC_RE.match(self.src)
        if not m:
            raise ValueError(f"src={self.src!r}; needs to be '{self.kind}-i' where i is an integer")
        kind, grade, suffix = m.groups()
        if kind != self.kind:
            raise ValueError(f'src={self.src!r}: {self.__class__.__name__} is wrong class')
        self.grade = int(grade)

    @classmethod
    def from_file(cls, subjects_dir, subject, src, parc=None):
        """SourceSpace dimension from MNE source space file"""
        if parc is None:
            parc = cls._default_parc
        filename = Path(subjects_dir) / subject / 'bem' / f'{subject}-{src}-src.fif'
        source_spaces = mne.read_source_spaces(str(filename))
        return cls.from_mne_source_spaces(source_spaces, src, subjects_dir, parc)

    @classmethod
    def from_mne_source_spaces(cls, source_spaces, src, subjects_dir,
                               parc='aparc', label=None):
        """SourceSpace dimension from MNE SourceSpaces object"""
        if label is None:
            vertices = [ss['vertno'] for ss in source_spaces]
        else:
            vertices, _ = label_src_vertno_sel(label, source_spaces)

        return cls(vertices, source_spaces[0]['subject_his_id'], src,
                   subjects_dir, parc)

    @LazyProperty
    def subjects_dir(self):
        try:
            return mne.utils.get_subjects_dir(self._subjects_dir, True)
        except KeyError:
            raise TypeError("subjects_dir was neither specified on SourceSpace "
                            "dimension nor as environment variable")

    def _sss_path(self, subjects_dir=None):
        if subjects_dir is None:
            subjects_dir = self.subjects_dir
        return Path(subjects_dir) / self.subject / 'bem' / self._filename.format(subject=self.subject, src=self.src)

    def __getstate__(self):
        state = Dimension.__getstate__(self)
        state.update(vertno=self.vertices, subject=self.subject, src=self.src, subjects_dir=self._subjects_dir, parc=self.parc, filename=self._filename)
        return state

    def __setstate__(self, state):
        if 'name' not in state:
            state['name'] = 'source'
            state['connectivity_type'] = 'custom'
        Dimension.__setstate__(self, state)
        self.vertices = state['vertno']
        self.subject = state['subject']
        self.src = state['src']
        self._subjects_dir = state['subjects_dir']
        self._filename = state.get('filename', '{subject}-{src}-src.fif')
        self.parc = state['parc']
        self._init_secondary()

    def __repr__(self):
        out = "<" + self.__class__.__name__
        if self.name != 'source':
            out += ' ' + self.name
        vert_repr = ', '.join(str(len(v)) for v in self.vertices)
        out += " [%s], %r" % (vert_repr, self.subject)
        if self.src is not None:
            out += ', %r' % self.src
        if self.parc is not None:
            out += ', parc=%s' % self.parc.name
        return out + '>'

    def __len__(self):
        return self._n_vert

    def __eq__(self, other):
        return (
            Dimension.__eq__(self, other) and
            self.subject == other.subject and
            self.src == other.src and
            len(self) == len(other) and
            all(np.array_equal(s, o) for s, o in zip(self.vertices, other.vertices))
        )

    def _assert_same_base(self, other):
        "Assert that ``other`` is based on the same source space"
        if self.subject != other.subject:
            raise IndexError(f"Source spaces can not be compared because they are defined on different MRI subjects ({self.subject} vs {other.subject}). Consider using eelbrain.morph_source_space().")
        elif self.src != other.src:
            raise IndexError(f"Source spaces of different types ({self.src} vs {other.src})")
        elif self.subjects_dir != other.subjects_dir:
            raise IndexError(f"Source spaces have differing subjects_dir:\n{self.subjects_dir}\n{other.subjects_dir}")

    def __getitem__(self, index):
        raise NotImplementedError

    def _axis_format(self, scalar, label):
        return (FormatStrFormatter('%i'),
                FixedLocator(np.arange(len(self)), 10),
                self._axis_label(label))

    def _copy(self, subject=None, parc=None):
        if subject is None:
            subject = self.subject
        if parc is None:
            parc = self.parc
        return self.__class__(self.vertices, subject, self.src, self.subjects_dir, parc, self._subgraph(), self.name, self._filename)

    def _cluster_properties(self, x):
        """Find cluster properties for this dimension

        Parameters
        ----------
        x : array of bool, (n_clusters, len(self))
            The cluster extents, with different clusters stacked along the
            first axis.

        Returns
        -------
        cluster_properties : Dataset
            A dataset with variables describing cluster properties along this
            dimension: "n_sources".
        """
        if np.any(np.sum(x, 1) == 0):
            raise ValueError("Empty cluster")

        ds = Dataset()

        # no clusters
        if len(x) == 0:
            ds['n_sources'] = Var([])
            ds['hemi'] = Factor([])
            if self.parc is not None:
                ds['location'] = Factor([])
            return ds

        # n sources
        ds['n_sources'] = Var(x.sum(1))

        # location
        if self.parc is not None:
            locations = []
            for x_ in x:
                parc_entries = self.parc[x_]
                argmax = np.argmax(np.bincount(parc_entries.x))
                location = parc_entries[argmax]
                locations.append(location)
            ds['location'] = Factor(locations)

        return ds

    def _distances(self):
        "Surface distances between source space vertices"
        dist = -np.ones((self._n_vert, self._n_vert))
        sss = self.get_source_space()
        i0 = 0
        for vertices, ss in zip(self.vertices, sss):
            if ss['dist'] is None:
                path = self._sss_path()
                raise RuntimeError(
                    f"Source space does not contain source distance "
                    f"information. To add distance information, run:\n"
                    f"src = mne.read_source_spaces({path!r})\n"
                    f"mne.add_source_space_distances(src)\n"
                    f"src.save({path!r}, overwrite=True)")
            i = i0 + len(vertices)
            dist[i0:i, i0:i] = ss['dist'][vertices, vertices[:, None]].toarray()
            i0 = i
        return dist

    def connectivity(self, disconnect_parc=False):
        """Create source space connectivity

        Parameters
        ----------
        disconnect_parc : bool
            Reduce connectivity to label-internal connections.

        Returns
        -------
        connetivity : array of int, (n_pairs, 2)
            array of sorted [src, dst] pairs, with all src < dts.
        """
        if self._n_vert == 0:
            return np.empty((0, 2), np.uint32)
        elif self._connectivity is None:
            if self.src is None or self.subject is None or self.subjects_dir is None:
                raise ValueError(
                    "In order for a SourceSpace dimension to provide "
                    "connectivity information it needs to be initialized with "
                    "src, subject and subjects_dir parameters")

            self._connectivity = connectivity = self._compute_connectivity()
            assert connectivity.max() < len(self)
        else:
            connectivity = self._connectivity

        if disconnect_parc:
            parc = self.parc
            if parc is None:
                raise RuntimeError("SourceSpace has no parcellation (use "
                                   ".set_parc())")
            idx = np.array([parc[s] == parc[d] for s, d in connectivity])
            connectivity = connectivity[idx]

        return connectivity

    def _compute_connectivity(self):
        raise NotImplementedError("Connectivity for %r source space" % self.kind)

    def circular_index(self, seeds, extent=0.05, name="globe"):
        """Return an index into all vertices closer than ``extent`` of a seed

        Parameters
        ----------
        seeds : array_like, (3,) | (n, 3)
            Seed location(s) around which to build index.
        extent : float
            Index vertices closer than this (in m in 3d space).
        name : str
            Name of the NDVar.

        Returns
        -------
        roi : NDVar  ('source',)
            Index into the spherical area around ``seeds``.
        """
        seeds = np.atleast_2d(seeds)
        dist = cdist(self.coordinates, seeds)
        mindist = np.min(dist, 1)
        x = mindist < extent
        dims = (self,)
        info = {'seeds': seeds, 'extent': extent}
        return NDVar(x, dims, info, name)

    @LazyProperty
    def coordinates(self):
        sss = self.get_source_space()
        coords = [ss['rr'][v] for ss, v in zip(sss, self.vertices)]
        return np.vstack(coords)

    @LazyProperty
    def normals(self):
        sss = self.get_source_space()
        normals = [ss['nn'][v] for ss, v in zip(sss, self.vertices)]
        return np.vstack(normals)

    def _array_index(self, arg, allow_vertex=True):
        if isinstance(arg, str):
            if self.parc is not None and arg in self.parc:
                return self.parc == arg
            elif allow_vertex:
                return self._array_index_for_vertex(arg)
            elif self.parc is None:
                raise IndexError(f"{arg!r}: {self.__class__.__name__} has no parcellation")
            else:
                raise IndexError(f"{arg!r}: {self.__class__.__name__} has no such label")
        elif isinstance(arg, Integral) or (isinstance(arg, np.ndarray) and arg.dtype.kind in 'ib'):
            return arg
        elif isinstance(arg, Sequence):
            if all(isinstance(v, str) for v in arg):
                if self.parc is not None and all(a in self.parc for a in arg):
                    return self.parc.isin(arg)
                elif allow_vertex:
                    return [self._array_index_for_vertex(v) for v in arg]
                else:
                    raise IndexError(f"{arg!r}")
            elif all(isinstance(v, INT_TYPES) for v in arg):
                return arg
            else:
                raise IndexError(f"{arg!r}")
        else:
            return Dimension._array_index(self, arg)

    def _array_index_for_vertex(self, vertex_desc):
        raise NotImplementedError(f"Index for {vertex_desc!r}")

    def _array_index_to(self, other):
        "Int index to access data from self in an order consistent with other"
        self._assert_same_base(other)
        if any(np.any(np.setdiff1d(o, s, True)) for s, o in zip(self.vertices, other.vertices)):
            raise IndexError(f"{other}: contains sources not in {self}")
        bool_index = np.hstack([np.in1d(s, o) for s, o in zip(self.vertices, other.vertices)])
        return np.flatnonzero(bool_index)

    def get_source_space(self, subjects_dir=None):
        "Read the corresponding MNE source space"
        if self.src is None:
            raise TypeError("Unknown source-space. Specify the src parameter "
                            "when initializing SourceSpace.")
        path = self._sss_path(subjects_dir)
        if not path.exists():
            raise IOError(
                f"Can't load source space because {path} does not exist; if "
                f"the MRI files for {self.subject} were moved, use "
                f"eelbrain.load.update_subjects_dir()")
        return mne.read_source_spaces(str(path))

    def index_for_label(self, label):
        """Return the index for a label

        Parameters
        ----------
        label : str | sequance of str
            One or several names of regions in the current parcellation.

        Returns
        -------
        index : NDVar of bool
            Index into the source space dim that corresponds to the label.
        """
        idx = self._array_index(label, allow_vertex=False)
        if isinstance(label, str):
            name = label
        elif isinstance(label, Sequence):
            name = '+'.join(label)
        elif isinstance(label, MNE_LABEL):
            name = label.name
        else:
            raise TypeError(f"{label!r}")
        return NDVar(idx, (self,), {}, name)

    def _is_superset_of(self, dim):
        self._assert_same_base(dim)
        return all(np.all(np.in1d(d, s)) for s, d in zip(self.vertices, dim.vertices))

    def index_into_dim(self, dim):
        if not self._is_superset_of(dim):
            raise ValueError(f"{dim}: Index source space has unknown vertices")
        index = np.hstack([np.in1d(s, d) for s, d in zip(self.vertices, dim.vertices)])
        return NDVar(index, (self,))

    def intersect(self, other, check_dims=True):
        """Create a Source dimension that is the intersection with dim

        Parameters
        ----------
        dim : Source
            Dimension to intersect with.
        check_dims : bool
            Check dimensions for consistency (not applicaple to this subclass).

        Returns
        -------
        intersection : Source
            The intersection with dim (returns itself if dim and self are
            equal)
        """
        self._assert_same_base(other)
        index = np.hstack([np.in1d(s, o) for s, o in zip(self.vertices, other.vertices)])
        return self[index]

    @property
    def values(self):
        raise NotImplementedError


class SourceSpace(SourceSpaceBase):
    """MNE surface-based source space

    Parameters
    ----------
    vertices : list of 2 int arrays
        The vertex identities of the dipoles in the source space (left and
        right hemisphere separately).
    subject : str
        The mri-subject name.
    src : str
        The kind of source space used (e.g., 'ico-4'; only ``ico`` is currently
        supported.
    subjects_dir : str
        The path to the subjects_dir (needed to locate the source space
        file).
    parc : None | str
        Add a parcellation to the source space to identify vertex location.
        Only applies to ico source spaces, default is 'aparc'.
    connectivity : 'grid' | 'none' | array of int, (n_edges, 2)
        Connectivity between elements. Set to ``"none"`` for no connections or
        ``"grid"`` to use adjacency in the sequence of elements as connection.
        Set to :class:`numpy.ndarray` to specify custom connectivity. The array
        should be of shape (n_edges, 2), and each row should specify one
        connection [i, j] with i < j, with rows sorted in ascending order. If
        the array's dtype is uint32, property checks are disabled to improve
        efficiency.
    name : str
        Dimension name (default ``"source"``).
    filename : str
        Filename template for the MNE source space file.

    Attributes
    ----------
    coordinates : array (n_sources, 3)
        Spatial coordinate for each source.
    normals : array (n_sources, 3)
        Orientation (direction) of each source.
    parc : Factor
        Parcellation (one label for each source).

    See Also
    --------
    VolumeSourceSpace : volume source space

    Notes
    -----
    besides numpy indexing, the following indexes are possible:

     - mne Label objects
     - 'lh' or 'rh' to select an entire hemisphere

    """
    kind = 'ico'

    def __init__(self, vertices, subject=None, src=None, subjects_dir=None,
                 parc='aparc', connectivity='custom', name='source', filename='{subject}-{src}-src.fif'):
        SourceSpaceBase.__init__(self, vertices, subject, src, subjects_dir, parc, connectivity, name, filename)

    def _init_secondary(self):
        SourceSpaceBase._init_secondary(self)
        assert len(self.vertices) == 2, "ico-based SourceSpaces need " \
                                        "exactly two vertices arrays"
        self.lh_vertices = self.vertices[0]
        self.rh_vertices = self.vertices[1]
        self.lh_n = len(self.lh_vertices)
        self.rh_n = len(self.rh_vertices)

    def _read_parc(self, parc: str) -> Factor:
        fname = self._ANNOT_PATH.format(
            subjects_dir=self.subjects_dir, subject=self.subject,
            hemi='%s', parc=parc)
        labels_lh, _, names_lh = read_annot(fname % 'lh')
        labels_rh, _, names_rh = read_annot(fname % 'rh')
        x_lh = labels_lh[self.lh_vertices]
        x_lh[x_lh == -1] = -2
        x_rh = labels_rh[self.rh_vertices]
        x_rh[x_rh >= 0] += len(names_lh)
        names = chain(('unknown-lh', 'unknown-rh'),
                      (name.decode() + '-lh' for name in names_lh),
                      (name.decode() + '-rh' for name in names_rh))
        return Factor(np.hstack((x_lh, x_rh)), parc,
                      labels={i: name for i, name in enumerate(names, -2)})

    def __iter__(self):
        return (temp % v for temp, vertices in
                zip(('L%i', 'R%i'), self.vertices) for v in vertices)

    def __getitem__(self, index):
        if isinstance(index, Integral):
            if index < self.lh_n:
                return 'L%i' % self.lh_vertices[index]
            elif index < self._n_vert:
                return 'R%i' % self.rh_vertices[index - self.lh_n]
            else:
                raise IndexError("SourceSpace Index out of range: %i" % index)

        int_index = index_to_int_array(index, self._n_vert)
        bool_index = np.bincount(int_index, minlength=self._n_vert).astype(bool)

        # vertices
        boundaries = np.cumsum(list(chain((0,), (len(v) for v in self.vertices))))
        vertices = [v[bool_index[start: stop]] if stop > start else np.empty(0, int)
                    for v, (start, stop) in zip(self.vertices, intervals(boundaries))]

        # parc
        parc = None if self.parc is None else self.parc[index]

        return SourceSpace(vertices, self.subject, self.src, self.subjects_dir,
                           parc, self._subgraph(int_index), self.name)

    def _as_uv(self):
        return Factor(('%s%i' % (hemi, i) for hemi, vertices in
                       zip(('L', 'R'), self.vertices) for i in vertices),
                      name=self.name)

    def _cluster_properties(self, x):
        ds = SourceSpaceBase._cluster_properties(self, x)
        # hemi
        hemis = []
        for x_ in x:
            where = np.flatnonzero(x_)
            src_in_lh = (where < self.lh_n)
            if np.all(src_in_lh):
                hemis.append('lh')
            elif np.any(src_in_lh):
                hemis.append('bh')
            else:
                hemis.append('rh')
        ds['hemi'] = Factor(hemis)
        return ds

    def _link_midline(self, maxdist=0.015):
        """Link sources in the left and right hemispheres

        Link each source to the nearest source in the opposing hemisphere if
        that source is closer than ``maxdist``.

        Parameters
        ----------
        maxdist : scalar [m]
            Add an interhemispheric connection between any two vertices whose
            distance is less than this number (in meters; default 0.015).
        """
        if self.kind != 'ico':
            raise ValueError("Can only link hemispheres in 'ico' source "
                             "spaces, not in %s" % repr(self.kind))
        old_con = self.connectivity()

        # find vertices to connect
        coords_lh = self.coordinates[:self.lh_n]
        coords_rh = self.coordinates[self.lh_n:]
        dists = cdist(coords_lh, coords_rh)
        close_lh, close_rh = np.nonzero(dists < maxdist)
        unique_close_lh = np.unique(close_lh)
        unique_close_rh = np.unique(close_rh)
        new_con = {(lh, np.argmin(dists[lh]) + self.lh_n) for lh in
                   unique_close_lh}
        new_con.update((np.argmin(dists[:, rh]), rh + self.lh_n) for rh in
                       unique_close_rh)
        new_con = np.array(sorted(new_con), np.uint32)
        self._connectivity = np.vstack((old_con, new_con))

    def _compute_connectivity(self):
        src = self.get_source_space()
        return _mne_tri_soure_space_graph(src, self.vertices)

    def _array_index(self, arg, allow_vertex=True):
        if isinstance(arg, mne.BiHemiLabel):
            lh_idx = self._array_index_hemilabel(arg.lh)
            rh_idx = self._array_index_hemilabel(arg.rh)
            return np.hstack((lh_idx, rh_idx))
        elif isinstance(arg, mne.Label):
            idx = np.zeros(len(self), dtype=np.bool8)
            idx_part = self._array_index_hemilabel(arg)
            if arg.hemi == 'lh':
                idx[:self.lh_n] = idx_part
            elif arg.hemi == 'rh':
                idx[self.lh_n:] = idx_part
            else:
                raise ValueError(f"{arg!r} with unknown value for label.hemi: {arg.hemi!r}")
            return idx
        elif isinstance(arg, str):
            if arg == 'lh':
                return slice(self.lh_n)
            elif arg == 'rh':
                if self.rh_n:
                    return slice(self.lh_n, None)
                else:
                    return slice(0, 0)
        elif isinstance(arg, self.__class__):
            sv = self.vertices
            ov = arg.vertices
            if all(np.array_equal(s, o) for s, o in zip(sv, ov)):
                return FULL_SLICE
            elif any(any(np.setdiff1d(o, s)) for o, s in zip(ov, sv)):
                raise IndexError("Index contains unknown sources")
            else:
                return np.hstack([np.in1d(s, o, True) for s, o in zip(sv, ov)])
        return SourceSpaceBase._array_index(self, arg, allow_vertex)

    def _array_index_for_vertex(self, vertex_desc):
        m = self._vertex_re.match(vertex_desc)
        if m is None:
            raise IndexError(f"{vertex_desc!r}: neither a label nor a valid vertex description")
        hemi, vertex = m.groups()
        vertex = int(vertex)
        vertices = self.vertices[hemi == 'R']
        i = int(np.searchsorted(vertices, vertex))
        if vertices[i] == vertex:
            if hemi == 'R':
                return i + self.lh_n
            else:
                return i
        else:
            raise IndexError(f"{vertex_desc!r}: SourceSpace does not contain this vertex")

    def _array_index_hemilabel(self, label: mne.Label):
        stc_vertices = self.vertices[label.hemi == 'rh']
        idx = np.in1d(stc_vertices, label.vertices, True)
        return idx

    def _dim_index(self, index):
        if np.isscalar(index):
            if index >= self.lh_n:
                return 'R%i' % (self.rh_vertices[index - self.lh_n])
            else:
                return 'L%i' % (self.lh_vertices[index])
        else:
            return SourceSpaceBase._dim_index(self, index)

    def _label(self, vertices, name, color, subjects_dir=None, sss=None):
        lh_vertices, rh_vertices = vertices
        if sss is None:
            sss = self.get_source_space(subjects_dir)

        if len(lh_vertices):
            lh = mne.Label(lh_vertices, hemi='lh', color=color).fill(sss, name + '-lh')
        else:
            lh = None

        if len(rh_vertices):
            rh = mne.Label(rh_vertices, hemi='rh', color=color).fill(sss, name + '-rh')
        else:
            rh = None

        return lh, rh

    def _mask_label(self, subjects_dir=None):
        "Create a Label that masks the areas not covered in this SourceSpace"
        sss = self.get_source_space(subjects_dir)
        if self.lh_n:
            lh_verts = np.setdiff1d(sss[0]['vertno'], self.lh_vertices)
        else:
            lh_verts = ()

        if self.rh_n:
            rh_verts = np.setdiff1d(sss[1]['vertno'], self.rh_vertices)
        else:
            rh_verts = ()

        return self._label((lh_verts, rh_verts), 'mask', (0, 0, 0), subjects_dir, sss)

    def _mask_ndvar(self, subjects_dir=None):
        if subjects_dir is None:
            subjects_dir = self.subjects_dir
        sss = self.get_source_space(subjects_dir)
        vertices = [sss[0]['vertno'], sss[1]['vertno']]
        data = [np.in1d(vert, self_vert) for vert, self_vert in
                zip(vertices, self.vertices)]
        source = SourceSpace(vertices, self.subject, self.src, subjects_dir,
                             self.parc.name, name=self.name)
        return NDVar(np.concatenate(data), (source,))

    def _read_surf(self, hemi, surf='orig'):
        path = Path(f'{self.subjects_dir}/{self.subject}/surf/{hemi}.{surf}')
        return read_geometry(path)

    def index_for_label(self, label):
        """Return the index for a label

        Parameters
        ----------
        label : str | sequance of str | Label | BiHemiLabel
            The name of a region in the current parcellation, or an :mod:`mne`
            :class:`~mne.label.Label` object. If the label does not
            match any sources in the SourceEstimate, a ValueError is raised.

        Returns
        -------
        index : NDVar of bool
            Index into the source space dim that corresponds to the label.
        """
        return SourceSpaceBase.index_for_label(self, label)

    def surface_coordinates(self, surf='white'):
        """Load surface coordinates for any FreeSurfer surface

        Parameters
        ----------
        surf : str
            Name of the FreeSurfer surface.

        Returns
        -------
        coords : array (n_sources, 3)
            Coordinates for each source contained in the source space.
        """
        out = []
        for hemi, vertices in zip(('lh', 'rh'), self.vertices):
            if len(vertices) == 0:
                continue
            coords, _ = self._read_surf(hemi, surf)
            out.append(coords[vertices])

        if len(out) == 1:
            return out[0]
        else:
            return np.vstack(out)


class VolumeSourceSpace(SourceSpaceBase):
    """MNE volume source space

    Parameters
    ----------
    vertices : list of 2 int arrays
        The vertex identities of the dipoles in the source space (left and
        right hemisphere separately).
    subject : str
        The mri-subject name.
    src : str
        The kind of source space used (e.g., 'ico-4'; only ``ico`` is currently
        supported.
    subjects_dir : str
        The path to the subjects_dir (needed to locate the source space
        file).
    parc : None | str
        Add a parcellation to the source space to identify vertex location.
        Only applies to ico source spaces, default is 'aparc'.
    connectivity : 'grid' | 'none' | array of int, (n_edges, 2)
        Connectivity between elements. Set to ``"none"`` for no connections or
        ``"grid"`` to use adjacency in the sequence of elements as connection.
        Set to :class:`numpy.ndarray` to specify custom connectivity. The array
        should be of shape (n_edges, 2), and each row should specify one
        connection [i, j] with i < j, with rows sorted in ascending order. If
        the array's dtype is uint32, property checks are disabled to improve
        efficiency.
    name : str
        Dimension name (default ``"source"``).
    filename : str
        Filename template for the MNE source space file.

    See Also
    --------
    SourceSpace : surface-based source space
    """
    kind = 'vol'
    _default_parc = 'aseg'

    def __init__(self, vertices, subject=None, src=None, subjects_dir=None,
                 parc=None, connectivity='custom', name='source', filename='{subject}-{src}-src.fif'):
        if isinstance(vertices, np.ndarray):
            vertices = [vertices]
        SourceSpaceBase.__init__(self, vertices, subject, src, subjects_dir, parc, connectivity, name, filename)

    def _read_parc(self, parc: str) -> Factor:
        path = Path(self.subjects_dir) / self.subject / 'mri' / f'{parc}.mgz'
        if not path.exists():
            raise ValueError(f"parc={parc!r}: parcellation does not exist at {path}")
        mgz = nibabel.load(str(path))
        voxel_to_mri = mgz.affine.copy()
        voxel_to_mri[:3] /= 1000
        mri_to_voxel = inv(voxel_to_mri)
        voxel_coords = mne.transforms.apply_trans(mri_to_voxel, self.coordinates)
        voxel_coords = np.round(voxel_coords).astype(int)
        x, y, z = voxel_coords.T
        data = mgz.get_data()
        x = data[x, y, z]
        labels = {item[0]: item[1] for item in mne.source_space._get_lut()}
        return Factor(x, labels=labels, name=parc)

    def _init_secondary(self):
        SourceSpaceBase._init_secondary(self)
        if len(self.vertices) != 1:
            raise ValueError("A VolumeSourceSpace needs exactly one vertices array")

    @LazyProperty
    def hemi(self):
        return Factor(np.sign(self.coordinates[:, 0]), labels={-1: 'lh', 0: 'midline', 1: 'rh'})

    @LazyProperty
    def lh_n(self):
        return np.sum(self.hemi == 'lh')

    @LazyProperty
    def rh_n(self):
        return np.sum(self.hemi == 'rh')

    def __iter__(self):
        return map(str, self.vertices[0])

    def __getitem__(self, index):
        if isinstance(index, Integral):
            try:
                return str(self.vertices[0][index])
            except IndexError:
                raise IndexError("VolumeSourceSpace Index out of range: %i" % index)
        else:
            parc = None if self.parc is None else self.parc[index]
            return VolumeSourceSpace(
                [self.vertices[0][index]], self.subject, self.src,
                self.subjects_dir, parc, self._subgraph(index), self.name)

    def _as_uv(self):
        return Factor(self.vertices[0], name=self.name)

    def _compute_connectivity(self):
        src = self.get_source_space()
        coords = src[0]['rr'][self.vertices[0]]
        dist_threshold = self.grade * 0.0011
        return _point_graph(coords, dist_threshold)

    def _distances(self):
        sss = self.get_source_space()
        coords = sss[0]['rr'][self.vertices[0]]
        return squareform(pdist(coords))

    def _array_index(self, arg, allow_vertex=True):
        if isinstance(arg, str):
            if arg in ('lh', 'rh'):
                return self.hemi == arg
        return SourceSpaceBase._array_index(self, arg, allow_vertex)

    def _array_index_for_vertex(self, vertex_desc):
        m = re.match(r'(\d+)$', vertex_desc)
        if m is None:
            raise IndexError(f"{vertex_desc!r}: neither a label nor a valid vertex description")
        return int(np.searchsorted(self.vertices[0], int(m.group(1))))

    def _dim_index(self, index):
        if np.isscalar(index):
            return str(self.vertices[0][index])
        else:
            return SourceSpaceBase._dim_index(self, index)


class UTS(Dimension):
    """Dimension object for representing uniform time series

    Parameters
    ----------
    tmin : float
        First time point (inclusive).
    tstep : float
        Time step between samples.
    nsamples : int
        Number of samples.

    Attributes
    ----------
    tmin : float
        Lowest time point in seconds.
    tmax : float
        Largest time point [s].
    tstep : float
        Time step for each sample [s].
    nsamples : int
        Number of samples.
    tstop : float
        Time sample after ``tmax`` [s] (consistent with indexing excluding end
        point).
    times : array (nsamples,)
        Array with all time points.

    Notes
    -----
    Special indexing:

    (tstart, tstop) : tuple
        Restrict the time to the indicated window (either end-point can be
        None).

    """
    _default_connectivity = 'grid'
    unit = 's'
    _tol = 0.000001  # tolerance for deciding if time values are equal

    def __init__(self, tmin, tstep, nsamples):
        Dimension.__init__(self, 'time', 'grid')
        self.tmin = float(tmin)  # Python float has superior precision
        self.tstep = float(tstep)
        self.nsamples = int(nsamples)
        self._init_secondary()

    def _init_secondary(self):
        self.tmax = self.tmin + self.tstep * (self.nsamples - 1)
        self.tstop = self.tmin + self.tstep * self.nsamples
        self._n_decimals = max(n_decimals(self.tmin), n_decimals(self.tstep))

    @LazyProperty
    def times(self):
        return self.tmin + np.arange(self.nsamples) * self.tstep

    @classmethod
    def from_int(cls, first, last, sfreq):
        """Create a UTS dimension from sample index and sampling frequency

        Parameters
        ----------
        first : int
            Index of the first sample, relative to 0.
        last : int
            Index of the last sample, relative to 0.
        sfreq : scalar
            Sampling frequency, in Hz.
        """
        tmin = first / sfreq
        nsamples = last - first + 1
        tstep = 1. / sfreq
        return cls(tmin, tstep, nsamples)

    def __getstate__(self):
        out = Dimension.__getstate__(self)
        out.update(tmin=self.tmin, tstep=self.tstep, nsamples=self.nsamples)
        return out

    def __setstate__(self, state):
        if 'name' not in state:
            state['name'] = 'time'
            state['connectivity'] = None
            state['connectivity_type'] = 'grid'
        Dimension.__setstate__(self, state)
        self.tmin = state['tmin']
        self.tstep = state['tstep']
        self.nsamples = state['nsamples']
        self._init_secondary()

    def __repr__(self):
        return "UTS(%s, %s, %s)" % (self.tmin, self.tstep, self.nsamples)

    def _as_scalar_array(self):
        return self.times

    def _axis_data(self):
        return self.times

    def _axis_im_extent(self):
        return self.tmin - 0.5 * self.tstep, self.tmax + 0.5 * self.tstep

    def _axis_format(self, scalar, label):
        use_s = max(self.tmax, -self.tmin) >= 10.
        if label is True:
            label = "Time [%s]" % ('s' if use_s else 'ms')

        if use_s:
            if scalar:
                fmt = FuncFormatter(lambda x, pos: '%.5g' % x)
            else:
                fmt = FuncFormatter(lambda x, pos: '%.5g' % self.times[x])
        elif scalar:
            fmt = FuncFormatter(lambda x, pos: '%i' % round(1e3 * x))
        else:
            fmt = FuncFormatter(lambda x, pos:
                                '%i' % round(1e3 * self.times[int(round(x))]))
        return fmt, None, label

    def _bin(self, start, stop, step, nbins):
        if nbins is not None:
            raise NotImplementedError("nbins for UTS dimension")

        if start is None:
            start = self.tmin

        if stop is None:
            stop = self.tstop

        n_bins = int(ceil(round((stop - start) / step, 2)))
        edges = [start + n * step for n in range(n_bins)]
        edges.append(stop)
        out_dim = UTS(start + step / 2, step, n_bins)
        return edges, out_dim

    def __len__(self):
        return self.nsamples

    def __eq__(self, other):
        return (Dimension.__eq__(self, other) and
                self.nsamples == other.nsamples and
                abs(self.tmin - other.tmin) < self._tol and
                abs(self.tstep - other.tstep) < self._tol)

    def __contains__(self, index):
        return self.tmin - self.tstep / 2 < index < self.tstop - self.tstep / 2

    def __getitem__(self, index):
        if isinstance(index, Integral):
            return self.times[index]
        elif not isinstance(index, slice):
            # convert index to slice
            int_index = index_to_int_array(index, self.nsamples)
            start = int_index[0]
            steps = np.unique(np.diff(int_index))
            if len(steps) > 1:
                raise NotImplementedError("non-uniform time series")
            step = steps[0]
            stop = int_index[-1] + step
            index = slice(start, stop, step)

        start = 0 if index.start is None else index.start
        if start < 0:
            start += self.nsamples
        stop = self.nsamples if index.stop is None else index.stop
        if stop < 0:
            stop += self.nsamples

        tmin = self.times[start]
        nsamples = stop - start
        if nsamples < 0:
            raise IndexError("Time index out of range: %s." % repr(index))

        if index.step is None or index.step == 1:
            tstep = self.tstep
        else:
            tstep = self.tstep * index.step
            nsamples = int(ceil(nsamples / index.step))

        return UTS(tmin, tstep, nsamples)

    def _cluster_bounds(self, x):
        """Cluster start and stop in samples

        Parameters
        ----------
        x : array of bool, (n_clusters, len(self))
            The cluster extents, with different clusters stacked along the
            first axis.
        """
        # find indices of cluster extent
        row, col = np.nonzero(x)
        try:
            ts = [col[row == i][[0, -1]] for i in range(len(x))]
        except IndexError:
            raise ValueError("Empty cluster")
        ts = np.array(ts)
        return ts

    def _cluster_properties(self, x):
        """Find cluster properties for this dimension

        Parameters
        ----------
        x : array of bool, (n_clusters, len(self))
            The cluster extents, with different clusters stacked along the
            first axis.

        Returns
        -------
        cluster_properties : Dataset
            A dataset with variables describing cluster properties along this
            dimension: "tstart", "tstop", "duration".
        """
        ds = Dataset()

        # no clusters
        if len(x) == 0:
            ds['tstart'] = Var([])
            ds['tstop'] = Var([])
            ds['duration'] = Var([])
            return ds

        # create time values
        bounds = self._cluster_bounds(x)
        tmin = self.times[bounds[:, 0]]
        tmax = self.times[bounds[:, 1]]
        ds['tstart'] = Var(tmin)
        ds['tstop'] = Var(tmax + self.tstep)
        ds['duration'] = ds.eval("tstop - tstart")
        return ds

    def _array_index(self, arg):
        if np.isscalar(arg):
            i = int(round((arg - self.tmin) / self.tstep))
            if 0 <= i < self.nsamples:
                return i
            else:
                raise ValueError("Time index %s out of range (%s, %s)"
                                 % (arg, self.tmin, self.tmax))
        elif isinstance(arg, UTS):
            if self.tmin == arg.tmin:
                start = None
                stop = arg.nsamples
            elif arg.tmin < self.tmin:
                err = ("The index time dimension starts before the reference "
                       "time dimension")
                raise DimensionMismatchError(err)
            else:
                start_float = (arg.tmin - self.tmin) / self.tstep
                start = int(round(start_float))
                if abs(start_float - start) > self._tol:
                    err = ("The index time dimension contains values not "
                           "contained in the reference time dimension")
                    raise DimensionMismatchError(err)
                stop = start + arg.nsamples

            if self.tstep == arg.tstep:
                step = None
            elif self.tstep > arg.tstep:
                err = ("The index time dimension has a higher sampling rate "
                       "than the reference time dimension")
                raise DimensionMismatchError(err)
            else:
                step_float = arg.tstep / self.tstep
                step = int(round(step_float))
                if abs(step_float - step) > self._tol:
                    err = ("The index time dimension contains values not "
                           "contained in the reference time dimension")
                    raise DimensionMismatchError(err)

            if stop == self.nsamples:
                stop = None

            return slice(start, stop, step)
        elif isinstance(arg, np.ndarray) and arg.dtype.kind in 'fi':
            return np.array([self._array_index(i) for i in arg])
        else:
            return super(UTS, self)._array_index(arg)

    def _array_index_for_slice(self, start, stop=None, step=None):
        "Create a slice into the time axis"
        if (start is not None) and (stop is not None) and (start >= stop):
            raise ValueError("tstart must be smaller than tstop")

        if start is None:
            start_ = None
        elif start <= self.tmin - self.tstep:
            raise IndexError("Time index slice out of range: start=%s" % start)
        else:
            start_float = (start - self.tmin) / self.tstep
            start_ = int(start_float)
            if start_float - start_ > 0.000001:
                start_ += 1

        if stop is None:
            stop_ = None
        elif stop - self.tstop > self._tol:
            raise ValueError("Time index slice out of range: stop=%s" % stop)
        else:
            stop_float = (stop - self.tmin) / self.tstep
            stop_ = int(stop_float)
            if stop_float - stop_ > 0.000001:
                stop_ += 1

        if step is None:
            step_ = None
        else:
            step_float = step / self.tstep
            step_ = int(round(step_float))
            if step_ != round(step_float, 4):
                raise ValueError("Time index slice step needs to be a multiple "
                                 "of the data time step (%s), got %s" %
                                 (self.tstep, step))

        return slice(start_, stop_, step_)

    def _array_index_to(self, other):
        "Int index to access data from self in an order consistent with other"
        if not isinstance(other, UTS):
            raise IndexError(f"{other}: not a valid index for UTS dimension")
        start = (other.tmin - self.tmin) / self.tstep
        if start % 1 or start < 0:
            raise IndexError(f"{other}: incompatible time axis")
        start = int(round(start))
        step = other.tstep / self.tstep
        if step % 1:
            raise IndexError(f"{other}: incompatible time axis")
        step = int(round(step))
        if other.tstop > self.tstop:
            raise IndexError(f"{other}: incompatible time axis")
        stop = start + other.nsamples
        return np.arange(start, stop, step)

    def _dim_index(self, arg):
        if isinstance(arg, slice):
            return slice(None if arg.start is None else self._dim_index(arg.start),
                         None if arg.stop is None else self._dim_index(arg.stop),
                         None if arg.step is None else arg.step * self.tstep)
        elif np.isscalar(arg):
            return round(self.tmin + arg * self.tstep, self._n_decimals)
        else:
            return Dimension._dim_index(self, arg)

    def intersect(self, dim, check_dims=True):
        """Create a UTS dimension that is the intersection with ``dim``

        Parameters
        ----------
        dim : UTS
            Dimension to intersect with.
        check_dims : bool
            Check dimensions for consistency (not applicaple to this subclass).

        Returns
        -------
        intersection : UTS
            The intersection with dim (returns itself if dim and self are
            equal)
        """
        if self == dim:
            return self
        elif self.tstep != dim.tstep:
            raise NotImplementedError("Intersection of UTS with unequal tstep :(")

        tstep = self.tstep
        tmin_diff = abs(self.tmin - dim.tmin) / tstep
        if abs(tmin_diff - round(tmin_diff)) > self._tol:
            raise DimensionMismatchError("UTS dimensions have different times")
        tmin = max(self.tmin, dim.tmin)

        tmax = min(self.tmax, dim.tmax)
        nsamples = int(round((tmax - tmin) / tstep)) + 1
        if nsamples <= 0:
            raise DimensionMismatchError("UTS dimensions don't overlap")

        return UTS(tmin, tstep, nsamples)

    def _union(self, other):
        # sloppy implementation
        if self == other:
            return self
        tstep = min(self.tstep, other.tstep)
        tmin = min(self.tmin, other.tmin)
        n_samples = int(round((max(self.tstop, other.tstop) - tmin) / tstep))
        return UTS(tmin, tstep, n_samples)


def intersect_dims(dims1, dims2, check_dims=True):
    """Find the intersection between two multidimensional spaces

    Parameters
    ----------
    dims1, dims2 : tuple of dimension objects
        Two spaces involving the same dimensions with overlapping values.
    check_dims : bool
        Check dimensions for consistency (e.g., channel locations in a Sensor
        dimension). Default is ``True``. Set to ``False`` to ignore non-fatal
        mismatches.

    Returns
    -------
    dims : tuple of Dimension objects
        Intersection of dims1 and dims2.
    """
    return tuple(d1.intersect(d2, check_dims=check_dims) for d1, d2 in zip(dims1, dims2))


EVAL_CONTEXT.update(Var=Var, Factor=Factor, extrema=extrema)

NDVarArg = typing.Union[NDVar, str]
CategorialArg = typing.Union[Factor, Interaction, NestedEffect, str]
FactorArg = typing.Union[Factor, str]
IndexArg = typing.Union[Var, np.ndarray, str]
