"""For distribution.
"""

from setuptools import setup, find_packages, find_namespace_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call


class PostDevelopCommand(develop):
  """Post-installation for development mode."""

  def run(self):
    check_call("apt-get install this-package".split())
    develop.run(self)


class PostInstallCommand(install):
  """Post-installation for installation mode."""

  def run(self):
    # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
    install.run(self)


setup(
    name="datahunters",
    version="0.0.9",
    description="library for collecting data",
    url="https://github.com/perceptance/datahunters",
    author="Jie Feng",
    author_email="jiefeng@perceptance.io",
    license="MIT",
    include_package_data=True,
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    install_requires=[],
    test_require=[])
