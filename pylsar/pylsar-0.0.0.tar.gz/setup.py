import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pylsar",
    version="0.0.0",
    author="Nicolas Rouviere",
    author_email="zesk06@gmail.com",
    description=("A scenarised REST API test tool"),
    license="BSD",
    keywords="REST requests",
    url="https://framagit.org/zesk06/pylsar",
    packages=["pylsar", "tests"],
    long_description=read("README.md"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=["requests", "jinja2", "pyyaml"],
    extras_require={"dev": ["pytest", "black", "isort", "pylint"]},
    entry_points={"console_scripts": ["pyl=pylsar.pylsar:main"]},
)
