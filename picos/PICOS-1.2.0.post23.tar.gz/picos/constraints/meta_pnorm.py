# coding: utf-8

#-------------------------------------------------------------------------------
# Copyright (C) 2012-2017 Guillaume Sagnol
# Copyright (C)      2018 Maximilian Stahlberg
#
# This file is part of PICOS.
#
# PICOS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PICOS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# This file implements a p-norm inequality constraint.
#-------------------------------------------------------------------------------

from ..tools import geomean
from .. import glyphs

from .constraint import MetaConstraint

class PNormConstraint(MetaConstraint):
    def __init__(self, pNorm, relation, rhs):
        from ..problem import Problem
        from ..expressions import AffinExp, NormP_Exp

        assert isinstance(pNorm, NormP_Exp)
        assert isinstance(rhs, AffinExp)
        assert relation in self.LE + self.GE
        assert len(rhs) == 1
        assert pNorm.num2 is None, \
            "Can't create a p-norm constraint for a (p,q)-norm."

        self.p = float(pNorm.numerator) / float(pNorm.denominator)

        if relation is self.LE:
            assert self.p >= 1, \
                "Upper bounding p-norm requires p s.t. the norm is convex."
        else:
            assert self.p < 1 and not self.p == 0, \
                "Lower bounding p-norm requires p s.t. the norm is concave."

        self.pNorm    = pNorm
        self.relation = relation
        self.rhs      = rhs

        P = Problem()
        m = len(pNorm.exp)

        if relation is self.LE:
            if self.p == 1:
                v = P.add_variable('v', m)
                P.add_constraint(pNorm.exp[:] <= v)
                P.add_constraint(-pNorm.exp[:] <= v)
                P.add_constraint((1 | v) < rhs)
            elif self.p == float('inf'):
                P.add_constraint(pNorm.exp <= rhs)
                P.add_constraint(-pNorm.exp <= rhs)
            else:
                x = P.add_variable('x', m)
                v = P.add_variable('v', m)
                amb = pNorm.numerator - pNorm.denominator
                b = pNorm.denominator
                oneamb = '|1|(' + str(amb) + ',1)'
                oneb = '|1|(' + str(b) + ',1)'
                for i in range(m):
                    if amb > 0:
                        if b == 1:
                            vec = (v[i]) // (rhs * oneamb)
                        else:
                            vec = (v[i] * oneb) // (rhs * oneamb)
                    else:
                        if b == 1:
                            vec = v[i]
                        else:
                            vec = (v[i] * oneb)
                    P.add_constraint(abs(pNorm.exp[i]) < x[i])
                    P.add_constraint(x[i] < geomean(vec))
                P.add_constraint((1 | v) < rhs)
        else:
            if self.p == 1:
                P.add_constraint(pNorm.exp > 0)
                P.add_constraint((1 | pNorm.exp) > rhs)
                print("\033[1;31m*** Warning -- generalized norm inequality, "
                    "expression is forced to be >=0 \033[0m")
            elif self.p == float('-inf'):
                P.add_constraint(pNorm.exp >= rhs)
                print("\033[1;31m*** Warning -- generalized norm inequality, "
                    "norm_-inf(x) is interpreted as min(x), not min(abs(x)) "
                    "\033[0m")
            elif self.p >= 0:
                v = P.add_variable('v', m)
                bma = -(pNorm.numerator - pNorm.denominator)
                a = pNorm.numerator
                onebma = '|1|(' + str(bma) + ',1)'
                onea = '|1|(' + str(a) + ',1)'
                for i in range(m):
                    if a == 1:
                        vec = (pNorm.exp[i]) // (rhs * onebma)
                    else:
                        vec = (pNorm.exp[i] * onea) // (rhs * onebma)
                    P.add_constraint(v[i] < geomean(vec))
                P.add_constraint(rhs < (1 | v))
            else:
                v = P.add_variable('v', m)
                b = abs(pNorm.denominator)
                a = abs(pNorm.numerator)
                oneb = '|1|(' + str(b) + ',1)'
                onea = '|1|(' + str(a) + ',1)'
                for i in range(m):
                    if a == 1 and b == 1:
                        vec = (pNorm.exp[i]) // (v[i])
                    elif a > 1 and b == 1:
                        vec = (pNorm.exp[i] * onea) // (v[i])
                    elif a == 1 and b > 1:
                        vec = (pNorm.exp[i]) // (v[i] * oneb)
                    else:
                        vec = (pNorm.exp[i] * onea) // (v[i] * oneb)
                    P.add_constraint(rhs < geomean(vec))
                P.add_constraint((1 | v) < rhs)

        super(PNormConstraint, self).__init__(P, pNorm.typeStr)

    def isGeneralized(self):
        return not (self.p > 1 or (self.p == 1 and self.relation is self.LE))

    def _expression_names(self):
        yield "pNorm"
        yield "rhs"

    def _get_prefix(self):
        return "_nop"

    def _str(self):
        if self.relation is self.LE:
            return glyphs.le(self.pNorm.string, self.rhs.string)
        else:
            return glyphs.ge(self.pNorm.string, self.rhs.string)

    def _get_slack(self):
        if self.isGeneralized():
            return -(self.rhs.value - self.pNorm.value)
        else:
            return self.rhs.value - self.pNorm.value
