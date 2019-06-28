import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mr_streams",
    version="0.0.1",
    author="isConic",
    description="an anti-pythonic map reduce utility",
    long_description_content_type="text/markdown",
    long_description= long_description,
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)