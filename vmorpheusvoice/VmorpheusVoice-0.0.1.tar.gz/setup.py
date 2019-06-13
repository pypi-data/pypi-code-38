#!/usr/bin/env python

import os
import re
from typing import Any

from setuptools import setup, find_packages
with open("requirements.txt") as f:
    install_requires = f.readlines()

setup(name="VmorpheusVoice",
      version="0.0.1",
      description="Convertidor de voz con basado en machine learning",
      long_description="Convierto la voz si tu metes muestras pregrabadas",
      author="Valdr Stiglitz",
      author_email="valdr.stiglitz@gmail.com",
      url="https://github.com/ValdrST/VMorpheus_voice",
      packages=['VmorpheusVoice','VmorpheusVoice.tools','VmorpheusVoice.core.audio'],
      include_package_data=True,
      install_requires=install_requires,
      entry_points={
          'console_scripts': ['VmorpheusVoice = VmorpheusVoice:main']
      },
      classifiers=[
          'Programming Language :: Python :: 3']
    
      )