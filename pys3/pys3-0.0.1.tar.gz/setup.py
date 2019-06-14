import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pys3",
    version="0.0.1",
    author="pdboef",
    author_email="p.d.boef@drebble.io",
    description="Tiny wrapper for basic S3 functions in boto3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pdenboef/pys3.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)