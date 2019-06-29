from setuptools import setup, find_packages
from konsoru import __version__

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name="konsoru",
    version=__version__,
    author="Wenrui Wu",
    url="https://github.com/DonovanWu/konsoru",
    description="A functional programming styled CLI console application framework based on argparse",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['docs', 'examples', 'tests', '*.tests']),
    python_requires='>=3.5',
)
