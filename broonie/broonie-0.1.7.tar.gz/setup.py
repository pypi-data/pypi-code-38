#!/usr/bin/env python
from __future__ import division, print_function
from setuptools import setup, find_packages

import os
import sys
import subprocess
import textwrap

def readme():
    with open('README.md') as f:
        return f.read()

def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('broonie', parent_package, top_path)
    config.add_subpackage('covariate_projection_reduction')
    config.add_subpackage('mergeMetadataToData')    
    config.make_config_py() 
    return config

def setup_package():
    src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    old_path = os.getcwd()
    os.chdir(src_path)
    sys.path.insert(0, src_path)
    
    metadata = dict(name='broonie',
                    version='0.1.7',
                    description='SVD PCA Projection Imputation Pipeline',
                    long_description=readme(),
                    classifiers=[
                        'Development Status :: 3 - Alpha',
                        'Intended Audience :: Science/Research',
                        'Intended Audience :: Developers',
                        'Programming Language :: Python',
                        'Programming Language :: Python :: 3',
                        'Topic :: Software Development',
                        'Topic :: Scientific/Engineering',
                        'Operating System :: Unix',
                        'Operating System :: POSIX :: Linux'                        
                    ],
                    keywords='pca projection imputation pipeline batch corrected',
                    url='http://github.com/RENCI/broonie',
                    author='Jeffery Tilson',
                    author_email='jtilson@renci.org',
                    packages=find_packages(),
                    platforms = [ "Windows", "Linux", "Solaris", "Mac OS-X", "Unix" ],
                    install_requires=['markdown', 'pandas', 'numpy', 'matplotlib', 'scikit-learn', 'scipy'],
                    test_suite='nose.collector',
                    zip_safe=False)

    setup(**metadata)
    return

if __name__ == '__main__':
    setup_package();
