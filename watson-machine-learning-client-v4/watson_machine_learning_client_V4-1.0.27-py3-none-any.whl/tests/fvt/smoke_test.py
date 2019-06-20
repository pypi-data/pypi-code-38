import unittest
from client import WatsonMachineLearningAPIClient

class ServiceInstance(unittest.TestCase):

    def setUp(self):
        print("Service Instance: setting up credentials")
        self.wml_credentials = {
          "url": "https://ibm-watson-ml.mybluemix.net",
          "access_key": "LOWlUa2Xh6u3Sz/XYSiLS7X6Ara3wtHuZA5Rizu5acu1UGa+wL1Yl1ZrirdK6oJ3pxSFKe9cZoFYLlzgPf++qpWZYcc+6fawL9S0V+2V79Adc+zik+ZHJYrsBRl9GAcs",
          "username": "1e3b0e5f-b86d-4cac-a857-07c83ff4e002",
          "password": "94ffa84e-f548-45d4-ace6-822b966ef773",
          "instance_id": "5c66fab9-f001-4f2b-b452-7728418721df"
        }

    def test_create_client(self):
        print("Creating client ...")

        client = WatsonMachineLearningAPIClient(self.wml_credentials)
        details = client.deployments.get_details()

        print(details)
        self.assertEqual(type(client), WatsonMachineLearningAPIClient)
        self.assertEqual(type(details), dict)


if __name__ == '__main__':
    unittest.main()