import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="pypaca",
    version="0.0.2",
    author="Vic Lee",
    author_email="viclee@nyu.edu",
    description="Simple utilities for complex projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vic-lee/pypaca",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
