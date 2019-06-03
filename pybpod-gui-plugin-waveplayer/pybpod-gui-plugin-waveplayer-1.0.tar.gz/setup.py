#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import re

version = ''
with open('pybpodgui_plugin_waveplayer/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name='pybpod-gui-plugin-waveplayer',
    version=version,
    description="""PyBpod wave player module controller""",
    author=['Ricardo Ribeiro','Sergio Copeto'],
    author_email='ricardo.ribeiro@research.fchampalimaud.org, sergio.copeto@research.fchampalimaud.org',
    license='Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>',
    url='',

    include_package_data=True,
    packages=find_packages(),

    package_data={'pybpodgui_plugin_waveplayer': ['resources/*.*',]}
)
