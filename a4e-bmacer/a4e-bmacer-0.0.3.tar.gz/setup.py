import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="a4e-bmacer",
    version="0.0.3",
    author="Brandon Macer",
    author_email="bmacer@cisco.com",
    description="A package for using AMP for Endpoint API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/a4e",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)