#!/usr/bin/env python

import setuptools


setuptools.setup(
        name='python-rigidbody',
        version='0.2',
        license='MIT',
        author='Joshua Downer',
        author_email='joshua.downer@gmail.com',
        url='http://github.com/jdowner/rigidbody',
        packages=['rigidbody'],
        install_requires=[
            'numpy',
            ],
        extras_require={
            "dev": [
                "pycodestyle",
                ]
            },
        tests_require = [
            'pycodestyle',
            'tox',
        ],
        platforms=['Unix'],
        )
