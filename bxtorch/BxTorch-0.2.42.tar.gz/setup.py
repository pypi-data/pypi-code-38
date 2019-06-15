#
#  setup.py
#  bxtorch
#
#  Created by Oliver Borchert on May 23, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#

from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='BxTorch',
    version='0.2.42',

    author='Oliver Borchert',
    author_email='borchero@in.tum.de',

    description='High-level abstractions for PyTorch.',
    long_description=long_description,
    long_description_content_type = 'text/markdown',

    url='https://github.com/borchero/bxtorch',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    python_requires='>=3.7',
    install_requires=[
        'torch>=1.1.0,<2.0.0',
        'numpy>=1.16.3,<2.0.0',
        'scipy>=1.3.0,<2.0.0',
        'numba>=0.43.1,<1.0.0',
        'scikit-learn>=0.20.3,<0.21.0'
    ],

    license='License :: OSI Approved :: MIT License',
    zip_safe=False
)
