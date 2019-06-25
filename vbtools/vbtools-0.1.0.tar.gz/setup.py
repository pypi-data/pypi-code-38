from setuptools import setup, Extension
from glob import glob
import unittest


def readme():
    with open('README.md') as f:
        return f.read()


def test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


setup(
    name='vbtools',
    version='0.1.0',
    description='A pipeline for analyzing fungal genomic data',
    long_description=readme(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Natural Language :: English'
    ],
    keywords=['bioinformatics'],
    url='https://github.com/broadinstitute/vbtools',
    project_urls={
        'Bug tracker': 'https://github.com/broadinstitute/vbtools/issues',
        'Documentation': 'https://github.com/broadinstitute/vbtools/README.md'
    },
    author='Xiao Li',
    author_email='xiaoli@broadinstitute.org',
    license='MIT',
    packages=['vbtools', 'vbtools.scripts'],
    package_dir={
        'vbtools': 'vbtools',
        'vbtools.scripts': 'scripts'
    },
    install_requires=[
        'vbtools>=0.1.0', 'numpy>=1.15.4' 'pandas>=0.23.4',
        'matplotlib>=3.0.2', 'seaborn>=0.9.0'
    ],
    test_suite='setup.test_suite',
    scripts=glob('scripts/*'),
    include_package_data=True,
    zip_safe=False
)
