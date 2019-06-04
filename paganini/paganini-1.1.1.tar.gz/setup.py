import os
from setuptools import setup, find_packages

setup(
    name = "paganini",
    version = "1.1.1",

    author = "Maciej Bendkowski, Sergey Dovgal",
    author_email = "maciej.bendkowski@tcs.uj.edu.pl, vic.north@gmail.com",
    description = "Multiparametric tuner for combinatorial specifications",

    license = "BSD3",
    url = "https://github.com/maciej-bendkowski/paganini",
    install_requires = ['numpy', 'sympy', 'cvxpy'],
    packages = find_packages(),

    # unit tests
    test_suite = 'tests.problems'
)
