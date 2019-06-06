# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 11:22:24 2018

@author: kevin.stanton
"""

from setuptools import setup, find_packages

with open("ReadMe.md", "r") as fh:
    long_description = fh.read()

setup(name='autodyna',
      version='2.2.6',
      description='A collection of LS-DYNA card writing tools',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://gitlab.arup.com/kevin.stanton/AutomatedCardGenerator_LS-DYNA',
      author='Kevin Stanton',
      author_email='kevin.stanton@arup.com',
      install_requires=['matplotlib',
                        'numpy',
                        'pywin32',
                        'pandas',
                        'datetime',
                        'psutil',
                        'scipy'],
      packages=find_packages(),
      data_files=[('autodyna',
                   ['autodyna/inputs_elasticBeams.xlsx',
                    'autodyna/inputs_elasticBeams.csv',
                    'autodyna/inputs_elasticBeams.txt',
                    'autodyna/inputs_hysBeams.xlsx',
                    'autodyna/inputs_hysBeams.csv',
                    'autodyna/inputs_hysBeams.txt',
                    'autodyna/settings.txt']),
                  ('autodyna/Array_Formatting',
                   ['autodyna/Array_Formatting/FormatForDYNA.xlsm',
                    'autodyna/Array_Formatting/ReadMe.md']),
                  ('autodyna/Resources/XTRACT',
                   ['autodyna/Resources/XTRACT/iai.key',
                    'autodyna/Resources/XTRACT/SmallXTRACT.ico',
                    'autodyna/Resources/XTRACT/XTRACT.cnt',
                    'autodyna/Resources/XTRACT/XTRACT.exe',
                    'autodyna/Resources/XTRACT/XTRACT.GID',
                    'autodyna/Resources/XTRACT/atl.dll',
                    'autodyna/Resources/XTRACT/checkKey.dll',
                    'autodyna/Resources/XTRACT/GDI32.DLL'])],
      include_package_data=True)
