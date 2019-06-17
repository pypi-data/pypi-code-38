#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# transmission: A tool for inferring endosymbiont biology from metagenome data.
# Copyright (C) 4-11-2018 Mark Juers

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import msprime as ms
import numpy as np
import pytest
import transmission as trans


@pytest.mark.parametrize(
    "Nm, tau, rho", [(2.6, 1.0, 0.5), (2.6, 0.5, 0.5), (2.6, 0.0, 0.5)]
)
def test_sim_fst(Nm, tau, rho):
    nchrom = 24
    d = 10
    pops = [ms.PopulationConfiguration(nchrom) for _ in range(d)]
    data = trans.sim(
        params=(0, tau, rho),
        host_theta=1,
        host_Nm=Nm,
        stats=("fst_mean",),
        population_config=pops,
        populations=np.repeat(np.arange(d), nchrom),
        random_seed=3,
        num_replicates=10,
        average_reps=True,
    )
    assert np.isclose(data[0], trans.fst(Nm, tau, rho), rtol=0.10)
