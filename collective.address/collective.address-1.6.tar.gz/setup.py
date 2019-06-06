# -*- coding: utf-8 -*-
"""Installer for the bda.aaf.site package."""

from setuptools import setup
from setuptools import find_packages

version = '1.6'

long_description = ('\n\n'.join([
    open('README.rst').read(),
    open('CHANGES.rst').read(),
]))


setup(
    name='collective.address',
    version=version,
    description="Dexterity address behavior.",
    long_description=long_description,
    classifiers=[
      "Framework :: Plone",
      "Programming Language :: Python",
      ],
    keywords='plone collective address',
    author='Johannes Raggam',
    author_email='raggam-nl@adm.at',
    url='https://github.com/collective/collective.address',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'plone.api',
        'plone.app.textfield',
        'plone.autoform',
        'plone.behavior',
        'plone.indexer',
        'plone.supermodel',
        'Products.CMFPlone',
        'pycountry',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.schema',
        'six',
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """
)
