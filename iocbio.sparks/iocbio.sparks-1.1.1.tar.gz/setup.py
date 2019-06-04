#!/usr/bin/env python3

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='iocbio.sparks',
      version='1.1.1',
      description='IOCBio Sparks: Semi-automatic calcium sparks detection software',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='IOCBio team',
      author_email='iocbio@sysbio.ioc.ee',
      license='GPLv3',
      url='https://gitlab.com/iocbio/sparks',
      packages=['iocbio.sparks',
                'iocbio.sparks.app',
                'iocbio.sparks.calc',
                'iocbio.sparks.gui',
                'iocbio.sparks.handler',
                'iocbio.sparks.io',
      ],
      entry_points={
          'gui_scripts': [
              'iocbio-sparks=iocbio.sparks.app.gui:main',
          ],
          'console_scripts': [
            'iocbio-sparks-synthetic = iocbio.sparks.app.synthetic_data:main',
            ],
          },
      package_data={'iocbio.sparks.app': ['*.png']},
      install_requires=[
          'tifffile',
          'PyQt5',
          'scipy',
          'numpy',
          'scikit-image',
          'pyqtgraph',
          'keyring',
          'psycopg2',
          'XlsxWriter',
          'records',
          'SQLAlchemy',
          'tablib',
          'Pillow'
      ],
      keywords = [],
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: X11 Applications :: Qt',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering',
      ],
     )
