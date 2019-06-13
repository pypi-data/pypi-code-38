# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = '1.3.0'
tests_require = ['zope.testing', 'manuel']

setup(
    name='ftw.recipe.solr',
    version=version,
    description="A zc.buildout recipe to install a Solr server",
    long_description=open("README.rst").read()
    + "\n" +
    open("HISTORY.txt").read(),
    classifiers=[
        'Framework :: Buildout :: Recipe',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
    ],
    keywords='',
    author='4teamwork AG',
    author_email='mailto:info@4teamwork.ch',
    url='https://github.com/4teamwork/ftw.recipe.solr',
    license='GPL2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['ftw', 'ftw.recipe'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        'jinja2',
    ],
    tests_require=tests_require,
    extras_require=dict(tests=tests_require),
    test_suite='ftw.recipe.solr.tests.test_docs.test_suite',
    entry_points={
        'zc.buildout': ['default = ftw.recipe.solr:Recipe'],
    },
)
