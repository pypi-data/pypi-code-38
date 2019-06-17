# This Python file uses the following encoding: utf-8
from setuptools import setup, find_packages

setup(
    name='waters',
    packages=find_packages(),
    version='0.0.1',
    description='Parsing MS data from Waters.',
    long_description='Parsing MS data from Waters.',
    author='Mateusz Krzysztof Łącki',
    author_email='matteo.lacki@gmail.com',
    url='https://github.com/MatteoLacki/waters/',
    # download_url='https://github.com/MatteoLacki/MassTodonPy/tree/GutenTag',
    keywords=[
        'Mass Spectrometry',
        'Waters'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Programming Language :: Python :: 3.7'],
    # install_requires=[],
    # include_package_data=True,
    # package_data={
    #     'data':
    #          ['data/contaminants.fasta']
    # },
    # scripts = []
)
