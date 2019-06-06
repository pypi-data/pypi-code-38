"""
Module for the Dataset class, which provides a wrapper around a pandas DataFrame
allowing for representation of 5C data across replicates and stages of data
processing both on disk and in memory.
"""

import os
import inspect

import numpy as np
import pandas as pd

from lib5c.parsers.primers import load_primermap
from lib5c.parsers.util import null_value
from lib5c.writers.primers import write_primermap
from lib5c.util.system import check_outdir
from lib5c.util.bed import get_mid_to_mid_distance
from lib5c.tools.helpers import infer_level_mapping


class Dataset(object):
    """
    Wrapper around a Pandas DataFrame.

    Attributes
    ----------
    df : pd.DataFrame
        Contains the core data in the Dataset. Columns should be either not
        hierarchical, or hierarchical with the lower level of the hierarchy
        matching the replicate names. The row index of this DataFrame must be
        '<upstream_fragment_name>_<downstream_fragment_name>'.
    pixelmap : pixelmap, optional
        A pixelmap to provide information about the fragments.
    repinfo : pd.DataFrame, optional
        Its row index should be the replicate names, its columns can provide
        arbitrary information about each replicate, such as its condition, etc.
    """
    def __init__(self, df, pixelmap=None, repinfo=None):
        """
        Base constructor.

        Parameters
        ----------
        df : pd.DataFrame
            The dataframe that makes up the Dataset.
        pixelmap : pixelmap, optional
            A pixelmap to bind to the Dataset.
        repinfo : repinfo-style pd.Dataframe, optional
            Repinfo to bind to the Dataset.
        """
        self.df = df
        self.pixelmap = pixelmap
        self.reverse_pixelmap = None
        self.repinfo = repinfo
        if repinfo is not None:
            self.reps = repinfo.index
            self.conditions = sorted(repinfo['condition'].unique())
            self.cond_reps = {cond: repinfo[repinfo['condition'] == cond].index
                              for cond in self.conditions}
        else:
            self.reps = None
            self.conditions = None
            self.cond_reps = None
        if pixelmap is not None:
            self._add_reverse_pixelmap()
            self._add_region_column()
            self._add_distance_column()

    def save(self, filename, sep=None):
        """
        Writes this Dataset to disk as a .csv/.tsv, and optionally writes the
        pixelmap and/or repinfo files to disk right next to it if either or both
        of these data structures exist in the Dataset.

        Parameters
        ----------
        filename : str
            The filename to write to.
        sep : str, optional
            The separator to use when writing the file. If ``filename`` ends
            with .csv or .tsv and ``sep`` is None, the separator will be
            determined automatically by the extension, but you can pass a value
            here to override it.
        """
        # check outdir
        check_outdir(filename)

        # resolve sep
        sep = self._resolve_sep(filename, sep)

        # base filename will be useful
        base_fname, ext = os.path.splitext(filename)

        # write pixelmap if we have one
        if self.pixelmap is not None:
            pixelmap_fname = '%s_map.bed' % base_fname
            extra_column_names = \
                list(set(self.pixelmap[self.pixelmap.keys()[0]][0].keys())
                     - {'chrom', 'start', 'end', 'name', 'region', 'number'})
            write_primermap(self.pixelmap, pixelmap_fname, extra_column_names)

        # write repinfo if we have one
        if self.repinfo is not None:
            repinfo_fname = '%s_repinfo%s' % (base_fname, ext)
            self.repinfo.to_csv(repinfo_fname, sep=sep)

        # write the main dataframe
        self.df.to_csv(filename, sep=sep)

    @classmethod
    def load(cls, filename, sep=None):
        """
        Loads a Dataset from disk.

        Parameters
        ----------
        filename : str
            The .csv or .tsv file to load the Dataset from. If a pixelmap or
            repinfo file is found next to this file, these files will also be
            loaded into the Dataset.
        sep : str, optional
            The separator to use when parsing the .csv/.tsv. Pass None to deduce
            this automatically from the file extension.

        Returns
        -------
        Dataset
            The loaded Dataset.
        """
        # resolve sep
        sep = cls._resolve_sep(filename, sep)

        # base filename will be useful
        base_fname, ext = os.path.splitext(filename)

        # load core dataframe
        df = pd.read_csv(filename, sep=sep, header=[0, 1], index_col=0)
        df.rename(columns=lambda x: '' if 'Unnamed' in x else x, inplace=True)

        # these are the names supplementary files should have if they exist
        pixelmap_fname = '%s_map.bed' % base_fname
        repinfo_fname = '%s_repinfo%s' % (base_fname, ext)

        # load pixelmap if it exists
        pixelmap = None
        if os.path.exists(pixelmap_fname):
            pixelmap = load_primermap(pixelmap_fname)

        # load repinfo if it exists
        repinfo = None
        if os.path.exists(repinfo_fname):
            repinfo = pd.read_csv(repinfo_fname, sep=sep, index_col=0)
            repinfo.index = repinfo.index.map(str)

        # return the loaded instance
        return cls(df, pixelmap=pixelmap, repinfo=repinfo)

    @classmethod
    def from_table_file(cls, table_file, name='counts', sep=None, pixelmap=None,
                        repinfo=None):
        """
        Creates a Dataset from a table file.

        The first column of the table file should be a FFLJ ID.

        The remaining columns should be count values for each replicate.

        The first row should specify the replicate names for each column.

        Parameters
        ----------
        table_file : str
            The table file to read counts from.
        name : str
            Top-level column name for the data.
        sep : str
            The separator to use when parsing the table file.'\t' for tsv
            tables, ',' for csv tables. Pass None to guess this from the
            filename.
        pixelmap : pixelmap, optional
            A pixelmap to bind to the Dataset.
        repinfo : repinfo-style pd.Dataframe, optional
            Repinfo to bind to the Dataset.

        Returns
        -------
        Dataset
            The new Dataset.
        """
        # resolve sep
        sep = cls._resolve_sep(table_file, sep)

        # read csv
        df = pd.read_csv(table_file, sep=sep, index_col=0)

        # make column hierarchy
        df.columns = pd.MultiIndex.from_arrays(
            [[name] * len(df.columns), df.columns])

        # return new Dataset
        return cls(df, pixelmap=pixelmap, repinfo=repinfo)

    @classmethod
    def from_counts_superdict(cls, counts_superdict, pixelmap, name='counts',
                              repinfo=None, rep_order=None):
        """
        Creates a Datset from a counts_superdict and associated pixelmap.

        Parameters
        ----------
        counts_superdict : counts_superdict
            Contains the data that will be put into the Dataset.
        pixelmap : pixelmap
            Needed to establish the row index on the Dataset.
        name : str
            Top-level column name for the data.
        repinfo : repinfo-style pd.Dataframe or list of str, optional
            Repinfo to bind to the Dataset. Pass a list of condition names to
            automatically create a repinfo object.
        rep_order : list of str, optional
            Pass this to guarantee the order of the columns for the replicates.
            Pass None to accept a random order.

        Returns
        -------
        Dataset
            The new Dataset.
        """
        # resolve rep_order
        if rep_order is None:
            rep_order = sorted(counts_superdict.keys())

        # establish regions
        region_order = counts_superdict[rep_order[0]].keys()

        # parallel lists to be filled in by the loop
        list_of_dict = []
        list_of_fflj_id = []

        # loop to fill in the parallel lists
        for region in region_order:
            for i in range(len(pixelmap[region])):
                for j in range(i + 1):
                    list_of_fflj_id.append(
                        '%s_%s' % (pixelmap[region][i]['name'],
                                   pixelmap[region][j]['name']))
                    list_of_dict.append(
                        {rep: counts_superdict[rep][region][i, j]
                         for rep in rep_order})

        # use the parallel lists to create a dataframe with fflj_id index
        df = pd.DataFrame(list_of_dict,
                          index=pd.Series(list_of_fflj_id, name='fflj_id'))

        # make column hierarchy
        df.columns = pd.MultiIndex.from_arrays(
            [[name] * len(df.columns), df.columns])

        # resolve repinfo
        if repinfo is not None and type(repinfo[0]) == str:
            repinfo = Dataset._make_repinfo(rep_order, repinfo)

        # return new Dataset
        return cls(df, pixelmap=pixelmap, repinfo=repinfo)

    def _add_reverse_pixelmap(self):
        """
        Reverses self.pixelmap, binding the result to self.reverse_pixelmap.
        """
        if self.pixelmap is None:
            raise ValueError('Dataset must have pixelmap bound to add reverse '
                             'pixelmap')
        self.reverse_pixelmap = {self.pixelmap[region][i]['name']: (region, i)
                                 for region in self.pixelmap
                                 for i in range(len(self.pixelmap[region]))}

    def _add_region_column(self):
        """
        Adds a 'region' column to self.df if one doesn't exist yet.

        Assumes that all interactions are cis.
        """
        # check if column already exists
        if 'region' in self.df.columns:
            return

        # check for reverse_pixelmap
        if self.reverse_pixelmap is None:
            raise ValueError('Dataset must have reverse_pixelmap bound to add '
                             'region column')

        self.df['region'] = [
            self.reverse_pixelmap[self._split_index(fflj_id)[0]][0]
            for fflj_id in self.df.index]

    def _distance(self, fflj_id):
        """
        Returns the mid-to-mid distance of an interaction given its FFLJ ID.

        Parameters
        ----------
        fflj_id : str
            The FFLJ ID of the interaction.

        Returns
        -------
        int
            Its mid-to-mid interaction distance in units of base pairs.
        """
        # check for reverse_pixelmap
        if self.reverse_pixelmap is None:
            raise ValueError('Dataset must have reverse_pixelmap bound to '
                             'compute interaction distances')

        left_name, right_name = self._split_index(fflj_id)
        left_region, left_index = self.reverse_pixelmap[left_name]
        right_region, right_index = self.reverse_pixelmap[right_name]

        return get_mid_to_mid_distance(self.pixelmap[left_region][left_index],
                                       self.pixelmap[right_region][right_index])

    def _add_distance_column(self):
        """
        Adds a 'distance' (in units of bins) column to self.df if one doesn't
        exist yet.

        Assumes that all interactions are cis.
        """
        # check if column already exists
        if 'distance' in self.df.columns:
            return

        self.df['distance'] = [self._distance(fflj_id)
                               for fflj_id in self.df.index]

    def add_column_from_counts(self, counts, name):
        """
        Adds a new column to this Dataset's df.

        The counts dict passed is assumed to match the pixelmap bound on this
        Dataset. If no pixelmap is bound, an ValueError will be raised.

        Parameters
        ----------
        counts : dict of np.ndarray
            Should contain the values that will make up the new column.
        name : str
            The name of the new column.
        """
        # check for reverse_pixelmap
        if self.reverse_pixelmap is None:
            raise ValueError('Dataset must have reverse_pixelmap bound to '
                             'add column from counts')

        # deduce dtype
        dtype = counts[counts.keys()[0]].dtype

        # define inner function
        def inner_fn(index):
            # split index
            left_name, right_name = self._split_index(index)

            # look up names in the reverse pixelmap
            region, left_index = self.reverse_pixelmap[left_name]
            other_region, right_index = self.reverse_pixelmap[right_name]

            # skip trans contacts
            if region != other_region:
                return null_value(dtype)

            return counts[region][left_index, right_index]

        self.df[name] = np.array([inner_fn(i) for i in self.df.index],
                                 dtype=dtype)

    def add_columns_from_counts_superdict(self, counts_superdict, name,
                                          rep_order=None):
        """
        Adds a new group of columns to the Dataset from a counts superdict
        structure.

        Parameters
        ----------
        counts_superdict : dict of dict of np.ndarray
            The outer keys are replicate names as strings, the inner keys are
            region names as strings, and the values are square, symmetric arrays
            of values for each replicate and region.
        name : str
            The name to use for the new group of columns.
        rep_order : list of str, optional
            Pass a list of replicate names to load the listed replicates in a
            specific order. Pass None to use the random order of the outer keys
            of ``counts_superdict``.
        """
        # resolve rep_order
        if rep_order is None:
            rep_order = counts_superdict.keys()

        for rep in rep_order:
            self.add_column_from_counts(counts_superdict[rep], (name, rep))

    def select(self, name='counts', rep=None, region=None):
        """
        Get a subset of this Dataset's DataFrame corresponding to a desired
        column, replicate, and/or region.

        Parameters
        ----------
        name : str
            The column name of a hierarchical or non-hierarchical column.
        rep : str, optional
            If ``name`` refers to a hierarchical column, you must specify which
            replicate you want to select data from by passing its name here.
        region : str, optional
            To select data from only one region, pass its name here. Pass None
            to select data from all regions.
        """
        idx = self.df[self.df['region'] == region].index if region\
            else self.df.index
        cols = (name, rep) if rep else name
        return self.df.loc[idx, cols]

    def counts(self, name='counts', rep=None, region=None, fill_value=None,
               dtype=None):
        """
        Converts this Dataset to a regional_counts matrix, a counts dict, a
        counts_superdict, or a regional_counts_superdict.

        Parameters
        ----------
        name : str
            The top-level column name to extract.
        rep : str, optional
            If name corresponds to a hierarchical column, pass a rep name to
            extract only one rep (return type will be a counts dict). Pass None
            to return a counts_superdict with all reps. If name corresponds to
            a normal column, this kwarg will be ignored.
        region : str, optional
            Pass a region name as a string to extract data for only one region.
            If name corresponds to a hierarchical column and rep was not passed,
            the return type will be a regional_counts_superdict. Otherwise, the
            return type will be a regional_counts matrix. Pass None to extract
            data for all regions.
        fill_value : any, optional
            The fill value for the counts_superdict (for entries not present in
            the Dataset). Pass None to use np.nan.
        dtype : dtype, optional
            The dtype to use for the np.array's in the counts_superdict. Pass
            None to guess them from the Dataset. If the data being extracted is
            strings, '\|S25' will be assumed.

        Returns
        -------
        regional_counts matrix, counts dict, counts_superdict, or
        regional_counts_superdict
            The data requested. See Parameters for explanation of return type.
            The general philosophy is that a counts_superdict will be returned,
            but any single-key levels will be squeezed.
        """
        # check for reverse_pixelmap
        if self.reverse_pixelmap is None:
            raise ValueError('Dataset must have reverse_pixelmap bound to '
                             'create counts_superdict')

        # check if name is hierachical
        is_hierarchial = hasattr(self.df[name], 'columns')

        # short-circuit: function calls itself repeatedly over reps
        if is_hierarchial and rep is None:
            return {rep: self.counts(name=name, rep=rep, region=region,
                                     fill_value=fill_value, dtype=dtype)
                    for rep in self.df[name].columns}

        # establish default regions
        region_order = self.pixelmap.keys()

        # honor region kwarg
        if region is not None:
            region_order = [region]

        # grab the relevant slice
        if is_hierarchial:
            if region is None:
                df_slice = self.df[name, rep]
            else:
                df_slice = self.df[self.df['region'] == region][name, rep]
        else:
            if region is None:
                df_slice = self.df[name]
            else:
                df_slice = self.df[self.df['region'] == region][name]

        # resolve dtype
        if dtype is None:
            dtype = df_slice.as_matrix().dtype
            if dtype == str:
                dtype = '|S25'

        # resolve fill_value
        if fill_value is None:
            fill_value = np.nan
            if str(dtype).startswith('|S') or \
                    (type(dtype) == str and dtype.startswith('|S')):
                fill_value = ''
            if dtype == int:
                fill_value = 0
            if dtype == bool:
                fill_value = False

        # set up counts_superdict
        counts = {region: np.tile(np.array(fill_value, dtype=dtype),
                                  [len(self.pixelmap[region]),
                                   len(self.pixelmap[region])])
                  for region in region_order}

        # fill counts_superdict
        for fflj_id, value in df_slice.iteritems():
            # resolve left and right fragment names
            left_name, right_name = self._split_index(fflj_id)

            # look up names in the reverse pixelmap
            region, left_index = self.reverse_pixelmap[left_name]
            other_region, right_index = self.reverse_pixelmap[right_name]

            # skip trans contacts
            if region != other_region:
                continue

            # fill value
            counts[region][left_index, right_index] = value
            counts[region][right_index, left_index] = value

        # squeeze trivial levels of the returned object
        if len(region_order) == 1:
            return counts[region_order[0]]
        return counts

    @staticmethod
    def _split_index(index):
        """
        Splits a row index value (FFLJ ID) into the individual fragment names.

        Currently this assumes the separator is '_' and that each fragment name
        has an equal number of '_'s, but this function should be used to do the
        splitting in case this changes in the future.

        Parameters
        ----------
        index : str
            The row index value (FFLJ ID) to split.

        Returns
        -------
        (str, str)
            The names of the interacting fragments.
        """
        pieces = index.split('_')
        return ('_'.join(pieces[:len(pieces)/2]),
                '_'.join(pieces[len(pieces)/2:]))

    @staticmethod
    def _resolve_sep(filename='', sep=None):
        """
        Utility method to resolve tablular file separator.

        Parameters
        ----------
        filename : str
            The filename.
        sep : str, optional
            The separator if one was specified, None otherwise.

        Returns
        -------
        str
            The resolved separator.
        """
        if sep is not None:
            return sep
        if filename.endswith('tsv'):
            return '\t'
        if filename.endswith('csv'):
            return ','
        return '\t'

    @staticmethod
    def _make_repinfo(reps, conditions):
        """
        Create a repinfo object given a list of rep names and condition names.

        Parameters
        ----------
        reps : list of str
            The replicate names as strings.
        conditions : list of str
            The condition names as strings.

        Returns
        -------
        pd.DataFrame
            The repinfo object.
        """
        condition_map = infer_level_mapping(reps, conditions)
        conditions = map(condition_map.__getitem__, reps)
        return pd.DataFrame(zip(reps, conditions),
                            columns=['replicate', 'condition']) \
            .set_index('replicate')

    def apply_per_region(self, fn, inputs, outputs, initial_values=0.0,
                         **kwargs):
        """
        Apply a function over the Dataset on a per-region basis.

        Parameters
        ----------
        fn : Callable
            The function to apply. It should take in pd.Series's or
            pd.DataFrames as its args, in the same order as inputs, and it
            should return 1D vectors, in the same order as outputs.
        inputs : list of (str or tuple of str)
            The list of columns to pass as inputs to fn. Use a tuple of strings
            to access hierarchical columns. Omit the secound level of a
            hierarchical column to pass all replicates to fn as a single
            pd.DataFrame. A single string or tuple will be wrapped in a list
            automatically.
        outputs : list of (str or tuple of str)
            Names of output columns to be added to the Dataset. Use a tuple of
            strings to create hierarchical columns.
        initial_values : list of any
            The values with which the new columns will be temporarily
            initialized. This should control the dtype of the new columns.
        """
        # promote all singleton args to list
        if type(inputs) != list:
            inputs = [inputs]
        if type(outputs) != list:
            outputs = [outputs]
        if type(initial_values) != list:
            initial_values = [initial_values] * len(outputs)

        # initialize output columns
        for i in range(len(outputs)):
            self.df[outputs[i]] = initial_values[i]

        # apply per region
        for region in self.pixelmap:
            # inject region kwarg if fn accepts it
            k = dict(kwargs)
            if 'region' in inspect.getargspec(fn)[0]:
                k['region'] = region

            # call fn
            results = fn(*[self.df.loc[self.df.region == region, inputs[i]]
                           for i in range(len(inputs))], **k)
            if type(results) not in [tuple, list]:
                results = [results]
            for i in range(len(outputs)):
                self.df.loc[self.df.region == region, outputs[i]] = results[i]

    def apply_per_replicate(self, fn, inputs, outputs, **kwargs):
        """
        Applies a function over the Dataset on a per-replicate basis.

        Parameters
        ----------
        fn : Callable
            The function to apply. It should take in pd.Series's as its args, in
            the same order as inputs, and it should return 1D vectors, in the
            same order as outputs.
        inputs : list of (str or tuple of str)
            The list of columns to pass as inputs to fn. Use a tuple of strings
            to access hierarchical columns. At least one input must refer to the
            top level of a hierarchical column, the first such column
            encountered will be used to determine the replicates to apply over.
            Non-hierarchical columns, or hierarchical columns fully specified by
            a tuple of strings will be broadcast across all replicates.
        outputs : list of str
            Names of top-level output columns to be added to the Dataset. The
            second level will be automatically filled in with the replicate
            names.
        """
        # promote all singleton args to list
        if type(inputs) != list:
            inputs = [inputs]
        if type(outputs) != list:
            outputs = [outputs]

        # identify reps (sub-columns of first hierarchical column)
        reps = None
        for i in range(len(inputs)):
            if hasattr(self.df[inputs[i]], 'columns'):
                reps = self.df[inputs[i]].columns
                break
        if reps is None:
            raise ValueError('none of the input columns are hierarchical')

        # apply per replicate
        for rep in reps:
            # inject rep kwarg if fn accepts it
            k = dict(kwargs)
            if 'rep' in inspect.getargspec(fn)[0]:
                k['rep'] = rep

            # call fn
            results = fn(*[self.df.loc[:, (inputs[i], rep)]
                           if hasattr(self.df[inputs[i]], 'columns')
                           else self.df.loc[:, inputs[i]]
                           for i in range(len(inputs))], **k)
            if type(results) not in [tuple, list]:
                results = [results]
            for i in range(len(outputs)):
                self.df.loc[:, (outputs[i], rep)] = results[i]

    def apply_per_replicate_per_region(self, fn, inputs, outputs,
                                       initial_values=0.0, **kwargs):
        """
        Applies a function over the Dataset on a per-replicate, per-region
        basis.

        Parameters
        ----------
        fn : Callable
            The function to apply. It should take in pd.Series's as its args, in
            the same order as inputs, and it should return 1D vectors, in the
            same order as outputs.
        inputs : list of (str or tuple of str)
            The list of columns to pass as inputs to fn. Use a tuple of strings
            to access hierarchical columns. At least one input must refer to the
            top level of a hierarchical column, the first such column
            encountered will be used to determine the replicates to apply over.
            Non-hierarchical columns, or hierarchical columns fully specified by
            a tuple of strings will be broadcast across all replicates.
        outputs : list of str
            Names of top-level output columns to be added to the Dataset. The
            second level will be automatically filled in with the replicate
            names.
        initial_values : list of any
            The values with which the new columns will be temporarily
            initialized. This should control the dtype of the new columns.
        """
        # promote inputs and outputs to list
        if type(inputs) != list:
            inputs = [inputs]
        if type(outputs) != list:
            outputs = [outputs]

        # identify reps and hierarchical columns
        reps = None
        for i in range(len(inputs)):
            if hasattr(self.df[inputs[i]], 'columns'):
                reps = self.df[inputs[i]].columns
                break
        if reps is None:
            raise ValueError('none of the input columns are hierarchical')

        # loop over reps
        for rep in reps:
            # inject rep kwarg if fn accepts it
            k = dict(kwargs)
            if 'rep' in inspect.getargspec(fn)[0]:
                k['rep'] = rep

            # apply per region
            self.apply_per_region(
                fn,
                [(inputs[i], rep)
                 if hasattr(self.df[inputs[i]], 'columns')
                 else inputs[i]
                 for i in range(len(inputs))],
                [(outputs[i], rep)
                 for i in range(len(outputs))],
                initial_values=initial_values,
                **k)

    def apply_across_replicates(self, fn, inputs, outputs, **kwargs):
        """
        Applies a matrix-to-matrix function over the Dataset.

        This is useful for functions that don't operate independently on each
        replicate of the Dataset.

        The main advantage of this function is that it handles the unboxing of
        the replicates after a matrix-to-matrix function is applied. If you are
        looking to apply a matrix-to-vector function over the Dataset, you can
        do it with a one-liner, assigning the vector result(s) to the new
        column(s) immediately.

        Parameters
        ----------
        fn : Callable
            The function to apply. It should take in np.ndarrays as its inputs
            and return np.ndarrays with the same size and shape. If some inputs
            are specified as individual columns, they will be passed to fn as
            np.ndarrays shaped as column vectors.
        inputs : list of (str or tuple of str)
            The list of columns to pass as inputs to fn. Use a tuple of strings
            to access hierarchical columns. At least one input must refer to the
            top level of a hierarchical column, the first such column
            encountered will be used to determine the replicates to apply over.
            Non-hierarchical columns, or hierarchical columns fully specified by
            a tuple of strings will be passed to fn as column vectors.
        outputs : list of str
            Names of top-level output columns to be added to the Dataset. The
            second level will be automatically filled in with the replicate
            names.
        """
        # promote all singleton args to list
        if type(inputs) != list:
            inputs = [inputs]
        if type(outputs) != list:
            outputs = [outputs]

        # identify reps (sub-columns of first hierarchical column)
        reps = None
        for i in range(len(inputs)):
            if hasattr(self.df[inputs[i]], 'columns'):
                reps = self.df[inputs[i]].columns
                break
        if reps is None:
            raise ValueError('none of the input columns are hierarchical')

        # apply fn
        results = fn(*[self.df.loc[:, inputs[i]].as_matrix()
                       if hasattr(self.df[inputs[i]], 'columns')
                       else self.df.loc[:, inputs[i]].as_matrix()[:, np.newaxis]
                       for i in range(len(inputs))], **kwargs)

        # promote results to list
        if type(results) not in [tuple, list]:
            results = [results]

        # unbox results
        for i in range(len(outputs)):
            for j in range(len(reps)):
                self.df.loc[:, (outputs[i], reps[j])] = results[i][:, j]

    def apply_across_replicates_per_region(self, fn, inputs, outputs,
                                           initial_values=0.0, **kwargs):
        """
        Applies a matrix-to-matrix function over the Dataset in a per-region
        manner.

        This is useful for functions that don't operate independently on each
        replicate of the Dataset, but which operate independently on each region
        of the Dataset.

        The main advantage of this function is that it handles the unboxing of
        the replicates after a matrix-to-matrix function is applied. If you are
        looking to apply a matrix-to-vector function over the Dataset in a
        per-region manner, you can do it with apply_per_region(), feeding a
        hierarchical column as an input.

        Parameters
        ----------
        fn : Callable
            The function to apply. It should take in np.ndarrays as its inputs
            and return np.ndarrays with the same size and shape. If some inputs
            are specified as individual columns, they will be passed to fn as
            np.ndarrays shaped as column vectors.
        inputs : list of (str or tuple of str)
            The list of columns to pass as inputs to fn. Use a tuple of strings
            to access hierarchical columns. At least one input must refer to the
            top level of a hierarchical column, the first such column
            encountered will be used to determine the replicates to apply over.
            Non-hierarchical columns, or hierarchical columns fully specified by
            a tuple of strings will be passed to fn as column vectors.
        outputs : list of str
            Names of top-level output columns to be added to the Dataset. The
            second level will be automatically filled in with the replicate
            names.
        initial_values : list of any
            The values with which the new columns will be temporarily
            initialized. This should control the dtype of the new columns.
        """
        # promote all singleton args to list
        if type(inputs) != list:
            inputs = [inputs]
        if type(outputs) != list:
            outputs = [outputs]
        if type(initial_values) != list:
            initial_values = [initial_values] * len(outputs)

        # identify reps (sub-columns of first hierarchical column)
        reps = None
        for i in range(len(inputs)):
            if hasattr(self.df[inputs[i]], 'columns'):
                reps = self.df[inputs[i]].columns
                break
        if reps is None:
            raise ValueError('none of the input columns are hierarchical')

        # initialize output columns
        for i in range(len(outputs)):
            for j in range(len(reps)):
                self.df[outputs[i], reps[j]] = initial_values[i]

        # apply per region
        for region in self.pixelmap:
            # inject region kwarg if fn accepts it
            k = dict(kwargs)
            if 'region' in inspect.getargspec(fn)[0]:
                k['region'] = region

            # call fn
            results = fn(*[
                self.df.loc[self.df.region == region, inputs[i]].as_matrix()
                if hasattr(self.df[inputs[i]], 'columns')
                else (self.df.loc[self.df.region == region, inputs[i]]
                      .as_matrix()[:, np.newaxis])
                for i in range(len(inputs))], **k)
            if type(results) not in [tuple, list]:
                results = [results]
            for i in range(len(outputs)):
                for j in range(len(reps)):
                    self.df.loc[self.df.region == region,
                                (outputs[i], reps[j])] = results[i][:, j]

    def dropna(self, name='counts', reps=None):
        """
        Drops NA's from the underlying dataframe.

        Parameters
        ----------
        name : str
            The name of the column to decide to drop based on.
        reps : list of str, optional
            If name refers to a hierarchial column, pass a list of rep names to
            only drop based on these reps. Pass None to drop based on the
            presence of an NA in any rep. If name does not refer to a
            hierarchical column this kwarg is ignored.
        """
        # check for hierarchical column
        if hasattr(self.df[name], 'columns'):
            # resolve reps for hierarchical column
            if reps is None:
                reps = self.df[name].columns

            # generate subset
            subset = [(name, rep) for rep in reps]
        else:
            subset = [name]

        # drop
        self.df.dropna(subset=subset, inplace=True)
