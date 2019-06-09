import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FundamentalAnalysis",
    version="0.1.2",
    author="JerBouma",
    author_email="jer.bouma@gmail.com",
    description="Allows for retrieving and analysing financial data of multiple companies at once.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JerBouma/FundamentalAnalysis",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)