import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='tornapi',
    version='0.0.1',
    license='MIT',
    author="Ryan Clark",
    author_email="nikkelclark@gmail.com",
    description="A python library to use torn api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NikkelClark/torn_api/python/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)