#!/usr/bin/env python
import codecs
import os
import sys
from shutil import rmtree

from setuptools import setup, find_packages, Command

here = os.path.abspath(os.path.dirname(__file__))

# for "about", this example put all the information in __versions__.py. Alternative option is put all the information
# here, that means put in setup, but except __version__ information.
# for me, prefer use __versions__.py, it is integrate into the package.
about = {}

with open(os.path.join(here, "news2play", "__version__.py")) as f:
    exec(f.read(), about)

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

if sys.argv[-1] == "upload":
    os.system("python setup.py sdist bdist_wheel upload")
    sys.exit()

packages = find_packages(exclude=[''])

requires = [
    'spacy',
    'pydub',
    'simpleaudio',
    'pytz',
    'colorlog',
    'flask',
    'flask-httpauth',
]

extras = {
    "dev": [
        # "twine>=1.5.0",
        "twine"
    ],
    "tests": [],
}


class PublishCommand(Command):
    """Support setup.py publish."""

    description = "Build and publish the package."
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
            rmtree(os.path.join(here, "dist"))
        except FileNotFoundError:
            pass
        self.status("Building Source distribution…")
        os.system("{0} setup.py sdist bdist_wheel".format(sys.executable))
        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")
        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(about["__version__"]))
        os.system("git push --tags")
        sys.exit()


setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=packages,
    # package_dir={'': ''},
    python_requires=">=3.0, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*,",
    setup_requires=[],
    install_requires=requires,
    extras_requires=extras,
    include_package_data=True,
    license=about['__license__'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    cmdclass={"publish": PublishCommand}
)
