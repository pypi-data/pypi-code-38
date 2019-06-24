# -*- coding: utf-8 -*-
"""Installer for the ideabox.policy package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="ideabox.policy",
    version="2.3.2",
    description="IdeaBox",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone",
    author="Martin Peeters",
    author_email="martin.peeters@affinitic.be",
    url="https://pypi.python.org/pypi/ideabox.policy",
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["ideabox"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Products.GenericSetup>=1.8.2",
        "Products.PasswordStrength",
        "Products.BeakerSessionDataManager",
        "cioppino.twothumbs",
        "collective.behavior.banner",
        "collective.behavior.richdescription",
        "collective.editablemenu",
        "collective.excelexport",
        "collective.disclaimer",
        "collective.taxonomy",
        "collective.z3cform.select2",
        "iaweb.mosaic",
        "ideabox.diazotheme.spirit",
        "imio.gdpr",
        "pas.plugins.imio",
        "password-generator",
        "plone.api",
        "plone.app.contenttypes",
        "plone.app.dexterity",
        "plone.app.discussion",
        "plone.app.imagecropping",
        "plone.app.lockingbehavior",
        "plone.app.mosaic",
        "plone.app.referenceablebehavior",
        "plone.app.relationfield",
        "plone.dexterity",
        "setuptools",
        "z3c.jbot",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            "plone.testing",
            "plone.app.robotframework[debug]",
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
