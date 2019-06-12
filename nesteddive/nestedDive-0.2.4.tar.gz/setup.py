import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nestedDive",
    version="0.2.4",
    author="RoelVoordendag",
    author_email="rvoordendag@gmail.com",
    description="Sorter for nested items",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RoelVoordendag/Deepdive",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)