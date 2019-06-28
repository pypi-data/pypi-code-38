import json
from typing import Dict, Set, Union

Interfaces = Dict[str, Dict[str, Union[str, int]]]


def read_interfaces(path: str) -> Interfaces:
	"""Reads an Interfaces JSON file at the given path and returns it as a dictionary."""
	with open(path, encoding='utf-8') as f:
		return json.load(f)


def factors(number: int, limit: int) -> Set[int]:
	return {x for x in [2**x for x in range(limit)] if number % x == 0}


def multiple(layer: int, limit: int) -> Set[str]:
	"""Returns a set of strings to be used as Slots with Pabianas default Clock.

	Args:
		layer: The layer in the hierarchy this Area is placed in.
			Technically, the number specifies how many of the Clocks signals are relevant to the Area.
			Between 1 and limit.
		limit: The number of layers of the hierarchy.
	"""
	return {str(x).zfill(2) for x in [2**x for x in range(limit)] if x % 2**(layer - 1) == 0}
