from setuptools import setup, find_packages
import sys, os

version = '0.0.5'

setup(name='bgtask',
      version=version,
      description="Simple, Fast, Redis based background task manager",
      long_description="""\
Simple, Fast, Redis based background task manager""",
      classifiers=[],
      keywords='task, redis, background worker muilti process',
      author='Alexander.Li',
      author_email='superpowerlee@gmail.com',
      url='https://github.com/ipconfiger/bgtask',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'redis',
          'errorbuster'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
