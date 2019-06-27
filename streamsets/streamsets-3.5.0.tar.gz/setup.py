#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2017 StreamSets, Inc.

"""The setup script."""

from setuptools import setup, find_packages
from setuptools.command.sdist import sdist as _sdist
from distutils.extension import Extension

requirements = [
    'dpath',
    'inflection',
    'javaproperties',
    'PyYAML',
    'pycryptodome',
    'requests'
]


class sdist(_sdist):
    """Cythonize .pyx files, but only when sdist is run to avoid requiring users to have
    Cython installed.
    """
    def run(self):
        from Cython.Build import cythonize
        cythonize(['streamsets/sdk/sch_api.pyx',
                   'streamsets/sdk/sdc_api.pyx',
                   'streamsets/sdk/examples/sqoop.pyx'],
                  compiler_directives={
                      # always_allow_keywords added because of issue similar to the one described
                      # on https://github.com/bottlepy/bottle/issues/453.
                      'always_allow_keywords': True,
                      'emit_code_comments': False
                  })
        _sdist.run(self)


cmdclass = {'sdist': sdist}

extensions = [Extension('streamsets.sdk.sch_api', ['streamsets/sdk/sch_api.c']),
              Extension('streamsets.sdk.sdc_api', ['streamsets/sdk/sdc_api.c']),
              Extension('streamsets.sdk.examples.sqoop', ['streamsets/sdk/examples/sqoop.c'])]

setup(
    name='streamsets',
    version='3.5.0',
    description='A Python SDK for StreamSets',
    author='StreamSets Inc.',
    packages=['streamsets.sdk', 'streamsets.sdk.examples'],
    include_package_data=True,
    install_requires=requirements,
    ext_modules=extensions,
    python_requires='>=3',
    entry_points={'console_scripts': ['streamsets-sqoop-import = streamsets.sdk.examples.sqoop:main']},
    zip_safe=False,
    cmdclass=cmdclass,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
