import unittest

from bdacore.metrics import generalized_jaccard_similarity_score, precision_with_fixed_recall, \
    recall_with_fixed_precision, binarize, is_valid_y_true


class MetricsTest(unittest.TestCase):
    def test_generalized_jaccard_similarity_score(self):
        # given
        a = [1, 1, 2, 3]
        b = [1, 2, 3, 4]

        # when
        g_score_jaccard = generalized_jaccard_similarity_score(a, b)

        # then
        self.assertEqual(g_score_jaccard, 0.6)

    def test_generalized_jaccard_similarity_score_empty(self):
        # given
        a = []
        b = []

        # when
        g_score_jaccard = generalized_jaccard_similarity_score(a, b)

        # then
        self.assertEqual(g_score_jaccard, 0.0)

    def test_precision_with_fixed_recall_should_return_expected_precision_for_given_example(self):
        # given
        y_test = [0, 0, 1, 1, 1, 1]
        y_pred = [0.6, 0.2, 0.3, 0.8, 0.9, 1.0]
        fixed_recall = 1.0
        expected_precision = 0.8
        expected_threshold = 0.3

        # when
        precision, threshold = precision_with_fixed_recall(y_test, y_pred, fixed_recall)

        # then
        self.assertEqual(precision, expected_precision)
        self.assertEqual(threshold, expected_threshold)

    def test_precision_with_fixed_recall_should_raise_exception_when_y_test_contains_only_0s(self):
        # given
        y_test = [0, 0]
        y_pred = [0.6, 0.2]
        fixed_recall = 0.0

        # when then
        with self.assertRaises(ValueError):
            precision_with_fixed_recall(y_test, y_pred, fixed_recall)

    def test_recall_with_fixed_precision_should_return_expected_recall_for_given_example(self):
        # given
        y_test = [0, 0, 1, 1, 1, 1]
        y_pred = [0.6, 0.2, 0.3, 0.8, 0.9, 1.0]
        fixed_precision = 1.0
        expected_recall = 0.75
        expected_threshold = 0.8

        # when
        recall, threshold = recall_with_fixed_precision(y_test, y_pred, fixed_precision)

        # then
        self.assertEqual(recall, expected_recall)
        self.assertEqual(threshold, expected_threshold)

    def test_recall_with_fixed_precision_should_raise_exception_when_y_test_contains_only_0s(self):
        # given
        y_test = [0, 0]
        y_pred = [0.6, 0.2]
        fixed_recall = 0.0

        # when then
        with self.assertRaises(ValueError):
            precision_with_fixed_recall(y_test, y_pred, fixed_recall)

    def test_binarize_should_convert_probas_to_ones_when_superior_or_equal_to_threshold_else_zeros(self):
        # given
        probas = [0.1, 0.5]
        threshold = 0.5
        expected_binary = [0, 1]

        # when
        binary = binarize(probas, threshold)

        # then
        self.assertEqual(binary, expected_binary)

    def test_is_valid_y_true_should_return_true_when_y_true_contains_at_least_one_1(self):
        # given
        y_true = [0, 1]

        # when then
        self.assertTrue(is_valid_y_true(y_true))

    def test_is_valid_y_true_should_return_false_when_y_true_contains_only_0s(self):
        # given
        y_true = [0, 0]

        # when then
        self.assertFalse(is_valid_y_true(y_true))
