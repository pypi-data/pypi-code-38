
import unittest
from jd.api import DogDong


class TestComm(unittest.TestCase):

    def test_sign(self):

        dog = DogDong("yourappkey", "yourappSecret")

        data = {
            "v": "2.0",
            "method": "jingdong.innovation.product.write.createSkus",
            "app_key": "yourappkey",
            "access_token": "yourtoken",
            "360buy_param_json": {"paramStrin": "abc"},
            "timestamp": "2019-06-27 15:41:49",
        }

        self.assertEqual(dog.comm.sign(
            data), "E79CD3D49918172CA907A4CB493D9361")


if __name__ == "__main__":
    unittest.main()
