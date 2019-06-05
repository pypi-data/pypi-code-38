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
# This file implements a (trace of) n-th power constraint.
#-------------------------------------------------------------------------------

import numpy as np
import cvxopt as cvx

from ..tools import new_param
from .. import glyphs

from .constraint import MetaConstraint

# TODO: Appears to contain redundant code, refactor it.
class TracePowConstraint(MetaConstraint):
    def __init__(self, power, relation, rhs):
        from ..problem import Problem
        from ..expressions import AffinExp, TracePow_Exp

        assert isinstance(power, TracePow_Exp)
        assert relation in self.LE + self.GE
        assert isinstance(rhs, AffinExp)
        assert len(rhs) == 1

        self.p = float(power.numerator) / float(power.denominator)

        assert self.p != 0 and self.p != 1, \
            "The TracePowConstraint should not be created for p = 0 and p = 1 "\
            "as there are more direct ways to represent such powers."

        if relation is self.LE:
            assert self.p <= 0 or self.p >= 1, \
                "Upper bounding p-th power needs p s.t. the power is convex."
        else:
            assert self.p >= 0 and self.p <= 1, \
                "Lower bounding p-th power needs p s.t. the power is concave."

        self.power    = power
        self.relation = relation
        self.rhs      = rhs

        P = Problem()
        a = power.numerator
        b = power.denominator

        if power.dim == 1:
            idt = new_param('1', 1)
            varcnt = 0
            v = []
        else:
            idt = new_param('I', cvx.spdiag([1.] * power.dim))
            varcnt = 1
            v = [P.add_variable('v[0]', (power.dim, power.dim), 'symmetric')]

        if relation is self.LE and a > b:
            pown = int(2**(np.ceil(np.log(a) / np.log(2))))

            if power.dim == 1:
                lis = [rhs] * b + [power.exp] * (pown - a) + [idt] * (a - b)
            else:
                lis = [v[0]] * b + [power.exp] * (pown - a) + [idt] * (a - b)

            while len(lis) > 2:
                newlis = []
                while lis:
                    v1 = lis.pop()
                    v2 = lis.pop()

                    if v1 is v2:
                        newlis.append(v2)
                    else:
                        if power.dim == 1:
                            v0 = P.add_variable('v[' + str(varcnt) + ']', 1)
                            P.add_constraint(v0**2 < v1 * v2)
                        else:
                            v0 = P.add_variable('v[' + str(varcnt) + ']',
                                (power.dim, power.dim), 'symmetric')
                            P.add_constraint(((v1 & v0) // (v0 & v2)) >> 0)

                        varcnt += 1
                        newlis.append(v0)
                        v.append(v0)
                lis = newlis

            if power.dim == 1:
                P.add_constraint(power.exp**2 < lis[0] * lis[1])
            else:
                P.add_constraint(
                    ((lis[0] & power.exp) // (power.exp & lis[1])) >> 0)
                P.add_constraint((idt | v[0]) < rhs)
        elif relation is self.LE and a <= b:
            a = abs(a)
            b = abs(b)

            pown = int(2**(np.ceil(np.log(a + b) / np.log(2))))

            if power.dim == 1:
                lis = [rhs] * b + [power.exp] * a + [idt] * (pown - a - b)
            else:
                lis = [v[0]] * b + [power.exp] * a + [idt] * (pown - a - b)

            while len(lis) > 2:
                newlis = []
                while lis:
                    v1 = lis.pop()
                    v2 = lis.pop()

                    if v1 is v2:
                        newlis.append(v2)
                    else:
                        if power.dim == 1:
                            v0 = P.add_variable('v[' + str(varcnt) + ']', 1)
                            P.add_constraint(v0**2 < v1 * v2)
                        else:
                            v0 = P.add_variable('v[' + str(varcnt) + ']',
                                (power.dim, power.dim), 'symmetric')
                            P.add_constraint(((v1 & v0) // (v0 & v2)) >> 0)

                        varcnt += 1
                        newlis.append(v0)
                        v.append(v0)
                lis = newlis

            if power.dim == 1:
                P.add_constraint(1 < lis[0] * lis[1])
            else:
                P.add_constraint(((lis[0] & idt) // (idt & lis[1])) >> 0)
                P.add_constraint((idt | v[0]) < rhs)
        elif relation is self.GE:
            pown = int(2**(np.ceil(np.log(b) / np.log(2))))

            if power.dim == 1:
                lis = [power.exp] * a + [rhs] * (pown - b) + [idt] * (b - a)

            else:
                lis = [power.exp] * a + [v[0]] * (pown - b) + [idt] * (b - a)

            while len(lis) > 2:
                newlis = []
                while lis:
                    v1 = lis.pop()
                    v2 = lis.pop()

                    if v1 is v2:
                        newlis.append(v2)
                    else:
                        if power.dim == 1:
                            v0 = P.add_variable('v[' + str(varcnt) + ']', 1)
                            P.add_constraint(v0**2 < v1 * v2)
                        else:
                            v0 = P.add_variable('v[' + str(varcnt) + ']',
                                (power.dim, power.dim), 'symmetric')
                            P.add_constraint(((v1 & v0) // (v0 & v2)) >> 0)

                        varcnt += 1
                        newlis.append(v0)
                        v.append(v0)
                lis = newlis

            if power.dim == 1:
                if power.M is None:
                    P.add_constraint(rhs**2 < lis[0] * lis[1])
                else:
                    P.add_constraint(v[0]**2 < lis[0] * lis[1])
                    P.add_constraint((power.M * v[0]) > rhs)
            else:
                P.add_constraint(((lis[0] & v[0]) // (v[0] & lis[1])) >> 0)
                if power.M is None:
                    P.add_constraint((idt | v[0]) > rhs)
                else:
                    P.add_constraint((power.M | v[0]) > rhs)
        else:
            assert False, "Dijkstra-IF fallthrough."

        super(TracePowConstraint, self).__init__(P, power.typeStr)

    # Support Constraint's LHS/RHS interface.
    lhs = property(lambda self: self.power)

    def isTrace(self):
        return self.power.dim > 1

    def _expression_names(self):
        yield "power"
        yield "rhs"

    def _get_prefix(self):
        return "_ntp"

    def _str(self):
        if self.relation is self.LE:
            return glyphs.le(self.power.string, self.rhs.string)
        else:
            return glyphs.ge(self.power.string, self.rhs.string)

    def _get_slack(self):
        if self.relation is self.LE:
            return self.rhs.value - self.power.value
        else:
            return self.power.value - self.rhs.value
