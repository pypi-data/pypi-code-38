#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from setuptools import setup, dist
dist.Distribution(dict(setup_requires=['bob.extension']))

from bob.extension.utils import load_requirements, find_packages
install_requires = load_requirements()

setup(

    name='bob.db.fv3d',
    version=open("version.txt").read().rstrip(),
    description='3D Fingervein Database Access API for Bob',
    url='https://gitlab.idiap.ch/bob/bob.db.fv3d',
    license='BSD',

    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',

    keywords='fingervein recognition, bob, bob.db, VERA, Fingervein',

    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=install_requires,

    entry_points = {
      'bob.db': [
        'fv3d = bob.db.fv3d.driver:Interface',
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
