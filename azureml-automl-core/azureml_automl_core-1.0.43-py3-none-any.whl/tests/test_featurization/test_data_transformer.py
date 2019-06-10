from typing import Any, Optional
import copy
import logging
import unittest
import pickle
import sys
from unittest.mock import patch

from ddt import ddt, file_data
from sklearn.pipeline import make_pipeline
import pandas as pd
import numpy as np

from azureml.automl.core import preprocess as pp
from azureml.automl.core._experiment_observer import ExperimentObserver
from azureml.automl.core.column_purpose_detection import ColumnPurposeDetector
from azureml.automl.core.featurizer.transformer import TextFeaturizers
from azureml.automl.core.featurizer.transformer.data import AbstractWordEmbeddingsProvider
from automl.client.core.common import memory_utilities
from automl.client.core.common.exceptions import DataException

from .mock_identity_transformer import MockIdentityTransformer


class MockWordEmbeddingsProvider(AbstractWordEmbeddingsProvider):
    """Mock word embeddings provider for test usage."""

    def _get_model(self) -> Any:
        self.initialize()
        return self._model

    def _is_lower(self):
        pass

    def __init__(self, vector_size=10):
        """Mock word embeddings provider."""
        self._vector_size = vector_size
        super().__init__("")

    def _get_vector_size(self):
        """Gets vector size."""
        return self._vector_size

    def initialize(self) -> None:
        """
        Overridden method of the base class.

        :return: None
        """
        self._model = {}
        for i in range(self.vector_size):
            self._model[str(i)] = np.random.rand(self.vector_size)


class UnserializableLogger(logging.Logger):
    def __dict__(self):
        raise AssertionError('Object should not have been serialized.')

    def __getstate__(self):
        raise AssertionError('Object should not have been serialized.')

    def __setstate__(self, state):
        raise AssertionError('Object should not have been serialized.')

    def log(self, lvl, msg, *args, **kwargs):
        pass

    def write(self, msg):
        pass


class DataTransformerTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(DataTransformerTests, self).__init__(*args, **kwargs)
        logger = UnserializableLogger('')
        observer = ExperimentObserver(file_handler=logger)
        self.tr = pp.DataTransformer("classification", logger=logger, observer=observer)

    def test_transform_without_learn_and_fit(self):
        """
        Test that calling transform function on data transformer without
        executing learning method should result in an exception.
        """
        train_array = np.repeat(['cat', 'bear'], 100)
        train_df = pd.DataFrame(data=train_array)

        # Call to transform() should fail since learn was
        # not called
        with self.assertRaises(Exception):
            self.tr.transform(train_df)

    def test_fit_transform_with_learn_and_fit(self):
        """
        Test that calling transform function on data transformer after
        executing learning method should not result in an exception.
        """
        train_array = np.repeat(['cat', 'bear'], 100)
        train_df = pd.DataFrame(data=train_array)

        # Call to fit_transform() shouldn't fail since learn was
        # called
        self.tr.fit_transform(train_df)

        # Call to transform() shouldn't fail since learn was
        # called
        self.tr.transform(train_df)

    def test_fit_transform_with_learn_and_fit_with_memory_over_limit(self):
        """
        Test that calling transform function on data transformer after
        executing learning method should not result in an exception.
        """
        logger = UnserializableLogger('')
        observer = ExperimentObserver(file_handler=logger)
        tr = pp.DataTransformer("classification", logger=logger, observer=observer)
        idenitity_transformer = MockIdentityTransformer(memory_estimate=sys.maxsize)
        # print(idenitity_transformer.__class__)
        train_array = np.repeat(['cat', 'bear'], 100)
        train_df = pd.DataFrame(data=train_array)

        tr._add_test_transforms([(0, [idenitity_transformer], {'alias': '1'})])
        # Call to fit_transform() shouldn't fail since learn was
        # called
        tr.fit_transform(train_df)

        # Call to transform() shouldn't fail since learn was
        # called
        transformerd_data = tr.transform(train_df)
        self.assertEqual(train_df.shape, transformerd_data.shape)

        self.assertFalse(idenitity_transformer.if_transform_called)

    def test_fit_transform_with_learn_and_fit_with_memory_in_limit(self):
        """
        Test that calling transform function on data transformer after
        executing learning method should not result in an exception.
        """
        logger = UnserializableLogger('')
        observer = ExperimentObserver(file_handler=logger)
        tr = pp.DataTransformer("classification", logger=logger, observer=observer)
        idenitity_transformer = MockIdentityTransformer(memory_estimate=10)
        # print(idenitity_transformer.__class__)
        train_array = np.repeat(['cat', 'bear'], 100)
        train_df = pd.DataFrame(data=train_array)

        tr._add_test_transforms([(0, [idenitity_transformer], {'alias': '1'})])
        # Call to fit_transform() shouldn't fail since learn was
        # called
        tr.fit_transform(train_df)

        # Call to transform() shouldn't fail since learn was
        # called
        transformerd_data = tr.transform(train_df)
        self.assertEqual(train_df.shape[0], transformerd_data.shape[0])
        self.assertEqual(transformerd_data.shape[1], 2)
        self.assertTrue(idenitity_transformer.if_transform_called)

    def test_categorical_train_data_and_numerical_retrained_data(self):
        """
        The data transformer has been trained with some data which looks like
        categorical but is retrained with data which looks like numerical. The
        data transformer should transform the retrained data as categorical data.
        """
        # Categorical data
        nparr = np.repeat([0, 1, 2], 100)
        df = pd.DataFrame(nparr)
        expected_shape = (nparr.shape[0], 3)

        # Transform categorical data
        transformed_data = self.tr.fit_transform(df)
        self.assertTrue(transformed_data.shape == expected_shape)

        # Craft numerical like data
        nparr = np.array([1, 2, 3, 4])
        expected_shape = (nparr.shape[0], 4)
        df = pd.DataFrame(nparr)

        # Even this numerical data should be expanded as categorical data
        transformed_data = self.tr.fit_transform(df)
        self.assertTrue(transformed_data.shape == expected_shape)

    def test_numerical_train_data_and_categorical_retrained_data(self):
        """
        The data transformer has been trained with some data which looks like
        numerical but is retrained with data which looks like categorical. The
        data transformer should transform the retrained data as numerical data.
        """
        # Numerical data
        nparr = np.repeat([0, 1, 2], 10)
        df = pd.DataFrame(nparr)
        expected_shape = (nparr.shape[0], 1)

        # Transform numerical data
        transformed_data = self.tr.fit_transform(df)
        self.assertTrue(transformed_data.shape == expected_shape)

        # Craft categorical like data
        nparr = np.repeat([1, 2, 3], 100)
        expected_shape = (nparr.shape[0], 1)

        # Even this categorical data should be treated as numerical data
        df = pd.DataFrame(nparr)
        transformed_data = self.tr.fit_transform(df)
        self.assertTrue(transformed_data.shape == expected_shape)

    def test_transformer_with_different_column_number_exception(self):
        tr = copy.deepcopy(self.tr)
        nparr = np.repeat([0, 1, 2], 10)
        df = pd.DataFrame(nparr)
        tr.fit(df)
        transformed_data = pd.DataFrame([[0, 1], [0, 1]])
        with self.assertRaises(DataException) as de:
            tr.transform(transformed_data)
        self.assertIn("The fitted data has 2 columns but the input data has 1 columns.", str(de.exception))

    def test_transformer_with_different_column_name_exception(self):
        tr = copy.deepcopy(self.tr)
        nparr = np.repeat([0, 1, 2], 10)
        df = pd.DataFrame(nparr)
        tr.fit(df)
        transformed_data = pd.DataFrame(np.repeat([0, 1, 2], 10), columns=['a'])
        with self.assertRaises(DataException) as de:
            tr.transform(transformed_data)
        self.assertIn("Input column not found in the fitted columns.", str(de.exception))

    def test_transformer_with_different_convertable_data_type(self):
        tr = copy.deepcopy(self.tr)
        nparr = np.repeat([1, 2, 3], 10)
        df = pd.DataFrame(nparr)
        tr.fit(df)
        expected_data = tr.transform(df)
        transformed_input_data = pd.DataFrame(np.repeat([1, 2, 3], 10))
        transformed_input_data[0] = transformed_input_data[0].astype(np.double)
        transformed_data = tr.transform(transformed_input_data)
        self.assertTrue(expected_data.shape == transformed_data.shape)
        self.assertTrue(tr._columns_types_mapping is not None and len(tr._columns_types_mapping) > 0)

    def test_transformer_with_different_unconvertable_data_exception(self):
        tr = copy.deepcopy(self.tr)
        nparr = np.repeat([0, 1, 2], 10)
        df = pd.DataFrame(nparr)
        tr.fit(df)
        transformed_data = pd.DataFrame(np.repeat(['a', 'b', 'c'], 10))
        with self.assertRaises(DataException) as de:
            tr.transform(transformed_data)
        self.assertIn("Error converting the input column as column does not match the fitted column type.",
                      str(de.exception))


@ddt
class TransformTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TransformTests, self).__init__(*args, **kwargs)
        self.tr = pp.DataTransformer("classification")

    def test_numeric(self):
        # impute numeric data
        nparr = np.zeros((3, 4))
        nparr[0, 0] = np.nan
        nparr[0, 1] = 1
        nparr[0, 2] = 1
        nparr[0, 3] = 1
        df = pd.DataFrame(nparr)
        expected_output = np.zeros((3, 5))
        # Since we have nan in the first row which is > 0.01% of the data
        # We will end up adding a "is imputed" column and will have that
        # bit set for the first row
        expected_output[0, 1] = 1  # for the imputation marker
        expected_output[0, 2] = 1
        expected_output[0, 3] = 1
        expected_output[0, 4] = 1

        transformed_data = self.tr.fit_transform(df)
        self.assertTrue(np.all(transformed_data == expected_output))

    def test_catints(self):
        # ints that should be categorical
        nparr = np.zeros((3000, 4), dtype=int)
        nparr[0] = np.ones(4)
        df = pd.DataFrame(nparr)
        expected_shape = (nparr.shape[0], 4)

        transformed_data = self.tr.fit_transform(df)
        self.assertTrue(transformed_data.shape == expected_shape)

    def test_high_cardinality(self):
        text = [["foo", "bar"], ["foo2", "bar2"]]
        df = pd.DataFrame(text)
        # features would be foo, bar, foo2, oo2, ar2. foo and bar would get
        # ommitted since max_df cut off is 0.95
        y = np.array([0, 1])
        with self.assertRaises(ValueError):
            self.tr.fit_transform(df, y)

    def test_unichar_text(self):
        text = [["a", "b"], ["c", "d"]]
        df = pd.DataFrame(text)
        y = np.array([0, 1])
        # This is considered to be hashes because of unique cardinality
        with self.assertRaises(ValueError):
            self.tr.fit_transform(df, y)

    def test_dates(self):
        dates = [["2018-01-02", 2.], ["2018-02-01", 3.]]
        df = pd.DataFrame(dates)
        # dates year, month, day and hour go as features.
        # Floats are scaled by min max.
        expected_output = np.array([[2.018e3, 1, 2, 1, 2, 1, 1, 0, 0, 0, 2],
                                    [2.018e3, 2, 1, 3, 32, 1, 1, 0, 0, 0, 3]])
        self.assertTrue(np.all(self.tr.fit_transform(df) == expected_output))

    def test_wrong_dates(self):
        dates = ["2018-01-02", "-"]
        series = pd.Series(dates)
        dt = pp.DateTimeFeaturesTransformer()
        mindate = pd.Timestamp.min
        expected_output = np.array([
            [2.018e3, 1, 2, 1, 2, 1, 1, 0, 0, 0],
            [
                mindate.year,
                mindate.month,
                mindate.day,
                mindate.dayofweek,
                mindate.dayofyear,
                3,
                3,
                mindate.hour,
                mindate.minute,
                mindate.second
            ]
        ])
        self.assertTrue(np.all(dt.transform(series) == expected_output))

    def test_hashes_with_one_column_strings_with_safe_conversion_to_text(self):
        # test with strings having identical lengths
        n = 10000
        s1 = pd.Series(np.random.rand(n))
        df = pd.DataFrame(s1)

        df[0] = df[0].astype(str)
        transformed_data = self.tr.fit_transform(df)
        assert (transformed_data.shape[0] == n)

    @file_data("test_data_transformer_data.json")
    def test_hashes_with_one_column_strings_with_safe_convertion_to_text_okcupid_dataset(self, X):
        df = pd.DataFrame(X)
        transformed_data = self.tr.fit_transform(df)
        assert transformed_data is not None

    def test_hashes_multiple_columns(self):
        # Test with strings that are in multiple columns
        n = 100
        sl = pd.DataFrame(np.random.rand(n, 2))
        df = pd.DataFrame(sl)

        df[0] = df[0].astype(str)
        df[1] = df[1].astype(str)
        with self.assertRaises(ValueError):
            self.tr.fit_transform(df)

    def test_categoricals_with_single_category(self):
        # Test with training data
        train_set_category_array = np.repeat('bear', 100)
        train_df = pd.DataFrame(data=train_set_category_array)
        # Since there is only one category, there is no data to transform
        # so test is exception got thrown
        with self.assertRaises(ValueError):
            self.tr.fit_transform(train_df)

        # Test with test data
        test_set_category_array = np.array(['bear', 'bear'])
        # Since the fit stage failed, calling transform on test data
        # should throw an exception
        with self.assertRaises(Exception):
            self.tr.transform(test_set_category_array)

    def test_categoricals_with_two_categories(self):
        # Test if training data is correctly label encoded
        train_set_category_array = np.repeat(['cat', 'bear'], 100)
        expected_train_set_label_array = np.repeat([1, 0], 100).transpose()
        expected_train_set_label_array.shape = (
            len(expected_train_set_label_array), 1)
        train_df = pd.DataFrame(data=train_set_category_array)
        single_category_transformed_data = self.tr.fit_transform(train_df)
        self.assertTrue(np.all(expected_train_set_label_array ==
                               single_category_transformed_data))

        # Test if test data is correctly label encoded
        test_set_category_array = np.array(['bear', 'cat'])
        expected_test_set_label_array = np.array([[0], [1]])
        actual_test_set_label_array = self.tr.transform(test_set_category_array)
        self.assertTrue(np.all(expected_test_set_label_array ==
                               actual_test_set_label_array))

    def test_newsgroups_transform(self):
        from sklearn.datasets import fetch_20newsgroups
        from sklearn.model_selection import train_test_split

        removedata = ('headers', 'footers', 'quotes')
        categories = ['alt.atheism', 'talk.religion.misc', 'comp.graphics', 'sci.space']

        data_train = fetch_20newsgroups(subset='train', categories=categories, shuffle=True, random_state=42,
                                        remove=removedata)
        X_train, _, y_train, _ = train_test_split(data_train.data, data_train.target, test_size=0.33,
                                                  random_state=42)

        X_train = pd.DataFrame(data=X_train)
        features = self.tr.fit_transform(X_train, y_train)
        assert features is not None

    def test_feat_sweep_disabling(self):
        self.tr = pp.DataTransformer("classification", enable_feature_sweeping=False)
        new_column_names = [str(i) for i in range(10)]
        dt = pd.DataFrame(np.random.rand(100, 10))
        stats_and_cp = ColumnPurposeDetector.get_raw_stats_and_column_purposes(dt)
        trs = self.tr._perform_feature_sweeping(pd.DataFrame(
            np.random.rand(100, 10)), np.random.rand(100), stats_and_cp, new_column_names)
        assert len(trs) == 0

    def test_feat_sweep_enabled(self):
        tr = pp.DataTransformer("classification", enable_feature_sweeping=True)
        removedata = ('headers', 'footers', 'quotes')
        categories = ['alt.atheism', 'talk.religion.misc', 'comp.graphics', 'sci.space']

        from sklearn.datasets import fetch_20newsgroups

        # TODO: fetch some regression dataset for regression tasks
        data_train = fetch_20newsgroups(subset='test', categories=categories, shuffle=True, random_state=42,
                                        remove=removedata)
        sampled_X = data_train.data[:300]
        sampled_y = data_train.target[:300]
        X = pd.DataFrame(sampled_X)
        y = sampled_y
        feat_data = tr.fit_transform_with_logger(X, y)
        assert feat_data is not None

    def test_sweeping_trs_added(self):
        tr = pp.DataTransformer("classification", enable_feature_sweeping=True)

        removedata = ('headers', 'footers', 'quotes')
        categories = ['alt.atheism', 'talk.religion.misc', 'comp.graphics', 'sci.space']

        from sklearn.datasets import fetch_20newsgroups

        # TODO: fetch some regression dataset for regression tasks
        data_train = fetch_20newsgroups(subset='test', categories=categories, shuffle=True, random_state=42,
                                        remove=removedata)
        sampled_X = data_train.data[:300]
        sampled_y = data_train.target[:300]

        X = pd.DataFrame(sampled_X)
        y = sampled_y

        tr._add_test_transforms(
            [(X.columns[0], make_pipeline(TextFeaturizers.string_cast(), TextFeaturizers.word_embeddings()))])

        feat_data = tr.fit_transform_with_logger(X, y)
        assert feat_data is not None


class PreprocessingLoggerTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(PreprocessingLoggerTests, self).__init__(*args, **kwargs)
        logger = UnserializableLogger('')
        observer = ExperimentObserver(file_handler=logger)
        self.tr = pp.DataTransformer("classification", logger=logger, observer=observer)

    def test_serialization(self):
        """
        Test to make sure serialization works as expected.
        """
        df = pd.DataFrame(data=[[1, 2, 9, 8], [4, 5, 2, 9], [7, 8, 2, 3]],
                          columns=['Column1', 'Column2', 'Column3', 'Column4'])

        # Transform the input data using the pre-processors
        try:
            self.tr.fit_transform_with_logger(df,
                                              logger=UnserializableLogger(''))
            pickle.loads(pickle.dumps(self.tr))
        except pickle.PickleError:
            self.fail('(De)serialization of DataTransformer failed!')


@ddt
class TestMemoryAwareFeaturization(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestMemoryAwareFeaturization, self).__init__(*args, **kwargs)

    @patch('automl.client.core.common.memory_utilities.get_available_physical_memory')
    def test_transforms_memory_available(self, get_available_physical_memory_mock):
        tr = pp.DataTransformer("classification")
        get_available_physical_memory_mock.return_value = 90

        from sklearn import datasets

        digits = datasets.load_digits()

        # Exclude the first 100 rows from training so that they can be used for test.
        X_train = digits.data[100:, :]
        y_train = digits.target[100:]

        features = tr.fit_transform(X_train, y_train)
        assert len(features) > 0

    @patch('automl.client.core.common.memory_utilities.get_available_physical_memory')
    def test_transforms_memory_unavailable(self, get_available_physical_memory_mock):
        tr = pp.DataTransformer("classification")
        get_available_physical_memory_mock.return_value = -1

        from sklearn import datasets
        digits = datasets.load_digits()

        # Exclude the first 100 rows from training so that they can be used for test.
        X_train = digits.data[100:, :]
        y_train = digits.target[100:]

        with self.assertRaises(Exception):
            tr.fit_transform(X_train, y_train)

    @file_data("test_data_transformer_data.json")
    @patch('azureml.automl.core.featurizer.transformer.text.wordembedding_transformer.WordEmbeddingTransformer.'
           'get_memory_footprint')
    @patch('automl.client.core.common.memory_utilities.get_available_physical_memory')
    def test_actual_transform_memory_available(self, get_available_physical_memory_mock,
                                               get_memory_foot_print_mock, X):
        get_available_physical_memory_mock.return_value = 1000
        get_memory_foot_print_mock.return_value = 100

        tr = pp.DataTransformer("classification", enable_feature_sweeping=True)

        X = pd.DataFrame(X)
        y = np.random.rand(X.shape[0])

        tr._add_test_transforms(
            [(X.columns[0], make_pipeline(TextFeaturizers.string_cast(), TextFeaturizers.word_embeddings(
                **{"embeddings_provider": MockWordEmbeddingsProvider()}
            )), {"alias": "3"})])

        feat_data = tr.fit_transform_with_logger(X, y)
        assert feat_data is not None
        # Mock word embeddings added with vector size of 10
        assert feat_data.shape == (23, 412)

    @file_data("test_data_transformer_data.json")
    @patch('azureml.automl.core.featurizer.transformer.text.wordembedding_transformer.WordEmbeddingTransformer.'
           'get_memory_footprint')
    @patch('automl.client.core.common.memory_utilities.get_available_physical_memory')
    def test_actual_transform_memory_unavailable(self, get_available_physical_memory_mock,
                                                 get_memory_foot_print_mock, X):
        get_available_physical_memory_mock.return_value = 1000
        get_memory_foot_print_mock.return_value = 10000

        tr = pp.DataTransformer("classification", enable_feature_sweeping=True)

        X = pd.DataFrame(X)
        y = np.random.rand(X.shape[0])

        tr._add_test_transforms(
            [(X.columns[0], make_pipeline(TextFeaturizers.string_cast(), TextFeaturizers.word_embeddings(
                **{"embeddings_provider": MockWordEmbeddingsProvider()}
            )), {"alias": "3"})])

        feat_data = tr.fit_transform_with_logger(X, y)
        assert feat_data is not None
        assert feat_data.shape == (23, 402)


@ddt
class TestColumnPurposeSweeping(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestColumnPurposeSweeping, self).__init__(*args, **kwargs)
        logger = UnserializableLogger('')
        observer = ExperimentObserver(file_handler=logger)
        self.tr = pp.DataTransformer("classification", logger=logger, observer=observer)

    @file_data("../test_columnpurpose_detection/test_dogbreeds_vs_fruit.json")
    def test_single_hashes_columns(self, X, y):
        X = pd.DataFrame(X)
        y = np.array(y)

        features = self.tr.fit_transform(X, y)
        assert features is not None


if __name__ == "__main__":
    unittest.main()
