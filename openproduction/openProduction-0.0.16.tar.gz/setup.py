from setuptools import setup, find_packages
from setuptools.command.install import install
import logging

setup(name='openProduction',
      version='0.0.16',
      description='A framework to model device production',
      url='https://github.com/Coimbra1984/openProduction',
      author='Markus Proeller',
      author_email='markus.proeller@pieye.org',
      license='GPLv3',
      include_package_data=True,
      install_requires=[
        "appdirs", "yapsy", "PyMySQL", "cmd2", "GitPython", "PyQtChart", 
        "pysmb", "pandas", "colorama"
      ],
      packages=find_packages(),
      test_suite="openProduction.tests",
      package_data={'': ['*.py', '*.yapsy-plugin'] },
      zip_safe=False)