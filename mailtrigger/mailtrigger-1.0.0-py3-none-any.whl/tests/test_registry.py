# -*- coding: utf-8 -*-

from mailtrigger.registry import REGISTRY


def test_registry():
    assert (REGISTRY is not None and len(REGISTRY) != 0)
