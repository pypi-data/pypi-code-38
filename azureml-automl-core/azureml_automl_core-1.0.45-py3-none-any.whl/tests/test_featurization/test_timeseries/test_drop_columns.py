import unittest
import pandas as pd
from pandas.util.testing import assert_frame_equal

from azureml.automl.core.featurizer.transformer.timeseries.drop_columns import DropColumns
from azureml.automl.core.featurizer.transformer.timeseries.forecasting_pipeline \
    import (AzureMLForecastPipeline, AzureMLForecastPipelineExecutionType)
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame


class TestFTKMLTransformersDropColumns(unittest.TestCase):
    """
    Unit tests for the DropColumns transform.

    Test column drop using the transform method and also as
    part of a forecast pipeline
    """

    def setUp(self):
        test_df = pd.DataFrame({'Date': pd.date_range('1/1/2011', periods=12, freq='M'),
                                'Type': 6 * ['a'] + 6 * ['b'],
                                'MainValue': range(12),
                                'AuxValue1': range(1, 13),
                                'AuxValue2': range(2, 14)})

        self.test_tsdf = TimeSeriesDataFrame(data=test_df,
                                             grain_colnames=['Type'],
                                             time_colname='Date',
                                             ts_value_colname='MainValue')

    def test_drop_grain(self):
        """
        Try to drop the column defining the grain. It shouldn't work!
        """
        drop_step = DropColumns('Type')
        out_tsdf = drop_step.transform(self.test_tsdf)
        out_column_names = list(out_tsdf.columns) + list(out_tsdf.index.names)

        self.assertTrue('Type' in out_column_names)

    def test_drop_time_index(self):
        """
        Try to drop the time index. It shouldn't work!
        """
        drop_step = DropColumns('Date')
        out_tsdf = drop_step.transform(self.test_tsdf)
        out_column_names = list(out_tsdf.columns) + list(out_tsdf.index.names)

        self.assertTrue('Date' in out_column_names)

    def test_drop_value(self):
        """
        Try to drop the value column. It shouldn't work!
        """
        drop_step = DropColumns('MainValue')
        out_tsdf = drop_step.transform(self.test_tsdf)
        out_column_names = list(out_tsdf.columns) + list(out_tsdf.index.names)

        self.assertTrue('MainValue' in out_column_names)

    def test_drop_empty_string(self):
        """
        Test the case when the drop columns list is an empty string
        """
        drop_step = DropColumns('')
        out_tsdf = drop_step.transform(self.test_tsdf)
        self.assertTrue(set(self.test_tsdf.columns) == set(out_tsdf.columns))

        # check that a column named '' is dropped as specified if it exists
        df_with_empty_string_col = pd.DataFrame(
            {'Date': pd.date_range('1/1/2011', periods=6, freq='D'),
             'Grain': [1] * 3 + [2] * 3,
             '': ['c', 'a', 't', 'd', 'o', 'g'],
             'Value': [0] * 6
             })

        tsdf_with_empty_string_col = TimeSeriesDataFrame(
            df_with_empty_string_col,
            time_colname='Date',
            grain_colnames=['Grain'],
            ts_value_colname='Value')

        without_empty_tsdf = drop_step.transform(tsdf_with_empty_string_col)
        expected_out_columns = set(tsdf_with_empty_string_col.columns).difference(set(['']))
        self.assertTrue(set(without_empty_tsdf.columns) == expected_out_columns)

        # check that remaining data is preserved
        wo_empty_df = df_with_empty_string_col.drop('', axis=1)
        wo_empty_df.set_index(['Date', 'Grain'], inplace=True)
        assert_frame_equal(without_empty_tsdf, wo_empty_df)

    def test_drop_empty_list(self):
        """Test the case when the drop columns list is an empty list."""
        drop_step = DropColumns([])
        out_tsdf = drop_step.transform(self.test_tsdf)

        self.assertTrue(set(self.test_tsdf.columns) == set(out_tsdf.columns))

    def test_drop_one_column(self):
        """Try dropping one auxiliary column."""
        drop_step = DropColumns('AuxValue1')
        out_tsdf = drop_step.transform(self.test_tsdf)

        self.assertFalse('AuxValue1' in out_tsdf.columns)

    def test_drop_multiple_columns(self):
        """Try dropping multiple auxiliary columns."""
        drop_step = DropColumns(['AuxValue1', 'AuxValue2'])
        out_tsdf = drop_step.transform(self.test_tsdf)

        self.assertFalse('AuxValue1' in out_tsdf.columns or
                         'AuxValue2' in out_tsdf.columns)

    def test_drop_one_column_in_pipeline(self):
        """Plug the drop transform into a pipeline and try removing a column."""
        # Need to add a dummy transform at the end since the transforms
        # executor excludes transforms on the last step
        pipeline = AzureMLForecastPipeline(steps=[
            ('drop_AuxValue1', DropColumns('AuxValue1')),
            ('drop_dummy', DropColumns(''))])
        out_tsdf = pipeline.execute_pipeline_op(
            AzureMLForecastPipelineExecutionType.transforms, self.test_tsdf)

        self.assertFalse('AuxValue1' in out_tsdf.columns)

    def test_drop_multiple_columns_in_pipeline(self):
        """Plug multiple drop transforms into a pipeline to remove multiple columns."""
        # Need to add a dummy transform at the end since the transforms
        # executor excludes transforms on the last step
        pipeline = AzureMLForecastPipeline(steps=[
            ('drop_AuxValue1', DropColumns('AuxValue1')),
            ('drop_AuxValue2', DropColumns('AuxValue2')),
            ('drop_dummy', DropColumns(''))])
        out_tsdf = pipeline.execute_pipeline_op(
            AzureMLForecastPipelineExecutionType.transforms, self.test_tsdf)

        self.assertFalse('AuxValue1' in out_tsdf.columns or
                         'AuxValue2' in out_tsdf.columns)


if __name__ == '__main__':
    unittest.main()
