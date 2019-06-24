#!/usr/bin/env python
from setuptools import setup, find_packages
import os
__author__ = 'stuber, adamkoziol'

setup(
    name="vsnpdev",
    version="0.0.15",
    packages=find_packages(),
    include_package_data=True,
    scripts=[os.path.join('vsnp', 'vSNP.py')],
    license='MIT',
    author='Adam Koziol',
    author_email='adam.koziol@canada.ca',
    description='USDA APHIS Veterinary Services (VS) Mycobacterium tuberculosis complex, '
                'mainly M. bovis, and Brucella sp. SNP pipeline. Genotyping from whole genome sequence (WGS) '
                'outputting BAM, VCF, SNP tables and phylogentic trees.',
    url='https://github.com/USDA-VS/vSNP',
    long_description=open('README.md').read(),
)
