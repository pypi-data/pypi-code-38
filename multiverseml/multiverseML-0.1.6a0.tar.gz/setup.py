# -*- coding: utf-8 -*-
from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='multiverseML',
    version='0.1.6-Alpha',
    url='https://github.com/cccadet/multiverseML/',
    license='GNU General Public License v3.0',
    author='Cristian Carlos dos Santos',
    author_email='perestra.ccds@gmail.com',
    keywords='multiverseML, machine-learning, pipeline',
    description=u'Aplicação para facilitar a criação de pipelines para desenvovimento de algoritmos de Machine Learning',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['multiverseml'],
    install_requires=[
        'subprocess',
        'os',
        'json',
        'datetime',
        'inspect',
        'pickle',
        'shutil',
        'numpy',
        'pandas',
        'flask',
        'pandas'
    ],
)