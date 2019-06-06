#
# Copyright (c) 2019 UCT Prague.
# 
# refa_test.py is part of Invenio Explicit ACLs 
# (see https://github.com/oarepo/invenio-explicit-acls).
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from lib2to3.fixer_base import BaseFix
from lib2to3.pgen2 import token
from lib2to3.pytree import Leaf
from lib2to3.refactor import RefactoringTool


class TestFixer(BaseFix):
    PATTERN = """
    classdef<any*>
    """

    def transform(self, node, results):
        node.children.extend([Leaf(token.INDENT, '    '), Leaf(token.COMMENT, 'b = 32')])


class Refa(RefactoringTool):
    def get_fixers(self):
        return ([], [TestFixer(self.options, self.fixer_log)])


rf = Refa([])

print(rf.refactor_string(
    """
class Blah:
    a = 12
    def b(self):
        print("c")
    """, 'a'))
