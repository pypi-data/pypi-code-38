# Upload package to PyPi.

from setuptools import setup

setup(name='yalecourses',
      version='0.1.2',
      description='Library for fetching data from the Yale Courses API.',
      url='https://github.com/ErikBoesen/yalecourses',
      author='Erik Boesen',
      author_email='me@erikboesen.com',
      license='GPL',
      packages=['yalecourses'],
      install_requires=['requests'])
