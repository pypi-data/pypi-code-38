
from setuptools import setup, find_packages

setup(
    name='turkce',
    version='0.1.0',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='turkce',
    long_description=open('README.txt').read(),
    url='https://github.com/turkceAI/python/',
    author='talhatarik',
    author_email='ttarikkucuk@gmail.com'
)
