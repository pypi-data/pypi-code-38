#
#  setup.py
#  bxgraph
#
#  Created by Oliver Borchert on June 20, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#

from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='BxGraph',
    version='0.1.1',

    author='Oliver Borchert',
    author_email='borchero@in.tum.de',

    description='Graph Management in Python.',
    long_description=long_description,
    long_description_content_type = 'text/markdown',

    url='https://github.com/borchero/bxgraph',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.16.3,<2.0.0',
        'scipy>=1.3.0,<2.0.0',
        'numba>=0.43.1,<1.0.0'
    ],

    license='License :: OSI Approved :: MIT License',
    zip_safe=False
)
