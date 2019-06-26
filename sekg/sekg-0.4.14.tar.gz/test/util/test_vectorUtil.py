from unittest import TestCase

import numpy as np

from sekg.util.vector_util import VectorUtil


class TestVectorUtil(TestCase):
    def test_get_weight_mean_vec(self):
        vectors = [
            np.array([10, 10, 10, 10]),
            np.array([10, 90, 90, 90]),
        ]
        result = VectorUtil.get_weight_mean_vec(vectors, weight_list=[1, 1])

        for right, t in zip(np.array([10, 50, 50, 50]), result):
            self.assertEqual(right, t)
        result = VectorUtil.get_weight_mean_vec(vectors, weight_list=[1, 9])
        for right, t in zip(np.array([10, 82, 82, 82]), result):
            self.assertEqual(right, t)

    def test_compute_idf_weight_dict(self):
        number_dict = {
            1: 10,
            2: 1,
            3: 20
        }

        result = VectorUtil.compute_idf_weight_dict(100, number_dict)

        result_number_dict = {
            1: 2.302585092994046,
            2: 4.605170185988092,
            3: 1.6094379124341003
        }
        for key, v in result_number_dict.items():
            self.assertEqual(v, result[key])
