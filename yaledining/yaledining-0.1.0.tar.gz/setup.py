# Upload package to PyPi.

from setuptools import setup

setup(name='yaledining',
      version='0.1.0',
      description='Library for abstractly fetching data from the Yale Dining API.',
      url='https://github.com/ErikBoesen/yaledining',
      author='Erik Boesen',
      author_email='me@erikboesen.com',
      license='GPL',
      packages=['yaledining'],
      install_requires=['requests'])
