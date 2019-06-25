'''Setup.py'''

from distutils.core import setup
from setuptools import find_packages

setup(
    name='pygini',
    version='0.0.1',
    author='Nicholas McKibben',
    author_email='nicholas.bgp@gmail.com',
    packages=find_packages(),
    scripts=[],
    url='https://github.com/mckib2/pygini',
    license='GPLv3',
    description='Compute the Gini index.',
    long_description=open('README.rst').read(),
    keywords=(
        'gini gini-index sparsity'),
    install_requires=[
        "numpy>=1.16.2",
    ],
    python_requires='>=3.6',
)
