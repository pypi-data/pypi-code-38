from setuptools import setup, find_packages
import sys, os

version = '0.0.2'

setup(name='silkworm',
      version=version,
      description="Utilities library for doing research with Prof. Roth",
      long_description="""\
SILKWORM is a set of Standard Integrated Libraries, Key for Working On Research at MESH. It is a collaborative project between undergraduates and graduates at IUB working for Prof. Roth that creates utiltities and shortcuts to make work more productive.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='silk worm silkworm roth utiltities util',
      author='Drason "Emmy" Chow',
      author_email='emchow@iu.edu',
      url='https://github.iu.edu/emchow/SILKWORM',
      license='MIT License',
      packages=['silkworm', 'silkworm.silktime'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
