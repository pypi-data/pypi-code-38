import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "dataSaver",
    version = "0.0.1",
    author = "Pedro A. Favuzzi",
    author_email = "pa.favuzzi@gmail.com",
    description = "Utility to save data to cvs as an easy (and very basic) to read and use alternative to tensorboard",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/Pensarfeo/dataSaver",
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = [            # I get to this in a second
        'numpy',
    ],
)