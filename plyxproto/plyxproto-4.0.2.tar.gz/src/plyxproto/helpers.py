# Copyright 2017-present Open Networking Foundation and others
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from six.moves import range
import sys


class LexHelper:
    offset = 0

    def get_max_linespan(self, p):
        defSpan = [1e60, -1]
        mSpan = [1e60, -1]
        for sp in range(0, len(p)):
            csp = p.linespan(sp)
            if csp[0] == 0 and csp[1] == 0:
                if hasattr(p[sp], "linespan"):
                    csp = p[sp].linespan
                else:
                    continue
            if csp is None or len(csp) != 2:
                continue
            if csp[0] == 0 and csp[1] == 0:
                continue
            if csp[0] < mSpan[0]:
                mSpan[0] = csp[0]
            if csp[1] > mSpan[1]:
                mSpan[1] = csp[1]
        if defSpan == mSpan:
            return (0, 0)
        return tuple([mSpan[0] - self.offset, mSpan[1] - self.offset])

    def get_max_lexspan(self, p):
        defSpan = [1e60, -1]
        mSpan = [1e60, -1]
        for sp in range(0, len(p)):
            csp = p.lexspan(sp)
            if csp[0] == 0 and csp[1] == 0:
                if hasattr(p[sp], "lexspan"):
                    csp = p[sp].lexspan
                else:
                    continue
            if csp is None or len(csp) != 2:
                continue
            if csp[0] == 0 and csp[1] == 0:
                continue
            if csp[0] < mSpan[0]:
                mSpan[0] = csp[0]
            if csp[1] > mSpan[1]:
                mSpan[1] = csp[1]
        if defSpan == mSpan:
            return (0, 0)
        return tuple([mSpan[0] - self.offset, mSpan[1] - self.offset])

    def set_parse_object(self, dst, p):
        dst.setLexData(
            linespan=self.get_max_linespan(p),
            lexspan=self.get_max_lexspan(p))
        dst.setLexObj(p)


class Base(object):
    parent = None
    lexspan = None
    linespan = None

    def v(self, obj, visitor):
        if obj is None:
            return
        elif hasattr(obj, "accept"):
            obj.accept(visitor)
        elif isinstance(obj, list):
            for s in obj:
                self.v(s, visitor)
            pass
        pass

    @staticmethod
    def p(obj, parent):
        if isinstance(obj, list):
            for s in obj:
                Base.p(s, parent)

        if hasattr(obj, "parent"):
            obj.parent = parent

# Lexical unit - contains lexspan and linespan for later analysis.


class LU(Base):

    def __init__(self, p, idx):
        self.p = p
        self.idx = idx
        self.pval = p[idx]
        self.lexspan = p.lexspan(idx)
        self.linespan = p.linespan(idx)

        # If string is in the value (raw value) and start and stop lexspan is the same, add real span
        # obtained by string length.
        if isinstance(self.pval, str) \
                and self.lexspan is not None \
                and self.lexspan[0] == self.lexspan[1] \
                and self.lexspan[0] != 0:
            self.lexspan = tuple(
                [self.lexspan[0], self.lexspan[0] + len(self.pval)])
        super(LU, self).__init__()

    @staticmethod
    def i(p, idx):
        if isinstance(p[idx], LU):
            return p[idx]
        if isinstance(p[idx], str):
            return LU(p, idx)
        return p[idx]

    def describe(self):
        return "LU(%s,%s)" % (self.pval, self.lexspan)

    def __str__(self):
        return self.pval

    def __repr__(self):
        return self.describe()

    def accept(self, visitor):
        self.v(self.pval, visitor)

    def __iter__(self):
        for x in self.pval:
            yield x

# Base node


class SourceElement(Base):
    '''
    A SourceElement is the base class for all elements that occur in a Protocol Buffers
    file parsed by plyproto.
    '''

    def __init__(self, linespan=[], lexspan=[], p=None):
        super(SourceElement, self).__init__()
        self._fields = []  # ['linespan', 'lexspan']
        self.linespan = linespan
        self.lexspan = lexspan
        self.p = p

    def __repr__(self):
        equals = ("{0}={1!r}".format(k, getattr(self, k))
                  for k in self._fields)
        args = ", ".join(equals)
        return "{0}({1})".format(self.__class__.__name__, args)

    def __eq__(self, other):
        try:
            return self.__dict__ == other.__dict__
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    def setLexData(self, linespan, lexspan):
        self.linespan = linespan
        self.lexspan = lexspan

    def setLexObj(self, p):
        self.p = p

    def accept(self, visitor):
        pass


class Visitor(object):

    def __init__(self, verbose=False):
        self.verbose = verbose

    def __getattr__(self, name):
        if not name.startswith('visit_'):
            raise AttributeError(
                'name must start with visit_ but was {}'.format(name))

        def f(element):
            if self.verbose:
                msg = 'unimplemented call to {}; ignoring ({})'
                print((msg.format(name, element)), file=sys.stderr)
            return True
        return f

    # visitor.visit_PackageStatement(self)
    # visitor.visit_ImportStatement(self)
    # visitor.visit_OptionStatement(self)
    # visitor.visit_FieldDirective(self)
    # visitor.visit_FieldType(self)
    # visitor.visit_FieldDefinition(self)
    # visitor.visit_EnumFieldDefinition(self)
    # visitor.visit_EnumDefinition(self)
    # visitor.visit_MessageDefinition(self)
    # visitor.visit_MessageExtension(self)
    # visitor.visit_MethodDefinition(self)
    # visitor.visit_ServiceDefinition(self)
    # visitor.visit_ExtensionsDirective(self)
    # visitor.visit_Literal(self)
    # visitor.visit_Name(self)
    # visitor.visit_Proto(self)
    # visitor.visit_LU(self)
