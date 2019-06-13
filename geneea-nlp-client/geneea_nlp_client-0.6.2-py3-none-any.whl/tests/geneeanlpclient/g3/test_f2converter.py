import json
from operator import itemgetter
from unittest import TestCase

from geneeanlpclient.common.dictutil import JsonType
from geneeanlpclient.g3 import toF2Dict, fromF2Dict, fromDict
from tests.geneeanlpclient.g3.examples import EXAMPLE_F2, EXAMPLE_F2_CS, EXAMPLE_PHENO
from geneeanlpclient.g3.f2converter import _F2Reader

class TestRW(TestCase):

    @staticmethod
    def _resortInstances(dictF2: JsonType):
        for e in dictF2['entities']:
            e['instances'] = sorted(e['instances'], key=itemgetter('segment', 'offset'))

        for t in dictF2['hashtags']:
            t['instances'] = sorted(t['instances'], key=itemgetter('segment', 'offset'))

    @staticmethod
    def _unifyTecto(dictF2: JsonType):
        for ts in dictF2['tectoSentences']:
            ts['tokens'] = [tt for tt in ts['tokens'] if tt['function'] != 'ROOT']
            for tt in ts['tokens']:
                tt.pop('tag', None) # 'tag' is nonsence in tecto-node and G3 does not provide it

    @staticmethod
    def _replaceClauseByRootF2(dictF2: JsonType) -> None:
        """
        Utility class to replace all 'clause' functions in tokens by 'root' in F2 dictionary. Readers replace clause by root.
        Clause is a deprecated non-UD function, equivalent to root.
        """

        for key in ['titleLemmas', 'leadLemmas', 'textLemmas']:
            for sentence in dictF2.get(key, []):
                for token in sentence:
                    if token.get('fun') == 'clause':
                        token['fun'] = 'root'

    def test_read_write(self):
        for fileName in [EXAMPLE_F2, EXAMPLE_F2_CS]:
            self.maxDiff = None

            with open(fileName, 'r') as file:
                obj = fromF2Dict(json.load(file))

            actual = toF2Dict(obj)
            del actual['keywords']  # G3 does not contain keywords except those promoted to tags

            with open(fileName, 'r') as file:
                expected = json.load(file)

                del expected['keywords']   # G3 does not contain keywords except those promoted to tags
                # G3 tags do not contain text attribute
                for t in expected.get('hashtags', []):
                    for m in t.get('instances', []):
                        del m['text']

                TestRW._replaceClauseByRootF2(expected)

            self.assertDictEqual(expected, actual)

    def test_readG3_writeF2(self):
        self.maxDiff = None

        with open(EXAMPLE_PHENO, 'r') as file:
            obj = fromDict(json.load(file))

        actual = toF2Dict(obj)
        del actual['keywords']  # G3 does not contain keywords except those promoted to tags
        for t in actual.get('hashtags', []):
            t.pop('type', None)  # ignore hashtag types they have different meaning in F2 and G3
        TestRW._resortInstances(actual)
        TestRW._unifyTecto(actual)

        with open(EXAMPLE_F2, 'r') as file:
            expected = json.load(file)

            del expected['keywords']  # G3 does not contain 'keywords' except those promoted to tags
            del expected['topic']  # G3 does not contain 'topic' field, topics are part of tags

            # G3 entities do not contain 'uid' attribute
            for e in expected.get('entities', []):
                e['uid'] = None
            # G3 tags do not contain 'text', 'uid' attribute
            for t in expected.get('hashtags', []):
                t.pop('uid', None)
                t.pop('type', None) # ignore hashtag types they have different meaning in F2 and G3
                t['weight'] = round(t['weight'], 3) # G3 rounds weight to 3 decimal places
                for m in t.get('instances', []):
                    del m['text']

            expected['sentiment']['value'] = round(expected['sentiment']['value'], 1)
            expected['sentiment']['sentenceVals'] = [round(v, 1) for v in expected['sentiment']['sentenceVals']]

            TestRW._replaceClauseByRootF2(expected)
            TestRW._resortInstances(expected)
            TestRW._unifyTecto(expected)

        self.assertDictEqual(expected, actual)

    def testIds(self):
        reader = _F2Reader()
        actual = [reader._getId('E') for idx in range(1, 10)]
        expected = [f'E{idx}' for idx in range(1, 10)]
        self.assertListEqual(expected, actual)
