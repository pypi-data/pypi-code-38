from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='locushandler',
    version='0.2.0',
    packages=['locushandler'],
    url='https://github.com/LocusAnalytics/LocusHandler',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
          'pandas', 'requests', ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
