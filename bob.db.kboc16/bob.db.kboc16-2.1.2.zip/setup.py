#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension']))

from bob.extension.utils import load_requirements
install_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='bob.db.kboc16',
    version=version,
    description='KBOC16 Database Access API for Bob',
    url='https://gitlab.idiap.ch/bob/bob.db.kboc16',
    license='BSD',
    author='Marta Gomez-Barrero',
    author_email='marta.gomez-barrero@h-da.de',
    maintainer='Andre Anjos',
    maintainer_email='andre.anjos@idiap.ch',
    keywords='keystroke recognition, bob, bob.db, kboc',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=install_requires,

    entry_points={
      'bob.db': [
        'kboc16 = bob.db.kboc16.driver:Interface',
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
