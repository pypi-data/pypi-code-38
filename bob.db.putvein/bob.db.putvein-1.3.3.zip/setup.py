#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension']))

from bob.extension.utils import load_requirements
install_requires = load_requirements()

version = open("version.txt").read().rstrip()

setup(

    name='bob.db.putvein',
    version=version,
    description='PUT Vein Database Access API for Bob',
    url='http://gitlab.idiap.ch/bob/bob.db.putvein',
    license='BSD',
    long_description=open('README.rst').read(),

    author='Philip Abbet',
    author_email='philip.abbet@idiap.ch',
    maintainer='Andre Anjos',
    maintainer_email='andre.anjos@idiap.ch',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires = install_requires,

    entry_points={
      'bob.db': [
        'putvein = bob.db.putvein.driver:Interface',
      ],
    },

    classifiers = [
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'Intended Audience :: Developers',
      'Intended Audience :: Education',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: BSD License',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      'Topic :: Database :: Front-Ends',
      ],
)
