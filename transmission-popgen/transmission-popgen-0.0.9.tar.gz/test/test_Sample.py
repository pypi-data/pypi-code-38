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
from transmission.transmission import Sample

num_samples = 4


@pytest.fixture
def single_replicate():
    """
    Generate a single replicate of two populations with msprime.
    """
    population_config = [
        ms.PopulationConfiguration(sample_size=num_samples) for _ in (0, 1)
    ]
    migration = np.full((2, 2), 10.0)
    np.fill_diagonal(migration, 0.0)
    out = ms.simulate(
        population_configurations=population_config,
        migration_matrix=migration,
        mutation_rate=0.5,
        random_seed=3,
    )
    return Sample(out)


# single_replicate genotypes
# array([[1, 1, 0, 1, 0],
#        [0, 0, 0, 0, 0],
#        [0, 0, 0, 0, 1],
#        [0, 0, 1, 1, 0],
#        [0, 0, 0, 0, 0],
#        [0, 0, 0, 0, 0],
#        [0, 0, 0, 0, 1],
#        [0, 0, 0, 0, 1]])


@pytest.fixture
def double_replicate():
    """
    Generate a double replicate of two populations with msprime.
    """
    population_config = [
        ms.PopulationConfiguration(sample_size=num_samples) for _ in (0, 1)
    ]
    migration = np.full((2, 2), 10.0)
    np.fill_diagonal(migration, 0.0)
    out = ms.simulate(
        population_configurations=population_config,
        migration_matrix=migration,
        mutation_rate=0.5,
        num_replicates=2,
        random_seed=3,
    )
    return Sample(out)


# double_replicate genotypes
# [array([[1, 1, 0, 1, 0],
#         [0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 1],
#         [0, 0, 1, 1, 0],
#         [0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 1],
#         [0, 0, 0, 0, 1]]),
#  array([[1, 0, 0, 0, 1, 0, 0],
#         [0, 1, 1, 0, 0, 0, 0],
#         [1, 0, 0, 0, 1, 0, 0],
#         [1, 0, 0, 0, 1, 0, 0],
#         [0, 0, 0, 0, 0, 1, 1],
#         [1, 0, 0, 0, 1, 0, 0],
#         [0, 0, 0, 1, 0, 0, 0],
#         [0, 0, 0, 1, 0, 0, 0]])


# single replicate
@pytest.mark.parametrize(
    "bias, expected",
    [
        (False, np.array([0.21875, 0.21875, 0.21875, 0.375, 0.46875])),
        (
            True,
            8.0
            / (8.0 - 1.0)
            * np.array([0.21875, 0.21875, 0.21875, 0.375, 0.46875]),
        ),
    ],
)
def test_h_no_average_one_rep(bias, expected, single_replicate):
    assert np.isclose(single_replicate.h(bias=bias), expected).all()


@pytest.mark.parametrize(
    "bias, expected", [(False, 0.300), (True, 8.0 / (8.0 - 1.0) * 0.300)]
)
def test_h_average_one_rep(bias, expected, single_replicate):
    assert np.isclose(single_replicate.h(bias=bias, average=True), expected)


@pytest.mark.parametrize(
    "threshold, expected", [(0, 1.928374656), (1, 0.771349862)]
)
def test_theta_w_one_rep(threshold, expected, single_replicate):
    assert np.isclose(
        expected,
        single_replicate.theta_w(by_population=False, threshold=threshold),
    )


# double replicate
@pytest.mark.parametrize(
    "bias, expected",
    [
        (
            False,
            [
                np.array([0.21875, 0.21875, 0.21875, 0.375, 0.46875]),
                np.array(
                    [0.5, 0.21875, 0.21875, 0.375, 0.5, 0.21875, 0.21875]
                ),
            ],
        ),
        (
            True,
            [
                (
                    8.0
                    / (8.0 - 1.0)
                    * np.array([0.21875, 0.21875, 0.21875, 0.375, 0.46875])
                ),
                (
                    8.0
                    / (8.0 - 1)
                    * np.array(
                        [0.5, 0.21875, 0.21875, 0.375, 0.5, 0.21875, 0.21875]
                    )
                ),
            ],
        ),
    ],
)
def test_h_no_average_two_reps(bias, expected, double_replicate):
    heterozygosity = double_replicate.h(bias=bias)
    out = [
        np.isclose(expected_local, heterozygosity[i]).all()
        for i, expected_local in enumerate(expected)
    ]
    assert all(out)


@pytest.mark.parametrize(
    "bias, expected",
    [
        (False, [0.300, 0.321428571]),
        (True, [(8.0 / (8.0 - 1.0) * 0.300), (8.0 / (8.0 - 1) * 0.321428571)]),
    ],
)
def test_h_average_two_reps(bias, expected, double_replicate):
    heterozygosity = double_replicate.h(bias=bias, average=True)
    out = [
        np.isclose(expected_local, heterozygosity[0, i]).all()
        for i, expected_local in enumerate(expected)
    ]
    assert all(out)


@pytest.mark.parametrize(
    "threshold, expected",
    [
        (0, np.array([1.928374656, 2.699724518])),
        (1, np.array([0.771349862, 1.157024793])),
    ],
)
def test_theta_w_two_reps(threshold, expected, double_replicate):
    out = np.isclose(double_replicate.theta_w(threshold=threshold), expected)
    assert out.all()


@pytest.mark.parametrize(
    "method, expected",
    [
        ("tajima", np.array([1.714285714, 2.571428571])),
        ("nei", np.array([1.5, 2.25])),
    ],
)
def test_pi_two_reps(method, expected, double_replicate):
    out = np.isclose(double_replicate.pi(pi_method=method), expected)
    assert out.all()


@pytest.mark.parametrize(
    "expected",
    [(np.array([[1, 1, 1, 2, 3]]), np.array([[4, 1, 1, 2, 4, 1, 1]]))],
)
def test_num_mutants(expected, double_replicate):
    test = double_replicate.num_mutants(
        populations=np.repeat(0, num_samples * 2)
    )
    assert all(np.array_equal(test[i], expected[i]) for i in range(len(test)))


@pytest.mark.parametrize(
    "expected",
    [
        {
            "which": (
                (np.zeros(5, int), np.arange(5)),
                (np.zeros(7, int), np.arange(7)),
            ),
            "num": (5, 7),
        },
        {
            "which": (
                (np.zeros(2, int), np.array([3, 4])),
                (np.zeros(3, int), np.array([0, 3, 4])),
            ),
            "num": (2, 3),
        },
    ],
)
def test_polymorphic_two_reps(expected, double_replicate):
    test = double_replicate.polymorphic()
    assert hash(frozenset(expected)) == hash(frozenset(test))


@pytest.mark.parametrize("expected", [np.array([5, 7])])
def test_segsites_two_reps(expected, double_replicate):
    test = double_replicate.segsites()
    assert all(test == expected)
