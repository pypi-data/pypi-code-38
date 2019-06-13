from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='dtrees',
    version='0.8b',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
)