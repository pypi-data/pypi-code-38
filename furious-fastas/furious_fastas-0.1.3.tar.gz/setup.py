# This Python file uses the following encoding: utf-8
from setuptools import setup, find_packages

setup(
    name='furious_fastas',
    packages=find_packages(),
    version='0.1.3',
    description='Module to update the fastas.',
    long_description='A simple project aiming at ordering the update of the local fasta DB, as done in the Stefan Tenzer group.',
    author='Mateusz Krzysztof Łącki',
    author_email='matteo.lacki@gmail.com',
    url='https://bitbucket.org/MatteoLacki/furious_fastas/src/master/',
    # download_url='https://github.com/MatteoLacki/MassTodonPy/tree/GutenTag',
    keywords=[
        'Mass Spectrometry',
        'fasta'
        'reverse fastas'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Programming Language :: Python :: 3.6'],
    install_requires=[
        'requests' # this severs as wget for Python
    ],
    # include_package_data=True,
    # package_data={
    #     'data':
    #          ['data/contaminants_uniprot_format.fasta']
    # },
    scripts = [
        "bin/update_fastas",
        "bin/reverse_fastas"
    ]
)
