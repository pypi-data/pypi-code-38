# -*- coding: utf-8 -*-
"""Installer for the collective.contentgroups package."""

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
    name="collective.contentgroups",
    version="1.0.0a1",
    description="Plone PAS plugin for content as groups",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone",
    author="Maurits van Rees",
    author_email="m.van.rees@zestsoftware.nl",
    url="https://github.com/collective/collective.contentgroups",
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["collective"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=["Products.GenericSetup>=1.8.2", "plone.api", "setuptools", "six"],
    extras_require={"test": ["plone.app.testing", "plone.testing>=5.0.0"]},
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
