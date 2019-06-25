import unittest

import numpy as np

from azureml.automl.core import preprocess as pp


class LabelEncoderTransformerTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(LabelEncoderTransformerTests, self).__init__(*args, **kwargs)
        self._hashing_seed_value = 0
        self.label_encoder_transformer = pp.LabelEncoderTransformer(
            self._hashing_seed_value)

    def test_label_encoding_unique_values(self):
        # Test if training data is correctly label encoded
        train_set_category_array = np.array(
            ['bear', 'cat', 'dog', 'elephant', 'rat'])
        expected_train_set_label_array = np.array([0, 1, 2, 3, 4])
        actual_train_set_label_array = self.label_encoder_transformer \
            .fit_transform(train_set_category_array)
        self.assertTrue(np.all(expected_train_set_label_array ==
                               actual_train_set_label_array))

        # Test if test data is correctly label encoded
        test_set_category_array = np.array(['bear', 'elephant', 'rat'])
        expected_test_set_label_array = np.array([0, 3, 4])
        actual_test_set_label_array = self.label_encoder_transformer.transform(test_set_category_array)
        self.assertTrue(np.all(expected_test_set_label_array ==
                               actual_test_set_label_array))

    def test_label_encoding_non_unique_values(self):
        # Test if training data is correctly label encoded
        train_set_category_array = np.array(
            ['bear', 'bear', 'cat', 'dog', 'elephant', 'rat', 'elephant'])
        expected_train_set_label_array = np.array([0, 0, 1, 2, 3, 4, 3])
        actual_train_set_label_array = self.label_encoder_transformer \
            .fit_transform(train_set_category_array)
        self.assertTrue(np.all(expected_train_set_label_array ==
                               actual_train_set_label_array))

        # Test if test data is correctly label encoded
        test_set_category_array = np.array(['bear', 'elephant', 'rat', 'rat'])
        expected_test_set_label_array = np.array([0, 3, 4, 4])
        actual_test_set_label_array = self.label_encoder_transformer.transform(test_set_category_array)
        self.assertTrue(np.all(expected_test_set_label_array ==
                               actual_test_set_label_array))

    def test_label_encoding_with_test_data_not_in_training_data(self):
        # Test if training data is correctly label encoded
        train_set_category_array = np.array(
            ['bear', 'bear', 'cat', 'dog', 'elephant', 'rat', 'elephant'])
        expected_train_set_label_array = np.array([0, 0, 1, 2, 3, 4, 3])
        actual_train_set_label_array = self.label_encoder_transformer \
            .fit_transform(train_set_category_array)
        self.assertTrue(np.all(expected_train_set_label_array ==
                               actual_train_set_label_array))

        # Test if test data which contains unknown category
        # is correctly label encoded
        test_set_category_array = np.array(['tiger', 'elephant', 'rat', 'rat'])
        expected_test_set_label_array = np.array([0, 3, 4, 4])
        actual_test_set_label_array = self.label_encoder_transformer.transform(test_set_category_array)
        self.assertTrue(np.all(expected_test_set_label_array ==
                               actual_test_set_label_array))


if __name__ == "__main__":
    unittest.main()
