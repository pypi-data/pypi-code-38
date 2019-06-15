#!/bin/python
import os
from setuptools import setup, find_packages
#from distutils.core import setup


entry_points = {
    'console_scripts': [
        "lmpline=linkageMapper.Pipeline:main",
        "lmview=linkageMapper.walkChromosomeResult:main",
        "lmdownload=linkageMapper.fetchDataNCBI:main",
        "lmprimer=linkageMapper.initializePrimerFile:main"
        ]
}

base_folder = os.path.dirname(os.path.realpath(__file__))
requirements = list(open(os.path.join(base_folder, "requirements.txt")).readlines())
setup(
    name='linkageMapper',
    version='0.88',
    description='Genomic similarities per region',
    author='Gabriel Araujo',
    author_email='gabriel_scf@hotmail.com',
    url='https://www.github.com/Gab0/linkageMapper',
    #packages=find_packages(),
    setup_requires=["numpy"],
    install_requires=requirements,
    packages=[
        'linkageMapper',
        'linkageMapper.walkChromosome',
        'linkageMapper.PrimerEngine',
        'linkageMapper.DrawGraphics',
        'linkageMapper.Database',
        'linkageMapper.skdistance'
    ],
    platforms='any',
    entry_points=entry_points
)
