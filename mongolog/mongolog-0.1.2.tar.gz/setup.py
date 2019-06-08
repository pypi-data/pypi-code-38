# -*- coding: utf-8 *-*
try:
    from setuptools import setup
except ImportError:
    from distutils import setup


long_description = open("README.rst").read()

setup(
    name='mongolog',
    version='0.1.2',
    description='Centralized logging made simple using MongoDB',
    long_description=long_description,
    author='Andrei Savu',
    author_email='contact@andreisavu.ro',
    maintainer='Jorge Puente Sarrín',
    maintainer_email="puentesarrin@gmail.com",
    url='https://github.com/puentesarrin/mongodb-log',
    packages=['mongolog'],
    keywords=["mongolog", "logging", "mongo", "mongodb"],
    install_requires=['pymongo'],
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: System :: Logging",
        "Topic :: Database",
    ]
)
