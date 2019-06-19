from shutil import copyfile

import setuptools
import imp
from setuptools.command.build_py import build_py

with open("README.md", "r") as fh:
    long_description = fh.read()


class UpdateLibrary(build_py):
    """
    Update 'inputs.py' for non-blocking gamepad access
    """
    def run(self):

        try:
            print("> START PATCHING!")
            copyfile('thunder_remote/patch/inputs.py', imp.find_module('inputs')[1])
            print("> PATCHING SUCCESSFUL!")
        except IOError:
            print("> PATCHING FAILED!")

        build_py.run(self)


setuptools.setup(
    cmdclass={
        'patch': UpdateLibrary
    },

    name="thunder-remote",
    version="0.6.0",
    author="Schrotty",
    author_email="rubenmaurer@live.de",
    description="A modified version of the 'pyController' package for usage with a ThunderBorg",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Schrotty/thunder-remote",
    keywords="thunder-borg borg remote-control remote rc",
    packages=setuptools.find_packages(),
    install_requires=[
        'inputs',
        'events',
        'enum34'
    ],
    license="MIT",
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries"
    ],
)