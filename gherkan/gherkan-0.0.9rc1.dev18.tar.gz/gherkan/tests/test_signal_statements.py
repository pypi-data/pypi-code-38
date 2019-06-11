import requests
import unittest

import gherkan.utils.gherkin_keywords as g
import gherkan.utils.constants as c

class TestSignalStatements(unittest.TestCase):

    def setUp(self):
        self.url = f"http://{self.__class__.host}:{self.__class__.port}/{{}}"

        resetResponse = requests.get(self.url.format("reset"))
        self.assertDictContainsSubset({"OK": True}, resetResponse.json())


    def compare_background_content(self, content, correct_background, lang):
        content_list = content.split("\n")
        content_list = [s.strip() for s in content_list]
        background_line_text = (g.get_kw(lang, "Background")) + ":"
        res_idx = content_list.index(background_line_text) + 1

        # case insensitive
        self.assertEqual(content_list[res_idx].lower(), correct_background.lower())


    def createStatementRequest(self, lang, statement):
        self.signalFile = f"""
            # language: {lang}

            Feature: StatementTest
              StatementTest dummy description
            Background:
              {statement}

            Scenario: given line is on
              Given lineOn
            """
        request = {'language': lang, 'scenarios': self.signalFile}

        return request

    def singleStatementTest(self, lang, statement, correctResponse):
        request = self.createStatementRequest(lang, statement)

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

            response = requests.get(self.url.format("nltext"))

            self.compare_background_content(response.content.decode(), correctResponse, lang)




    # =============== TESTS ===============
    def test_line_is_on(self):
        statement = "given lineOn"
        statementResponses = [
            ("en", "Given line is on"),
            ("cs", "Pokud linka jest zapnutý")
        ]

        for lang, statementResponse in statementResponses:
            self.singleStatementTest(lang, statement, statementResponse)


    def test_station_xzx_free(self):
        statement = "given stationXZXFree"
        statementResponses = [
            ("en", "given station XZX is free"),
            ("cs", "pokud stanice XZX jest volný"),
        ]
        for lang, statementResponse in statementResponses:
            self.singleStatementTest(lang, statement, statementResponse)


    def test_shuttle_y_goes_zz(self):
        statement = "given shuttleYDestination == XZZ"
        statementResponses = [
            ("en", "given shuttle Y goes to station XZZ"),
            ("cs", "pokud vozíček Y pojede do stanice XZZ"),
        ]

        for lang, statementResponse in statementResponses:
            self.singleStatementTest(lang, statement, statementResponse)


    def test_r1_picks_cube_one(self):
        statement = "given robotR1ProgramNumber == 2"
        statementResponses = [
            ("en", "given robot R1 picks up cube 1"),
            ("cs", "pokud robot R1 zvedne kostka 1")
        ]

        for lang, statementResponse in statementResponses:
            self.singleStatementTest(lang, statement, statementResponse)


    def test_storage_is_empty(self):
        statement = "given storageCount == 0"
        statementResponses = [
            ("en", "given storage contain 0 pieces"),
            ("cs", "pokud sklad obsahuje 0 kusů")
        ]

        for lang, statementResponse in statementResponses:
            self.singleStatementTest(lang, statement, statementResponse)



if __name__ == '__main__':
    unittest.TestCase.host = "localhost"
    unittest.TestCase.port = 5000
    unittest.main()
