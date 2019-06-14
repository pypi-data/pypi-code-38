from subprocess import PIPE, Popen, call
import os.path

from distutils.core import setup

from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools import setup, find_packages

version = '0.7.1'

def download():
  p = Popen(["which", "ec"], stdout=PIPE, stderr=PIPE)
  stdout, _ = p.communicate()

  # Make a copy of the current environment
  env = {
    'EC_VERSION': version,
    'EC_DEST': os.path.dirname(stdout),
  }

  call(["./scripts/install.sh"], env=env)

class PostDevelopCommand(develop):
  def run(self):
    develop.run(self)
    download()

class PostInstallCommand(install):
  def run(self):
    install.run(self)
    download()

setup(
  name = 'eclectica',
  packages=find_packages(),
  package_data = {
    'scripts': ['scripts/install.sh'],
  },
  version = version,
  description = 'Cool and eclectic version manager for any language',
  author = 'Oleg Gaidarenko',
  author_email = 'markelog@gmail.com',
  url = 'https://github.com/markelog/eclectica',
  license = 'MIT',
  include_package_data=True,
  zip_safe=False,
  keywords = [
    'eclectica',
    'version',
    'manager',
    'binary',
    'environment'
  ],
  classifiers = [],
  cmdclass = {
    'develop': PostDevelopCommand,
    'install': PostInstallCommand,
  },
  entry_points={'console_scripts': [
    'ec = eclectica.main:main',
    'ec-proxy = eclectica.main:main']}
)
