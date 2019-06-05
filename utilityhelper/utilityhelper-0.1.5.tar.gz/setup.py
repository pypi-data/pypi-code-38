#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import sys
from shutil import rmtree

from setuptools import setup, find_packages, Command
from distutils.command.build        import build as orig_build
from setuptools.command.install     import install as orig_install
from setuptools.command.bdist_egg   import bdist_egg as orig_bdist_egg
from setuptools.command.sdist       import sdist as orig_sdist
try:
    from wheel.bdist_wheel import bdist_wheel as orig_bdist_wheel
    haveWheel = True
except ImportError:
    haveWheel = False

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

about = {}

with open(os.path.join(here, "utilityhelper", "__version__.py")) as f:
    exec(f.read(), about)

setup_required = [
    "pbr"
]

install_required = [
    "pip>=9.0.1",
    "setuptools>=36.2.1",
]


# https://pypi.python.org/pypi/stdeb/0.8.5#quickstart-2-just-tell-me-the-fastest-way-to-make-a-deb
class DebCommand(Command):
    """Support for setup.py deb"""

    description = "Build and publish the .deb package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "deb_dist"))
        except Exception as e:
            pass
        self.status(u"Creating debian mainfest…")
        os.system(
            "python setup.py --command-packages=stdeb.command sdist_dsc -z artful --package3=pipenv --depends3=python3-virtualenv-clone"
        )
        self.status(u"Building .deb…")
        os.chdir("deb_dist/pipenv-{0}".format(about["__version__"]))
        os.system("dpkg-buildpackage -rfakeroot -uc -us")


if haveWheel:
    class wx_bdist_wheel(orig_bdist_wheel):
        def finalize_options(self):
            # Do a bit of monkey-patching to let bdist_wheel know that there
            # really are extension modules in this build, even though they are
            # not built here.
            def _has_ext_modules(self):
                return True
            from setuptools.dist import Distribution
            #Distribution.is_pure = _is_pure
            Distribution.has_ext_modules = _has_ext_modules

            orig_bdist_wheel.finalize_options(self)


        def run(self):
            # Ensure that there is a basic library build for bdist_egg to pull from.
            self.run_command("build")

            # Run the default bdist_wheel command
            orig_bdist_wheel.run(self)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        try:
            print("\033[1m{0}\033[0m".format(s))
        except:
            pass

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except Exception as e:
            pass
        self.status("Building Source distribution…")
        os.system("{0} setup.py sdist bdist_wheel".format(sys.executable))
        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")
        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(about["__version__"]))
        os.system("git push --tags")
        sys.exit()


# Map these new classes to the appropriate distutils command names.

CMDCLASS = {
    # 'build'       : orig_build,
    # 'bdist_egg'   : orig_bdist_egg,
    # 'install'     : orig_install,
    # 'sdist'       : orig_sdist,
    'upload'        : UploadCommand,
    'deb'           : DebCommand,
    }

# if haveWheel:
#     CMDCLASS['bdist_wheel'] = wx_bdist_wheel

# WARNING: Uploading via this command is deprecated, use twine to upload instead (https://pypi.org/p/twine/)
# error: Must create and upload files in one command (e.g. setup.py sdist upload)
# if sys.argv[-1] == "publish":
#     os.system("python setup.py sdist bdist_wheel upload")
#     sys.exit()

setup(
    name="utilityhelper",
    version=about["__version__"],
    description="assistant tool for coding",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Lemon Gong",
    author_email="gll72344@gmail.com",
    url="https://github.com/leileigong/utility-helper",
    packages=find_packages(exclude=[]),
    entry_points={
    },
    package_data={
        "": ["LICENSE", "NOTICES"],
    },
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*",
    setup_requires=setup_required,
    install_requires=install_required,
    extras_require={},
    include_package_data=True,
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    # pbr=True,
    platforms='any',
    cmdclass=CMDCLASS,
)



