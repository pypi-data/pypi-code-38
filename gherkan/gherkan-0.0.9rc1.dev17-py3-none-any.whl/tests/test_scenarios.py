import requests
import unittest

import json
import os

import gherkan.utils.constants as c

class TestNLScenarios(unittest.TestCase):

    def setUp(self):
        self.url = f"http://{self.__class__.host}:{self.__class__.port}/{{}}"
        self.test_path = os.path.join(c.GHERKAN_ROOT_DIR, "tests", "scenarios")

        resetResponse = requests.get(self.url.format("reset"))
        self.assertDictContainsSubset({"OK": True}, resetResponse.json())


    def compare_multiline(self, testee, teststr):
        if not isinstance(testee, str) or not isinstance(teststr, str):
            self.assertFalse("No strings given to compare!")
            return

        self.assertEqual(testee.lower().replace("\n", " ").split(),
                         teststr.lower().replace("\n", " ").split())


    def scenarioTest(self, input_filename, correct_output_filename):
        with open(os.path.join(self.test_path, input_filename), "rt", encoding="utf-8") as f:
            request = json.load(f)

        with open(os.path.join(self.test_path, correct_output_filename), "rt", encoding="utf-8") as f:
            correctResponse = f.read()

        response = requests.post(self.url.format("nltext"), data=request)
        try:
            response = response.json()
        except Exception as exception:
            self.fail(
                "An exception was raised while trying to convert response to JSON. "
                "This is most likely due to the fact that the response was of different type.\n"
                "The exception: {}\nResponse text (if possible):\n{}".format(
                    exception, response.text))
        else:
            # self.assertDictContainsSubset({"errors": False}, response)
            response = requests.get(self.url.format("signals"))

            content = response.content.decode()

            # print(content)
            self.compare_multiline(content, correctResponse)


    def get_files(self, scenario_name, level, lang):
        nl_filename = f"{scenario_name}_{level}_NL_{lang}.json"
        signal_filename = f"{scenario_name}_{level}_signals_{lang}.txt"

        return nl_filename, signal_filename



    # =============== TESTS ===============

    def test_montrac_easy_en(self):
        nl_filename, signal_filename = self.get_files("Montrac", "easy", "en")
        self.scenarioTest(nl_filename, signal_filename)

    def test_montrac_easy_cs(self):
        nl_filename, signal_filename = self.get_files("Montrac", "easy", "cs")
        self.scenarioTest(nl_filename, signal_filename)

    def test_bgscenarioDif_basic_en(self):
        nl_filename, signal_filename = self.get_files("BgScenarioDiff", "basic", "en")
        self.scenarioTest(nl_filename, signal_filename)

    def test_bgscenarioDif_easy_en(self):
        nl_filename, signal_filename = self.get_files("BgScenarioDiff", "easy", "en")
        self.scenarioTest(nl_filename, signal_filename)

    def test_r1FillStorage_easy_en(self):
        nl_filename, signal_filename = self.get_files("r1FillStorage", "easy", "en")
        self.scenarioTest(nl_filename, signal_filename)

    def test_r1FillStorage_easy_cs(self):
        nl_filename, signal_filename = self.get_files("r1FillStorage", "easy", "cs")
        self.scenarioTest(nl_filename, signal_filename)

    def test_r1NormalSeq_easy_en(self):
        nl_filename, signal_filename = self.get_files("r1NormalSeq", "easy", "en")
        self.scenarioTest(nl_filename, signal_filename)

    @unittest.skip("TODO")
    def test_r1NormalSeq_easy_cs(self):
        nl_filename, signal_filename = self.get_files("r1NormalSeq", "easy", "cs")
        self.scenarioTest(nl_filename, signal_filename)

    def test_r2FillStorage_easy_en(self):
        nl_filename, signal_filename = self.get_files("r2FillStorage", "easy", "en")
        self.scenarioTest(nl_filename, signal_filename)

    def test_r2FillStorage_easy_cs(self):
        nl_filename, signal_filename = self.get_files("r2FillStorage", "easy", "cs")
        self.scenarioTest(nl_filename, signal_filename)

    def test_r3FillStorage_easy_en(self):
        nl_filename, signal_filename = self.get_files("r3FillStorage", "easy", "en")
        self.scenarioTest(nl_filename, signal_filename)

    def test_r3FillStorage_easy_cs(self):
        nl_filename, signal_filename = self.get_files("r3FillStorage", "easy", "cs")
        self.scenarioTest(nl_filename, signal_filename)


if __name__ == '__main__':
    unittest.TestCase.host = "localhost"
    unittest.TestCase.port = 5000
    unittest.main()
