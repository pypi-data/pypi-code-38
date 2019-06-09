import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="atd_socratautil",
    version="0.0.2",
    author="City of Austin",
    author_email="transportation.data@austintexas.gov",
    description="Utilities interacting with the Socrata Open Data API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cityofaustin/atd-utils-socrata",
    install_requires = [
        "atd_datautil",
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: Public Domain",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta", 
    ),
)

