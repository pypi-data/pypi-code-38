import setuptools
from mungo.common import mungoversion

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mungo",
    version=f"{mungoversion}",
    author="Christopher Schröder, Till Hartmann",
    author_email="christopher.schroeder@uni-due.de, till.hartmann@udo.edu",
    description="Quick environment solver",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/christopher-schroeder/mungo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
    entry_points={
        'console_scripts': ['mungo=mungo.cli:main'],
    },
    install_requires=['pulp', 'pyyaml', 'joblib', 'graphviz', 'fastcache', 'python-igraph', 'tqdm'],
)
