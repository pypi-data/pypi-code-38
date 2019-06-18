from unittest import TestCase

import datetime

from geneeanlpclient.g3 import AnalysisType, Request, Diacritization, Domain, LanguageCode, TextType
from tests.geneeanlpclient.g3.examples import example_req_js


class TestRequest(TestCase):

    def test_simple_build(self):
        req = Request.Builder().build(text='Unit Test')
        self.assertDictEqual(
            {'text': 'Unit Test'}, req.toDict()
        )

    def test_read_and_write(self):
        exampleReqDict = example_req_js()

        bldr = Request.Builder(
            analyses=[AnalysisType.ENTITIES, AnalysisType.SENTIMENT],
            domain='news',
            language='en',
            textType='clean',
            diacritization='yes',
            returnMentions=True,
            returnItemSentiment=True
        ).setCustomConfig(custom_key=['custom value'])

        builtReq = bldr.build(
            title='Angela Merkel in New Orleans',
            text='Angela Merkel left Germany. She move to New Orleans to learn jazz. That\'s amazing.'
        )

        exmapleReq = Request.fromDict(exampleReqDict)
        self.assertTupleEqual(exmapleReq, builtReq)
        self.assertDictEqual(exampleReqDict, exmapleReq.toDict())

    def test_read_and_write2(self):
        exampleReqDict = example_req_js()

        bldr = Request.Builder(
            analyses=[AnalysisType.ENTITIES, AnalysisType.SENTIMENT],
            domain=Domain.NEWS,
            language=LanguageCode.EN,
            textType=TextType.CLEAN,
            diacritization=Diacritization.YES,
            returnMentions=True,
            returnItemSentiment=True
        ).setCustomConfig(custom_key=['custom value'])

        builtReq = bldr.build(
                    title='Angela Merkel in New Orleans',
                    text='Angela Merkel left Germany. She move to New Orleans to learn jazz. That\'s amazing.'
        )

        exmapleReq = Request.fromDict(exampleReqDict)
        self.assertTupleEqual(exmapleReq, builtReq)
        self.assertDictEqual(exampleReqDict, exmapleReq.toDict())

    def test_refDate(self):
        self.assertEqual('2019-05-12', Request.Builder._refDate(datetime.datetime(2019, 5, 12)))
        self.assertEqual('2019-05-12', Request.Builder._refDate(datetime.date(2019, 5, 12)))
        self.assertEqual('2019-05-12', Request.Builder._refDate('2019-05-12'))

        self.assertEqual('2019-05-02', Request.Builder._refDate('2019-5-2'))

        self.assertEqual('NOW', Request.Builder._refDate('now'))

        with self.assertRaises(ValueError):
            Request.Builder._refDate('5.12.2019')

        with self.assertRaises(ValueError):
            Request.Builder._refDate('2019-15-02')
