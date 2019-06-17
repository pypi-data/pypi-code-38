from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(name='pollworker',
      version=version,
      description="Polling queue and distribute messages to worker processes and process it with your own function",
      long_description="""\
Polling queue and distribute messages to worker processes and process it with your own function""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='multiprocess, queue, redis, sqs, rebitmq, zmq',
      author='Alexander.Li',
      author_email='superpowerlee@gmail.com',
      url='https://github.com/ipconfiger/pollworker',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'errorbuster'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
