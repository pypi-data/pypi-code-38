import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="promptory",
    version="0.0.0",
    author="Dustin Winski",
    author_email="dustinwinski@gmail.com",
    description="The simple Python library to create and manage document-based datastores that live as directories and JSON files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dustinwinski",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)

