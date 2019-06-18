from unittest import TestCase

from typing import List, Tuple, Iterable

from geneeanlpclient.common import ud
from geneeanlpclient.g3.model import Token, TreeBuilder, Tree, CharSpan


def pretendToken(idx: int, text: str='', charStart: int=0) -> Token:
    return Token(
        id=f't{idx}',
        idx=idx,
        text=text,
        charSpan=CharSpan(charStart, charStart+len(text)),
        corrText=text,
        corrCharSpan=CharSpan(charStart, charStart+len(text)),
        deepLemma='DL'+text,
        lemma='L'+text,
        pos=ud.UPos.X,
        morphTag='',
        feats={},
        fnc=ud.UDep.DEP
    )


def buildTree(tokens: List[str], deps: List[Tuple[int, int]]) -> Tree[Token]:
    builder = TreeBuilder[Token]()

    charOffset = 0

    for idx, text in enumerate(tokens):
        builder.addNode(pretendToken(idx, text, charOffset))
        charOffset += len(text) + 1

    for dep in deps:
        builder.addDependency(dep[0], dep[1])

    return builder.build()


def buildIdxTree(idxs: Iterable[int], deps: List[Tuple[int, int]]) -> Tree[Token]:
    """
    :param idxs:  token indexes
    :param deps:  list of tuples (child, parent)
    :return:
    """
    builder = TreeBuilder[Token]()

    for idx in idxs:
        builder.addNode(pretendToken(idx))

    for dep in deps:
        builder.addDependency(childIdx=dep[0], parentIdx=dep[1])

    return builder.build()


class TestTreeBuilder(TestCase):
    def test_build_1(self):
        # 5 tokens all depend on the last one
        tree = buildIdxTree(range(6), [(0, 5), (1, 5), (2, 5), (3, 5), (4, 5)])

        for i in range(6):
            self.assertEqual(tree.tokens[i].idx, i)

        self.assertEqual(tree.root, tree.tokens[5])
        self.assertIs(tree.root.parent, None)

        for token in tree.tokens[:5]:
            self.assertEqual(token.parent, tree.root)
            self.assertEqual(token.children, [])

    def test_build_2(self):
        # 5 tokens all depend on the previous one
        tree = buildIdxTree(range(6), [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4)])

        for i in range(6):
            self.assertEqual(tree.tokens[i].idx, i)

        self.assertEqual(tree.root, tree.tokens[0])
        self.assertIs(tree.root.parent, None)

        self.assertEqual(tree.tokens[0].parent, None)
        self.assertEqual(tree.tokens[1].parent, tree.tokens[0])
        self.assertEqual(tree.tokens[2].parent, tree.tokens[1])
        self.assertEqual(tree.tokens[3].parent, tree.tokens[2])
        self.assertEqual(tree.tokens[4].parent, tree.tokens[3])
        self.assertEqual(tree.tokens[5].parent, tree.tokens[4])

        self.assertEqual(tree.tokens[0].children, [tree.tokens[1]])
        self.assertEqual(tree.tokens[1].children, [tree.tokens[2]])
        self.assertEqual(tree.tokens[2].children, [tree.tokens[3]])
        self.assertEqual(tree.tokens[3].children, [tree.tokens[4]])
        self.assertEqual(tree.tokens[4].children, [tree.tokens[5]])
        self.assertEqual(tree.tokens[5].children, [])

    def test_dummyDependencies(self):
        # 6 tokens, all depend on the first one
        builder = TreeBuilder[Token]()

        for idx in range(6):
            builder.addNode(pretendToken(idx))

        builder.addDummyDependecies()

        tree = builder.build()

        for i in range(6):
            self.assertEqual(tree.tokens[i].idx, i)

        self.assertEqual(tree.root, tree.tokens[0])
        self.assertIs(tree.root.parent, None)

        self.assertEqual(tree.tokens[0].parent, None)
        self.assertEqual(tree.tokens[1].parent, tree.tokens[0])
        self.assertEqual(tree.tokens[2].parent, tree.tokens[0])
        self.assertEqual(tree.tokens[3].parent, tree.tokens[0])
        self.assertEqual(tree.tokens[4].parent, tree.tokens[0])
        self.assertEqual(tree.tokens[5].parent, tree.tokens[0])

        self.assertEqual(tree.tokens[0].children, [tree.tokens[1], tree.tokens[2], tree.tokens[3], tree.tokens[4], tree.tokens[5]])
        self.assertEqual(tree.tokens[1].children, [])
        self.assertEqual(tree.tokens[2].children, [])
        self.assertEqual(tree.tokens[3].children, [])
        self.assertEqual(tree.tokens[4].children, [])
        self.assertEqual(tree.tokens[5].children, [])

    def test_build_nonprojective(self):
        # non projective tree ( 0 and 1 depend on 5 and are fronted; 4 is the root)
        tree = buildIdxTree(range(6), [(0, 1), (1, 5), (2, 3), (3, 4), (5, 4)])

        for i in range(6):
            self.assertEqual(tree.tokens[i].idx, i)

    def test_build_error_gap(self):
        # token idx=3 missing
        with self.assertRaises(ValueError) as ctx:
            buildIdxTree([0, 1, 2, 4, 5], [(0, 5), (1, 5), (2, 5), (4, 5)])

        self.assertEqual('Indexes are not sequential.', str(ctx.exception))

    def test_build_error_initial_gap(self):
        # token idx=0 missing
        with self.assertRaises(ValueError) as ctx:
            buildIdxTree([1, 2, 3, 4, 5], [(1, 5), (2, 5), (3, 5), (4, 5)])

        self.assertEqual('Indexes are not sequential.', str(ctx.exception))

    def test_build_error_multiple_roots(self):
        with self.assertRaises(ValueError) as ctx:
            buildIdxTree(range(6), [(0, 2), (1, 2), (3, 5), (4, 5)])

        self.assertEqual('Multiple roots.', str(ctx.exception))

    def test_build_error_circular(self):
        with self.assertRaises(ValueError) as ctx:
            buildIdxTree(range(6), [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (4, 2)])

        self.assertEqual('Node 4 has multiple parents.', str(ctx.exception))
