"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages

setup(
    name='green-example',
    version='1.0.1',
    description='A sample Python hello world lambda function for AWS Greengrass.',
    license='MIT',
    author='Halim Qarroum',
    author_email='qarroumh@amazon.lu',
    packages=['green-example'],
    install_requires=['arrow'],
    keywords=['greengrass', 'hello-world', 'pip']
)