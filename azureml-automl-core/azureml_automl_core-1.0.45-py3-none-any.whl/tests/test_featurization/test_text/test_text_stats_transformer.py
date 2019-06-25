import sys
import unittest
import numpy as np
from azureml.automl.core.featurizer.transformer.text import TextFeaturizers


class TestTextStatsTransformer(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.tr = TextFeaturizers.text_stats()
        super(TestTextStatsTransformer, self).__init__(*args, **kwargs)

    def test_transform(self):
        x = np.array(['A', 3])
        expected_output = [{
            "n_periods": 0,
            "n_words": 0,
            "n_capitals": 0,
            "n_exclamations": 0,
            "n_questions": 0,
            "n_chars": 1
        }, {
            "n_periods": 0,
            "n_words": 0,
            "n_capitals": 0,
            "n_exclamations": 0,
            "n_questions": 0,
            "n_chars": 1
        }]
        self.assertTrue(self.tr.fit_transform(x) == expected_output)
        memory_footprint = self.tr.get_memory_footprint(x, y=None)
        self.assertEqual(6 * sys.getsizeof(float) * len(x), memory_footprint)

    def test_transform_with_text(self):
        X = np.array(['This has three sentences. TWO CAPITALS. One exclamation! '
                      'What was the question by the way? Seventeen words.'])
        features = self.tr.fit_transform(X)
        assert features is not None
        expected = [{'n_periods': 3, 'n_words': 17, 'n_capitals': 6,
                     'n_exclamations': 1, 'n_questions': 1, "n_chars": len(X[0])}]
        assert features == expected
        memory_footprint = self.tr.get_memory_footprint(X, y=None)
        self.assertEqual(6 * sys.getsizeof(float) * len(X), memory_footprint)


if __name__ == '__main__':
    unittest.main()
