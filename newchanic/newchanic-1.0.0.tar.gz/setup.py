import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="newchanic",
    version="1.0.0",
    description="Simulate a universe powered by Newton's mechanic",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Louis-Saglio/newchanic",
    author="Louis Saglio",
    author_email="louis.saglio@ynov.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["newchanic"],
    include_package_data=True,
    install_requires=["pygame"],
)
