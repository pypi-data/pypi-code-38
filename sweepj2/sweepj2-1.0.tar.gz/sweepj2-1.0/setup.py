from setuptools import setup

setup(
    name='sweepj2',
    version='1.0',
    author='The Popper Development Team',
    author_email='ivo@cs.ucsc.edu',
    url='https://github.com/ivotron/sweepj2',
    description='Utilities for running parameter sweeps by providing a Jinja2 template and a parameter space (in YAML).',
    scripts=['bin/sweepj2'],
    install_requires=[
        'Jinja2',
        'pyyaml'
    ],
    keywords='parameter sweep, grid search',
    license='MIT',
)