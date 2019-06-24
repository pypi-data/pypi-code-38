import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PingPad",
    version="0.0.1",
    author="Bajato Madison",
    author_email="bayumunajat@gmail.com",
    description="Client-server ping sender and receiver",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/subajat1/PingPad",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
