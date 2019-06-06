import setuptools
from larry import __author__, __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "larry-birdy",
    version = __version__,
    author = __author__,
	license = 'MIT',
	keywords = 'twitter api tweet larry birdy search',
    description = "A proof-of-concept sentence-oriented Twitter API client for Python, based on 'birdy'.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/programmatizoumenos/larry-birdy",
    packages = setuptools.find_packages(),
	include_package_data = True,
	install_requires = ['birdy'],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
	zip_safe = False
)