# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup

version = '0.1.2'

setup(name='qgsgl',
      version=version,
      description='Convert QGIS project into webmapgl style',
      long_description='\n'.join([open(f).read() for f in [
          'README.md',
          'CHANGELOG.md'
      ]]),
      long_description_content_type='text/markdown',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Win32 (MS Windows)',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Topic :: Database',
          'Topic :: Scientific/Engineering :: GIS',
          'Programming Language :: Python :: 3.6',
      ],
      keywords='QGIS gl',
      author='Edmond Lai',
      author_email='klai@ccrpc.org',
      url='https://ccrpc.org/programs/transportation/',
      packages=find_packages(exclude=['ez_setup']),
      install_requires=[
      ],
      package_data={'qgsgl': ['tests/testdata/*.geojson',
                              'tests/testdata/*.gml',
                              'tests/testdata/*.xsd']},
      include_package_data=True
      )
