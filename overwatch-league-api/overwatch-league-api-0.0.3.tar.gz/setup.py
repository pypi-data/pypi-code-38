import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="overwatch-league-api",
    version="0.0.3",
    author="Summer Labs Inc.",
    author_email="admin@draftbuff.com",
    description="An Overwatch League API Client Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/draftbuff/overwatch-league-api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
