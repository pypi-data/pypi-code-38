#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#   ZopeEdit, client for ExternalEditor
#
##############################################################################

import os
from setuptools import setup, find_packages
from edopkg import config

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
setup(
        name='edopkg',
        version=config.VERSION,
        zip_safe=False,
        author="xiehaiyang",
        author_email="service@everydo.com",
        url="http://everydo.com/",
        description=u"Easydo Package Syncer",
        long_description=README,
        packages = find_packages(),
        entry_points = {
            'console_scripts': ['edopkg = edopkg.main:main']
        },
        install_requires=[
            'edo_client',
            'PyYAML'
        ],
)
