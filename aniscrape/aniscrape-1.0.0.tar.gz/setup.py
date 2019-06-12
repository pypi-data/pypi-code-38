import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aniscrape",
    version="1.0.0",
    author="Tami ",
    author_email="tammyshead@tuta.io",
    description="Scraper for aniSearch.de and .com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TA40/aniScrape",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)