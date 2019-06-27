import setuptools
from setuptools.command.install import install

from setup.PatchLibrary import PatchLibrary

with open("README.md", "r") as fh:
    long_description = fh.read()


class CustomInstallCommand(install):
    def run(self):
        install.run(self)

        self.run_command('patch')


setuptools.setup(
    cmdclass={
        'patch': PatchLibrary,
        'install': CustomInstallCommand
    },

    name="thunder-remote",
    version="0.6.2",
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
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries"
    ],
)
