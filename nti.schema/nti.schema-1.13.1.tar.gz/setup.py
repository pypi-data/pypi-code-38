#!/usr/bin/env python
import codecs
from setuptools import setup, find_packages

version = '1.13.1'

entry_points = {
}


def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()


setup(
    name='nti.schema',
    version=version,
    author='Jason Madden',
    author_email='open-source@nextthought.com',
    description=('Zope schema related support'),
    long_description=(
        _read('README.rst')
        + '\n\n'
        + _read('CHANGES.rst')
    ),
    license='Apache',
    keywords='zope schema',
    url='https://github.com/NextThought/nti.schema',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Framework :: Zope3',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'Acquisition',
        'nti.i18n',
        'six',
        'setuptools',
        'zope.event',
        'zope.schema >= 4.8.0',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.vocabularyregistry',
        'zope.deprecation',
        'zope.deferredimport >= 4.2.1',
    ],
    extras_require={
        'test': [
            'pyhamcrest',
            'nti.testing',
            'zope.testrunner',
        ],
        'docs': [
            'Sphinx',
            'nti.testing',
            'repoze.sphinx.autointerface',
            'sphinx_rtd_theme',
        ],
    },
    namespace_packages=['nti'],
    entry_points=entry_points,
)
