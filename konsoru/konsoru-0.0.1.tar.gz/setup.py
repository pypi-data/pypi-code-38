from setuptools import setup, find_packages
from konsoru import __version__

setup(
    name="konsoru",
    version=__version__,
    author="Wenrui Wu",
    url="https://github.com/DonovanWu/konsoru.git",
    description="A functional programming styled CLI console application framework based on argparse",
    packages=find_packages(exclude=['docs', 'examples', 'tests', '*.tests']),
    python_requires='>=3.5',
)
