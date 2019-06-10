# Copyright (c) Microsoft Corporation. All rights reserved.
"""Classes for collecting summary statistics on the data produced by a Dataflow."""
from collections import namedtuple, OrderedDict
from typing import Any, Dict, List, Tuple, Union
import json
from .engineapi.api import EngineAPI
from ._pandas_helper import have_pandas
from .engineapi.typedefinitions import (ActivityReference, DataField, ExecuteInspectorCommonArguments,
                                        FieldType, InspectorArguments, ProfileResult, Moments, Quantiles, HistogramBin,
                                        ValueCount, TypeCount, STypeCount, SType, HistogramCompareMethod, StringLengthCount)
from .value import value_from_field

_MAX_ROW_COUNT = 2**31 - 1

ValueCountEntry = namedtuple('ValueCountEntry', ['value', 'count'])
STypeCountEntry = namedtuple('STypeCountEntry', ['stype', 'count'])
HistogramBucket = namedtuple('HistogramBucket', ['lower_bound', 'upper_bound', 'count'])
TypeCountEntry = namedtuple('TypeCountEntry', ['type', 'count'])

class DTypes(Dict):
    def __init__(self, dict):
        super().__init__(dict)

    def __repr__(self):
        column_types = ["""{0!s:<25}{1!s:<16}""".format(column, dtype, end=' ') for (column, dtype) in self.items()]
        return '\n'.join(column_types)

class _Inspector:
    @classmethod
    def _from_execution(
        cls,
        engine_api: EngineAPI,
        context: ActivityReference,
        inspector: Union[str, 'InspectorArguments']):
        if isinstance(inspector, str):
            inspector = json.loads(inspector)
        return engine_api.execute_inspector(ExecuteInspectorCommonArguments(
            context=context,
            inspector_arguments=inspector,
            offset=0,
            row_count=_MAX_ROW_COUNT))

class DataProfile:
    """
    A DataProfile collects summary statistics on the data produced by a Dataflow.

    :var columns: Profile information for each result column.
    :vartype columns: Dict[str, ColumnProfile]
    """

    def __init__(self):
        self.columns = OrderedDict()

    @classmethod
    def _from_execution(cls,
                        engine_api: EngineAPI,
                        context: ActivityReference,
                        include_stype_counts: bool = False,
                        number_of_histogram_bins = 10,
                        include_average_spaces_count: bool = False,
                        include_string_lengths: bool = False):
        table_inspector = engine_api.execute_inspector(ExecuteInspectorCommonArguments(
            context=context,
            inspector_arguments=InspectorArguments(inspector_type='Microsoft.DPrep.TableInspector', arguments={
                "includeSTypeCounts": include_stype_counts,
                "numberOfHistogramBins": number_of_histogram_bins,
                "includeAverageSpacesCount": include_average_spaces_count,
                "includeStringLengths": include_string_lengths
            }),
            offset=0,
            row_count=_MAX_ROW_COUNT))
        column_names = [column_definition.id for column_definition in table_inspector.column_definitions]
        rows = table_inspector.rows_data.rows

        FieldAndValue = namedtuple('FieldAndValue', ['field', 'value'])
        def values_for_column(fields):
            return {
                name: FieldAndValue(field=field,
                                    value=value_from_field(field) if field is not None and field.type != FieldType.NULL and field.type != FieldType.ERROR else None)
                for name, field in zip(column_names, fields)
            }

        dp = cls()
        dp.columns = OrderedDict([(row[0].value, ColumnProfile(values_for_column(row))) for row in rows])
        return dp

    @classmethod
    def _from_json(cls, json_str):
        dp = cls()
        pr_list = json.loads(json_str)
        for col in pr_list:
            dp.columns[col['columnName']] = ColumnProfile.from_pod(col)
        return dp

    @property
    def dtypes(self) -> Dict[str, FieldType]:
        """
        Column data types.

        :return: A dictionary, where key is the column name and value is :class:`azureml.dataprep.FieldType`.
        """
        return DTypes({column: column_profile.type for (column, column_profile) in self.columns.items()})

    @property
    def shape(self) -> Tuple[int,int]:
        """
        Shape of the data produced by the Dataflow.

        :return: Tuple of row count and column count.
        """
        return (self.row_count, len(self.columns.keys()))

    @property
    def row_count(self) -> int:
        """
        Count of rows in this DataProfile.

        :return: Count of rows.
        :rtype: int
        """
        for column_profile in self.columns.values():
            # return count of rows from first column profile we iterate over.
            return int(column_profile.count)

    def _to_json(self):
        # convert to list to preserve order
        columns_list = [v for v in self.columns.values()]
        return json.dumps(columns_list, cls=_DataProfileEncoder)

    @property
    def stype_counts(self) -> Dict[str, List[Tuple[SType,int]]]:
        """
        Columns with semantic types found, each with a list of the found semantic types.

        .. remarks::

            Only columns where semantic types were found are included in the dictionary, which means the lists are never empty.
            The lists are each ordered descending by the count of values found that matched the semantic type.

        :return: A dictionary, where key is the column name and value is a list of :class:`azureml.dataprep.STypeCountEntry`.
        """
        if len(self.columns) == 0 or next(iter(self.columns.values())).stype_counts is None:
            return None

        return {
            column: column_profile.stype_counts
            for (column, column_profile) in self.columns.items()
            if len(column_profile.stype_counts) > 0
        }

    def compare(self, other_profile, include_columns=None, exclude_columns=None, histogram_compare_method = HistogramCompareMethod.WASSERSTEIN):
        """
        Compares the current profile with other_dataset profile. With the exception of Histogram difference, all are subtract '-' operations.
        For histogram difference, it is the statistical distance scaled [0, ∞]. If there are no histograms, the default value is None.

        :param other_profile: Another data profile for comparison.
        :type other_profile: DataProfile
        :param include_columns: List of column names to be included in comparison.
        :type include_columns: List[str]
        :param exclude_columns: List of column names to be excluded in comparison.
        :type exclude_columns: List[str]
        :param histogram_compare_method: Enum describing the method.
        :type histogram_compare_method: HistogramCompareMethod
        :return: Difference of the profiles.
        :rtype: DataProfileDifference
        """
        from .profile_compare import _ProfileCompare
        return _ProfileCompare.compare_profiles(self, other_profile, include_columns, exclude_columns, histogram_compare_method)

    def _repr_html_(self):
        """
        HTML representation for IPython.
        """
        if not have_pandas():
            return None
        else:
            import pandas as pd

        stats = [column_profile.get_stats() for column_profile in self.columns.values()]
        return pd.DataFrame(stats, index=self.columns.keys(), columns=ColumnProfile._STAT_COLUMNS).to_html()

    def __repr__(self):
        return '\n'.join(map(str, self.columns.values()))


class ColumnProfile(ProfileResult):
    """
    A ColumnProfile collects summary statistics on a particular column of data produced by a Dataflow.

    :var column_name: Name of column
    :vartype column_name: str
    :var type: Type of values in column
    :vartype type: FieldType

    :var min: Minimum value
    :vartype min: Any
    :var max: Maximum value
    :vartype max: Any
    :var count: Count of rows
    :vartype count: int
    :var missing_count: Count of rows with a missing value
    :vartype missing_count: int
    :var not_missing_count: Count of rows with a value
    :vartype not_missing_count: int
    :var error_count: Count of rows with an error value
    :vartype error_count: int
    :var percent_missing: Percent of the values that are missing
    :vartype percent_missing: float
    :var empty_count: Count of rows with empty string value
    :vartype empty_count: int

    :var lower_quartile: Estimated 25th-percentile value
    :vartype lower_quartile: float
    :var median: Estimated median value
    :vartype median: float
    :var upper_quartile: Estimated 75th-percentile value
    :vartype upper_quartile: float
    :var mean: Mean
    :vartype mean: float
    :var std: Standard deviation
    :vartype std: float
    :var variance: Variance
    :vartype variance: float
    :var skewness: Skewness
    :vartype skewness: float
    :var kurtosis: Kurtosis
    :vartype kurtosis: float
    :var quantiles: Dictionary of quantiles
    :vartype quantiles: Dict[float, float]

    :var value_counts: Counts of discrete values in the data; None if too many values.
    :vartype value_counts: List[ValueCountEntry]
    :var type_counts: Counts of discrete types in the data.
    :vartype type_counts: List[TypeCountEntry]
    :var histogram: Histogram buckets showing the distribution of the data; None if data is non-numeric.
    :vartype histogram: List[HistogramBucket]
    :var stype_counts: List of semantic type names and counts of values that matched. None if the profile did not contain semantic type counts. Can be an empty list when there were no matches.
    :vartype stype_counts: List[STypeCountEntry]
    """
    def __init__(self, values: Dict[str, Any] = None):
        if values is None:
            super(ColumnProfile, self).__init__()
        else:
            field_type = FieldType(values.get('type').value)
            is_numeric = ColumnProfile._is_numeric_type(field_type)
            super(ColumnProfile, self).__init__(
                column_name=values.get('Column').value,
                type=field_type,
                count=values.get('count').value,
                empty_count=values.get('num_empty').value,
                error_count=values.get('num_errors').value,
                missing_count=values.get('num_missing').value,
                not_missing_count=values.get('num_not_missing').value,
                percent_missing=values.get('%missing').value,
                max=values.get('max').field,
                min=values.get('min').field,
                moments=ColumnProfile._prepare_moments(values) if is_numeric else None,
                quantiles=ColumnProfile._prepare_quartiles(values) if is_numeric else None,
                histogram=ColumnProfile._prepare_histogram(values.get('histogram')),
                type_counts=ColumnProfile._prepare_type_counts(values.get('type_count').value),
                value_counts=ColumnProfile._prepare_value_counts(values.get('value_count').value),
                s_type_counts=ColumnProfile._prepare_stype_counts(values.get('stype_count').value),
                unique_values=values.get('unique_values').value,
                average_spaces_count=values.get('average_spaces_count').value if values.get('average_spaces_count') is not None else None,
                string_lengths=ColumnProfile._prepare_length_counts(values.get('string_lengths').value) if values.get('string_lengths') is not None else None
            )
        self._quantiles_dict = None

    @property
    def name(self) -> str:
        """
        (Deprecated. Use column_name instead.)
        """
        return self.column_name

    @property
    def kurtosis(self) -> float:
        return None if self.moments is None else self.moments.kurtosis

    @property
    def mean(self) -> float:
        return None if self.moments is None else self.moments.mean

    @property
    def skewness(self) -> float:
        return None if self.moments is None else self.moments.skewness

    @property
    def std(self) -> float:
        return None if self.moments is None else self.moments.standard_deviation

    @property
    def variance(self) -> float:
        return None if self.moments is None else self.moments.variance

    @property
    def quantiles(self) -> Dict[float, float]:
        if self._quantiles_dict is None:
            quantiles = super(ColumnProfile, self).quantiles
            self._quantiles_dict = OrderedDict([
                (0.001, None if quantiles is None else quantiles.p0_d1),
                (0.01, None if quantiles is None else quantiles.p1),
                (0.05, None if quantiles is None else quantiles.p5),
                (0.25, None if quantiles is None else quantiles.p25),
                (0.50, None if quantiles is None else quantiles.p50),
                (0.75, None if quantiles is None else quantiles.p75),
                (0.95, None if quantiles is None else quantiles.p95),
                (0.99, None if quantiles is None else quantiles.p99),
                (0.999, None if quantiles is None else quantiles.p99_d9)])
        return self._quantiles_dict

    @property
    def lower_quartile(self) -> float:
        return self.quantiles[0.25]

    @property
    def median(self) -> float:
        return self.quantiles[0.50]

    @property
    def upper_quartile(self) -> float:
        return self.quantiles[0.75]

    @property
    def max(self) -> object:
        return value_from_field(super(ColumnProfile, self).max)

    @property
    def min(self) -> object:
        return value_from_field(super(ColumnProfile, self).min)

    @property
    def value_counts(self) -> List[ValueCountEntry]:
        vcs = super(ColumnProfile, self).value_counts
        return None if vcs is None else [ValueCountEntry(value=value_from_field(vc.value),
                                                         count=vc.count) for vc in vcs]

    @property
    def type_counts(self) -> List[TypeCountEntry]:
        tcs = super(ColumnProfile, self).type_counts
        return None if tcs is None else [TypeCountEntry(type=tc.type,
                                                        count=tc.count) for tc in tcs]

    @property
    def histogram(self) -> List[HistogramBucket]:
        bins = super(ColumnProfile, self).histogram
        return None if bins is None else [HistogramBucket(lower_bound=b.lower_bound,
                                                          upper_bound=b.upper_bound,
                                                          count=b.count) for b in bins]

    @property
    def stype_counts(self) -> List[STypeCountEntry]:
        stcs = super(ColumnProfile, self).s_type_counts
        return None if stcs is None else [STypeCountEntry(stype=stc.s_type,
                                                        count=stc.count) for stc in stcs]

    @property
    def _is_numeric(self) -> bool:
        return ColumnProfile._is_numeric_type(self.type)

    @staticmethod
    def _is_numeric_type(t: FieldType) -> bool:
        return t == FieldType.INTEGER or t == FieldType.DECIMAL

    @staticmethod
    def _prepare_moments(values: Dict[str, Any]):
        return Moments(kurtosis=values.get('kurtosis').value,
                       mean=values.get('mean').value,
                       skewness=values.get('skewness').value,
                       standard_deviation=values.get('standard_deviation').value,
                       variance=values.get('variance').value)

    @staticmethod
    def _prepare_quartiles(values: Dict[str, Any]):
        return Quantiles(p0_d1=values.get('0.1%').value,
                         p1=values.get('1%').value,
                         p5=values.get('5%').value,
                         p25=values.get('25%').value,
                         p50=values.get('50%').value,
                         p75=values.get('75%').value,
                         p95=values.get('95%').value,
                         p99=values.get('99%').value,
                         p99_d9=values.get('99.9%').value)

    @staticmethod
    def _prepare_value_counts(entries: List[Any]):
        if entries and len(entries) > 0:
            return [ValueCount(value=entry['value'],
                               count=int(entry['count'])) for entry in entries]
        return None

    @staticmethod
    def _prepare_type_counts(entries: List[Any]):
        return [TypeCount(type=FieldType(entry['type']),
                          count=float(entry['count'])) for entry in entries]

    @staticmethod
    def _prepare_stype_counts(entries: List[Any]):
        if entries is not None and len(entries) > 0:
            result = [
                STypeCount(s_type = entry['sType'], count = int(entry['count']))
                for entry in entries
                if int(entry['count']) > 0 # empty list when none match
            ]
            result.sort(key=lambda ec: -ec.count)
            return result

        return None

    @staticmethod
    def _prepare_length_counts(entries: List[Any]):
        if entries is not None and len(entries) > 0:
            result = [
                StringLengthCount(length = entry['length'], count = int(entry['count']))
                for entry in entries
            ]
            result.sort(key=lambda ec: ec.length)
            return result

        return None

    @staticmethod
    def _prepare_histogram(fields: List[Dict[str, Any]]):
        if fields.value:
            values = (f['value'] for f in fields.value)
            def generate_buckets():
                last_position = None
                for position, count in zip(values, values):
                    if last_position is not None:
                        yield HistogramBin(lower_bound=last_position, upper_bound=position, count=count)
                    last_position = position
            histogram = list(generate_buckets())
            if len(histogram) > 0:
                return histogram
        return None

    def get_stats(self):
        return [
            self.type, self.min, self.max, self.count, self.missing_count, self.not_missing_count, self.percent_missing,
            self.error_count, self.empty_count, self.unique_values or '',
            self.quantiles[0.001] if self._is_numeric else '',
            self.quantiles[0.01] if self._is_numeric else '',
            self.quantiles[0.05] if self._is_numeric else '',
            self.quantiles[0.25] if self._is_numeric else '',
            self.quantiles[0.50] if self._is_numeric else '',
            self.quantiles[0.75] if self._is_numeric else '',
            self.quantiles[0.95] if self._is_numeric else '',
            self.quantiles[0.99] if self._is_numeric else '',
            self.quantiles[0.999] if self._is_numeric else '',
            self.mean if self._is_numeric else '',
            self.std if self._is_numeric else '',
            self.variance if self._is_numeric else '',
            self.skewness if self._is_numeric else '',
            self.kurtosis if self._is_numeric else ''
        ]

    _STAT_COLUMNS = [
        'Type', 'Min', 'Max', 'Count', 'Missing Count', 'Not Missing Count', 'Percent Missing', 'Error Count',
        'Empty Count', 'Unique Values', '0.1% Quantile (est.)', '1% Quantile (est.)', '5% Quantile (est.)', '25% Quantile (est.)', '50% Quantile (est.)',
        '75% Quantile (est.)', '95% Quantile (est.)', '99% Quantile (est.)', '99.9% Quantile (est.)', 'Mean', 'Standard Deviation', 'Variance',
        'Skewness', 'Kurtosis'
    ]

    def _repr_html_(self):
        """
        HTML representation for IPython.
        """
        if not have_pandas():
            return None
        else:
            import pandas as pd
        return pd.DataFrame(self.get_stats(), index=ColumnProfile._STAT_COLUMNS, columns=['Statistics']).to_html()

    def __repr__(self):
        result = """\
ColumnProfile:
    column_name: {0}
    type: {1}

    min: {2}
    max: {3}
    count: {4}
    missing_count: {5}
    not_missing_count: {6}
    percent_missing: {7}
    error_count: {8}
    empty_count: {9}
    unique_values: {10}

""".format(self.column_name,
           self.type,
           self.min,
           self.max,
           self.count,
           self.missing_count,
           self.not_missing_count,
           self.percent_missing,
           self.error_count,
           self.empty_count,
           self.unique_values or '')

        if self._is_numeric:
            result += """\

    Quantiles (est.):
         0.1%: {0!s}
           1%: {1!s}
           5%: {2!s}
          25%: {3!s}
          50%: {4!s}
          75%: {5!s}
          95%: {6!s}
          99%: {7!s}
        99.9%: {8!s}

    mean: {9!s}
    std: {10!s}
    variance: {11!s}
    skewness: {12!s}
    kurtosis: {13!s}
""".format(self.quantiles[0.001],
           self.quantiles[0.01],
           self.quantiles[0.05],
           self.quantiles[0.25],
           self.quantiles[0.50],
           self.quantiles[0.75],
           self.quantiles[0.95],
           self.quantiles[0.99],
           self.quantiles[0.999],
           self.mean,
           self.std,
           self.variance,
           self.skewness,
           self.kurtosis)

        return result


class _DataProfileEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ColumnProfile):
            return obj.to_pod()
        if isinstance(obj, DataField):
            return obj.to_pod()
        return super(_DataProfileEncoder, self).default(obj)
