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
            "num_sentences": 0,
            "num_words": 0,
            "n_capitals": 0,
            "n_exclamations": 0,
            "n_questions": 0
        }, {
            "num_sentences": 0,
            "num_words": 0,
            "n_capitals": 0,
            "n_exclamations": 0,
            "n_questions": 0
        }]
        self.assertTrue(self.tr.fit_transform(x) == expected_output)

    def test_transform_with_text(self):
        X = np.array(['This has three sentences. TWO CAPITALS. One exclamation! '
                      'What was the question by the way? Seventeen words.'])
        features = self.tr.fit_transform(X)
        assert features is not None
        expected = [{'num_sentences': 3, 'num_words': 17, 'n_capitals': 6, 'n_exclamations': 1, 'n_questions': 1}]
        assert features == expected


if __name__ == '__main__':
    unittest.main()
