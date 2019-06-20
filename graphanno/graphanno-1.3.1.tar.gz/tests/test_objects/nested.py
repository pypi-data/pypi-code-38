"""Nested classes definition."""
from typing import List


class SubLeaf:
    """Even smaller leaf, which is a part of bigger one. Pretty weird, huh?"""

    value: str


class Leaf:
    """Leaf class definition."""

    value: str
    leaflets: List[SubLeaf]


class TopLevel:
    """Top level class which references to Leaf."""

    leaf: Leaf
    name: str
