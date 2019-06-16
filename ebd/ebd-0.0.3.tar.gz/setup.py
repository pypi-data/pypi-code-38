import setuptools
import setuptools.command
import setuptools.command.install
import os
import pathlib


class PostInstallCommand(setuptools.command.install.install):
    def run(self):
        rc_filename = os.path.join(pathlib.Path.home(), ".bashrc")
        if os.path.exists(rc_filename):
            with open(rc_filename) as file:
                print(file.read())
        else:
            print(f"{rc_filename} does not exist")
        setuptools.command.install.install.run(self)


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ebd",
    version="0.0.3",
    author="Fiely Teach",
    author_email="admin@admin.ru",
    description="Wrapper for LFSM-enabled systems.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    packages=setuptools.find_packages(),
    cmdclass={
        'install': PostInstallCommand
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
