import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="alephmarcreader",
    version="0.0.1",
    author="Tobias Schweizer, Digital Humanities Lab, University of Basel; Balduin Landolt, University of Basel",
    author_email="t.schweizer@unibas.ch",
    description="A package to read Marc files obtained from Aleph, catalogue of the library of the University of Basel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dhlab-basel/alephmarcreader.git",
    packages=setuptools.find_packages(exclude=("alephmarc21reader.tests",)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
)