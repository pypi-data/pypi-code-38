# -*- coding: utf8
import os

from setuptools import setup

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_THIS_DIR, "README.rst")) as f:
    long_description = f.read()

setup(
    name='renew',
    description="Gives a reproducible manner to your objects and can serialize them in 100% pythonic format.",
    version='0.5.3',
    author='Michał Kaczmarczyk',
    author_email='michal.s.kaczmarczyk@gmail.com',
    maintainer='Michał Kaczmarczyk',
    maintainer_email='michal.s.kaczmarczyk@gmail.com',
    license='MIT license',
    url='https://gitlab.com/kamichal/renew',
    long_description=long_description,
    long_description_content_type='text/x-rst; charset=UTF-8',
    packages=['renew'],
    requires=['six'],
    install_requires=['six'],
    keywords='',
    classifiers=[
        # https://pypi.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Code Generators',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
)
