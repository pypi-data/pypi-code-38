from setuptools import setup
from networktools.requeriments import read

requeriments = read()

setup(name='tasktools',
      version='0.9.1',
      description='Some useful tools for asycnio Tasks: async while, the Scheduler and Assignator classes',
      url='https://tasktools.readthedocs.io/en/latest/',
      author='David Pineda Osorio',
      author_email='dpineda@uchile.cl',
      license='GPL3',
      install_requires=requeriments,
      packages=['tasktools'],
      zip_safe=False)
