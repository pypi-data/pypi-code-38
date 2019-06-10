from unittest import TestCase

from sekg.metric.ir import InformationRetrievalMetric


class TestInformationRetrievalMetric(TestCase):
    def test_precision(self):
        result, separate_avg = InformationRetrievalMetric.precision(
            [([1, 1, 1], 10), ([0, 0], 2), ([0, 1, 1, 1, 0, 1, 0, 1, 1, 0], 10)])
        self.assertEqual(result, 0.5333333333333333)
        self.assertEqual(separate_avg, [1, 0, 0.6])

        result, separate_avg = InformationRetrievalMetric.precision(([1, 1, 1], 10))

        self.assertEqual(result, 1)
        self.assertEqual(separate_avg, [1])

    def test_recall(self):
        result, separate_avg = InformationRetrievalMetric.recall(
            [([1, 1, 1], 10), ([0, 0], 2), ([0, 1, 1, 1, 0, 1, 0, 1, 1, 0], 10)])

        self.assertEqual(result, 0.3)
        self.assertEqual(separate_avg, [0.3, 0, 0.6])

        result, separate_avg = InformationRetrievalMetric.recall(([1, 1, 1], 10))

        self.assertEqual(result, 0.3)
        self.assertEqual(separate_avg, [0.3])

    def test_mrr(self):
        result, separate_avg = InformationRetrievalMetric.mrr(
            [([1, 1, 1], 10), ([0, 0], 2), ([0, 1, 1, 1, 0, 1, 0, 1, 1, 0], 10)])

        self.assertEqual([1, 0, 0.5], separate_avg)
        self.assertEqual(0.5, result)

        result, separate_avg = InformationRetrievalMetric.mrr(([1, 1, 1], 10))

        self.assertEqual(1, result)
        self.assertEqual([1], separate_avg)

    def test_map(self):
        result, separate_avg = InformationRetrievalMetric.map(
            [([1, 1, 1], 10), ([0, 0], 2), ([0, 1, 1, 1, 0, 1, 0, 1, 1, 0], 10)])

        self.assertEqual([0.3, 0, 0.38749999999999996], separate_avg)
        self.assertEqual(0.22916666666666666, result)

        result, separate_avg = InformationRetrievalMetric.map(([1, 1, 1], 10))

        self.assertEqual(0.3, result)
        self.assertEqual([0.3], separate_avg)
        result, separate_avg = InformationRetrievalMetric.map(([1, 0, 1, 0, 0, 1, 0, 0], 3))

        self.assertEqual(0.7222222222222222, result)
        self.assertEqual([0.7222222222222222], separate_avg)

    def test_f1(self):
        result, separate_avg = InformationRetrievalMetric.f1(
            [([1, 1, 1], 10), ([0, 0], 2), ([0, 1, 1, 1, 0, 1, 0, 1, 1, 0], 10)])

        self.assertEqual([0.4615384615384615, 0.0, 0.6], separate_avg)
        self.assertEqual(0.35384615384615387, result)

        result, separate_avg = InformationRetrievalMetric.f1(([1, 1, 1], 10))

        self.assertEqual(0.4615384615384615, result)
        self.assertEqual([0.4615384615384615], separate_avg)
        result, separate_avg = InformationRetrievalMetric.f1(([1, 0, 1, 0, 0, 1, 0, 0], 3))

        self.assertEqual(0.5454545454545454, result)
        self.assertEqual([0.5454545454545454], separate_avg)
