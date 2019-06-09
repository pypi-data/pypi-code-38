import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="atd_jobutil",
    version="0.0.3",
    author="City of Austin",
    author_email="transportation.data@austintexas.gov",
    description="Utilities for registering PostgREST scripting jobs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cityofaustin/atd-utils-jobs",
    install_requires = [
        "arrow",
        "requests",
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: Public Domain",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta", 
    ),
)

