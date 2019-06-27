#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup

setup(
    name='Bopytex',
    version='0.1',
    description='Jinja environment for latex with computing macros',
    author='Benjamin Bertrand',
    author_email='lafrite@poneyworld.net',
    packages=['bopytex'],
    install_requires=[
        'jinja2',
        'path.py',
        #'Mapytex',
        ],
    # dependency_links=[
    #     "git+http://git.poneyworld.net/pyMath/#egg=pyMath",
    #     ],
    entry_points={
        "console_scripts": ['bopytex= bopytex.bopytex:main']
        },
    )

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
