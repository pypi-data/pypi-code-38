import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "dataManager",
    version = "0.0.2",
    author = "Pedro A. Favuzzi",
    author_email = "pa.favuzzi@gmail.com",
    description = "A simple library to simplify data handling in deep learning environments. With an API non dissimilar to PyTorch DataLoader",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/Pensarfeo/DataManager",
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