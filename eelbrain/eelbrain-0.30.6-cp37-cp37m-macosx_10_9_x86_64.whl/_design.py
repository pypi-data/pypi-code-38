'''
Use data vessels to construct an experiment trial list.

Usage
=====

Creating Design
---------------

1) The first step is to construct a Dataset from the variables that are
   permutated in the experiment. This is done by creating a list of `Variable`
   objects (one for each variable) and submitting it to the `permute` function.
2) The second step is to add to the Dataset additional variables that need
   randomization. A tool that can be used for this is the `random_factor`
   function.


Exporting to Matlab
-------------------

The goal is to export a struct with a record for each trial, in which variables
are accessed as in::

    > trial(i).varname
    OR
    > var = 'varname'
    > trial(i).(var)

Some data associated with the experiment don't change across trials (color
values, images, ...). Such values can be exported separately with the values
parameter:

    >>> export_mat(ds, values={'colors': {'red': [255, 0, 0]}}

Can be used in matlab as:

    >> colors.red
    ans =
             255           0           0

'''
from itertools import product
from math import ceil
import os

import numpy as np
import scipy.io

from ._data_obj import (Dataset, Factor, ascategorial, asfactor, assub,
                        check_length)
from ._utils import ui
from .save import pickle


_max_iter = 1e3


class RandomizationError(Exception):
    "custom error for failures in randomization"
    pass


class Variable:
    """Variable for a design

    Parameters
    ----------
    name : str
        name for the Variable
    values : iterable of str
        list of values that the Variable can assume (iterable, i.e. can be
        dict with keys)
    rand : bool
        randomize the sequence of values
    urn : list of Variables
        Variables which are drawn from the same urn BEFORE the
        current Variable (i.e. the current Variable can only assume values
        not taken by any PI in urn.
    """
    def __init__(self, name, values, rand=True, urn=()):
        self.is_rand = rand
        self.name = name

        # validate urn
        for u in urn:
            if not all(v1 == v2 for v1, v2 in zip(values, u.values)):
                raise ValueError("urn contains incommensurable Variable")
        self.urn = urn

        # validate values:
        assert all(isinstance(v, str) for v in values)
        assert len(values) < 256, "not implemented"
#        self.values = values
        self.cells = dict(enumerate(values))
        self.N = len(values)  # theN of categories
        self.Ndraw = self.N - len(self.urn)  # the N of possible values for each trial


def permute(variables):
    """
    Create a Dataset from permuting variables.

    Parameters
    ----------
    variables : sequence
        Sequence of (name, values) tuples. For examples:
        ``(('A', ('a1', 'a2')), ('B', ('b1', 'b2')))``

    Examples
    --------
    >>> print(permute((('A', ('a1', 'a2')),('B', ('b1', 'b2')))))
    A    B
    -------
    a1   b1
    a1   b2
    a2   b1
    a2   b2
    """
    names = (v[0] for v in variables)
    cases = tuple(product(*(v[1] for v in variables)))
    return Dataset.from_caselist(names, cases)


def permute_(variables, count='caseID', randomize=False):
    # sort variables
    perm_rand = []  # permutated and randomized
    perm_nonrand = []  # permutated and not randomized
    for v in variables:
        if v.is_rand:
            perm_rand.append(v)
        else:
            perm_nonrand.append(v)

    perm_n = [v.Ndraw for v in variables]
    n_trials = np.prod(perm_n)
    n_properties = len(variables)
    out = np.empty((n_trials, n_properties), dtype=int)

    # permutatet variables
    for i, v in enumerate(variables):
        t = np.prod(perm_n[:i])
        r = np.prod(perm_n[i + 1:])
        if len(v.urn) == 0:
            out[:, i] = np.tile(np.arange(v.N), t).repeat(r)
        else:
            base = np.arange(v.N)
            for v0 in variables[:i]:
                if v0 in v.urn:
                    base = np.ravel([base[base != j] for j in range(v.N)])
                else:
                    base = np.tile(base, v.Ndraw)

            out[:, i] = np.repeat(base, r)

    if randomize:
        # shuffle those perm factors that should be shuffled
        n_rand_bins = np.prod([v.Ndraw for v in perm_nonrand])
        rand_bin_len = int(n_trials / n_rand_bins)
        for i in range(0, n_trials, rand_bin_len):
            np.random.shuffle(out[i:i + rand_bin_len])

    # create Dataset
    ds = Dataset(name='Design')
    for i, v in enumerate(variables):
        x = out[:, i]
        f = Factor(x, v.name, labels=v.cells)
        ds.add(f)

    if count:
        ds.index(count)

    return ds


def random_factor(values, n=None, name=None, rand=True, balance=None, urn=None,
                  require_exact_balance=True, sub=None, ds=None):
    """Create a Factor with random values

    Parameters
    ----------
    values : list
        Values (Factor labels) from which to sample.
    n : None | int
        Length of the new Factor. Can be None if another data-object is
        specified in at least one other argument.
    name : None | str
        Name of the Factor.
    rand : bool
        Randomize sequence of values (instead of just iterating over the
        range).
    balance : None | categorial
        Cells over which the values in the new Factor should be balanced.
    urn : None | list of Factors
        Factors which have already drawn from the same urn. I.e., for each
        index, the new Factor should contain a value that is different from
        the Factors in urn.
    require_exact_balance : bool
        Raise an error if balancing exactly is not possible.
    sub : None | index array
        Only fill up part of the Factor (the other cells will have the default
        '' empty string value).
    ds : None | Dataset
        If a Dataset is specified, ``urn``, ``balance`` and ``sub`` can be
        specified as str (names in ds).
    """
    # convert input args
    sub = assub(sub, ds)
    if urn is not None:
        if n is None:
            urn_0 = asfactor(urn[0], None, ds)
            n = len(urn_0)
        urn = [asfactor(f, sub, ds) for f in urn]
    if balance is not None:
        if n is None:
            balance_ = ascategorial(balance, None, ds)
            n = len(balance_)
        balance = ascategorial(balance, sub, ds)
    elif n is None:
        err = ("If neither urn not balance are specified, n needs to be "
               "explicitly specified.")
        raise ValueError(err)
    if urn is not None:
        check_length(urn + [balance])
    if sub is not None:
        n_tgt = n
        n = len(np.empty(n)[sub])

    i = 0
    while i < _max_iter:
        try:
            f = _try_make_random_factor(name, values, n, rand, balance, urn,
                                        require_exact_balance)
        except RandomizationError:
            i += 1
        except:
            raise
        else:
            if sub is not None:
                f_sub = f
                f = Factor([''], repeat=n_tgt, name=name)
                f[sub] = f_sub
            return f

    err = ("Random list generation exceeded max-iter (%i)" % i)
    raise RandomizationError(err)


def _try_make_random_factor(name, values, n, rand, balance, urn,
                            require_exact_balance):
    n_values = len(values)
    x = np.empty(n, dtype=int)
    cells = dict(enumerate(values))

    if balance is not None:
        regions = balance

        # for now, they have to be of equal length
        region_lens = [np.sum(regions == cell) for cell in regions.cells]
        if len(set(region_lens)) > 1:
            raise NotImplementedError

        region_len = region_lens[0]
    else:
        regions = Factor('?' * n, "regions")
        region_len = n

    # generate random values with equal number of each value
    exact_balance = (region_len % n_values == 0)
    if exact_balance:
        values = np.arange(region_len, dtype=int) % n_values
    elif require_exact_balance:
        raise ValueError("No exact balancing possible")
    else:
        _len = int(ceil(region_len / n_values)) * n_values
        values = np.arange(_len, dtype=int) % n_values

        # drop trailing values randomly
        if rand:  # and _randomize:
            np.random.shuffle(values[-n_values:])
        values = values[:region_len]

    # cycle through values of the balance containers
    for region in regions.cells:
        if rand:  # and _randomize:
            np.random.shuffle(values)

        # indexes into the current out array rows
        c_index = (regions == region)
        c_indexes = np.where(c_index)[0]  # location

        if urn:  # the Urn has been drawn from already
            if not rand:
                raise NotImplementedError

            # source and target indexes
            for si, ti in zip(range(region_len), c_indexes):
                if any(cells[values[si]] == u[ti] for u in urn):

                    # randomized order in which to test other
                    # values for switching
                    switch_order = list(range(region_len))
                    switch_order.pop(si)
                    np.random.shuffle(switch_order)

                    switched = False
                    for si_switch in switch_order:
                        ti_switch = c_indexes[si_switch]
#                        a = values[si] not in out[ti_switch, urn_indexes]
#                        b = values[si_switch] not in out[ti, urn_indexes]
                        a = any(cells[values[si]] == u[ti_switch] for u in urn)
                        b = any(cells[values[si_switch]] == u[ti] for u in urn)
                        if not (a or b):
                            values[[si, si_switch]] = values[[si_switch, si]]
                            switched = True
                            break

                    if not switched:
                        msg = "No value found for switching! Try again."
                        raise RandomizationError(msg)

        x[c_index] = values
    return Factor(x, name, labels=cells)


def complement(base, name=None, values=None, ds=None):
    """Factor with values that complement the Factors in ``base``

    Create a Factor that contains for each index the value that is not on any
    other Factor at this index.

    Parameters
    ----------
    base : list of Factors
        Factors that together, on each case, contain all the values spare one.
    name : str
        Name for Factor.
    values : list of str | None
        values for the Factor. If None, the first Factor's values are used.
    ds : None | Dataset
        If a Dataset is specified, ``urn``, ``balance`` and ``sub`` can be
        specified as str (names in ds).
    """
    base = [asfactor(f, None, ds) for f in base]
    N = len(base[0])
    if values is None:
        values = base[0].cells

    cells = dict(enumerate(values))

    grid = np.empty((N, len(values)), dtype=bool)
    for i, v in cells.items():
        grid[:, i] = np.all([f != v for f in base], axis=0)

    grid_sum = np.sum(grid, axis=1)
    if np.any(grid_sum > 1):
        raise ValueError("More than one unused values for at least on case")
    elif np.any(grid_sum < 1):
        raise ValueError("No unused values for at least on case")

    out = Factor('?' * N, name=name)
    for i in cells:
        out[grid[:, i]] = cells[i]

    return out


def shuffle_cases(dataset, inplace=False, blocks=None):
    """Shuffle the cases in a Dataset.

    Parametters
    -----------
    dataset : Dataset
        Dataset to shuffle.
    inplace : bool
        If True, the input Dataset itself is modified, and the function does
        not return anything; if False, a new Dataset containing the shuffled
        variables is returned and the original Dataset is left unmodified.
    blocks : categorial
        defines blocks between which cases are not exchanged.
    """
    index = np.arange(dataset.n_cases)
    if blocks is None:
        np.random.shuffle(index)
    else:
        for cell in blocks.cells:
            i = blocks == cell
            subindex = index[i]
            np.random.shuffle(subindex)
            index[i] = subindex

    if inplace:
        for k in dataset:
            dataset[k] = dataset[k][index]
    else:
        return dataset.sub(index)


def export_mat(dataset, values=None, destination=None):
    """
    Usage::

        >>> export_mat(dataset,
        ...            values={varname -> {cellname -> value}},
        ...            destination='/path/to/file.mat')


    Arguments
    ---------

    dataset : Dataset
        Dataset containing the trial list

    values : `None` or `{varname -> {cellname -> value}}`
        additional values that should be stored, where: `varname` is the
        variable name by which the struct will be available in matlab;
        `cellname` is the name of the struct's field, and `value` is the value
        of that field.

    destination : None or str
        Path where the mat file should be saved. If `None`, the ui will ask
        for a location.

    """
    # Make sure we have a valid destination
    if destination is None:
        print_path = True
        destination = ui.ask_saveas("Mat destination", "Where do you want to save the mat file?", [("Matlab File", '*.mat')])
        if not destination:
            print("aborted")
            return
    else:
        print_path = False

    if not isinstance(destination, str):
        raise ValueError("destination is not a string")

    dirname = os.path.dirname(destination)
    if not os.path.exists(dirname):
        if ui.ask("Create %r?" % dirname, "No folder named %r exists. Should "
                  "it be created?" % dirname):
            os.mkdir(dirname)
        else:
            print("aborted")
            return

    if not destination.endswith('mat'):
        os.path.extsep.join(destination, 'mat')

    # assemble the mat file contents
    mat = {'trials': list(dataset.itercases())}
    if values:
        mat.update(values)

    if print_path:
        print('Saving: %r' % destination)
    scipy.io.savemat(destination, mat, do_compression=True, oned_as='row')


def save(dataset, destination=None, values=None, pickle_values=False):
    """Save the Dataset

    Save the dataset with the same name in 3 different formats:

      - mat: matlab file
      - pickled Dataset
      - TSV: tab-separated values

    """
    if destination is None:
        msg = ("Pick a name to save the Dataset (without extension; '.mat', "
               "'.pickled' and '.tsv' will be appended")
        destination = ui.ask_saveas("Save Dataset", msg, None)

    if not destination:
        return

    destination = str(destination)
    if ui.test_targetpath(destination):
        msg_temp = "Writing: %r"

        dest = os.path.extsep.join((destination, 'pickled'))
        print(msg_temp % dest)
        pickle(dataset, dest)

        if pickle_values:
            dest = os.path.extsep.join((destination + '_values', 'pickled'))
            print(msg_temp % dest)
            pickle(values, dest)

        dest = os.path.extsep.join((destination, 'mat'))
        print(msg_temp % dest)
        export_mat(dataset, values, dest)

        dest = os.path.extsep.join((destination, 'tsv'))
        print(msg_temp % dest)
        dataset.save_txt(dest)
