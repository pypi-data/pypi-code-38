import setuptools
import setuptools.command
import setuptools.command.install
import setuptools.command.develop
import os
import pathlib


def get_rc_candidate():
    home = os.path.expanduser("~")
    bashrc = os.path.join(home, ".bashrc")
    if os.path.exists(bashrc):
        return bashrc
    profile = os.path.join(home, ".profile")
    if os.path.exists(profile):
        return profile


def setup_odus():
    rc = get_rc_candidate()
    if rc is not None:
        with open(rc) as file:
            print("rc file content:")
            print(file.read())
    else:
        print("no suitable rc found")


class PostInstallCommand(setuptools.command.install.install):
    def run(self):
        print("install command")
        setup_odus()
        setuptools.command.install.install.run(self)


class PostDevelopCommand(setuptools.command.develop.develop):
    def run(self):
        print("develop command")
        setuptools.command.develop.develop.run(self)


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ebd",
    version="0.0.6",
    author="Fiely Teach",
    author_email="admin@admin.ru",
    description="Wrapper for LFSM-enabled systems.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    packages=setuptools.find_packages(),
    cmdclass={
        "install": PostInstallCommand,
        "develop": PostDevelopCommand
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
