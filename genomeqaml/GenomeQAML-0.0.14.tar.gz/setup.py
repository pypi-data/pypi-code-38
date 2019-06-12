#!/usr/bin/env python
from setuptools import setup
__author__ = 'adamkoziol'
setup(
    name="GenomeQAML",
    version="0.0.14",
    packages=['genomeqaml'],
    # package_data={'genomeqaml': ['*.msh', '*.p']},
    data_files=[('', ['genomeqaml/refseq.msh', 'genomeqaml/model.p', 'genomeqaml/dataframe.p'])],
    # include_package_data=True,
    license='MIT',
    scripts=['genomeqaml/classify.py'],
    author='OLC Bioinformatics',
    author_email='adam.koziol@canada.ca',
    description='CFIA OLC Genome Quality Assessment with Machine Learning',
    url='https://github.com/OLC-LOC-Bioinformatics/GenomeQAML',
    install_requires=[
        'click',
        'biopython',
        'scipy',
        'pandas',
        'sklearn',
        'genewrappers'
    ]
)
