# Upload package to PyPi.

from setuptools import setup

setup(name='yaleorgdirectory',
      version='0.1.0',
      description='Library for fetching data from the Yale OrgDirectory API.',
      url='https://github.com/ErikBoesen/yaleorgdirectory',
      author='Erik Boesen',
      author_email='me@erikboesen.com',
      license='GPL',
      packages=['yaleorgdirectory'],
      install_requires=['requests'])
