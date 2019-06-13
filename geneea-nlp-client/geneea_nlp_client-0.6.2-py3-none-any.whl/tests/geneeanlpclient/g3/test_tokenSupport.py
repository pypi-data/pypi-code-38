
from unittest import TestCase

from geneeanlpclient.g3.model import CharSpan, TokenSupport
from tests.geneeanlpclient.g3.examples import example_obj
from tests.geneeanlpclient.g3.test_treeBuilder import buildTree


class TestTokenSupport(TestCase):
    TREE = buildTree(['a', 'b', 'c', 'd', 'e', 'f'], [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)])

    def test_a(self):
        # [a] b c d e f
        #  0 12345678901
        sup = TokenSupport.of([self.TREE.tokens[0]])
        self.assertEqual(sup.len(), 1)
        self.assertTrue(sup.isContinuous)

        spans = list(sup.spans())
        self.assertEqual([sup], spans)

        self.assertEqual(sup.first, self.TREE.tokens[0])
        self.assertEqual(sup.last, self.TREE.tokens[0])

        self.assertEqual(sup.charSpan, CharSpan(0, 1))
        self.assertEqual(sup.firstCharParaIdx, 0)
        self.assertEqual(sup.lastCharParaIdx, 1)

    def test_bcd(self):
        # a [b c d] e f
        # 01 23456 78901
        sup = TokenSupport.of([self.TREE.tokens[1], self.TREE.tokens[2], self.TREE.tokens[3]])
        self.assertEqual(sup.len(), 3)
        self.assertTrue(sup.isContinuous)

        spans = list(sup.spans())
        self.assertEqual([sup], spans)

        self.assertEqual(sup.first, self.TREE.tokens[1])
        self.assertEqual(sup.last, self.TREE.tokens[3])

        self.assertEqual(sup.charSpan, CharSpan(2, 7))
        self.assertEqual(sup.firstCharParaIdx, 2)
        self.assertEqual(sup.lastCharParaIdx, 7)

    def test_b_de(self):
        # a [b] c [d e] f
        # 01 2 345 678 901
        sup = TokenSupport.of([self.TREE.tokens[1], self.TREE.tokens[3], self.TREE.tokens[4]])
        self.assertEqual(sup.len(), 3)
        self.assertFalse(sup.isContinuous)

        spans = list(sup.spans())
        self.assertEqual(2, len(spans))
        self.assertEqual(TokenSupport.of([self.TREE.tokens[1]]), spans[0])
        self.assertEqual(TokenSupport.of([self.TREE.tokens[3], self.TREE.tokens[4]]), spans[1])

        self.assertEqual(sup.first, self.TREE.tokens[1])
        self.assertEqual(sup.last, self.TREE.tokens[4])

        self.assertEqual(sup.charSpan, CharSpan(2, 9))
        self.assertEqual(sup.firstCharParaIdx, 2)
        self.assertEqual(sup.lastCharParaIdx, 9)

    def test_of_check(self):
        with self.assertRaises(ValueError):
            TokenSupport.of([])

        obj = example_obj()
        # para[1] "Angela Merkel left Germany. She move to New Orleans to learn jazz. That's amazing."

        # token support across two sentences
        with self.assertRaises(ValueError):
            TokenSupport.of([obj.paragraphs[1].sentences[0].tokens[-1], obj.paragraphs[1].sentences[1].tokens[0]])
        with self.assertRaises(ValueError):
            TokenSupport.of([obj.paragraphs[0].sentences[0].tokens[-1], obj.paragraphs[1].sentences[0].tokens[0]])

    def test_of_text(self):
        obj = example_obj()
        # para[1] "Angela Merkel left Germany. She move to New Orleans to learn jazz. That's amazing."

        tokens = obj.paragraphs[1].sentences[0].tokens

        sup = TokenSupport.of(tokens[0:1])
        self.assertEqual(sup.text, 'Angela')
        self.assertEqual(sup.texts(), ['Angela'])

        sup = TokenSupport.of(tokens[2:3])
        self.assertEqual(sup.text, 'left')
        self.assertEqual(sup.texts(), ['left'])

        sup = TokenSupport.of(tokens[0:3])
        self.assertEqual(sup.text, 'Angela Merkel left')
        self.assertEqual(sup.texts(), ['Angela Merkel left'])

        sup = TokenSupport.of(tokens[0:1] + tokens[2:3])
        self.assertEqual(sup.text, 'Angela Merkel left')
        self.assertEqual(sup.texts(), ['Angela', 'left'])

