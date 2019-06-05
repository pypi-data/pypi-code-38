from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

import versioneer

PACKAGE_NAME = "esgf-scraper"
AUTHOR = "Jared Lewis"
EMAIL = "jared.lewis@climate-energy-college.org"
URL = "https://gitlab.com/magicc/esgf-scraper"

DESCRIPTION = "Keeps a local data repository in syncronisation with ESGF"
README = "README.rst"

SOURCE_DIR = "src"

REQUIREMENTS = ["click", "scrapy", "esgf-pyclient", "myproxyclient", "pyyaml", "pandas"]
REQUIREMENTS_TESTS = ["codecov", "pytest-cov", "pytest>=4.0", "pytest-mock"]
REQUIREMENTS_DOCS = ["sphinx>=1.4", "sphinx_rtd_theme", "sphinx-click"]
REQUIREMENTS_DEPLOY = ["twine>=1.11.0", "setuptools>=38.6.0", "wheel>=0.31.0"]

requirements_dev = [
    *["flake8", "black", "isort"],
    *REQUIREMENTS_TESTS,
    *REQUIREMENTS_DOCS,
    *REQUIREMENTS_DEPLOY,
]

requirements_extras = {
    "docs": REQUIREMENTS_DOCS,
    "tests": REQUIREMENTS_TESTS,
    "deploy": REQUIREMENTS_DEPLOY,
    "dev": requirements_dev,
}

with open(README, "r") as readme_file:
    README_TEXT = readme_file.read()


class ESGFScrapper(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        pytest.main(self.test_args)


cmdclass = versioneer.get_cmdclass()
cmdclass.update({"test": ESGFScrapper})

setup(
    name=PACKAGE_NAME,
    version=versioneer.get_version(),
    description=DESCRIPTION,
    long_description=README_TEXT,
    long_description_content_type="text/x-rst",
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    project_urls={
        "Documentation": "https://magicc.gitlab.io/esgf-scraper/",
        "Source": "https://gitlab.com/magicc/esgf-scraper",
    },
    license="MIT License",
    classifiers=[  # full list at https://pypi.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords=["esgf", "cmip6", "scrape"],
    packages=find_packages(SOURCE_DIR),
    package_dir={"": SOURCE_DIR},
    install_requires=REQUIREMENTS,
    extras_require=requirements_extras,
    cmdclass=cmdclass,
    entry_points={"console_scripts": ["esgf=esgf_scraper.cli:cli"]},
)
