from distutils.command.build import build
from distutils.core import setup
from itertools import chain
from os.path import basename, dirname, join, splitext

from setuptools.command.develop import develop
from setuptools.command.easy_install import easy_install
from setuptools.command.install_lib import install_lib

pth_hook_file = "better_packaging.pth"


class BuildWithPTH(build):
    def run(self):
        build.run(self)
        path = join(dirname(__file__), pth_hook_file)
        dest = join(self.build_lib, basename(path))
        self.copy_file(path, dest)


class EasyInstallWithPTH(easy_install):
    def run(self):
        easy_install.run(self)
        path = join(dirname(__file__), pth_hook_file)
        dest = join(self.install_dir, basename(path))
        self.copy_file(path, dest)


class InstallLibWithPTH(install_lib):
    def run(self):
        install_lib.run(self)
        path = join(dirname(__file__), pth_hook_file)
        dest = join(self.install_dir, basename(path))
        self.copy_file(path, dest)
        self.outputs = [dest]

    def get_outputs(self):
        return chain(install_lib.get_outputs(self), self.outputs)


class DevelopWithPTH(develop):
    def run(self):
        develop.run(self)
        path = join(dirname(__file__), pth_hook_file)
        dest = join(self.install_dir, basename(path))
        self.copy_file(path, dest)


setup(
    name="better_packaging",
    packages=["better_packaging"],
    version="0.0.5",
    description="Automatically discover and install pip packages for local dev",
    author="Alexander Miasoiedov",
    author_email="github@myasoedv.com",
    url="",
    download_url="",
    keywords=[
        "pip",
        "pip install",
        "local",
        "locals",
        "autoinstall",
        "requirements.txt",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=["pigar", "better_exceptions"],
    cmdclass={
        "build": BuildWithPTH,
        "easy_install": EasyInstallWithPTH,
        "install_lib": InstallLibWithPTH,
        "develop": DevelopWithPTH,
    },
)
