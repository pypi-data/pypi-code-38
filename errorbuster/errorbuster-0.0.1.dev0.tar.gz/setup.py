from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(name='errorbuster',
      version=version,
      description="Format traceback object to JSON for human read and easy process in Report System",
      long_description="""\
Format traceback object to JSON for human read and easy process in Report System""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='Error, Traceback',
      author='Alexander.Li',
      author_email='superpowerlee@gmail.com',
      url='https://github.com/ipconfiger/errorbuster',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
