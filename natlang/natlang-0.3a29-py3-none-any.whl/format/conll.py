# -*- coding: utf-8 -*-
# Python version: 2/3
#
# CoNLL U data format
# Simon Fraser University
# Jetic Gu
#
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import copy
import inspect
import unittest
import progressbar

from natlang.exporter import exportToFile


defaultEntryIndex = {
    # This is taken from http://universaldependencies.org/format.html
    # CoNLL-U
    "ID": 0,  # Word index, integer starting at 1 for each new sentence;
    "FORM": 1,  # Word form or punctuation symbol.
    "LEMMA": 2,  # Lemma or stem of word form.
    "UPOS": 3,  # Universal part-of-speech tag.
    "XPOS": 4,  # Language-specific part-of-speech tag; underscore if not
                # available.
    "FEATS": 5,  # List of morphological features from the universal feature
                 # inventory or from a defined language-specific extension;
                 # underscore if not available.
    "HEAD": 6,  # Head of the current word, which is either a value of ID or
                # zero (0).
    "DEPREL": 7,  # Universal dependency relation to the HEAD (root iff HEAD =
                  # 0) or a defined language-specific subtype of one.
    "DEPS": 8,  # Enhanced dependency graph in the form of a list of
                # head-deprel pairs.
                # Note (Jetic): Universal dependencies don't use this at all.
    "MISC": 9,  # Any other annotation.
    "__name__": "CoNLL U",
}

defaultCommentMark = '#'
if sys.version_info[0] < 3:
    # OK this is a tad silly
    _lArrow = u'\u250C'.encode('utf-8')
    _rArrow = u'\u2514'.encode('utf-8')
    _vArrow = u'\u2502'.encode('utf-8')
    _hArrow = u'\u2500'.encode('utf-8')
else:
    _lArrow = u'\u250C'
    _rArrow = u'\u2514'
    _vArrow = u'\u2502'
    _hArrow = u'\u2500'


class Node():
    '''
    This is the main data structure of a dependency, a Node instance is a node
    on the tree. The structure of the subtree with node x as root can be viewed
    by calling x.__repr__()
    '''
    def __init__(self, parent=None):
        self.value = ()
        self.phrase = []
        self.id = 0
        self.parent = parent
        self.deprel = ""
        self.leftChild = None
        self.rightChild = None
        self.sibling = None
        self.depth = -1
        self.format = None
        self.rawEntries = []
        return

    def __repr__(self, __spacing=[], __showSibling=False):
        '''
        This method prints the structure of the subtree with self as root.
        '''
        if self.leftChild is not None:
            if len(__spacing) != 0 and __spacing[-1] == _lArrow and\
                    self.parent is not None and self.parent.leftChild == self:
                self.leftChild.__repr__(__spacing[:-1] + [' ', _lArrow], True)
            else:
                self.leftChild.__repr__(__spacing + [_lArrow], True)

        for i, entry in enumerate(__spacing):
            if i == 0:
                print(' ', end='')
            if i == len(__spacing) - 1:
                print(entry, end='')
            elif entry != " ":
                print(_vArrow + "       ", end='')
            else:
                print("        ", end='')

        if self.parent is None:
            print("ROOT")
        elif len(__spacing) == 0:
            print(self.value[0])
        else:
            print(_hArrow + self.deprel + _hArrow + self.value[0])

        if self.rightChild is not None:
            if len(__spacing) != 0 and __spacing[-1] == _rArrow and\
                    self.sibling is None:
                self.rightChild.__repr__(__spacing[:-1] + [' ', _rArrow], True)
            else:
                self.rightChild.__repr__(__spacing + [_rArrow], True)

        if self.sibling is not None and __showSibling is True:
            self.sibling.__repr__(__spacing, True)

        return "\nRepresentation: " +\
            "conll.Node(\"" + str((self.id,) + self.value) + "\")\n" +\
            "Leafnode Label: " + str([n.value[0] for n in self.phrase]) +\
            "\n"

    def __len__(self):
        return len(self.phrase)

    def calcPhrase(self, force=False):
        if self.phrase == [] or force is True:
            self.phrase = []
            if self.leftChild is not None:
                self.phrase += self.leftChild.calcPhrase(force)

            if self.parent is not None:
                self.phrase += [self]

            if self.rightChild is not None:
                self.phrase += self.rightChild.calcPhrase(force)

            if self.sibling is not None:
                self.sibling.calcPhrase(force)

        if self.sibling is not None:
            return self.phrase + self.sibling.calcPhrase()
        return self.phrase

    def _exportSubTree(self):
        content = []
        if self.leftChild is not None:
            content += self.leftChild._exportSubTree()
        # If current node is root then does not output
        if self.parent is not None:
            content.append("\t".join(self.rawEntries))
        if self.rightChild is not None:
            content += self.rightChild._exportSubTree()

        if self.sibling is not None:
            content += self.sibling._exportSubTree()

        return content

    def export(self):
        content = self._exportSubTree() + [""]

        return "\n".join(content)


def constructFromText(rawContent, entryIndex=defaultEntryIndex):
    content = [line.strip().split('\t') for line in rawContent]
    # adding the root node
    nodes = [Node()]
    if "__name__" in entryIndex:
        nodes[0].format = entryIndex
    nodes[0].value = ("-ROOT-", )

    for i, line in enumerate(content, start=1):
        # Check ID for data integrity
        if int(line[entryIndex["ID"]]) != i:
            sys.stderr.write(
                "natlang.format.conll [WARN]: Corrupt data format\n")
            return None

        # force the first value in node.value to be FORM
        # temporarily store parent id in node.parent
        # store everything else in node.value
        newNode = Node()
        newNode.format = entryIndex
        newNode.rawEntries = line
        newNode.id = i
        newNode.parent = int(line[entryIndex["HEAD"]])
        newNode.deprel = line[entryIndex["DEPREL"]]

        newNode.value = (line[entryIndex["FORM"]], )
        for i, item in enumerate(line):
            if i != entryIndex["ID"] and i != entryIndex["HEAD"] and\
                    i != entryIndex["DEPREL"] and i != entryIndex["FORM"]:
                newNode.value += (line[i] if line[i] != '_' else None, )

        nodes.append(newNode)

    # replace node.parent with real entity.
    # add sibling, leftChild, rightChild
    for node in nodes[1:]:
        node.parent = nodes[node.parent]
        if node.parent.id > node.id:
            # leftChild
            if node.parent.leftChild is None:
                node.parent.leftChild = node
                continue
            tmp = node.parent.leftChild
            while tmp.sibling is not None:
                tmp = tmp.sibling
            tmp.sibling = node
        else:
            # rightChild
            if node.parent.rightChild is None:
                node.parent.rightChild = node
                continue
            tmp = node.parent.rightChild
            while tmp.sibling is not None:
                tmp = tmp.sibling
            tmp.sibling = node
    nodes[0].calcPhrase(force=True)
    return nodes[0]


def load(fileName,
         linesToLoad=sys.maxsize,
         entryIndex=defaultEntryIndex, commentMark=defaultCommentMark,
         verbose=True):
    fileName = os.path.expanduser(fileName)
    content = []
    widgets = [progressbar.Bar('>'), ' ', progressbar.ETA(),
               progressbar.FormatLabel(
               '; Total: %(value)d lines (in: %(elapsed)s)')]
    if verbose is True:
        loadProgressBar =\
            progressbar.ProgressBar(widgets=widgets,
                                    maxval=min(
                                        sum(1 for line in open(fileName)),
                                        linesToLoad)).start()
    i = 0
    entry = []
    with open(fileName) as file:
        for rawLine in file:
            i += 1
            if verbose is True:
                loadProgressBar.update(i)
            line = rawLine.strip()

            if line != "" and line[0] != commentMark:
                entry.append(line)
            else:
                content.append(constructFromText(entry))
                entry = []
                if i >= linesToLoad:
                    break

    if len(entry) > 0:
        content.append(constructFromText(entry))

    if verbose is True:
        loadProgressBar.finish()
    return content


class TestTree(unittest.TestCase):
    def testBuildTreeA(self, x=None):
        rawLine = [
            "1	From	from	ADP	IN	_	3	case	_	_",
            "2	the	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_",
            "3	AP	AP	PROPN	NNP	Number=Sing	4	nmod	_	_",
            "4	comes	come	VERB	VBZ,	" +
            "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_",
            "5	this	this	DET	DT	Number=Sing|PronType=Dem	6	det	_	_",
            "6	story	story	NOUN	NN	Number=Sing	4	nsubj	_	_",
            "7	:	:	PUNCT	:	_	4	punct	_	_]"]
        if x is None:
            x = constructFromText(rawLine)

        correctEntirePhraseForm = ["From", "the", "AP", "comes", "this",
                                   "story", ":"]
        correctLSubPhraseForm = ["From", "the", "AP"]
        correctRSubPhraseForm = ["this", "story"]

        self.assertSequenceEqual(
            correctEntirePhraseForm,
            [n.value[0] for n in x.phrase])
        self.assertSequenceEqual(
            correctLSubPhraseForm,
            [n.value[0] for n in x.rightChild.leftChild.phrase])
        self.assertSequenceEqual(
            correctRSubPhraseForm,
            [n.value[0] for n in x.rightChild.rightChild.phrase])
        return

    def testBuildTreeB(self, x=None):
        rawText = """1	President	President	PROPN	NNP	Number=Sing	2	compound	_	_
        2	Bush	Bush	PROPN	NNP	Number=Sing	5	nsubj	_	_
        3	on	on	ADP	IN	_	4	case	_	_
        4	Tuesday	Tuesday	PROPN	NNP	Number=Sing	5	nmod	_	_
        5	nominated	nominate	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin""" +\
            """	0	root	_	_
        6	two	two	NUM	CD	NumType=Card	7	nummod	_	_
        7	individuals	individual	NOUN	NNS	Number=Plur	5	dobj	_	_
        8	to	to	PART	TO	_	9	mark	_	_
        9	replace	replace	VERB	VB	VerbForm=Inf	5	advcl	_	_
        10	retiring	retire	VERB	VBG	VerbForm=Ger	11	amod	_	_
        11	jurists	jurist	NOUN	NNS	Number=Plur	9	dobj	_	_
        12	on	on	ADP	IN	_	14	case	_	_
        13	federal	federal	ADJ	JJ	Degree=Pos	14	amod	_	_
        14	courts	court	NOUN	NNS	Number=Plur	11	nmod	_	_
        15	in	in	ADP	IN	_	18	case	_	_
        16	the	the	DET	DT	Definite=Def|PronType=Art	18	det	_	_
        17	Washington	Washington	PROPN	NNP	Number=Sing	18	compound	_	_
        18	area	area	NOUN	NN	Number=Sing	14	nmod	_	SpaceAfter=No
        19	.	.	PUNCT	.	_	5	punct	_	_"""
        if x is None:
            x = constructFromText(rawText.split('\n'))

        correctEntirePhraseForm = [
            "President", "Bush", "on", "Tuesday", "nominated", "two",
            "individuals", "to", "replace", "retiring", "jurists", "on",
            "federal", "courts", "in", "the", "Washington", "area", "."]
        correctLSubPhraseForm = ["President", "Bush"]
        correctLSSubPhraseForm = ["on", "Tuesday"]
        correctRSubPhraseForm = ["two", "individuals"]
        correctRSSubPhraseForm = [
            "to", "replace", "retiring", "jurists", "on", "federal", "courts",
            "in", "the", "Washington", "area"]

        self.assertSequenceEqual(
            correctEntirePhraseForm,
            [n.value[0] for n in x.phrase])
        self.assertSequenceEqual(
            correctLSubPhraseForm,
            [n.value[0] for n in x.rightChild.leftChild.phrase])
        self.assertSequenceEqual(
            correctLSSubPhraseForm,
            [n.value[0] for n in x.rightChild.leftChild.sibling.phrase])
        self.assertSequenceEqual(
            correctRSSubPhraseForm,
            [n.value[0] for n in x.rightChild.rightChild.sibling.phrase])
        return

    def testLoader(self):
        currentdir = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))
        parentdir = os.path.dirname(currentdir)
        content = load(parentdir + "/test/sampleCoNLLU.conll", verbose=False)
        A = content[0]
        B = content[1]
        self.testBuildTreeA(A)
        self.testBuildTreeB(B)

    def testExporter(self):
        currentdir = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))
        parentdir = os.path.dirname(currentdir)
        content = load(parentdir + "/test/sampleCoNLLU.conll", verbose=False)
        exportToFile(content, parentdir + "/test/.sampleCoNLLU.conll.tmp")
        exportedContent = load(
            parentdir + "/test/.sampleCoNLLU.conll.tmp", verbose=False)
        self.testBuildTreeA(exportedContent[0])
        self.testBuildTreeB(exportedContent[1])


if __name__ == '__main__':
    if not bool(getattr(sys, 'ps1', sys.flags.interactive)):
        unittest.main()
    else:
        rawLine = [
            "1	From	from	ADP	IN	_	3	case	_	_",
            "2	the	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_",
            "3	AP	AP	PROPN	NNP	Number=Sing	4	nmod	_	_",
            "4	comes	come	VERB	VBZ,	" +
            "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_",
            "5	this	this	DET	DT	Number=Sing|PronType=Dem	6	det	_	_",
            "6	story	story	NOUN	NN	Number=Sing	4	nsubj	_	_",
            "7	:	:	PUNCT	:	_	4	punct	_	_]"]
        x = constructFromText(rawLine)
        rawText = """1	President	President	PROPN	NNP	Number=Sing	2	compound	_	_
        2	Bush	Bush	PROPN	NNP	Number=Sing	5	nsubj	_	_
        3	on	on	ADP	IN	_	4	case	_	_
        4	Tuesday	Tuesday	PROPN	NNP	Number=Sing	5	nmod	_	_
        5	nominated	nominate	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin""" +\
            """	0	root	_	_
        6	two	two	NUM	CD	NumType=Card	7	nummod	_	_
        7	individuals	individual	NOUN	NNS	Number=Plur	5	dobj	_	_
        8	to	to	PART	TO	_	9	mark	_	_
        9	replace	replace	VERB	VB	VerbForm=Inf	5	advcl	_	_
        10	retiring	retire	VERB	VBG	VerbForm=Ger	11	amod	_	_
        11	jurists	jurist	NOUN	NNS	Number=Plur	9	dobj	_	_
        12	on	on	ADP	IN	_	14	case	_	_
        13	federal	federal	ADJ	JJ	Degree=Pos	14	amod	_	_
        14	courts	court	NOUN	NNS	Number=Plur	11	nmod	_	_
        15	in	in	ADP	IN	_	18	case	_	_
        16	the	the	DET	DT	Definite=Def|PronType=Art	18	det	_	_
        17	Washington	Washington	PROPN	NNP	Number=Sing	18	compound	_	_
        18	area	area	NOUN	NN	Number=Sing	14	nmod	_	SpaceAfter=No
        19	.	.	PUNCT	.	_	5	punct	_	_"""
        y = constructFromText(rawText.split('\n'))
        print("Use the two Nodes x and y for testing new methods on Node.")
        print("Use unittest.main() to start unit test")
