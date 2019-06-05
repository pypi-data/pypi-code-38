import setuptools

from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info

import time


class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        print("Installing..")
        time.sleep(60)
        print("Installing done!")


class CustomDevelopCommand(develop):
    def run(self):
        develop.run(self)


class CustomEggInfoCommand(egg_info):
    def run(self):
        egg_info.run(self)

setuptools.setup(
    name="simulating-pkg-taking-1min-to-install",
    version="0.0.1",
    author="Youngbin K",
    author_email="ykim828@hotmail.com",
    description="A small example package",
    packages=setuptools.find_packages(),
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
        'egg_info': CustomEggInfoCommand,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)