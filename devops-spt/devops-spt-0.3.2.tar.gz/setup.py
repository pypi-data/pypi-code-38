"""Describe the devops-spt package distro to the Distutils"""
from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md'), encoding='utf-8') as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name='devops-spt',
    version='0.3.2',
    description='Devops support functions in a Python package',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/dksmiffs/devops-spt',
    author='Dave Smith',
    author_email='dave.k.smith@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='devops',
    packages=find_packages(),
    license="MIT",
)
