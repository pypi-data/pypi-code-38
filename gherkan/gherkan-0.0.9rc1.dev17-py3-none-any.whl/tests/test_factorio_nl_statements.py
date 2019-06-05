import requests
import unittest

import gherkan.utils.gherkin_keywords as g
import gherkan.utils.constants as c



class TestNLStatements(unittest.TestCase):

    def setUp(self):
        self.url = f"http://{self.__class__.host}:{self.__class__.port}/{{}}"

        resetResponse = requests.get(self.url.format("reset"))
        self.assertDictContainsSubset({"OK": True}, resetResponse.json())


    def compare_scenario_content(self, content, correct_scenario, lang):
        content_list = content.split("\n")
        content_list = [s.strip() for s in content_list]

        idx = 0

        for i, line in enumerate(content_list):
            if line.startswith(g.get_kw(lang, "Scenario")):
                idx = i+1
                break

        scenario = " ".join(content_list[idx:])

        self.assertEqual(scenario.lower().split(),
                         correct_scenario.lower().replace("\n", " ").split())


    def createStatementRequest(self, lang, statement):
        request = {
            "feature": "StatementTest",
            "feature_desc": "StatementTest dummy description",
            "language": lang,
            # dummy background, only scenario is tested
            "background": "given line is on" if lang == "en"
                            else "pokud linka je zapnutá",
            "text_raw": "scenario " + statement
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

            self.compare_scenario_content(response.content.decode(), correctResponse, lang)




    # =============== TESTS ===============
    @unittest.skip("TODO")
    def test_a31_fill_words(self):
        statements = [
            ("cs", "Ehm pokud je ten no ehm vozíček X na takzvané jak bych to řekl pozici Y"),
        ]
        statementResponse = "{} shuttleXAtStationY == 1"

        for lang, statement in statements:
            self.singleStatementTest(lang, statement, statementResponse.format(g.get_kw(lang, "Given")))

    @unittest.skip("TODO")
    def test_a32_synonyms_homonyms(self):
        statements = [
            ("cs", "Jestliže je vozíček X v pozici Y, tak robot R1 vyloží všechny kostičky"),
            ("cs", "Pokud stojí vozíček X ve stanici Y, pak robot R1 vyndá všechny kostičky."),
            ("cs", "Pokud se nachází vozíček X v místě Y, potom robot vyskládá všechny kostičky."),
        ]
        statementResponse = "{} shuttleXAtStationY {} robotR1ProgramNumber == 6"

        for lang, statement in statements:
            self.singleStatementTest(lang, statement, statementResponse.format(g.get_kw(lang, "Given"),
                                                                               g.get_kw(lang, "Then")))

    @unittest.skip("TODO")
    def test_a33_common_subject(self):
        statements = [
            ("cs", "Když součástky 1, 2 a 3 jsou na stole"),
        ]
        statementResponse = "{} part1OnTable && part2OnTable && part3OnTable {} lineOn"

        for lang, statement in statements:
            self.singleStatementTest(lang, statement, statementResponse.format(g.get_kw(lang, "When")))

    @unittest.skip("TODO")
    def test_a34_multiple_actions(self):
        statements = [
            ("cs", "Když robot R3 zvedne kostičku a vyloží kostičku."),
        ]
        statementResponse = "{} (robotR3ProgramNumber == 3) && (robotR3ProgramNumber == 4)"

        for lang, statement in statements:
            self.singleStatementTest(lang, statement, statementResponse.format(g.get_kw(lang, "When")))

    @unittest.skip("TODO")
    def test_a35_action_type(self):
        statements = [
            ("cs", "Pokud je linka zapnutá, pak vynuť vozíček X jede do stanice Y"),
            ("en", "Given line is on, then force shuttle X goes to station Y."),
        ]
        statementResponse = "{} lineOn {} force(shuttleXDestination, y)"

        for lang, statement in statements:
            self.singleStatementTest(lang, statement, statementResponse.format(g.get_kw(lang, "Given"),
                                                                               g.get_kw(lang, "Then")))

    @unittest.skip("TODO")
    def test_a36_unexpressed_subject(self):
        statements = [
            ("cs", "Když je vozíček X ve stanici Y, pak jede do stanice Z."),
        ]
        statementResponse = "{} shuttleXAtStationY {} shuttleXDestination == Z"

        for lang, statement in statements:
            self.singleStatementTest(lang, statement, statementResponse.format(g.get_kw(lang, "Given"),
                                                                               g.get_kw(lang, "Then")))


    def test_a37_multilingual(self):
        statements = [
            ("en", "When shuttle XX goes to station Z."),
            ("cs", "Když vozíček XX jede do stanice Z."),
        ]
        statementResponse = "{} shuttleXXDestination == Z"

        for lang, statement in statements:
            self.singleStatementTest(lang, statement, statementResponse.format(g.get_kw(lang, "When")))



if __name__ == '__main__':
    unittest.TestCase.host = "localhost"
    unittest.TestCase.port = 5000
    unittest.main()
