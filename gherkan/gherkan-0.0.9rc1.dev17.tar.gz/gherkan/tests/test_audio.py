import requests
import unittest
import os
import gherkan.utils.gherkin_keywords as g
import gherkan.utils.constants as c



class TestAudio(unittest.TestCase):

    def setUp(self):
        self.url = f"http://{self.__class__.host}:{self.__class__.port}/{{}}"

        resetResponse = requests.get(self.url.format("reset"))
        self.assertDictContainsSubset({"OK": True}, resetResponse.json())


    def compare_multiline(self, testee, teststr):
        if not isinstance(testee, str) or not isinstance(teststr, str):
            self.assertFalse("No strings given to compare!")
            return

        self.assertEqual(testee.lower().replace("\n", " ").split(),
                         teststr.lower().replace("\n", " ").split())


    def transcribeAudio(self, lang, audioFilename):
        request = {
            "language": lang,
        }
        files = {'upload_file': open(audioFilename, 'rb')}
        response = requests.post(self.url.format("audio"), data=request, files=files)
        try:
            response = response.json()
        except Exception as exception:
            self.fail(
                "An exception was raised while trying to convert response to JSON. "
                "This is most likely due to the fact that the response was of different type.\n"
                "The exception: {}\nResponse text (if possible):\n{}".format(
                    exception, response.text))

        if not "transcript" in response:
            raise Exception(response["message"])

        return response["transcript"]


    def rawTextToSignal(self, lang, transcript):
        request = {
            "feature": "Montrac",
            "feature_desc": "Test audia",
            "background": "Jakmile linka je zapnutá",
            "text_raw": transcript,
            "language": lang
        }
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
            self.assertDictContainsSubset({"errors": False}, response)

            response = requests.get(self.url.format("signals"))
            return response


    def singleAudioTest(self, lang, audioFilename, correctResponse):
        transcript = self.transcribeAudio(lang, audioFilename)
        response = self.rawTextToSignal(lang, transcript)

        self.compare_multiline(response.content.decode(), correctResponse)



    # =============== TESTS ===============
    def test_audio(self):
        lang="cs"
        audioFilename=os.path.join(os.path.dirname(os.path.realpath(__file__)),os.pardir,"speech_recognition","montrac.wav")

        correctResponse = """# language: cs
            Požadavek: Montrac
                Test audia
            Kontext:
              Pokud lineOn
            
            Scénář: jakmile stanice z je volná pak vozíček y jede do stanice z
              Když stationzFree
              Pak shuttleYDestination == z
            Scénář: jakmile robot R1 zvedne kostku 1 pak robot R1 položí kostičku 1 na vozíček y na pozici 1
              Když robotR1ProgramNumber == 2
              Pak robotR1ProgramNumber == 10
            Scénář: když stanice x je volná a robot R1 skončil vykládání kostičky 1 pak vozíček y jede do stanice X
              Když (stationxFree) && (robotR1ProgramNumber == 11 && robotR1ProgramEnded)
              Pak shuttleYDestination == X
            """

        self.singleAudioTest(lang, audioFilename, correctResponse)


if __name__ == '__main__':
    unittest.TestCase.host = "localhost"
    unittest.TestCase.port = 5000
    unittest.main()
