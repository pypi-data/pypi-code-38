# -*- coding: utf-8 -*-
'''
Installation and testing for the gcshelpers library.
'''
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

RUNTIME_REQUIREMENTS = [
    'google-cloud-pubsub',
    'google-cloud-storage'
]

TEST_REQUIREMENTS = [
    'nose',
    'coverage'
]

DEV_REQUIREMENTS = [
    'pylint',
    'autopep8',
    'rope',
    'notebook'
]

DOC_REQUIREMENTS = [
    'sphinx',
    'recommonmark',
    'sphinx_rtd_theme',
    'doc8',
    'm2r'
]

DIST_REQUIREMENTS = [
    'twine'
]

setup(name='gcshelpers-SaschaJust',
      version='0.1a1',
      description='gcshelpers: a collection of helper classes and functions for the mozintermittent Google Cloud services.',
      long_description_content_type="text/markdown",
      long_description=long_description,
      url='https://gitlab.com/mozintermittent/python-libraries/gcshelpers',
      author='Sascha Just',
      author_email='sascha.just@own-hero.net',
      license='MIT',
      packages=['gcshelpers'],
      install_requires=RUNTIME_REQUIREMENTS,
      tests_require=TEST_REQUIREMENTS,
      extras_require={
        'develop': DEV_REQUIREMENTS,
        'docs': DOC_REQUIREMENTS,
        'test': TEST_REQUIREMENTS,
        'dist': DIST_REQUIREMENTS
      },
      zip_safe=False,
      python_requires='>=3.6',
      include_package_data=True,
      test_suite='nose.collector',
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ])
 