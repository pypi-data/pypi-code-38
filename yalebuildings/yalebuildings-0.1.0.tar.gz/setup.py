# Upload package to PyPi.

from setuptools import setup

setup(name='yalebuildings',
      version='0.1.0',
      description='Library for fetching data from the Yale Buildings API.',
      url='https://github.com/ErikBoesen/yalebuildings',
      author='Erik Boesen',
      author_email='me@erikboesen.com',
      license='GPL',
      packages=['yalebuildings'],
      install_requires=['requests'])
