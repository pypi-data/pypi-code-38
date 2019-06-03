# encoding: utf-8

"""Cube-partition objects.

A cube-partition allows cubes of various dimensionality to be processed in a uniform
way. For example, a 2D cube becomes a `_Slice` object, but a 3D cube is "sliced" into
a sequence of `_Slice` objects; a `_Slice` object corresponds to a crosstab, and can be
operated on consistently whether it is "alone" or one of a sequence that came from a 3D
cube.

Cube-partition objects are typically used for display of secondary analysis, often in an
Excel spreadsheet but also other formats.

The three types of cube partition are the *slice*, *strand*, and *nub*, which are 2D,
1D, and 0D respectively.
"""

from __future__ import division

import numpy as np

from cr.cube.enum import DIMENSION_TYPE as DT
from cr.cube.frozen_min_base_size_mask import MinBaseSizeMask
from cr.cube.measures.new_pairwise_significance import NewPairwiseSignificance
from cr.cube.matrix import TransformedMatrix
from cr.cube.scalar import MeansScalar
from cr.cube.stripe import TransformedStripe
from cr.cube.util import lazyproperty


class CubePartition(object):
    """A slice, a strand, or a nub drawn from a cube-response.

    These represent 2, 1, or 0 dimensions of a cube, respectively.
    """

    @classmethod
    def factory(
        cls,
        cube,
        slice_idx=0,
        transforms=None,
        population=None,
        ca_as_0th=None,
        mask_size=0,
    ):
        """Return slice, strand, or nub object appropriate to passed parameters."""
        if cube.ndim == 0:
            return _Nub(cube)
        if cube.ndim == 1 or ca_as_0th:
            return _Strand(
                cube, transforms, population, ca_as_0th, slice_idx, mask_size
            )
        return _Slice(cube, slice_idx, transforms, population, mask_size)


class _Slice(object):
    """2D cube partition.

    A slice represents the cross-tabulation of two dimensions, often, but not
    necessarily contributed by two different variables. A CA variable has two dimensions
    which can be crosstabbed in a slice.
    """

    def __init__(self, cube, slice_idx, transforms, population, mask_size):
        self._cube = cube
        self._slice_idx = slice_idx
        self._transforms_arg = transforms
        self._population = population
        self._mask_size = mask_size

    # ---interface ---------------------------------------------------

    @lazyproperty
    def base_counts(self):
        return np.array([row.base_values for row in self._matrix.rows])

    @lazyproperty
    def column_base(self):
        return np.array([column.base for column in self._matrix.columns]).T

    @lazyproperty
    def column_index(self):
        """ndarray of column index percentages.

        The index values represent the difference of the percentages to the
        corresponding baseline values. The baseline values are the univariate
        percentages of the corresponding variable.
        """
        return np.array([row.column_index for row in self._matrix.rows])

    @lazyproperty
    def column_labels(self):
        """Sequence of str column element names suitable for use as column headings."""
        return tuple(column.label for column in self._matrix.columns)

    @lazyproperty
    def column_margin(self):
        return np.array([column.margin for column in self._matrix.columns]).T

    @lazyproperty
    def column_percentages(self):
        return self.column_proportions * 100

    @lazyproperty
    def column_proportions(self):
        return np.array([col.proportions for col in self._matrix.columns]).T

    @lazyproperty
    def columns_dimension_name(self):
        """str name assigned to columns-dimension.

        Reflects the resolved dimension-name transform cascade.
        """
        return self._columns_dimension.name

    @lazyproperty
    def columns_dimension_type(self):
        """Member of `cr.cube.enum.DIMENSION_TYPE` describing columns dimension."""
        return self._columns_dimension.dimension_type

    @lazyproperty
    def counts(self):
        return np.array([row.values for row in self._matrix.rows])

    @lazyproperty
    def dimension_types(self):
        """Sequence of member of `cr.cube.enum.DIMENSION_TYPE` for each dimension.

        Items appear in rows-dimension, columns-dimension order.
        """
        return tuple(dimension.dimension_type for dimension in self.dimensions)

    @lazyproperty
    def dimensions(self):
        """tuple containing (rows_dimension, columns_dimension) for this slice.

        Both items are `cr.cube.dimension.Dimension` objects.
        """
        # TODO: I question whether the dimensions should be published. Whatever folks
        # might need to know, like types or whatever, should be available as individual
        # properties. The dimensions are kind of an internal, especially since they
        # won't necessarily match the returned data-matrix in terms of element-order and
        # presence.
        return self._dimensions

    @lazyproperty
    def inserted_column_idxs(self):
        return tuple(
            i for i, column in enumerate(self._matrix.columns) if column.is_insertion
        )

    @lazyproperty
    def inserted_row_idxs(self):
        return tuple(i for i, row in enumerate(self._matrix.rows) if row.is_insertion)

    @lazyproperty
    def means(self):
        return np.array([row.means for row in self._matrix.rows])

    @lazyproperty
    def min_base_size_mask(self):
        return MinBaseSizeMask(self, self._mask_size)

    @lazyproperty
    def name(self):
        """str name assigned to this slice.

        A slice takes the name of its rows-dimension.
        """
        return self.rows_dimension_name

    @lazyproperty
    def ndim(self):
        """int count of dimensions for this slice, unconditionally 2."""
        return 2

    @lazyproperty
    def pairwise_indices(self):
        alpha = self._transforms_dict.get("pairwise_indices", {}).get("alpha", 0.05)
        only_larger = self._transforms_dict.get("pairwise_indices", {}).get(
            "only_larger", True
        )
        return NewPairwiseSignificance(
            self, alpha=alpha, only_larger=only_larger
        ).pairwise_indices

    @lazyproperty
    def pairwise_significance_tests(self):
        """tuple of _ColumnPairwiseSignificance tests.

        Result has as many elements as there are columns in the slice. Each
        significance test contains `p_vals` and `t_stats` (ndarrays that represent
        probability values and statistical scores).
        """
        return tuple(
            NewPairwiseSignificance(self).values[column_idx]
            for column_idx in range(len(self._matrix.columns))
        )

    @lazyproperty
    def population_counts(self):
        return (
            self.table_proportions * self._population * self._cube.population_fraction
        )

    @lazyproperty
    def pvals(self):
        return np.array([row.pvals for row in self._matrix.rows])

    @lazyproperty
    def row_base(self):
        return np.array([row.base for row in self._matrix.rows])

    @lazyproperty
    def row_labels(self):
        return tuple(row.label for row in self._matrix.rows)

    @lazyproperty
    def row_margin(self):
        return np.array([row.margin for row in self._matrix.rows])

    @lazyproperty
    def row_percentages(self):
        return self.row_proportions * 100

    @lazyproperty
    def row_proportions(self):
        return np.array([row.proportions for row in self._matrix.rows])

    @lazyproperty
    def rows_dimension_description(self):
        """str description assigned to rows-dimension.

        Reflects the resolved dimension-description transform cascade.
        """
        return self._rows_dimension.description

    @lazyproperty
    def rows_dimension_fills(self):
        """sequence of RGB str like "#def032" fill colors for row elements.

        The values reflect the resolved element-fill transform cascade. The length and
        ordering of the sequence correspond to the rows in the slice, including
        accounting for insertions and hidden rows.
        """
        return tuple(row.fill for row in self._matrix.rows)

    @lazyproperty
    def rows_dimension_name(self):
        """str name assigned to rows-dimension.

        Reflects the resolved dimension-name transform cascade.
        """
        return self._rows_dimension.name

    @lazyproperty
    def rows_dimension_type(self):
        """Member of `cr.cube.enum.DIMENSION_TYPE` specifying type of rows dimension."""
        return self._rows_dimension.dimension_type

    @lazyproperty
    def scale_means_column(self):
        if np.all(np.isnan(self._columns_dimension_numeric)):
            return None

        inner = np.nansum(self._columns_dimension_numeric * self.counts, axis=1)
        not_a_nan_index = ~np.isnan(self._columns_dimension_numeric)
        denominator = np.sum(self.counts[:, not_a_nan_index], axis=1)
        return inner / denominator

    @lazyproperty
    def scale_means_column_margin(self):
        if np.all(np.isnan(self._columns_dimension_numeric)):
            return None

        column_margin = self.column_margin
        if len(column_margin.shape) > 1:
            # Hack for MR, where column margin is a table. Figure how to
            # fix with subclassing
            column_margin = column_margin[0]

        not_a_nan_index = ~np.isnan(self._columns_dimension_numeric)
        return np.nansum(self._columns_dimension_numeric * column_margin) / np.sum(
            column_margin[not_a_nan_index]
        )

    @lazyproperty
    def scale_means_row(self):
        if np.all(np.isnan(self._rows_dimension_numeric)):
            return None
        inner = np.nansum(self._rows_dimension_numeric[:, None] * self.counts, axis=0)
        not_a_nan_index = ~np.isnan(self._rows_dimension_numeric)
        denominator = np.sum(self.counts[not_a_nan_index, :], axis=0)
        return inner / denominator

    @lazyproperty
    def scale_means_row_margin(self):
        if np.all(np.isnan(self._rows_dimension_numeric)):
            return None

        row_margin = self.row_margin
        if len(row_margin.shape) > 1:
            # Hack for MR, where row margin is a table. Figure how to
            # fix with subclassing
            row_margin = row_margin[:, 0]

        not_a_nan_index = ~np.isnan(self._rows_dimension_numeric)
        return np.nansum(self._rows_dimension_numeric * row_margin) / np.sum(
            row_margin[not_a_nan_index]
        )

    @lazyproperty
    def shape(self):
        return self.counts.shape

    @lazyproperty
    def summary_pairwise_indices(self):
        alpha = self._transforms_dict.get("pairwise_indices", {}).get("alpha", 0.05)
        only_larger = self._transforms_dict.get("pairwise_indices", {}).get(
            "only_larger", True
        )
        return NewPairwiseSignificance(
            self, alpha=alpha, only_larger=only_larger
        ).summary_pairwise_indices

    @lazyproperty
    def table_base(self):

        # We need to prune/order by both dimensions
        if self.dimension_types == (DT.MR, DT.MR):
            # TODO: Remove property from the assembler, when we figure out the pruning
            # by both rows and columns
            return self._matrix.table_base

        # We need to prune/order by rows
        if self.dimension_types[0] == DT.MR:
            return np.array([row.table_base for row in self._matrix.rows])

        # We need to prune/order by columns
        if self.dimension_types[1] == DT.MR:
            return np.array([column.table_base for column in self._matrix.columns])

        # No pruning or reordering since single value
        return self._matrix.table_base_unpruned

    @lazyproperty
    def table_base_unpruned(self):
        return self._matrix.table_base_unpruned

    @lazyproperty
    def table_margin(self):
        # We need to prune/order by both dimensions
        if self.dimension_types == (DT.MR, DT.MR):
            # TODO: Remove property from the assembler, when we figure out the pruning
            # by both rows and columns
            return self._matrix.table_margin

        # We need to prune/order by rows
        if self.dimension_types[0] == DT.MR:
            return np.array([row.table_margin for row in self._matrix.rows])

        # We need to prune/order by columns
        if self.dimension_types[1] == DT.MR:
            return np.array([column.table_margin for column in self._matrix.columns])

        # No pruning or reordering since single value
        return self._matrix.table_margin_unpruned
        # return self._matrix.table_margin

    @lazyproperty
    def table_margin_unpruned(self):
        return self._matrix.table_margin_unpruned

    @lazyproperty
    def table_name(self):
        """Provides differentiated name for each stacked table of a 3D cube."""
        if self._cube.ndim < 3:
            return None

        title = self._cube.name
        table_name = self._cube.dimensions[0].valid_elements[self._slice_idx].label
        return "%s: %s" % (title, table_name)

    @lazyproperty
    def table_percentages(self):
        return self.table_proportions * 100

    @lazyproperty
    def table_proportions(self):
        return np.array([row.table_proportions for row in self._matrix.rows])

    @lazyproperty
    def zscore(self):
        return np.array([row.zscore for row in self._matrix.rows])

    # ---implementation (helpers)-------------------------------------

    @lazyproperty
    def _columns_dimension(self):
        return self._dimensions[1]

    @lazyproperty
    def _columns_dimension_numeric(self):
        return np.array([column.numeric for column in self._matrix.columns])

    @lazyproperty
    def _dimensions(self):
        """tuple of (rows_dimension, columns_dimension) Dimension objects."""
        return tuple(
            dimension.apply_transforms(transforms)
            for dimension, transforms in zip(
                self._cube.dimensions[-2:], self._transform_dicts
            )
        )

    @lazyproperty
    def _matrix(self):
        """The TransformedMatrix object for this slice."""
        return TransformedMatrix.matrix(self._cube, self._dimensions, self._slice_idx)

    @lazyproperty
    def _rows_dimension(self):
        return self._dimensions[0]

    @lazyproperty
    def _rows_dimension_numeric(self):
        return np.array([row.numeric for row in self._matrix.rows])

    @lazyproperty
    def _transform_dicts(self):
        """Pair of dict (rows_dimension_transforms, columns_dimension_transforms).

        Resolved from the `transforms` argument provided on construction, it always has
        two members, even when one or both dimensions have no transforms. The transforms
        item is an empty dict (`{}`) when no transforms are specified for that
        dimension.
        """
        return (
            self._transforms_dict.get("rows_dimension", {}),
            self._transforms_dict.get("columns_dimension", {}),
        )

    @lazyproperty
    def _transforms_dict(self):
        """dict containing all transforms for this slice, provided as `transforms` arg.

        This value is an empty dict (`{}`) when no transforms were specified on
        construction.
        """
        return self._transforms_arg if self._transforms_arg is not None else {}


class _Strand(object):
    """1D cube-partition.

    A strand can arise from a 1D cube (non-CA univariate), or as a partition of
    a CA-cube (CAs are 2D) into a sequence of 1D partitions, one for each subvariable.
    """

    def __init__(self, cube, transforms, population, ca_as_0th, slice_idx, mask_size):
        self._cube = cube
        self._transforms_arg = transforms
        self._population = population
        self._ca_as_0th = ca_as_0th
        # TODO: see if we really need this.
        self._slice_idx = slice_idx
        self._mask_size = mask_size

    @lazyproperty
    def base_counts(self):
        return tuple(row.base_value for row in self._stripe.rows)

    @lazyproperty
    def bases(self):
        """Sequence of weighted base for each row."""
        return tuple(np.broadcast_to(self.table_margin, self._shape))

    @lazyproperty
    def counts(self):
        return tuple(row.count for row in self._stripe.rows)

    @lazyproperty
    def dimension_types(self):
        """Sequence of `cr.cube.enum.DIMENSION_TYPE` member for each dimension.

        Length one in this case, containing only rows-dimension type.
        """
        # TODO: remove need for this in exporter, at least for 1D case.
        return (self._rows_dimension.dimension_type,)

    @lazyproperty
    def dimensions(self):
        """tuple of (row,) Dimension object."""
        # TODO: I question whether the dimensions should be published. Whatever folks
        # might need to know, like types or whatever, should be available as individual
        # properties. The dimensions are kind of an internal, especially since they
        # won't necessarily match the returned data-matrix in terms of element-order and
        # presence.
        return (self._rows_dimension,)

    @lazyproperty
    def inserted_row_idxs(self):
        # TODO: add integration-test coverage for this.
        return tuple(i for i, row in enumerate(self._stripe.rows) if row.is_insertion)

    @lazyproperty
    def means(self):
        return tuple(row.mean for row in self._stripe.rows)

    @lazyproperty
    def min_base_size_mask(self):
        mask = self.table_base < self._mask_size
        strand_shape = (self.row_count,)

        if self.table_base.shape == strand_shape:
            return mask

        return np.logical_or(np.zeros(strand_shape, dtype=bool), mask)

    @lazyproperty
    def name(self):
        return self.rows_dimension_name

    @lazyproperty
    def ndim(self):
        """int count of dimensions for this strand, unconditionally 1."""
        return 1

    @lazyproperty
    def population_counts(self):
        return tuple(
            self._table_proportions_as_array
            * self._population
            * self._cube.population_fraction
        )

    @lazyproperty
    def row_base(self):
        return np.array([row.base for row in self._stripe.rows])

    @lazyproperty
    def row_count(self):
        return len(self._stripe.rows)

    @lazyproperty
    def row_labels(self):
        return tuple(row.label for row in self._stripe.rows)

    @lazyproperty
    def row_margin(self):
        return np.array([row.margin for row in self._stripe.rows])

    @lazyproperty
    def rows_dimension_fills(self):
        """sequence of RGB str like "#def032" fill colors for row elements.

        The values reflect the resolved element-fill transform cascade. The length and
        ordering of the sequence correspond to the rows in the slice, including
        accounting for insertions and hidden rows.
        """
        return tuple(row.fill for row in self._stripe.rows)

    @lazyproperty
    def rows_dimension_name(self):
        """str name assigned to rows-dimension.

        Reflects the resolved dimension-name transform cascade.
        """
        return self._rows_dimension.name

    @lazyproperty
    def rows_dimension_type(self):
        """Member of DIMENSION_TYPE enum describing type of rows dimension."""
        return self._rows_dimension.dimension_type

    @lazyproperty
    def scale_mean(self):
        """float mean of numeric-value applied to elements, or None.

        This value is `None` when no row-elements have a numeric-value assigned.
        """
        numeric_values = self._numeric_values

        # ---return None when no row-element has been assigned a numeric value. This
        # ---avoids a division-by-zero error.
        if np.all(np.isnan(numeric_values)):
            return None

        # ---produce operands with rows without numeric values removed. Notably, this
        # ---excludes subtotal rows.
        is_a_number_mask = ~np.isnan(numeric_values)
        numeric_values = numeric_values[is_a_number_mask]
        counts = self._counts_as_array[is_a_number_mask]

        # ---calculate numerator and denominator---
        total_numeric_value = np.sum(numeric_values * counts)
        total_count = np.sum(counts)

        # ---overall scale-mean is the quotient---
        return total_numeric_value / total_count

    @lazyproperty
    def table_base(self):
        """1D, single-element ndarray (like [3770])."""
        # For MR strands, table base is also a strand, since subvars never collapse.
        # We need to keep the ordering and hiding as in rows dimension. All this
        # information is already accessible in the underlying rows property
        # of the `_stripe`.
        if self.dimension_types[0] == DT.MR:
            return np.array([row.table_base for row in self._stripe.rows])

        # TODO: shouldn't this just be the regular value for a strand? Maybe change to
        # that if exporter always knows when it's getting this from a strand. The
        # ndarray "wrapper" seems like unnecessary baggage when we know it will always
        # be a scalar.
        return self._stripe.table_base_unpruned

    @lazyproperty
    def table_base_unpruned(self):
        return self._stripe.table_base_unpruned

    @lazyproperty
    def table_margin(self):
        # For MR strands, table base is also a strand, since subvars never collapse.
        # We need to keep the ordering and hiding as in rows dimension. All this
        # information is already accessible in the underlying rows property
        # of the `_stripe`.
        if self.dimension_types[0] == DT.MR:
            return np.array([row.table_margin for row in self._stripe.rows])

        return self._stripe.table_margin_unpruned
        # return self._stripe.table_margin

    @lazyproperty
    def table_margin_unpruned(self):
        return self._stripe.table_margin_unpruned

    @lazyproperty
    def table_name(self):
        """Only for CA-as-0th case, provides differentiated names for stacked tables."""
        if not self._ca_as_0th:
            return None

        title = self._cube.name
        table_name = self._cube.dimensions[0].valid_elements[self._slice_idx].label
        return "%s: %s" % (title, table_name)

    @lazyproperty
    def table_percentages(self):
        return tuple(self._table_proportions_as_array * 100)

    @lazyproperty
    def table_proportions(self):
        return tuple(row.table_proportions for row in self._stripe.rows)

    @lazyproperty
    def unweighted_bases(self):
        """Sequence of base count for each row, before weighting.

        When the rows dimension is multiple-response, each value is different,
        reflecting the base for that individual subvariable. In all other cases, the
        table base is repeated for each row.
        """
        return tuple(np.broadcast_to(self.table_base, self._shape))

    # ---implementation (helpers)-------------------------------------

    @lazyproperty
    def _counts_as_array(self):
        """1D ndarray of count for each row."""
        return np.array([row.count for row in self._stripe.rows])

    @lazyproperty
    def _numeric_values(self):
        """Array of numeric-value for each element in rows dimension.

        The items in the array can be numeric or np.nan, which appears for an inserted
        row (subtotal) or where the row-element has been assigned no numeric value.
        """
        return np.array([row.numeric_value for row in self._stripe.rows])

    @lazyproperty
    def _rows_dimension(self):
        """Dimension object for the single dimension of this strand."""
        return self._cube.dimensions[-1].apply_transforms(self._row_transforms_dict)

    @lazyproperty
    def _row_transforms_dict(self):
        """Transforms dict for the single (rows) dimension of this strand."""
        transforms_dict = {} if self._transforms_arg is None else self._transforms_arg
        return transforms_dict.get("rows_dimension", {})

    @lazyproperty
    def _shape(self):
        """The shape this strand would have it it were an array (which it isn't)."""
        return (self.row_count,)

    @lazyproperty
    def _stripe(self):
        """The post-transforms 1D data-partition for this strand."""
        return TransformedStripe.stripe(
            self._cube, self._rows_dimension, self._ca_as_0th, self._slice_idx
        )

    @lazyproperty
    def _table_proportions_as_array(self):
        return np.array([row.table_proportions for row in self._stripe.rows])


class _Nub(object):
    """0D slice."""

    def __init__(self, cube):
        self._cube = cube

    @lazyproperty
    def means(self):
        return self._scalar.means

    @lazyproperty
    def ndim(self):
        """int count of dimensions, unconditionally 0 for a Nub."""
        return 0

    @lazyproperty
    def table_base(self):
        return self._scalar.table_base

    # ---implementation (helpers)-------------------------------------

    @lazyproperty
    def _scalar(self):
        """The pre-transforms data-array for this slice."""
        return MeansScalar(self._cube.counts, self._cube.base_counts)
