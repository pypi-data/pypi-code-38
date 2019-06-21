# -*- coding: utf-8 -*-
# Python version: 2/3
#
# Abstract Meaning Representation Graph class
# Simon Fraser University
# Jetic Gu
#
# This module contains functions and classes necessary for loading Abstract
# Meaning Representation trees. 2 examples are provided in TestTree.
#
from __future__ import absolute_import
import sys
import os
import unittest
import inspect
import progressbar
from copy import deepcopy
from six import string_types


class NodeAMR:
    '''
    This is the main data structure of a tree, a Node instance is a node on the
    tree. The structure of the subtree with node x as root can be viewed by
    calling x.__repr__()
    '''
    def __init__(self, hyperlink=None):
        self.id = ""  # instance id: "b" in "(b/boy)"
        self.concept = ""  # concept name: "boy" in "(b/boy)"
        self.hyperlink = None
        self.parent = None
        self.link = []  # arguments
        self.linkType = ""
        if hyperlink is not None:
            self.id = hyperlink.id
            self.hyperlink = hyperlink
        return

    def __repr__(self, __spacing="", __dispChild=True):
        '''
        This method prints the structure of the graph.
        '''
        if __dispChild is False:
            return "NodeAMR"
        if self.hyperlink is None:
            sys.stdout.write("(" + self.id + " / " + self.concept)
            for (relation, entry) in self.link:
                sys.stdout.write("\n" + __spacing + "      " + relation + " ")
                if isinstance(entry, NodeAMR):
                    entry.__repr__(__spacing + "      ")
                else:
                    sys.stdout.write(entry)
            sys.stdout.write(")")
            if __spacing == "":
                sys.stdout.write("\n")
        else:
            sys.stdout.write(self.id)
        return "NodeAMR"

    def __len__(self):
        raise NotImplemented

    def export(self):
        if self.hyperlink is not None:
            return self.id

        result = "( " + self.id + " / " + self.concept
        for (relation, entry) in self.link:
            result += " " + relation + " "
            if isinstance(entry, NodeAMR):
                result += entry.export()
            else:
                result += entry
        result += " )"
        return result


def constructAMRFromStr(string):
    '''
    This method constructs an AMR graph from a string.
    @param string: str, in Penn Treebank format
    @return root: NodeAMR, the root node.
    '''
    elements = string.replace(" / ", "-/-").split("\"")
    for i in range(len(elements)):
        if i % 2 == 0:
            elements[i] = elements[i].replace(")", "\t)\t")
            elements[i] = elements[i].replace("(", "\t(\t")
            elements[i] = elements[i].replace(" ", "\t")

    elements = [i for i in "\"".join(elements).split("\t") if i != ""]
    instances = {}

    # Generate Instances
    for i in range(len(elements)):
        if "-/-" in elements[i]:
            newInstance = NodeAMR()
            newInstance.id, newInstance.concept =\
                tuple(elements[i].split("-/-"))
            instances[newInstance.id] = newInstance
            elements[i] = newInstance
        elif i != 0 and isinstance(elements[i - 1], string_types) and\
                elements[i - 1][0] == ":" and elements[i] in instances:
            newInstance = NodeAMR(hyperlink=instances[elements[i]])
            elements[i] = newInstance

    def constructGraph(elements):
        result = None
        i = -1
        count = 0
        main = None
        while i < len(elements) - 1:
            i += 1

            if isinstance(elements[i], NodeAMR) and\
                    elements[i].hyperlink is None:
                main = elements[i]
                continue
            if isinstance(elements[i], NodeAMR) and\
                    elements[i].hyperlink is not None:
                main.link[-1] += (elements[i],)
                continue
            if elements[i] == "(":
                count += 1
                if count > 1:
                    length, Node = constructGraph(elements[i:])
                    main.link[-1] += (Node,)
                    i += length - 1
                continue
            if elements[i] == ")":
                count -= 1
                if count == 0:
                    return i, main
                continue
            if elements[i][0] == ":":
                main.link.append((elements[i], ))
                continue
            if elements[i][0] == "\"":
                main.link[-1] += (elements[i],)
                continue
            main.link[-1] += (elements[i],)

    _, root = constructGraph(elements)
    return root


def load(fileName, linesToLoad=sys.maxsize, verbose=True):
    fileName = os.path.expanduser(fileName)
    content = []
    i = 0
    widgets = [progressbar.Bar('>'), ' ', progressbar.ETA(),
               progressbar.FormatLabel(
               '; Total: %(value)d sents (in: %(elapsed)s)')]
    if verbose is True:
        loadProgressBar =\
            progressbar.ProgressBar(widgets=widgets,
                                    maxval=min(
                                        sum(1 for line in open(fileName)),
                                        linesToLoad)).start()
    for line in open(fileName):
        i += 1
        if verbose is True:
            loadProgressBar.update(i)
        content.append(constructAMRFromStr(line))
        if i == linesToLoad:
            break
    if verbose is True:
        loadProgressBar.finish()
    return content


class TestAMR(unittest.TestCase):
    def testBuildAMR_A(self, x=None):
        str = "( a / and :op1 ( i / international ) :op2 ( m / military ) " +\
            ":op3 ( t / terrorism ) )"
        if x is None:
            x = constructAMRFromStr(str)
        self.assertEqual(str.split(), x.export().split())
        return

    def testBuildAMR_B(self, x=None):
        str =\
            "( s / start-01 :ARG0 ( p / picture :ARG1-of ( l / " +\
            "look-forward-03 :ARG0 ( p2 / person ) :ARG1-of ( l2 / long-03 " +\
            ") ) ) :ARG1 ( e / emerge-01 :ARG1-of ( f / frequent-02 ) :loca" +\
            "tion ( m / media :mod ( v / various ) :ARG1-of ( m2 / major-02" +\
            " ) :location ( c / city :wiki \"Hong_Kong\" :name ( n / name :" +\
            "op1 \"Hong\" :op2 \"Kong\" ) ) ) ) :time ( d / date-entity :ye" +\
            "ar 2005 :season ( s2 / summer ) ) )"
        if x is None:
            x = constructAMRFromStr(str)
        self.assertEqual(str.split(), x.export().split())
        return

    def testBuildAMR_C(self, x=None):
        str =\
            "(w / want-01 :ARG0 (b / boy) :ARG1 (g / go-02 :ARG0 b))"
        if x is None:
            x = constructAMRFromStr(str)
        str = str.replace("(", " ( ").replace(")", " ) ")
        self.assertEqual(str.split(), x.export().split())
        return

    def testLoadAMRFromFile(self):
        import warnings
        currentdir = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))
        parentdir = os.path.dirname(currentdir)
        warnings.simplefilter("ignore")
        content = load(parentdir + "/test/sampleAMR.amr", verbose=False)
        rawText = list(open(parentdir + "/test/sampleAMR.amr"))
        for amr, str in zip(content, rawText):
            self.assertEqual(str.split(), amr.export().split())
        return


if __name__ == '__main__':
    import __main__ as main
    if not bool(getattr(sys, 'ps1', sys.flags.interactive)):
        unittest.main()
    else:
        str = "( a / and :op1 ( i / international ) :op2 ( m / military ) " +\
            ":op3 ( t / terrorism ) )"
        x = constructAMRFromStr(str)
        str =\
            "( s / start-01 :ARG0 ( p / picture :ARG1-of ( l / " +\
            "look-forward-03 :ARG0 ( p2 / person ) :ARG1-of ( l2 / long-03 " +\
            ") ) ) :ARG1 ( e / emerge-01 :ARG1-of ( f / frequent-02 ) :loca" +\
            "tion ( m / media :mod ( v / various ) :ARG1-of ( m2 / major-02" +\
            " ) :location ( c / city :wiki \"Hong_Kong\" :name ( n / name :" +\
            "op1 \"Hong\" :op2 \"Kong\" ) ) ) ) :time ( d / date-entity :ye" +\
            "ar 2005 :season ( s2 / summer ) ) )"
        y = constructAMRFromStr(str)
        str =\
            "(w / want-01 :ARG0 (b / boy) :ARG1 (g / go-02 :ARG0 b))"
        z = constructAMRFromStr(str)
        print("Use the three Nodes x, y, z for testing new methods on Node.")
        print("Use unittest.main() to start unit test")
