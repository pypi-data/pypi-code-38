#!/usr/bin/python2
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import re

with open('README.md', 'r') as fd:
    long_description = fd.read()

setup(
	name='Python video annotator - module - deeplab',
	version="0.901",
	description="""""",
	author=['Manuel Manso'],
	author_email='manel_manso@hotmail.com',
	url='https://bitbucket.org/fchampalimaud/pythonvideoannotator-module-deeplab',
	long_description = long_description,
    long_description_content_type = 'text/markdown',

	packages=find_packages(),
	install_requires=['pyyaml']
)
