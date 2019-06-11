import requests
import unittest

import gherkan.utils.gherkin_keywords as g
import gherkan.utils.constants as c



class TestNLStatements(unittest.TestCase):

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
        request = {
            "feature": "StatementTest",
            "feature_desc": "StatementTest dummy description",
            "language": lang,
            "background": statement,
            # dummy scenario, only background is tested
            "text_raw": "scenario given line is on" if lang == "en"
                            else "scenario pokud linka je zapnutá"
        }
        return request

    def singleStatementTest(self, lang, statement, correctResponse):
        request = self.createStatementRequest(lang, statement)

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

            self.compare_background_content(response.content.decode(), correctResponse, lang)




    # =============== TESTS ===============
    def test_line_is_on(self):
        statements = [
            ("en", "given line is on"),
            ("cs", "pokud je linka zapnutá"),
            ("cs", "pokud linka je zapnutá"),
        ]
        statementResponse = "{} lineon"

        for lang, statement in statements:
            self.singleStatementTest(lang, statement, statementResponse.format(g.get_kw(lang, "Given")))

    def test_station_xzx_free(self):
        statements = [
            ("en", "given station XZX is free"),
            ("cs", "pokud je stanice XZX volná"),
        ]
        statementResponse = "{} stationXZXFree"

        for lang, statement in statements:
            self.singleStatementTest(lang, statement, statementResponse.format(g.get_kw(lang,"Given")))

    def test_shuttle_y_goes_xzz(self):
        statements = [
            ("en", "given shuttle Y goes to station XZZ"),
            ("cs", "pokud vozíček Y jede do stanice XZZ"),
        ]
        statementResponse = "{} shuttleYDestination == XZZ"

        for lang, statement in statements:
            self.singleStatementTest(lang, statement, statementResponse.format(g.get_kw(lang,"Given")))

    def test_r1_picks_cube_one(self):
        statements = [
            ("en", "given robot R1 picks up cube 1"),
            ("en", "given robot R1 picks up cube one"),
            ("en", "given robot R1 picks up cube number 1"),
            ("cs", "pokud robot R1 zvedne kostku 1"),
            ("cs", "pokud robot R1 zvedne kostku jedna"),
            ("cs", "pokud robot R1 zvedne kostku číslo 1"),
        ]
        statementResponse = "{} robotR1ProgramNumber == 2"

        for lang, statement in statements:
            self.singleStatementTest(lang, statement, statementResponse.format(g.get_kw(lang,"Given")))

    def test_storage_is_empty(self):
        statements = [
            ("en", "given storage is empty"),
            ("cs", "pokud sklad je prázdný")
        ]
        statementResponse = "{} storageCount == 0"

        for lang, statement in statements:
            self.singleStatementTest(lang, statement, statementResponse.format(g.get_kw(lang,"Given")))

    @unittest.skip("TODO")
    def test_goes_to_station_at_robot(self):
        # TODO [issue #67] robot incorrectly marked as actor
        statements = [
            ("en", "given shuttle Z goes to station RRR by robot R"),
            ("cs", "pokud vozík Z jede do stanice RRR u robotu R")
        ]
        statementResponse = "{} shuttleZDestination == RRR"

        for lang, statement in statements:
            self.singleStatementTest(lang, statement, statementResponse.format(g.get_kw(lang,"Given")))


    def test_goes_to_station_at_table(self):
        statements = [
            ("en", "given shuttle Z goes to station RRR by table R"),
            ("cs", "pokud vozík Z jede do stanice RRR u stolu R")
        ]
        statementResponse = "{} shuttleZDestination == RRR"

        for lang, statement in statements:
            self.singleStatementTest(lang, statement, statementResponse.format(g.get_kw(lang,"Given")))




if __name__ == '__main__':
    unittest.TestCase.host = "localhost"
    unittest.TestCase.port = 5000
    unittest.main()
