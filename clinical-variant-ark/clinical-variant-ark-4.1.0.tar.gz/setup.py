import os
from distutils.core import setup
from setuptools import find_packages
import pyark


test_deps = ['mock']

# read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='clinical-variant-ark',
    version=pyark.VERSION,
    description='A Python client for the Clinical Variant Ark',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    scripts=[],
    url='https://github.com/genomicsengland/pyark',
    download_url="https://github.com/genomicsengland/pyark/archive/v{}.tar.gz".format(pyark.VERSION),
    license='Apache',
    author=['Pablo Riesgo Ferreiro', 'Kevin Savage', 'William Bellamy'],
    author_email='pablo.riesgo-ferreiro@genomicsengland.co.uk',
    install_requires=[
        'requests',
        'furl==1.0.1',
        'gelreportmodels==7.2.10',
        'enum34',
        'pandas',
        'mock',
        'future',
        'pytest'
    ],
    tests_require=test_deps,
    extras_require={'test': test_deps},
    keywords=['CVA', 'pyark', 'clinical variant ark', 'Genomics England'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
      ]
)
