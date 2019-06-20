import os
import glob
from distutils.core import setup

with open('VERSION') as version_file:
    version = version_file.read().strip()

scripts = glob.glob("bin/*")

setup(
  name='calio-toolbox',
  version=version,
  author='calio',
  author_email='vipcalio@gmail.com',
  url='https://gitlab.com/calio/toolbox',
  license="MIT",
  long_description="A collections of tools and libraries by calio",
  packages=['toolbox'],
  scripts=scripts,
  install_requires=["npyscreen"],
)
