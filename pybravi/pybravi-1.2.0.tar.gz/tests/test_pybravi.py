#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pybravi` package."""


from pybravi.lattice import create_lattice_vector, create_lattice, radial_slicer
from pybravi.lattice import rectangle_slicer
from pybravi.lattice import _centroid, translation
import numpy as np


def test_create_lattice_vector():
    vec_a, vec_b = create_lattice_vector([10, 0], -120)
    assert not np.array_equal(vec_a, vec_b)

    rads = np.arccos(vec_a.dot(vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b)))
    expected_rads = np.radians(120)
    assert np.abs(rads - expected_rads) <= 0.001


def test_create_lattice():
    vecs = create_lattice_vector([10, 0], -120)
    points = create_lattice((2, 2), vecs)

    # Everything should be roughly 10 from the origin
    for point in points:
        norm = np.linalg.norm(point - np.array([0, 0]))
        if norm != 0:
            assert np.abs(norm - 10 <= 0.001)


def test_create_lattice_nonzero():
    x_component = 1/np.tan(np.arcsin(1/10))
    vecs = create_lattice_vector([x_component, 1], -120)
    points = create_lattice((2, 2), vecs)

    # Everything should be roughly 10 from the origin
    for point in points:
        norm = np.linalg.norm(point - np.array([0, 0]))
        if norm != 0:
            assert np.abs(norm - 10 <= 0.001)


def test_radial_slicer():
    func = radial_slicer(radius=1)
    test_points = np.array([[1, 0],
                            [-1, 0],
                            [0, -1],
                            [0, 1],
                            [2, 0]])
    res = func(test_points)
    for point in res:
        assert not np.array_equal(point, np.array([2, 0]))
        assert np.array_equal(point, np.array([1, 0])) or \
            np.array_equal(point, np.array([-1, 0])) or \
            np.array_equal(point, np.array([0, 1])) or \
            np.array_equal(point, np.array([0, -1]))


def test_centroid():
    points = np.array([[0, 1],
                       [1, 0],
                       [-1, 0],
                       [0, -1]])
    center = _centroid(points)
    assert np.array_equal(center, np.array([0, 0]))


def test_shift_centroid():
    x_component = 1/np.tan(np.arcsin(1/10))
    vecs = create_lattice_vector([x_component, 1], -120)
    points = create_lattice((2, 2), vecs)
    func = translation(new_center=np.array([0, 0]))
    new_points = func(points)
    center = _centroid(new_points)
    assert np.array_equal(center, np.array([0, 0]))


def test_create_lattice_slicer_transform():
    x_component = 1/np.tan(np.arcsin(1/10))
    vecs = create_lattice_vector([x_component, 1], -120)

    slicer = radial_slicer(radius=10)
    center = translation(new_center=np.array([0, 0]))
    points = create_lattice((5, 5), vecs, slicer=slicer, translate=center)

    print(_centroid(points))
    dist = np.linalg.norm(_centroid(points) - np.array([0, 0]))
    assert dist <= 0.001
    assert len(points) == 7


def test_rectangle_slider():
    func = rectangle_slicer((-1, 1), (-1, 1))
    test_points = np.array([[1, 1],
                            [1, -1],
                            [-1, 1],
                            [-1, -1],
                            [2, 2]])
    res = func(test_points)
    for point in res:
        assert not np.array_equal(point, np.array([2, 2]))
        assert np.array_equal(point, np.array([1, 1]))
        assert np.array_equal(point, np.array([1, -1]))
        assert np.array_equal(point, np.array([-1, 1]))
        assert np.array_equal(point, np.array([-1, -1]))
