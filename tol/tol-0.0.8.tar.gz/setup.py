# -*- coding: utf-8 -*-

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='tol',
    version='0.0.8',
    packages=['tol'],
    author='Øystein S. Haaland',
    author_email='oystein@beat.no',
    description="tøl n1 (norrønt tól 'reiskap') kollektivt: (små)saker",
    long_description=readme(),
    url='https://github.com/beat-no/tol'
)
