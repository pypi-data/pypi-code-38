import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.md'), encoding='UTF-8') as f:
    long_description = '\n' + f.read()

about = {}

with open(os.path.join(here, "__version__.py")) as f:
    exec(f.read(), about)


class DebianCommon(Command):
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
        except FileNotFoundError:
            pass
        self.status(u"Creating debian manifest…")
        os.system(
            "python setup.py --command-packages=stdeb.command sdist_dsc -z artful --package3=pipenv --depends3=python3-virtualenv-clone"
        )
        self.status(u"Building .deb…")
        os.chdir("deb_dist/pipenv-{0}".format(about["__version__"]))
        os.system("dpkg-buildpackage -rfakeroot -uc -us")


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status("Building Source distribution…")
        os.system("{0} setup.py sdist bdist_wheel".format(sys.executable))
        # os.system("{0} setup.py sdist bdist_wheel bdist_wininst".format(sys.executable))
        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")
        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(about["__version__"]))
        os.system("git push --tags")
        sys.exit()


setup(
    name="tan_up",
    version=about["__version__"],
    description="A tool of opening current folder in terminal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Xarrow/tan",
    author="helixcs",
    author_email="zhangjian12424@gmail.com",
    license="MIT",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    install_requires=[],
    keywords=["tan", "popup window", "opening current folder in terminal"],
    # If your package is a single module, use this instead of 'packages':
    py_modules=['tan', ],
    # If your package has custom module ,
    # Full list :https://docs.python.org/3.6/distutils/setupscript.html
    packages=find_packages(exclude=["tests"]),
    python_requires='>=3.6.0',
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
        "deb": DebianCommon
    },
    # packing to command tool interface
    entry_points={
        'console_scripts': ['tan=tan:tan_cli','tancp=tan:tancp_cli','tanls=tan:tanls_cli']
    }

)
