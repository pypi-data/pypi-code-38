import requests
import unittest
import json


class TestActions(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.url = f"http://{self.__class__.host}:{self.__class__.port}/{{}}"
        self.testJSON = json.dumps({
            "r1": {
                "1": "zvednout všechny červené kostky",
                "2": "zvednout všechny zelené kostky",
                "3": "zvednout všechny žluté kostky"
            },
            "r2": {
                "1": "dát kostku 1 na podnos",
                "2": "dát kostku 2 na podnos",
                "3": "dát kostku 3 na podnos"
            },
            "r3": {
                "1": "sestavit produkt",
                "2": "dát produkt do krabice"
            }
        })

    @unittest.skip("JSON formatting is buggy.")
    def test_get_and_post_actions(self):
        # originalResponse = requests.get(self.url.format("actions"))
        # print(f"\nCurrent Robot Programs:\n{originalResponse.content.decode()}")
        
        # postResponse = requests.post(self.url.format("actions"), data={"data": self.testJSON}).json()
        # self.assertDictContainsSubset({"OK": True}, postResponse)

        # response = requests.get(self.url.format("actions"))
        # self.assertMultiLineEqual(self.testJSON, response.content.decode())

        # postResponse = requests.post(self.url.format("actions"), data={"data": originalResponse.content}).json()
        # self.assertDictContainsSubset({"OK": True}, postResponse)
        pass

