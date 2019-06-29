#!/usr/bin/env python
from rulz import plugin, run_graph


@plugin()
def one():
    return 1


@plugin()
def two():
    return 2


@plugin(one, two)
def add(a, b):
    return a + b


if __name__ == "__main__":
    print(run_graph())
