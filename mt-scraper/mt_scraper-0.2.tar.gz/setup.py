from setuptools import setup, find_packages
from os.path import join, dirname
import mt_scraper

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'mt_scraper',
    version = mt_scraper.__version__,
    packages = find_packages(),
    #packages = [mt_scraper, ],
	author = mt_scraper.__author__,
    author_email = mt_scraper.__email__,
    description = "Easy multythread web scraper",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/pypa/sampleproject",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)