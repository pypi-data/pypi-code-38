#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from setuptools import setup, dist
dist.Distribution(dict(setup_requires=['bob.extension']))

# load the requirements.txt for additional requirements
from bob.extension.utils import load_requirements, find_packages
install_requires = load_requirements()

setup(
    name='bob.pad.vein',
    version=open("version.txt").read().rstrip(),
    description='Implements tools for spoofing or presentation attack detection in vein biometrics',
    url='https://gitlab.idiap.ch/bob/bob.pad.vein',
    license='GPLv3',
    author='Pedro Tome',
    author_email='pedro.tome@idiap.ch',
    maintainer='Andre Anjos',
    maintainer_email='andre.anjos@idiap.ch',
    keywords='bob',
    long_description=open('README.rst').read(),
    packages=find_packages('bob'),
    include_package_data=True,

    install_requires=install_requires,

    entry_points={

      # registered configurations:
      'bob.bio.config': [
        # databases
        'verafinger-pad = bob.pad.vein.configurations.verafinger',

        # baselines
        'fourier = bob.pad.vein.configurations.fourier',

        # other
        'parallel = bob.pad.vein.configurations.parallel',
        'gridio4g48 = bob.pad.vein.configurations.gridio4g48',
        'grid = bob.pad.vein.configurations.gridio4g48',
        ],

      },

    classifiers=[
      'Framework :: Bob',
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
    )
