#  ---------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  ---------------------------------------------------------
"""compare helper class."""
from .typeconversions import FieldType
from .errorhandlers import NumpyImportError
from ._pandas_helper import have_numpy
from .engineapi.typedefinitions import (
    HistogramCompareMethod,
    QuantilesDifference,
    ColumnProfileDifference,
    MomentsDifference,
    ValueCountDifference,
    DataProfileDifference)


class _ProfileCompare:
    """Library code to help with compare operations."""

    @staticmethod
    def compare_profiles(
        lhs_profile,
        rhs_profile,
        include_columns,
        exclude_columns,
        histogram_compare_method
        ):
        """
            If include and exclude columns are None, comparison is on full profile by finding matched columns.
            If both Include and exclude columns are provided then comparison will consider include first then apply exclude list.
            If only exclude column list is provided then columns remaining after exclusion will be compared.
        """
        matched_column_profiles = list()
        unmatched_column_profiles = list()
        selected_column_list = _ProfileCompare._select_columns_for_compare(lhs_profile, rhs_profile, include_columns, exclude_columns)

        _ProfileCompare._find_lhs_matched_columns(
            lhs_profile,
            rhs_profile,
            matched_column_profiles,
            unmatched_column_profiles,
            selected_column_list)

        _ProfileCompare._find_rhs_unmatched_columns(lhs_profile,
                                                    rhs_profile,
                                                    unmatched_column_profiles,
                                                    selected_column_list)

        list_column_difference = _ProfileCompare._compare_column_profile(
            matched_column_profiles,
            histogram_compare_method)
        ds_profile_diff = DataProfileDifference()
        ds_profile_diff.column_profile_difference = list_column_difference
        ds_profile_diff.unmatched_column_profiles = unmatched_column_profiles

        return ds_profile_diff

    @staticmethod
    def _select_columns_for_compare(lhs_profile, rhs_profile, include_columns, exclude_columns):
        """
        """
        column_list = list()
        for column in lhs_profile.columns.values():
            column_list.append(column.name)

        for r_column in rhs_profile.columns.values():
            if r_column.name not in column_list:
                column_list.append(column.name)

        if include_columns is None and exclude_columns is None:
            return column_list
        elif include_columns is not None and exclude_columns is not None:
            filtered_list = list([x for x in include_columns if x not in exclude_columns])
            if filtered_list is None or len(filtered_list) == 0:
                raise Exception("Both Include and Exclude column lists match")
            else:
                return list([x for x in filtered_list if x in column_list])
        elif include_columns is not None and exclude_columns is None:
            return list([x for x in include_columns if x in column_list])
        else:
            return list([x for x in column_list if x not in exclude_columns])
        pass

    @staticmethod
    def _find_lhs_matched_columns(
        lhs_profile,
        rhs_profile,
        matched_column_profiles,
        unmatched_column_profiles,
        selected_column_list
    ):
        """
        """
        for lhs_column_profile in lhs_profile.columns.values():
            foundMatch = False
            if lhs_column_profile.name in selected_column_list:
                for rhs_column_profile in rhs_profile.columns.values():
                    if lhs_column_profile.name == rhs_column_profile.name and lhs_column_profile.type == rhs_column_profile.type:
                        matched_column_profiles.append((lhs_column_profile, rhs_column_profile))
                        foundMatch = True
                        break
                if not foundMatch:
                    unmatched_column_profiles.append((lhs_column_profile.name, 1))
        pass

    @staticmethod
    def _find_rhs_unmatched_columns(
        lhs_profile,
        rhs_profile,
        unmatched_column_profiles,
        selected_column_list
    ):
        for rhs_column_profile in rhs_profile.columns.values():
            found_match = False
            if rhs_column_profile.name in selected_column_list:
                for lhs_column_profile in lhs_profile.columns.values():
                    if lhs_column_profile.name == rhs_column_profile.name and lhs_column_profile.type == rhs_column_profile.type:
                        found_match = True
                        break
            if not found_match:
                 unmatched_column_profiles.append((rhs_column_profile.name, - 1))

    @staticmethod
    def _compare_column_profile(columns: list, histogram_distance_method: HistogramCompareMethod):
        list_column_difference = list()
        for lhs_column_profile, rhs_column_profile in columns:
            col_diff = ColumnProfileDifference()
            col_diff.name = lhs_column_profile.name
            col_diff.column_type = lhs_column_profile.type
            col_diff.difference_in_count_in_percent = _ProfileCompare._compare_count_in_percent(
                lhs_column_profile.count,
                rhs_column_profile.count)
            col_diff.difference_in_empty_value_rows_in_percent = _ProfileCompare._compare_count_in_percent(
                lhs_column_profile.empty_count,
                rhs_column_profile.empty_count)
            col_diff.difference_in_error_value_rows_in_percent = _ProfileCompare._compare_count_in_percent(
                lhs_column_profile.error_count,
                rhs_column_profile.error_count)
            col_diff.difference_in_missing_value_rows_in_percent = _ProfileCompare._compare_count_in_percent(
                lhs_column_profile.missing_count,
                rhs_column_profile.missing_count)
            col_diff.difference_in_not_missing_value_rows_in_percent = _ProfileCompare._compare_count_in_percent(
                lhs_column_profile.not_missing_count,
                rhs_column_profile.not_missing_count)
            if lhs_column_profile.type in({FieldType.INTEGER, FieldType.DECIMAL}):
                col_diff.difference_in_min = lhs_column_profile.min - rhs_column_profile.min
                col_diff.difference_in_max = lhs_column_profile.max - rhs_column_profile.max
                diff_in_moments = MomentsDifference()
                diff_in_moments.difference_in_mean = lhs_column_profile.moments.mean - rhs_column_profile.moments.mean
                diff_in_moments.difference_in_standard_deviation = lhs_column_profile.moments.standard_deviation - rhs_column_profile.moments.standard_deviation
                diff_in_moments.difference_in_kurtosis = lhs_column_profile.moments.kurtosis - rhs_column_profile.moments.kurtosis
                diff_in_moments.difference_in_skewness = lhs_column_profile.moments.skewness - rhs_column_profile.moments.skewness
                diff_in_moments.difference_in_variance = lhs_column_profile.moments.variance - rhs_column_profile.moments.variance
                col_diff.difference_in_moments = diff_in_moments
                col_diff.difference_in_median = lhs_column_profile.median - rhs_column_profile.median
                col_diff.difference_in_quantiles = _ProfileCompare._compare_quantiles(
                    lhs_column_profile.quantiles,
                    rhs_column_profile.quantiles)
            elif lhs_column_profile.type == FieldType.DATE:
                col_diff.difference_in_min = (lhs_column_profile.min - rhs_column_profile.min).total_seconds()
                col_diff.difference_in_max = (lhs_column_profile.max - rhs_column_profile.max).total_seconds()
            else:
                # TODO implement string comparisions in future versions.
                # min / max / std / mean / mode / skewness diff should consider categorical values
                pass

            if lhs_column_profile.type != FieldType.DATE:
                col_diff.difference_in_histograms = _ProfileCompare._compare_histogram_bins(
                    lhs_column_profile=lhs_column_profile,
                    rhs_column_profile=rhs_column_profile,
                    histogram_distance_method=histogram_distance_method)
            col_diff.difference_in_value_counts_in_percent = _ProfileCompare._compare_value_counts(
                lhs_column_profile.value_counts,
                rhs_column_profile.value_counts,
                lhs_column_profile.type)

            list_column_difference.append(col_diff)
        return list_column_difference

    @staticmethod
    def _compare_quantiles(lhs_quantiles, rhs_quantiles):

        q_diff = QuantilesDifference()
        q_diff.difference_in_p0_d1 = lhs_quantiles[0.001] - rhs_quantiles[0.001]
        q_diff.difference_in_p1 = lhs_quantiles[0.01] - rhs_quantiles[0.01]
        q_diff.difference_in_p25 = lhs_quantiles[0.25] - rhs_quantiles[0.25]
        q_diff.difference_in_p5 = lhs_quantiles[0.05] - rhs_quantiles[0.05]
        q_diff.difference_in_p50 = lhs_quantiles[0.5] - rhs_quantiles[0.5]
        q_diff.difference_in_p75 = lhs_quantiles[0.75] - rhs_quantiles[0.75]
        q_diff.difference_in_p95 = lhs_quantiles[0.95] - rhs_quantiles[0.95]
        q_diff.difference_in_p99 = lhs_quantiles[0.99] - rhs_quantiles[0.99]
        q_diff.difference_in_p99_d9 = lhs_quantiles[0.999] - rhs_quantiles[0.999]

        return q_diff

    @staticmethod
    def _compare_value_counts(lhs_value_counts, rhs_value_counts, fieldType):
        return_dict = list()
        value_list = list()
        if lhs_value_counts is None and rhs_value_counts is None:
            return None
        elif lhs_value_counts is None or len(lhs_value_counts) == 0:
            for value_count in rhs_value_counts:
                percent = _ProfileCompare._compare_count_in_percent(0, value_count.count)
                _ProfileCompare._set_valuecountdiff(fieldType, return_dict, value_count.value, percent)
            return return_dict
        elif rhs_value_counts is None or len(rhs_value_counts) == 0:
            for value_count in lhs_value_counts:
                percent = _ProfileCompare._compare_count_in_percent(value_count.count, 0)
                _ProfileCompare._set_valuecountdiff(fieldType, return_dict, value_count.value, percent)
            return return_dict
        else:
            lhs_count = len(lhs_value_counts)
            rhs_count = len(rhs_value_counts)

        if lhs_count > rhs_count:
            for r_value_count in rhs_value_counts:
                for l_value_count in lhs_value_counts:
                    if r_value_count.value == l_value_count.value:
                        percent = _ProfileCompare._compare_count_in_percent(
                            l_value_count.count, r_value_count.count)
                        _ProfileCompare._set_valuecountdiff(fieldType, return_dict, l_value_count.value, percent)
                        value_list.append(r_value_count.value)
                        break
                if r_value_count.value not in value_list:
                    value_list.append(r_value_count.value)
                    _ProfileCompare._set_valuecountdiff(fieldType, return_dict, r_value_count.value, - r_value_count.count)

            for l_value_count in lhs_value_counts:
                if l_value_count.value not in value_list:
                    value_list.append(l_value_count.value)
                    _ProfileCompare._set_valuecountdiff(fieldType, return_dict, l_value_count.value, l_value_count.count)
        else:
            for l_value_count in lhs_value_counts:
                for r_value_count in rhs_value_counts:
                    if r_value_count.value == l_value_count.value:
                        percent = _ProfileCompare._compare_count_in_percent(
                            l_value_count.count, r_value_count.count)
                        _ProfileCompare._set_valuecountdiff(fieldType, return_dict, l_value_count.value, percent)
                        value_list.append(l_value_count.value)
                        break
                if l_value_count.value not in value_list:
                    _ProfileCompare._set_valuecountdiff(fieldType, return_dict, l_value_count.value, l_value_count.count)
                    value_list.append(l_value_count.value)

            for r_value_count in rhs_value_counts:
                if r_value_count.value not in value_list:
                    _ProfileCompare._set_valuecountdiff(fieldType, return_dict, r_value_count.value, - r_value_count.count)
                    value_list.append(r_value_count.value)
        return return_dict

    @staticmethod
    def _set_valuecountdiff(fieldType, return_dict, value, count):
        from .engineapi.typedefinitions import DataField
        valueCountDiff = ValueCountDifference()
        if(fieldType != FieldType.DATE):
            valueCountDiff.value = value
        else:
            date_value = value.strftime("%m/%d/%Y, %H:%M:%S")
            valueCountDiff.value = date_value

        valueCountDiff.difference_in_percent = count
        return_dict.append(valueCountDiff)

    @staticmethod
    def _compare_count_in_percent(lhs_count, rhs_count):
        """
            Always rhs_count - lhs_count and then find the percent deviation
        """
        if lhs_count == 0:
            return - rhs_count
        if rhs_count == 0:
            return lhs_count
        if lhs_count == rhs_count:
            return 0

        one_percent = rhs_count / 100
        diff = lhs_count - rhs_count
        return diff / one_percent

    @staticmethod
    def _compare_histogram_bins(lhs_column_profile, rhs_column_profile, histogram_distance_method):
        if not have_numpy():
            raise NumpyImportError()
        else:
            import numpy as np
        from scipy.stats import wasserstein_distance
        from scipy.stats import energy_distance

        if lhs_column_profile.histogram == None or rhs_column_profile.histogram == None:
            return None

        lhs_cdf_arry = []
        lhs_weights_arry = []
        rhs_cdf_arry = []
        rhs_weights_arry = []
        for bin in lhs_column_profile.histogram:
            lhs_cdf_arry.append((bin.lower_bound + bin.upper_bound)/2)
            lhs_weights_arry.append(bin.count)

        for bin in rhs_column_profile.histogram:
            rhs_cdf_arry.append((bin.lower_bound + bin.upper_bound)/2)
            rhs_weights_arry.append(bin.count)

        if not 0 < np.sum(lhs_weights_arry) < np.inf:
            lhs_weights_arry = None
        if not 0 < np.sum(rhs_weights_arry) < np.inf:
            rhs_weights_arry = None
        if histogram_distance_method.value == HistogramCompareMethod.WASSERSTEIN.value:
            return wasserstein_distance(lhs_cdf_arry, rhs_cdf_arry, lhs_weights_arry, rhs_weights_arry)
        elif histogram_distance_method.value == HistogramCompareMethod.ENERGY.value:
            return energy_distance(lhs_cdf_arry, rhs_cdf_arry, lhs_weights_arry, rhs_weights_arry)
        else:
            raise NotImplementedError()
