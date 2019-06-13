from setuptools import setup, find_packages
from os.path import join, dirname
import dtrees

setup(
    name='dtrees',
    version=dtrees.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
)