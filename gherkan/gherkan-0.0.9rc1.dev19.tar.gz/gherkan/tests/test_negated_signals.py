import requests
import unittest

import gherkan.utils.gherkin_keywords as g
import gherkan.utils.constants as c

class TestNegatedSignalStatements(unittest.TestCase):

    def setUp(self):
        self.url = f"http://{self.__class__.host}:{self.__class__.port}/{{}}"

        resetResponse = requests.get(self.url.format("reset"))
        self.assertDictContainsSubset({"OK": True}, resetResponse.json())



    def test_negate_signal_file(self):
        lang = "en"
        signalFile = f"""
            # language: {lang}

            Feature: StatementTest
              StatementTest dummy description
            Background:
              Given lineOn

            Scenario: dummy description
              Given ((shuttleYDestination == XZZ) || stationXZXFree) && robotR1ProgramNumber == 2
            """

        correct_response = f"""# language: {lang}

            Feature: StatementTest
              StatementTest dummy description
            Background:
              Given ! lineOn

            Scenario: dummy description
              Given ((shuttleYDestination != XZZ) && (! stationXZXFree)) || (robotR1ProgramNumber != 2)
            """

        request = {'language': lang, 'scenarios': signalFile}

        response = requests.post(self.url.format("signals"), data=request)
        try:
            response = response.json()
        except Exception as exception:
            self.fail(
                "An exception was raised while trying to convert response to JSON. "
                "This is most likely due to the fact that the response was of different type.\n"
                "The exception: {}\nResponse text (if possible):\n{}".format(
                    exception, response.text))
        else:
            self.assertDictContainsSubset({"OK": True}, response)

            response = requests.get(self.url.format("signals_negated"))
            content = response.content.decode()

            content_list = [s.strip().lower() for s in content.split("\n")]
            correct_response_list = [s.strip().lower() for s in correct_response.split("\n")]

            # case correct_response_list
            self.assertEqual(content_list, correct_response_list)



if __name__ == '__main__':
    unittest.TestCase.host = "localhost"
    unittest.TestCase.port = 5000
    unittest.main()
