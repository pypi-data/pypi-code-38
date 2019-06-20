#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Mon 12 Oct 2015 22:32:22 CEST

from setuptools import setup, dist

dist.Distribution(dict(setup_requires=['bob.extension']))

from bob.extension.utils import load_requirements, find_packages

install_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='bob.db.avspoof',
    version=version,
    description='Audio AVspoof Attack Database Access API for Bob',
    url='http://gitlab.idiap.ch/bob/bob.db.avspoof',
    license='BSD',
    author='Pavel Korshunov',
    author_email='pavel.korshunov@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=install_requires,

    entry_points={
        # bob database declaration
        'bob.db': [
            'avspoof = bob.db.avspoof.driver:Interface',
        ],
    },

    classifiers=[
        'Framework :: Bob',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Database :: Front-Ends',
    ],
)
