#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Fixtures for dhd tests"""

import pytest
import pandas as pd
import os

here = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def load_pkl_connect():
    sinks = pd.read_pickle(os.path.join(here, "data/sinks.pkl"))
    streets = pd.read_pickle(os.path.join(here, "data/streets.pkl"))
    sources = pd.read_pickle(os.path.join(here, "data/sources.pkl"))
    barriers = pd.read_pickle(os.path.join(here, "data/barriers.pkl"))
    return sinks, streets, sources, barriers


@pytest.fixture
def load_pkl_evolve():
    vertices = pd.read_pickle(os.path.join(here, "data/vertices.pkl"))
    terminals = pd.read_pickle(os.path.join(here, "data/terminals.pkl"))
    return vertices, terminals
