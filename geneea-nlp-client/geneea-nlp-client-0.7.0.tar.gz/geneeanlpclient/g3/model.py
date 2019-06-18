# Copyright 2019 Geneea Analytics s.r.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Objects encapsulating the result of full analysis.

Basic objects:

* G3 - analysis of a single document
* Paragraph, Sentence, CharSpan
* Entity
* Tag
* Relation

Objects related to tokens and tecto tokens:

* Token - surface token (basic unit of morphology and surface syntax)
* TectoToken - tectogrammatical token (basic unit of deep syntax)
* NodeUtils - general utility classes for manipulating lists of tokens and tectotokens
* Tree - class encapsulating ordered rooted trees of tokens or tecto tokens
* TreeBuilder - builder for syntactic and tecto trees (tokens and tecto tokens should not be constructed directly)
* TokenSupport - list of tokens within a sentence (used for Entity.Mention, Tag.Mention, Relation.Support TectoToken, etc)
"""

from abc import ABC

from itertools import chain
from typing import (Any, TypeVar, Generic, Union, Optional, List, Callable, Iterable, Dict, Mapping, Sequence,
    NamedTuple, Iterator, cast)

from geneeanlpclient.common import ud
from geneeanlpclient.common.common import isSequential, toBool


class Sentiment(NamedTuple):
    """ Class encapsulating sentiment of a document, sentence or relation """
    mean: float
    """ Average sentiment """
    label: str
    """ Human readable label describing the average sentiment """
    positive: float
    """ Average sentiment of positive items """
    negative: float
    """ Average sentiment of negative items """


class Language(NamedTuple):
    """ Language of the document. """
    detected: str
    """ Language of the document as detected """


class CharSpan(NamedTuple):
    """ Continuous non-empty span of text, relative to some large text """
    start: int
    """ The first character of this span as a zero-based offset within the full text """
    end: int
    """ Zero-based index of the character immediately following this span """

    @staticmethod
    def of(start: int, end: int) -> 'CharSpan':
        """
        Creates a CharSpan object from start and end indexes.

        :param start: the first character of this span as a zero-based offset within the full text
        :param end: the character immediately following this span. The span cannot be empty.
        """
        if start < 0:
            raise ValueError(f'Start character index cannot be negative ({start})')
        if end <= start:
            raise ValueError(f'End character must be after the start character ({end})')

        return CharSpan(start, end)

    @staticmethod
    def withLen(start: int, length: int) -> 'CharSpan':
        """
        Creates a CharSpan object from start index and text length.

        :param start: the first character of this span as a zero-based offset within the full text
        :param length: the length of this span
        """
        if length <= 0:
            raise ValueError(f'Length has to be greater than zero ({length})')

        return CharSpan.of(start, start + length)

    def __len__(self):
        """ Length of the span in characters """
        return self.end - self.start

    def isValid(self) -> bool:
        """ Returns true if the span is valid, i.e. the start index precedes the end index. """
        return 0 <= self.start < self.end

    def extractText(self, fullText: str) -> str:
        """ Substring of a full text as denoted by this span """
        if len(fullText) < self.end:
            raise ValueError(f'Text too short ({len(fullText)}) for the span ({self}).')

        return fullText[self.start:self.end]


class _Node(ABC):
    """
    This is an implementation class, used as a super class of Token and TectoToken.
    We use the word node to refer to both tokens and tecto-tokens.
    In general, we assume that any tree can be non-projective  (i.e. generate by context-sensitive grammar),
    but not that for a tecto tree the linear order of nodes has no meaning.

    All nodes in the tree should be of the same type: either all Tokens or all TectoTokens.
    """

    def __init__(self, *, id: str, idx: int) -> None:
        self.id: str = id
        """ ID of the node used to refer to it from other objects """
        self._idx: int = idx
        """ Zero-based index of the token within the sentence """
        self._parent: Optional[_Node] = None
        """ Tokens that this token depends on. None for the root. """
        self._children: List[_Node] = []
        """ Tokens that depend of this token, ordered by word-order """
        self.sentence: 'Sentence' = None   # can be None only during construction.
        """ Sentence this token belongs to """

    @property
    def idx(self) -> int:
        """ Zero-based index of this token reflecting its word-order position within the sentence. """
        return self._idx

    @property
    def isLeaf(self) -> bool:
        """ Check whether this token is a leaf (i.e has no dependents). """
        return len(self._children) == 0

    @property
    def isRoot(self) -> bool:
        """ Check whether this token is the root of the sentence. """
        return self._parent is None

    @property
    def isContinuous(self) -> bool:
        """
        Checks if the phrase dominated by this token is continuous.
        """
        return NodeUtils.isContinuous(NodeUtils.coverage(self))

    @property
    def depth(self) -> int:
        """
        Depth of this token in the dependency tree.

        :returns: distance, i.e. number of dependency edges, from the root of the sentence
        """
        if self._parent:
            return self._parent.depth + 1
        else:
            return 0

    def toSimpleString(self) -> str:
        """ Converts the token to a default non-recursive string; overriden in subclasses. """
        return str(self.idx)

    def toTreeString(self, printToken: Union[Callable[['Token'], str], Callable[['TectoToken'], str]]) -> str:
        """
        Parenthesised representation of this tree.

        :param printToken: function printing individual tokens
        :returns: string representation of the tree rooted in this token
        """
        if self._children:
            childrenStr = ','.join([c.toTreeString(printToken) for c in self._children])
            return printToken(self) + '(' + childrenStr + ')'
        else:
            return printToken(self)

    def toIndentTreeString(self, printToken:
        Union[Callable[['Token'], str], Callable[['TectoToken'], str]],
        indentStr: str = '   ',
        depth: int=0
    ) -> str:
        """
        Indented representation of this tree.

        :param printToken: function printing individual tokens
        :param indentStr: string used to indent each level from the previous one
        :param depth: indentation level to start with
        :returns: string representation of the tree rooted in this token
        """
        if self._children:
            childrenStr = '\n'.join([c.toIndentTreeString(printToken, indentStr=indentStr, depth=depth + 1) for c in self._children])
            childrenStr = f'\n{childrenStr}\n'
        else:
            childrenStr = ''

        return depth*indentStr + printToken(self) + childrenStr

    def toSimpleTreeString(self) -> str:
        """
        Simple representation of this tree using toSimpleString to convert individual nodes.
        """
        return self.toTreeString(lambda t: t.toSimpleString())

    def toSimpleIndentTreeString(self) -> str:
        """
        Simple indented representation of this tree using toSimpleString to convert individual nodes.
        """
        return self.toIndentTreeString(lambda t: t.toSimpleString())


class Token(_Node):
    """
    A token including basic morphological and syntactic information.
    A token is similar to a word, but includes punctuation.
    Tokens have an zero-based index reflecting their position within their sentence.
    The morphological and syntactical features might be None (deepLemma, lemma, morphTag, pos, fnc, parent),
    or empty (children) if not requested or supported.
    """

    FEAT_LEMMA_INFO = 'lemmaInfo'
    # lemma info features, a list of strings
    FEAT_NEGATED = 'negated'
    # key presence signifies it is a negated word, value = True
    FEAT_UNKNOWN = 'unknown'
    # key presence signifies it is an unknown word, value = True

    def __init__(self, *,
        id: str,
        idx: int,
        text: str,
        charSpan: CharSpan,
        corrText: str,
        corrCharSpan: CharSpan,
        deepLemma: str = None,
        lemma: str = None,
        pos: ud.UPos = None,
        feats: Mapping[str, Union[str, List[str]]] = None,
        morphTag: str = None,
        fnc: ud.UDep = None
    ) -> None:
        _Node.__init__(self, id=id, idx=idx)
        self.text = text
        """ Text of this token """
        self.charSpan = charSpan
        """ Character span within the paragraph """
        self.corrText = corrText
        """ Text of this token after correction """
        self.corrCharSpan = corrCharSpan
        """ Character span within the paragraph (after correction) """
        self.deepLemma = deepLemma
        """ Lemma of the token e.g. bezpecny. None if not requested/supported. """
        self.lemma = lemma
        """ Simple lemma of the token, e.g. nejnebezpecnejsi (in Cz, includes negation and grade). 
        None if not requested/supported. """
        self.pos = pos
        """ Google universal tag. None if not requested/supported. """
        self.feats: Mapping[str, Union[str, List[str]]] = feats or {}
        """ Universal and custom features """
        self.morphTag = morphTag
        """ Morphological tag, e.g. AAMS1-...., VBD, ... None if not requested/supported. """
        self.fnc = fnc
        """ Label of the dependency edge. None if not requested/supported. """

    def __repr__(self) -> str:
        return ('Token('
                f'id={self.id!r}, idx={self.idx!r}, '
                f'text={self.text!r}, fnc={self.charSpan!r}, '
                f'text={self.corrText!r}, fnc={self.corrCharSpan!r}, '
                f'deepLemma={self.deepLemma!r}, surfaceLemma={self.lemma!r}, '
                f'pos={self.pos!r},  feats={self.feats!r}, morphTag={self.morphTag!r}, fnc={self.fnc!r}, '
                f'children={NodeUtils.toSimpleString(self.children, quote=True)}, '
                f'parent={self.parent.toSimpleString() if self.parent else -1!r})')

    def __hash__(self):
        return hash(self.id)

    @property
    def parent(self) -> Optional['Token']:
        """ Dependency parent of this token. None if root of the sentence or result contains not syntax info. """
        return self._parent

    @property
    def children(self) -> List['Token']:
        """ Dependents of this token ordered by word-order. """
        return cast(List[Token], self._children)

    @property
    def leftChildren(self) -> List['Token']:
        """
        Children of this token that precede it.
        """
        return [cast(Token, c) for c in self.children if c.idx < self.idx]

    @property
    def rightChildren(self) -> List['Token']:
        """
        Children of this token that follow it.
        """
        return [cast(Token, c) for c in self.children if c.idx > self.idx]

    @property
    def isNegated(self) -> bool:
        """
        True iff the token form contains a negation prefix.
        """
        return toBool(self.feats.get(Token.FEAT_NEGATED))

    @property
    def isUnknown(self) -> bool:
        """
        True iff the token is unknown to the lemmatizer. The lemma provided is the same as the token itself.
        """
        return toBool(self.feats.get(Token.FEAT_UNKNOWN))

    def offsetToken(self, offset: int) -> Optional['Token']:
        """
        Token following or preceding this token within the sentence.

        :param offset: relative offset. The following tokens have a positive offset,
            preceding a negative one. The ext token has offset = 1.
        :returns: the token at the relative offset or None if the offset is invalid
        """
        tokens = self.sentence.tokens
        if 0 <= self.idx + offset < len(tokens):
            return tokens[self.idx + offset]
        else:
            return None

    def previous(self) -> Optional['Token']:
        """
        The previous token or None if this token is sentence initial.
        """
        return self.offsetToken(-1)

    def next(self) -> Optional['Token']:
        """
        The next token or None if this token is sentence final.
        """
        return self.offsetToken(1)

    def toSimpleString(self) -> str:
        """ Converts the token to a default non-recursive string: index + text """
        return self.toStringITx()

    def toStringITx(self) -> str:
        """ Converts the token to a non-recursive string: index + text """
        return f'{self.idx}:{self.corrText}'

    def toStringITxF(self) -> str:
        """ Converts the token to a non-recursive string: index + text + function """
        return f'{self.idx}:{self.corrText}:{self.fnc}'


class TokenSupport(NamedTuple):
    """
    Tokens within a single sentence; ordered by word-order; non-empty, continuous or discontinuous.
    Do not construct directly, use TokenSupport.of
    """
    tokens: List[Token]
    """ The tokens of this support. """
    isContinuous: bool
    """ Is this support a continuous sequence of tokens, i.e. a token span? """

    @staticmethod
    def of(tokens: Sequence[Token]) -> 'TokenSupport':
        """
        Creates a TokenSupport object from a list of tokens.

        :param tokens: non-empty list of tokens (might not be sorted)
        """
        if not tokens:
            raise ValueError("Tokens cannot be None or empty")
        if not NodeUtils.isFromSameSentence(tokens):
            raise ValueError("Tokens are not from the same sentence.")
        tokens = NodeUtils.sorted(tokens)
        isContinuous = NodeUtils.isContinuous(tokens)
        return TokenSupport(tokens, isContinuous)

    def spans(self) -> Iterable['TokenSupport']:
        """
        Breaks this token support into continuous sub-sequences of tokens.

        :return: series of token supports together equivalent to this token support
        """
        if self.isContinuous:
            yield self
        else:
            start = 0
            prev = self.tokens[0]
            for i in range(1, len(self.tokens)):
                cur = self.tokens[i]
                if prev.idx + 1 != cur.idx:
                    yield TokenSupport(self.tokens[start:i], isContinuous=True)
                    start = i
                prev = cur

            yield TokenSupport(self.tokens[start:], isContinuous=True)

    @property
    def sentence(self) -> 'Sentence':
        return self.tokens[0].sentence

    def __iter__(self) -> Iterator[Token]:
        return iter(self.tokens)

    def len(self) -> 'int':
        """ Number of covered tokens. """
        return len(self.tokens)

    def __len__(self) -> int:
        """ Number of covered tokens. """
        return len(self.tokens)

    @property
    def first(self) -> Token:
        """ The first token. """
        return self.tokens[0]

    @property
    def last(self) -> Token:
        """ The last token. """
        return self.tokens[-1]

    @property
    def charSpan(self) -> CharSpan:
        """ The character span between the first and last token relative to the enclosing paragraph;
        for discontinuous support this includes intervening gaps. """
        return CharSpan(self.firstCharParaIdx, self.lastCharParaIdx)

    @property
    def firstCharParaIdx(self) -> int:
        """ Index of the first character within the enclosing paragraph. """
        return self.first.charSpan.start

    @property
    def lastCharParaIdx(self) -> int:
        """ Index of the last character within the enclosing paragraph. """
        return self.last.charSpan.end

    def texts(self) -> List[str]:
        """ The coverage texts of each of the continuous spans, ordered by word-order."""
        return [s.text for s in self.spans()]

    @property
    def text(self) -> str:
        """
        Substring of a full text as denoted by this support (before correction).
        For discontinuous supports, the result includes the intervening gaps.
        From ``' '.join(tokenSupport.texts())`` differs in correctly reflecting whitespace in the original text.
        """
        return self.charSpan.extractText(self.sentence.paragraph.text)


class TectoToken(_Node):
    """
    A tecto token, i.e. a tectogrammatical abstraction of a word (e.g. 'did not sleep' are three tokens but a single
    tecto-token)
    Tecto tokens have an zero-based index reflecting their position within their sentence.
    """

    def __init__(self, *,
        id: str,
        idx: int,
        fnc: str,
        lemma: str,
        tokenSupport: TokenSupport = None,       # the root or dropped phrases have no surface realization
        entityMention: 'Entity.Mention' = None,
        entity: 'Entity' = None,
        feats: Mapping[str, Union[str, List[str]]] = None
    ) -> None:
        _Node.__init__(self, id=id, idx=idx)
        self.lemma = lemma
        """ Tecto lemma  """
        self.feats: Mapping[str, Union[str, List[str]]] = feats or {}
        """ Grammatical and other features of the tecto token """
        self.tokenSupport = tokenSupport
        """ Surface token corresponding to this tecto token; not necessarily adjacent; ordered by word-order """
        self.entityMention = entityMention
        """ Entity mention associated with this tecto token; None if there is no such entity. """
        self.entity = entity
        """ Legacy value: Entity associated with this tecto token; None if there is no such entity. 
        (Used only by F2, not by G3) """
        self.fnc = fnc
        """ Label of the dependency edge. """

    @property
    def parent(self) -> Optional['TectoToken']:
        """ Dependency parent of this tecto token. None if this token is the root of the sentence. """
        return self._parent

    @property
    def children(self) -> List['TectoToken']:
        """ Dependents of this token ordered by word-order. """
        return cast(List[TectoToken], self._children)

    def __repr__(self):
        return ('TectoToken('
                f'id={self.id!r}, idx={self.idx!r}, '
                f'text={self.lemma!r}, '
                f'features={self.feats!r}, '
                f'tokens={self.tokenSupport!r}, '
                f'entityMention={self.entityMention!r}, entity={self.entity!r}, '
                f'fnc={self.fnc!r}, '
                f'children={NodeUtils.toSimpleString(self.children, quote=True)}, '
                f'parent={self.parent.toSimpleString() if self.parent else -1!r})')

    def __hash__(self):
        return hash(self.id)

    def toSimpleString(self) -> str:
        """ Converts the tecto token to a default non-recursive string: index + lemma """
        return self.toStringIL()

    def toStringIL(self) -> str:
        """ Converts the tecto token to a non-recursive string: index + lemma """
        return f'{self.idx}:{self.lemma}'

    def toStringILF(self) -> str:
        """ Converts the tecto token to a non-recursive string: index + lemma + function """
        return f'{self.idx}:{self.lemma}:{self.fnc}'


Node = TypeVar('Node', _Node, Token, TectoToken)


class NodeUtils:
    @staticmethod
    def sorted(tokens: Sequence[Node]) -> List[Node]:
        """
        Orders a list of tokens by word-order (i.e. their sentence index).
        Requires the tokens to be from the same sentence (not checked).

        :return: sorted list of tokens
        """
        return sorted(tokens, key=lambda t: t.idx)

    @staticmethod
    def isSorted(tokens: Sequence[Node]) -> bool:
        """
        Checks if a list of tokens is sorted by word-order (i.e. their sentence index).
        Requires the tokens to be from the same sentence (not checked).
        """
        return all(tokens[i].idx < tokens[i+1].idx for i in range(len(tokens)-1))

    @staticmethod
    def isFromSameSentence(tokens: Sequence[Node]) -> bool:
        """
        Checks if all the tokens come from the same sentence.

        :return: true if the list of tokens is empty, all they are all within the same sentence, false otherwise.
        """
        return all(tokens[i].sentence == tokens[i+1].sentence for i in range(len(tokens)-1))

    @staticmethod
    def isContinuous(tokens: Sequence[Node]) -> bool:
        """
        Checks if the tokens form a continuous sequence.
        Assumes the tokens to be sorted and from the same sentence (not checked).

        :return: true if the list is continuous, false otherwise.
        """
        return isSequential([t.idx for t in tokens])

    @staticmethod
    def toSimpleString(tokens: Sequence[Node], quote: bool=False) -> str:
        """
        Utility method for creating strings with a simplified token list.

        :param tokens: tokens to print
        :param quote: surround each node string with single quotes; useful for __repr__ string
        """
        if quote:
            return '[' + ', '.join('\'' + c.toSimpleString() + '\'' for c in tokens) + ']'
        else:
            return '[' + ', '.join(c.toSimpleString() for c in tokens) + ']'

    @staticmethod
    def coverage(node: Node, reflexive=True, ordered=True) -> List[Node]:
        """
        All nodes dominated by a node.

        :param node: node to get coverage of
        :param reflexive: whether the node itself is included
        :param ordered: whether should the result be ordered by word order
        :return: coverage of a node
        """
        chunks = [NodeUtils.coverage(c, ordered=False) for c in node._children]

        if reflexive:
            chunks += [[node]]

        tokens = list(chain.from_iterable(chunks))

        if ordered:
            tokens = NodeUtils.sorted(tokens)

        return tokens

    @staticmethod
    def inOrder(node: Node) -> Iterable[Node]:
        """
        In-order iterator over the subtree of this token.

        :param node: root of the tree to traverse
        """
        for c in node.leftChildren:
            yield from NodeUtils.inOrder(c)

        yield node

        for c in node.rightChildren:
            yield from NodeUtils.inOrder(c)

    @staticmethod
    def filteredInOrder(node: Node, skipPredicate: Callable[[Node], bool], includeFilteredRoot: bool = True) -> Iterable[Node]:
        """
        In-order iterator over the subtree of this token which optionally skips some subtrees.

        :param node: root of the tree to traverse
        :param skipPredicate: when this predicate is true on any token, the token's subtree is not traversed
        :param includeFilteredRoot: if true the tokens on which skipPredicate function returns true are included in the result;
           otherwise they are not
        """
        if skipPredicate(node):
            if includeFilteredRoot:
                yield node
        else:
            for c in node.leftChildren:
                yield from NodeUtils.filteredInOrder(c, skipPredicate, includeFilteredRoot)

            yield node

            for c in node.rightChildren:
                yield from NodeUtils.filteredInOrder(c, skipPredicate, includeFilteredRoot)

    @staticmethod
    def preOrder(node: Node) -> Iterable[Node]:
        """
        Pre-order iterator over the subtree of this token.

        :param node: root of the tree to traverse
        """
        yield node

        for c in node._children:
            yield from NodeUtils.preOrder(c)

    @staticmethod
    def filteredPreOrder(node: Node, skipPredicate: Callable[[Node], bool], includeFilteredRoot: bool = True) -> Iterable[Node]:
        """
        Pre-order iterator over the subtree of a node which optionally skips some subtrees.

        :param node: root of the tree to traverse
        :param skipPredicate: when this predicate is true on any node, the node's subtree is not traversed
        :param includeFilteredRoot: if true, the nodes on which skipPredicate function returns true are included in the result;
        """
        if skipPredicate(node):
            if includeFilteredRoot:
                yield node
        else:
            yield node

            for c in node._children:
                yield from NodeUtils.filteredPreOrder(c, skipPredicate, includeFilteredRoot)


class Tree(Generic[Node]):
    def __init__(self, root: Node, tokens: Sequence[Node]) -> None:
        self.root = root
        self.tokens = tokens


class TreeBuilder(Generic[Node]):
    """ Builder creating a dependency tree out of tokens. """

    def __init__(self) -> None:
        self._nodes: List[Node] = []
        self._deps: Dict[int, int] = {}

    def addNode(self, node: Node) -> 'TreeBuilder[Node]':
        """
        Record a single token as a node of the tree.

        :param node: token to add. Its index must be correct, parent and children fields are ignored.
        :return: the builder to allow chained calls
        """
        self._nodes.append(node)
        return self

    def addNodes(self, nodes: Iterable[Node]) -> 'TreeBuilder[Node]':
        """
        Record a collection of tokens as nodes of the tree.

        :param nodes: tokens to add. Their index must be correct, parent and children fields are ignored.
        :return: the builder to allow chained calls
        """
        self._nodes.extend(nodes)
        return self

    def addDependency(self, childIdx: int, parentIdx: int) -> 'TreeBuilder[Node]':
        """
        Record a dependency edge. The tokens connected by the edge might be added later.

        :param childIdx: index of the child token (note: tokens are indexed within their sentences)
        :param parentIdx: index of the parent token (note: tokens are indexed within their sentences)
        :return: the builder to allow chained calls
        """
        if childIdx < 0:
            raise ValueError(f'Negative node index {childIdx}.')
        if parentIdx < 0:
            raise ValueError(f'Negative node index {parentIdx}.')
        if childIdx == parentIdx:
            raise ValueError(f'Dependency edge cannot be reflexive.')
        if childIdx in self._deps and self._deps[childIdx] != parentIdx:
            raise ValueError(f'Node {childIdx} has multiple parents.')

        self._deps[childIdx] = parentIdx
        return self

    def addDummyDependecies(self):
        """ All nodes are hanged to the first one. """
        if self._deps:
            raise ValueError('Dummy dependencies cannot be added when other dependencies have been specified.')
        if not self._nodes:
            return

        self._nodes = NodeUtils.sorted(self._nodes)
        for n in self._nodes[1:]:
            self.addDependency(n.idx, 0)

    def _fillParents(self):
        maxIdx = len(self._nodes) - 1
        for c, p in self._deps.items():
            if maxIdx < c:
                raise ValueError(f'The child of the dependency edge {c} -> {p} is out of range (max={maxIdx}).')
            if maxIdx < p:
                raise ValueError(f'The parent of the dependency edge {c} -> {p} is out of range (max={maxIdx}).')

            self._nodes[c]._parent = self._nodes[p]

    def _findRoot(self):
        roots = [n for n in self._nodes if n.isRoot]

        if len(roots) == 0:
            raise ValueError('No root.')
        if len(roots) > 1:
            raise ValueError('Multiple roots.')

        return roots[0]

    def _fillChildren(self):
        for n in self._nodes:
            n._children = [c for c in self._nodes if c._parent == n]

    def build(self) -> Optional[Tree[Node]]:
        if not self._nodes:
            return None

        """ Creates an ordered dependency tree based on the contents this builder. """
        self._nodes = NodeUtils.sorted(self._nodes)

        if not isSequential([n.idx for n in self._nodes]) or self._nodes[0].idx != 0:
            raise ValueError(f'Indexes are not sequential.')

        self._fillParents()
        root = self._findRoot()  # exactly one root check; addDependency checks for multiple parents => tree
        self._fillChildren()

        return Tree[Node](tokens=self._nodes, root=root)


class Entity:
    """ A class encapsulating an Entity. """
    class Mention:

        def __init__(self, *,
            id: str,
            mwl: str,
            text: str,
            tokenSupport: TokenSupport,
            sentiment: Sentiment = None,
            feats: Mapping[str, str] = None
        ) -> None:
            self.mentionOf: Entity = None
            """ Entity this mention belongs to """
            self.id = id
            """ ID of the mention used to refer to it from other objects """
            self.text = text
            """ The form of this entity mention, as it occurs in the text. """
            self.mwl = mwl
            """ Lemma of this mention (potentially multiword lemma), i.e. base form of the entity expression. """
            self.tokenSupport = tokenSupport
            """ Tokens of this entity mention. """
            self.sentiment = sentiment
            """ Sentiment of this mention. Note: Not supported yet. """
            self.feats: Mapping[str, str] = feats or {}
            """ Custom features/properties. """

        @property
        def sentence(self) -> 'Sentence':
            """
            Sentence containing this entity mention.
            Entity mention belongs to maximally one sentence; artificial mentions without tokens belong to no sentence.
            """
            return self.tokenSupport.sentence

        @property
        def isContinuous(self) -> bool:
            """ Checks whether the entity mention is continuous (most are). """
            return self.tokenSupport.isContinuous

        def __repr__(self):
            return ('EntityMention('
                    f'id={self.id!r}, '
                    f'text={self.text!r}, mwl={self.mwl!r}, '
                    f'tokenSupport={self.tokenSupport!r}, sentiment={self.sentiment!r})')

        def __hash__(self):
            return hash(self.id)

    def __init__(self, *,
        id: str,
        gkbId: str = None,
        stdForm: str,
        entityType: str,
        feats: Mapping[str, str] = None,
        mentions: List[Mention],
        sentiment: Sentiment = None
    ) -> None:
        self.id = id
        """ ID of the entity used to refer to it from other objects """
        self.gkbId = gkbId
        """ Unique identifier of this entity in Geneea knowledge-base """
        self.stdForm = stdForm
        """ Standard form of the entity, abstracting from alternative names """
        self.type = entityType
        """ Basic type of this entity (e.g. person, location, ...)"""
        self.feats: Mapping[str, str] = feats or {}
        """ Custom features/properties. """
        self.mentions = mentions
        """ Actual occurrences of this entity in the text. Empty if not requested/supported."""
        self.sentiment = sentiment
        """ Sentiment of this entity. None if not requested. """

    def __repr__(self):
        return ('Entity('
                f'id={self.id!r}, gkbId={self.gkbId!r}, stdForm={self.stdForm!r}, '
                f'type={self.type!r}, '
                f'features={self.feats!r}, mentions={self.mentions!r})')

    def __hash__(self):
        return hash(self.id)


class Tag:
    TYPE_CONTENT = 'content'
    """ Type of the tag with the main topic of the document """
    TYPE_TOPIC = 'topic'
    """ Type of the tag with the main topic of the document """
    TYPE_TOPIC_DISTRIBUTION = 'topic.distribution'
    """ Type of the tags with the topic distribution of the document """

    class Mention:

        def __init__(self, *,
            id: str,
            tokenSupport: TokenSupport,
            sentiment: Sentiment = None,
            feats: Mapping[str, str] = None
        ) -> None:
            self.mentionOf: Tag = None
            """ Tag this mention belongs to """
            self.id = id
            """ ID of the mention used to refer to it from other objects """
            self.tokenSupport: TokenSupport = tokenSupport
            """ Tokens of this tag mention. """
            self.sentiment = sentiment
            """ Sentiment of this mention. Not supported yet.  """
            self.feats: Mapping[str, str] = feats or {}
            """ Custom features/properties. """

        @property
        def sentence(self) -> 'Sentence':
            """
            Sentence containing this tag mention.
            Tag mention belongs to maximally one sentence; artificial mentions without tokens belong to no sentence.
            """
            return self.tokenSupport.sentence

        @property
        def isContinuous(self) -> bool:
            """ Checks whether the tag mention is continuous (most are). """
            return self.tokenSupport.isContinuous

        def __repr__(self):
            return ('TagMention('
                    f'id={self.id!r}, '
                    f'tokenSupport={self.tokenSupport!r}, sentiment={self.sentiment!r})')

        def __hash__(self):
            return hash(self.id)

    def __init__(self, *,
        id: str,
        gkbId: str = None,
        stdForm: str,
        tagType: str,
        relevance: float,
        feats: Mapping[str, str] = None,
        mentions: List[Mention],
        sentiment: Sentiment = None
    ) -> None:
        self.id = id
        """ ID of the tag used to refer to it from other objects """
        self.gkbId = gkbId
        """ Unique identifier of this tag in Geneea knowledge-base. None if not found/linked. """
        self.stdForm = stdForm
        """ Standard form of the tag, abstracting from its alternative names """
        self.type = tagType
        """ Domain-specific type (e.g. content, theme, iAB, department) """
        self.relevance = relevance
        """ Relevance of the tag relative to the content of the document """
        self.feats: Mapping[str, str] = feats or {}
        """ Custom features """
        self.mentions = mentions
        """ Text segments related to this tag. Empty if not appropriate/requested/supported. """
        self.sentiment = sentiment
        """ Sentiment of this tag. Not supported yet.  """

    def __repr__(self):
        return ('Tag('
                f'id={self.id!r}, '
                f'uid={self.gkbId!r}, text={self.stdForm!r}, '
                f'type={self.type!r}, weight={self.relevance!r}, '
                f'features={self.feats!r}, mentions={self.mentions!r})')

    def __hash__(self):
        return hash(self.id)


class Relation:
    TYPE_ATTR = 'attr'
    """ Attribute relation (e.g. `good(pizza)` for _good pizza_, _pizza is good_), the attribute is  """
    TYPE_RELATION = 'relation'
    """ Verbal relation (e.g. `eat(pizza)` for _eat a pizza._"""
    TYPE_EXTERNAL = 'external'
    """ Relation where at least one argument is outside of the the document (e.g. between `pizza` in the document and 
    `food` item in the knowledgebase) """

    FEAT_NEGATED = 'negated'
    # key presence signifies it is a negated word, value = True
    FEAT_MODALITY = 'modality'
    # feature storing info about modality

    class Argument(NamedTuple):
        name: str
        """ Name of the argument (e.g. John) """
        type: str
        """ Type of the argument (subject, object) """
        entity: Optional[Entity]
        """ The entity corresponding to this argument, if any. None if the argument is not an entity. """

    class Support(NamedTuple):
        """ Tokens corresponding to a single head (predicate) of a relation """
        tokenSupport: TokenSupport
        """ Tokens corresponding to the head of the relation """
        tectoToken: Optional[TectoToken]
        """ Tecto token corresponding to the tokens. None if tecto tokens are not part of the model.  """

        def __repr__(self):
            return ('Relation('
                    f'tokenSupport={self.tokenSupport!r}, '
                    f'tectoToken={self.tectoToken!r}'
            )

    def __init__(self, *,
        id: str,
        name: str,
        textRepr: str,
        type: str,
        args: List[Argument],
        feats: Mapping[str, str] = None,
        support: List[Support],
        sentiment: Sentiment = None
    ) -> None:
        self.id = id
        """ ID of the relation used to refer to it from other objects """
        self.textRepr = textRepr
        """ Human readable representation of the relation, e.g. `eat-not(SUBJ:John, DOBJ:pizza) """
        self.name = name
        """ Name of the relation , e.g. `eat` for _eat a pizza_ or `good` for _a good pizza_ """
        self.type = type
        """ One of Relation.TYPE_ATTR, Relation.TYPE_RELATION, Relation.TYPE_EXTERNAL """
        self.args = args
        """ Arguments of the relation (subject, possibly an object). """
        self.feats: Mapping[str, str] = feats or {}
        """ Any features of the relation e.g. [modality: can] """
        self.support = support
        """ Tecto-tokens of all the mentions of the relations (restricted to its head). Empty if not requested. """
        self.sentiment = sentiment
        """ Sentiment of this relation. None if not requested. """

    @property
    def isNegated(self) -> bool:
        return toBool(self.feats.get(Relation.FEAT_NEGATED))

    @property
    def modality(self) -> Optional[str]:
        return self.feats.get(Relation.FEAT_MODALITY)

    def __repr__(self):
        return ('Relation('
                f'id={self.id!r}, '
                f'stdForm={self.textRepr!r}, name={self.name!r}, '
                f'type={self.type!r}, args={self.args!r}'
                f'features={self.feats!r}, support={self.support!r})'
        )

    def __hash__(self):
        return hash(self.id)


class Sentence:
    """ A single sentence with its morphological, syntactical, deep-syntactical and sentimental analysis """
    def __init__(self, *,
        id: str,
        root: Token,
        tokens: List[Token],
        tectoRoot: TectoToken = None,
        tectoTokens: List[TectoToken],
        sentiment: Sentiment = None
    ) -> None:
        self.id = id
        """ ID of the sentence used to refer to it from other objects """
        self.paragraph: 'Paragraph' = None
        """ the paragraph containing this sentence """
        self.root = root
        """ Token which is the root of the syntactic structure of the sentence """
        self.tokens = tokens
        """ All tokens of the sentence ordered by word-order """
        self.tectoRoot = tectoRoot
        """ Tecto token which is the root of the tecto structure of the sentence """
        self.tectoTokens = tectoTokens
        """ All tecto tokens of the sentence; the order has no meaning """
        self.sentiment = sentiment
        """ Optional sentiment of the sentence """

    @property
    def text(self):
        """ text of the sentence (before correction) """
        return self.charSpan.extractText(self.paragraph.text)

    @property
    def charSpan(self):
        """ text span within the paragraph """
        return CharSpan(self.tokens[0].charSpan.start, self.tokens[-1].charSpan.end)

    @property
    def corrText(self):
        """ corrected text of the sentence """
        return self.corrCharSpan.extractText(self.paragraph.corrText)

    @property
    def corrCharSpan(self):
        """ corrected text span within the paragraph """
        return CharSpan(self.tokens[0].corrCharSpan.start, self.tokens[-1].corrCharSpan.end)

    def __repr__(self):
        return ('Sentence('
                f'id={self.id!r}, '
                f'charSpan={self.charSpan!r}, '
                f'root={self.root.toSimpleString()!r}, '
                f'tokens={NodeUtils.toSimpleString(self.tokens, quote=True)}, '
                f'tectoRoot={self.tectoRoot.toSimpleString() if self.tectoRoot else None!r}, '
                f'tectoTokens={NodeUtils.toSimpleString(self.tectoTokens, quote=True)}, '
                f'sentiment={self.sentiment!r})')

    def __hash__(self):
        return hash(self.id)


class Paragraph:
    TYPE_TITLE = 'TITLE'
    """ Type of a paragraph representing a title of the whole document. Also used for email subjects. """
    TYPE_ABSTRACT = 'ABSTRACT'
    """ Type of a paragraph representing an abstract (lead or perex) of the whole document """
    TYPE_BODY = 'BODY'
    """ Type of a paragraph containing regular text (for now this is used for the whole body of the document) """
    TYPE_SECTION_HEADING = 'section_heading'
    """ Type of a paragraph representing a section/chapter heading (not used yet) """

    def __init__(self, *,
        id: str,
        type: str,
        text: str,
        corrText: str,
        sentences: List[Sentence]
    ) -> None:
        self.id = id
        """ ID of the paragraph used to refer to it from other objects """
        self.container: G3 = None
        """ the full analysis object containing this paragraph """
        self.type = type
        """ title, section heading, lead, body text, etc. For now, it is simply the segment type: title, lead, body"""
        self.text = text
        """ the original paragraph text (token offsets link here) """
        self.corrText = corrText
        """ the paragraph text after correction (corrected token offsets link here) """
        self.sentences = sentences
        """ the sentences the paragraph consists of """

    @property
    def tokens(self) -> Iterable[Token]:
        """
        Tokens across all sentences.
        """
        for s in self.sentences:
            for t in s.tokens:
                yield t

    @property
    def tectoTokens(self) -> Iterable[TectoToken]:
        """
        Tecto tokens across all sentences.
        """
        for s in self.sentences:
            for t in s.tectoTokens:
                yield t

    def __repr__(self):
        return ('Paragraph('
                f'id={self.id!r}, '
                f'paraType={self.type!r}, '
                f'text={self.text!r}, corrText={self.corrText!r}, '
                f'sentence={self.sentences!r})')

    def __hash__(self):
        return hash(self.id)


class G3:
    def __init__(self, *,
        apiVersion: str = None,
        docId: str = None,
        language: Language,
        paragraphs: List[Paragraph],
        docSentiment: Optional[Sentiment],
        entities: List[Entity],
        tags: List[Tag],
        relations: List[Relation],
        usedChars: int = None,
        metadata: Mapping[str, Any] = None,
        debugInfo: Any = None
    ) -> None:
        self.apiVersion = apiVersion or '3.0.0'
        """ The version of the API. """
        self.docId = docId
        """ Document id """
        self.language = language
        """ Language of the document and analysis. """
        self.paragraphs = paragraphs
        """ The paragraphs within the document. For F2, these are segments. """
        self.docSentiment = docSentiment
        """ Sentiment of the document. """
        self.entities = entities
        """ The entities in the document. """
        self.tags = tags
        """ The tags of the document. """
        self.relations = relations
        """ The relations in the document. """
        self.usedChars = usedChars
        """ Characters billed for the analysis. """
        self.metadata = metadata
        """ The extra non-NLP type of information related to analysis."""
        self.debugInfo = debugInfo
        """ Debugging information, if any """

    def __repr__(self):
        return ('G3('
                f'docId={self.docId!r}, language={self.language!r}, paragraphs={self.paragraphs!r}, '
                f'sentiment={self.docSentiment!r}, entities={self.entities!r}, tags={self.tags!r}, '
                f'relations={self.relations!r}, metadata={self.metadata!r})')

    @property
    def sentences(self) -> Iterable[Sentence]:
        """
        Sentences across all paragraphs.
        """
        for p in self.paragraphs:
            for s in p.sentences:
                yield s

    @property
    def tokens(self) -> Iterable[Token]:
        """
        Tokens across all paragraphs.
        """
        for s in self.sentences:
            for t in s.tokens:
                yield t

    @property
    def tectoTokens(self) -> Iterable[TectoToken]:
        """
        Tecto tokens across all paragraphs.
        """
        for s in self.sentences:
            for t in s.tectoTokens:
                yield t

    def getParaByType(self, paraType: str) -> Optional[Paragraph]:
        """
        Returns a paragraph with the specified type.
        Throws a ValueError if there are more than one, and return None if there are none.
        This is intended for legacy paragraphs corresponding to title/lead/text segments.

        :return: a paragraph with the specified type.
        """
        paras = [p for p in self.paragraphs if p.type == paraType]
        if len(paras) > 1:
            raise ValueError(f'Multiple paragraphs with the type {paraType}')
        return paras[0] if paras else None

    def title(self) -> Optional[Paragraph]:
        """
        Returns the title paragraph if present, None if not, and throws a ValueError if there are multiple title paragraphs.
        """
        return self.getParaByType(Paragraph.TYPE_TITLE)

    def lead(self) -> Optional[Paragraph]:
        """
        Returns the lead paragraph if present, None if not, and throws a ValueError if there are multiple lead paragraphs.
        """
        return self.getParaByType(Paragraph.TYPE_ABSTRACT)

    def body(self) -> Optional[Paragraph]:
        """
        Returns the body paragraph if present, None if not, and throws a ValueError if there are multiple body paragraphs.
        """
        return self.getParaByType(Paragraph.TYPE_BODY)
