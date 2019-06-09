import matplotlib
import numpy as np
import pytest

import closely

matplotlib.use("Agg")


@pytest.mark.parametrize("n_points,n_dim", [(2, 2), (2, 3), (3, 2), (3, 3)])
def test_solution(n_points, n_dim):
    X = np.random.random((1000, n_dim))
    pairs, distances = closely.solve(X, n=n_points)
    assert isinstance(pairs, np.ndarray)
    assert len(pairs) >= n_points
    assert isinstance(distances, np.ndarray)


def test_quantile():
    X = np.random.random((1000, 8))
    pairs, distances = closely.solve(X, quantile=0.01)
    assert isinstance(pairs, np.ndarray)
    assert isinstance(distances, np.ndarray)


@pytest.mark.parametrize("ordered", [True, False])
def test_show_linkage(ordered):
    X = np.random.random((1000, 8))
    ordered_dist_mat = closely.distance_matrix(X, ordered=ordered)
    closely.show_linkage(ordered_dist_mat)
