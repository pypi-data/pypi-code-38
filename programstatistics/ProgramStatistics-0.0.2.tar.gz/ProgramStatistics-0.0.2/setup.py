import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ProgramStatistics",
    version="0.0.2",
    author="JD.W-Christy",
    author_email="me@joshuawchristy.com",
    description="A set of tools for generating and perfroming statistics on \
                  abstract syntax trees ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abercon/Program-Statistics",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ])
