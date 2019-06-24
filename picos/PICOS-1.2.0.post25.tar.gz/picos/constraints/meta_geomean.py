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
# This file implements a geometric mean inequality constraint.
#-------------------------------------------------------------------------------

from .. import glyphs

from .constraint import MetaConstraint

# TODO: Comment the code, potentially use human readable variable names.
class GeoMeanConstraint(MetaConstraint):
    def __init__(self, geoMean, lowerBound):
        from ..problem import Problem
        from ..expressions import AffinExp, GeoMeanExp

        assert isinstance(geoMean, GeoMeanExp)
        assert isinstance(lowerBound, AffinExp)
        assert len(lowerBound) == 1

        self.geoMean    = geoMean
        self.lowerBound = lowerBound

        P     = Problem()
        m     = len(geoMean.exp)
        lm    = [[i] for i in range(m - 1, -1, -1)]
        K     = []
        depth = 0
        u     = {}

        while len(lm) > 1:
            depth += 1
            nlm = []
            while lm:
                i1 = lm.pop()[-1]
                if lm:
                    i2 = lm.pop()[0]
                else:
                    i2 = 'x'
                nlm.insert(0, (i2, i1))
                k = str(depth) + ':' + str(i1) + '-' + str(i2)
                K.append(k)
                u[k] = P.add_variable('u[' + k + ']', 1)
            lm = nlm

        root = K[-1]
        maxd = int(K[-1].split(':')[0])
        P.remove_variable(u[root].name)
        u[root] = lowerBound

        for k in K:
            i1 = int(k.split('-')[0].split(':')[1])
            i2 = k.split('-')[1]
            if i2 != 'x':
                i2 = int(i2)
            if k[:2] == '1:':
                if i2 != 'x':
                    P.add_constraint(
                        u[k]**2 < geoMean.exp[i1] * geoMean.exp[i2])
                else:
                    P.add_constraint(u[k]**2 < geoMean.exp[i1] * lowerBound)
            else:
                d = int(k.split(':')[0])
                if i2 == 'x' and d < maxd:
                    k2pot = [ki for ki in K \
                        if ki.startswith(str(d - 1) + ':') \
                        and int(ki.split(':')[1].split('-')[0]) >= i1]
                    k1 = k2pot[0]
                    if len(k2pot) == 2:
                        k2 = k2pot[1]
                        P.add_constraint(u[k]**2 < u[k1] * u[k2])
                    else:
                        P.add_constraint(u[k]**2 < u[k1] * lowerBound)
                else:
                    k1 = [ki for ki in K \
                        if ki.startswith(str(d - 1) + ':' + str(i1))][0]
                    k2 = [ki for ki in K if ki.startswith(str(d - 1) + ':') \
                        and ki.endswith('-' + str(i2))][0]
                    P.add_constraint(u[k]**2 < u[k1] * u[k2])

        super(GeoMeanConstraint, self).__init__(P, geoMean.typeStr)

    def _expression_names(self):
        yield "geoMean"
        yield "lowerBound"

    def _get_prefix(self):
        return "_geo"

    def _str(self):
        return glyphs.le(self.lowerBound.string, self.geoMean.string)

    def _get_slack(self):
        return self.geoMean.value - self.lowerBound.value
