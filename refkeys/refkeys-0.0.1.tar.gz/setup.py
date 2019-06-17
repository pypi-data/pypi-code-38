import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="refkeys",
    version="0.0.1",
    author="Ravin Kumar",
    author_email="mr.ravin_kumar@hotmail.com",
    description="This repository contains a tool for secret-sharing among two parties.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mr-ravin/refkeys",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
