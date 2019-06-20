import requests
import unittest

import gherkan.utils.gherkin_keywords as g
import gherkan.utils.constants as c

class TestMappingSignal(unittest.TestCase):

    def setUp(self):
        self.url = f"http://{self.__class__.host}:{self.__class__.port}/{{}}"

        resetResponse = requests.get(self.url.format("reset"))
        self.assertDictContainsSubset({"OK": True}, resetResponse.json())


    @unittest.skip("Not implemented yet.")
    def test_mapping_signal_file(self):
        lang = "en"
        signalFile = f"""
            # language: {lang}

            Požadavek: Robot R1
                Robot R1 má na starosti kompletaci skládání Chassi. Robot postupně zbírá kostičky potřebené ke kompletaci.
                Kontext:
            Pokud LineOn == 1 || (robotR1ProgramNumber == 1 && robotR2ProgramNumber == 1)

            Scénář: Normální běh linky - Robot R1 - Skládání Chassi - braní kostičky číslo 1
                Když ShuttleXyAtStationYZ == 1 && edge(StationLocked, 1)
                Pak   robotR1ProgramNumber == 1 && edge(robotR1ProgramStart, 1)

            Scénář: Normální běh linky - Robot R1 - Skládání Chassi - pokládání kostičky číslo 1
                Když  robotR1ProgramNumber == 1 && edge(robotR1ProgramEnd, 1)
                Pak   robotR1ProgramNumber == 2
            """
        requestData = {
            "feature" : "robot R1",
            "feature_desc" : "lorem ipsum",
            "background" : "given Line is On",
            "text_raw" : "scenario As soon as shuttle XY is in the station ZX, then robot r1 picks "
                        "up cube one. scenario when robot r3 picks up cube one, robot r2 assembles the product.",
            "language" : {lang}
        }
        correct_response = f"""\\n    \\"LineOn\\": \\"LineOn\\",\\n    \\"robotR1ProgramNumber\\": \\"robotR1ProgramNumber\\",\\n    \\"robotR2ProgramNumber\\": \\"robotR2ProgramNumber\\",\\n    \\"ShuttleXyAtStationYZ\\": \\"ShuttleXyAtStationYZ\\",\\n    \\"StationLocked\\": \\"StationLocked\\",\\n    \\"robotR1ProgramStart\\": \\"robotR1ProgramStart\\",\\n    \\"robotR1ProgramEnd\\": \\"robotR1ProgramEnd\\"\\n"""
# %%
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
            response = requests.get(self.url.format("signal_map"))
            content = response.content.decode()

            content_list = [s.strip().lower() for s in content.split("\n")]
            correct_response_list = [s.strip().lower() for s in correct_response.split("\n")]


if __name__ == '__main__':
    unittest.TestCase.host = "localhost"
    unittest.TestCase.port = 5000
    unittest.main()
